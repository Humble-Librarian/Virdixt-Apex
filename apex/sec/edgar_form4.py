"""
High-Speed SEC Form 4 XML Parser & Insider Flow Vectorizer
Extracts C-suite equity transactions and classifies trades using the Cohen-Malloy-Pomorski (2012) framework.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from apex.config import CONFIG
from apex.core.types import InsiderTransaction, InsiderFlowSummary


# Normalized target C-suite officer titles
C_SUITE_TITLES = {
    "ceo", "chief executive officer",
    "cfo", "chief financial officer",
    "coo", "chief operating officer",
    "president", "general counsel",
    "director", "executive chairman"
}


class Form4Parser:
    """Fast XML parser for SEC Form 4 (Statement of Changes in Beneficial Ownership)."""

    @classmethod
    def parse_xml_string(cls, xml_content: str) -> List[InsiderTransaction]:
        """Parses raw Form 4 XML content into structured transactions."""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return []
        return cls._extract_transactions(root)

    @classmethod
    def parse_xml_file(cls, file_path: Path) -> List[InsiderTransaction]:
        """Parses a local Form 4 XML file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except (ET.ParseError, FileNotFoundError):
            return []
        return cls._extract_transactions(root)

    @classmethod
    def _extract_transactions(cls, root: ET.Element) -> List[InsiderTransaction]:
        transactions: List[InsiderTransaction] = []

        # 1. Extract Reporting Owner Info
        owner_name = "Unknown Insider"
        officer_title = "Officer"
        owner_elem = root.find(".//reportingOwner")
        if owner_elem is not None:
            name_elem = owner_elem.find(".//rptOwnerName")
            if name_elem is not None and name_elem.text:
                owner_name = name_elem.text.strip()

            title_elem = owner_elem.find(".//officerTitle")
            if title_elem is not None and title_elem.text:
                officer_title = title_elem.text.strip()
            else:
                # Check if director
                is_dir = owner_elem.find(".//isDirector")
                if is_dir is not None and is_dir.text in ("1", "true", "True"):
                    officer_title = "Director"

        # 2. Extract Non-Derivative Transactions (Direct stock sales/purchases)
        for tx_node in root.findall(".//nonDerivativeTransaction"):
            # Transaction Date
            date_elem = tx_node.find(".//transactionDate/value")
            tx_date = date_elem.text.strip() if date_elem is not None and date_elem.text else ""

            # Transaction Coding (P = Purchase, S = Sale, etc.)
            code_elem = tx_node.find(".//transactionCoding/transactionCode")
            tx_code = code_elem.text.strip() if code_elem is not None and code_elem.text else "U"

            # Shares
            shares_elem = tx_node.find(".//transactionAmounts/transactionShares/value")
            try:
                shares = float(shares_elem.text.strip()) if shares_elem is not None and shares_elem.text else 0.0
            except ValueError:
                shares = 0.0

            # Price Per Share
            price_elem = tx_node.find(".//transactionAmounts/transactionPricePerShare/value")
            try:
                price = float(price_elem.text.strip()) if price_elem is not None and price_elem.text else 0.0
            except ValueError:
                price = 0.0

            total_value = round(shares * price, 2)

            # Acquired/Disposed Code (A = Acquired, D = Disposed)
            ad_elem = tx_node.find(".//transactionAmounts/transactionAcquiredDisposedCode/value")
            ad_code = ad_elem.text.strip() if ad_elem is not None and ad_elem.text else ""

            # Normalize code: if Disposed and code is not P, treat as S
            if ad_code == "D" and tx_code not in ("P", "M"):
                tx_code = "S"

            transactions.append(
                InsiderTransaction(
                    filing_date=tx_date,
                    insider_name=owner_name,
                    officer_title=officer_title,
                    transaction_code=tx_code,
                    shares=shares,
                    price_per_share=price,
                    total_value=total_value,
                    is_opportunistic=True,  # Will be classified by Analyzer
                )
            )

        return transactions


class InsiderTradeAnalyzer:
    """
    Computes Net Outflow Velocity and applies the Cohen-Malloy-Pomorski (CMP)
    routine vs. opportunistic classification framework.
    """

    @staticmethod
    def is_c_suite(title: str) -> bool:
        """Determines if the officer title matches targeted C-suite positions."""
        title_lower = title.lower()
        # Exclude Vice Presidents unless they explicitly hold CEO/CFO/COO title
        if "vice president" in title_lower and not any(
            t in title_lower for t in ("chief executive", "chief financial", "chief operating")
        ):
            return False
        return any(c in title_lower for c in C_SUITE_TITLES)

    @classmethod
    def classify_routine_vs_opportunistic(
        cls,
        current_txs: List[InsiderTransaction],
        historical_txs: Optional[List[InsiderTransaction]] = None
    ) -> List[InsiderTransaction]:
        """
        Cohen, Malloy, & Pomorski (2012) Classifier:
        If an insider traded in the exact same calendar month in >= 2 prior years,
        the trade is marked as 'routine' (is_opportunistic = False).
        Otherwise, it is marked 'opportunistic'.
        """
        if not historical_txs:
            # Without multi-year history, assume opportunistic
            return current_txs

        # Map insider -> set of historical calendar months traded
        history_map: Dict[str, Dict[int, set[int]]] = {}
        for tx in historical_txs:
            try:
                dt = datetime.strptime(tx.filing_date, "%Y-%m-%d")
                insider = tx.insider_name.lower()
                if insider not in history_map:
                    history_map[insider] = {}
                if dt.month not in history_map[insider]:
                    history_map[insider][dt.month] = set()
                history_map[insider][dt.month].add(dt.year)
            except ValueError:
                continue

        classified: List[InsiderTransaction] = []
        for tx in current_txs:
            try:
                dt = datetime.strptime(tx.filing_date, "%Y-%m-%d")
                insider = tx.insider_name.lower()
                prior_years = history_map.get(insider, {}).get(dt.month, set())
                # If traded in this exact calendar month across >= 2 prior years
                is_routine = len(prior_years) >= 2
                tx.is_opportunistic = not is_routine
            except ValueError:
                tx.is_opportunistic = True
            classified.append(tx)

        return classified

    @classmethod
    def calculate_flow_summary(
        cls,
        transactions: List[InsiderTransaction],
        earnings_date: Optional[str] = None,
        lookback_days: int = 90,
        average_daily_volume_usd: float = 50_000_000.0,
    ) -> InsiderFlowSummary:
        """
        Aggregates insider dispositions within the pre-earnings window.
        Calculates Net Outflow Velocity (V_dump).
        """
        ref_date = datetime.strptime(earnings_date, "%Y-%m-%d") if earnings_date else datetime.now()
        window_start = ref_date - timedelta(days=lookback_days)

        sales_val = 0.0
        purchases_val = 0.0
        opp_sales = 0
        routine_sales = 0
        sellers: set[str] = set()

        for tx in transactions:
            # Date filter
            if tx.filing_date:
                try:
                    tx_dt = datetime.strptime(tx.filing_date, "%Y-%m-%d")
                    if tx_dt < window_start or tx_dt > ref_date:
                        continue
                except ValueError:
                    pass

            # Only track C-suite & Directors
            if not cls.is_c_suite(tx.officer_title):
                continue

            if tx.transaction_code == "S":
                sales_val += tx.total_value
                sellers.add(f"{tx.insider_name} ({tx.officer_title})")
                if tx.is_opportunistic:
                    opp_sales += 1
                else:
                    routine_sales += 1
            elif tx.transaction_code == "P":
                purchases_val += tx.total_value

        net_outflow = sales_val - purchases_val

        # Net Disposition Velocity V_dump (normalized 0 to 100)
        # Ratio of opportunistic sales relative to market average daily volume
        adv_ratio = (sales_val / max(average_daily_volume_usd, 1_000_000.0)) * 100.0
        v_dump = min(100.0, max(0.0, adv_ratio))

        is_abnormal = (sales_val > 2_000_000.0 and opp_sales >= 1) or (v_dump > 15.0)

        return InsiderFlowSummary(
            total_sales_value=round(sales_val, 2),
            total_purchases_value=round(purchases_val, 2),
            net_outflow_usd=round(net_outflow, 2),
            opportunistic_sales_count=opp_sales,
            routine_sales_count=routine_sales,
            c_suite_sellers=sorted(list(sellers)),
            dump_velocity_v=round(v_dump, 2),
            is_abnormal_liquidation=is_abnormal,
        )
