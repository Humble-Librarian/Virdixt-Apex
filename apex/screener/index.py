"""
Activist Short Screener & Conviction Index Engine
Combines forensic accounting, acoustic biomarkers, linguistic evasion, and insider dumping into the ASI score.
"""

import math
from datetime import datetime
from typing import List, Dict, Any, Optional

from apex.config import CONFIG
from apex.core.types import (
    ActivistShortThesis,
    ConvictionTier,
    TradeStructure,
    ForensicAccountingVector,
    AcousticBiomarkerVector,
    LinguisticObfuscationVector,
    InsiderFlowSummary,
    DissonanceComposite,
)
from apex.dissonance.cross_modal import CrossModalDissonanceCalculator


class ActivistShortScreener:
    """Computes the Activist Short Index (ASI) and structures the asymmetric short thesis."""

    @classmethod
    def evaluate(
        cls,
        ticker: str,
        company_name: str,
        accounting: ForensicAccountingVector,
        acoustic: AcousticBiomarkerVector,
        linguistic: LinguisticObfuscationVector,
        insider: Optional[InsiderFlowSummary] = None,
        days_to_cover: float = 3.5,
        borrow_fee_annual_percent: float = 2.5,
        analysis_date: Optional[str] = None,
    ) -> ActivistShortThesis:
        today = analysis_date or datetime.now().strftime("%Y-%m-%d")

        # 1. Compute Cross-Modal Dissonance
        dissonance = CrossModalDissonanceCalculator.compute(
            linguistic=linguistic,
            accounting=accounting,
            acoustic=acoustic,
        )

        # 2. Forensic Accounting Risk Subscore (0 to 100)
        acct_score = 10.0
        if accounting.beneish_m_score is not None:
            # Beneish: -3.0 (Clean) to 0.0 (Extreme manipulation)
            m = accounting.beneish_m_score
            acct_score = min(100.0, max(0.0, (m + 3.0) * 33.3))
            if accounting.beneish_risk == "MANIPULATION_RISK":
                acct_score = max(acct_score, 75.0)

        if accounting.dechow_risk_multiple > 1.85:
            acct_score = max(acct_score, 70.0)
        if accounting.sloan_anomaly_flag:
            acct_score = min(100.0, acct_score + 15.0)
        if accounting.altman_zone == "DISTRESS":
            acct_score = min(100.0, acct_score + 20.0)

        # 3. Acoustic Deception Subscore (0 to 100)
        acoust_score = min(100.0, max(0.0, acoustic.cmdi_score * 10.0))
        if acoustic.acute_stress_flag:
            acoust_score = max(acoust_score, 75.0)

        # 4. Linguistic Obfuscation Subscore (0 to 100)
        ling_score = min(100.0, max(0.0, linguistic.epistemic_hedging_score))
        if linguistic.is_evasive_deflection:
            ling_score = min(100.0, ling_score + 25.0)
        if linguistic.gunning_fog_index > CONFIG.thresholds.gunning_fog_obfuscation_threshold:
            ling_score = min(100.0, ling_score + 15.0)

        # 5. Insider Liquidation Subscore (0 to 100)
        insider_score = 0.0
        if insider is not None:
            insider_score = min(100.0, max(0.0, insider.dump_velocity_v))
            if insider.is_abnormal_liquidation:
                insider_score = max(insider_score, 75.0)

        # 6. Activist Short Index (ASI) Weighted Synthesis
        w_acct = 0.35
        w_acoust = 0.25
        w_ling = 0.20
        w_insider = 0.20

        raw_asi = (
            w_acct * acct_score
            + w_acoust * acoust_score
            + w_ling * ling_score
            + w_insider * insider_score
        )

        # Cross-Modal Dissonance Booster (Non-linear cognitive disconnect penalty)
        if dissonance.composite_dissonance_score > 60.0:
            boost = (dissonance.composite_dissonance_score - 60.0) * 0.25
            raw_asi = min(100.0, raw_asi + boost)

        asi = round(min(100.0, max(0.0, raw_asi)), 1)

        # 7. Map Conviction Tier
        tier = cls._determine_tier(asi)

        # 8. Downside Valuation Target
        downside_pct = cls._estimate_downside(asi, accounting)

        # 9. Short Squeeze & Trade Structure Selection
        trade_struct, squeeze_risk = cls._structure_trade(
            asi=asi,
            dtc=days_to_cover,
            borrow_fee=borrow_fee_annual_percent,
        )

        # 10. Catalysts & Citations
        catalysts = cls._compile_catalysts(accounting, acoustic, linguistic, insider)

        return ActivistShortThesis(
            ticker=ticker.upper(),
            company_name=company_name,
            analysis_date=today,
            asi_score=asi,
            conviction_tier=tier,
            downside_target_percent=downside_pct,
            recommended_trade_structure=trade_struct,
            days_to_cover=round(days_to_cover, 1),
            borrow_fee_annual_percent=round(borrow_fee_annual_percent, 2),
            short_squeeze_risk_level=squeeze_risk,
            key_forensic_catalysts=catalysts,
            insider_dump_summary=insider,
            forensic_accounting=accounting,
            acoustic_biomarkers=acoustic,
            linguistic_vector=linguistic,
        )

    @staticmethod
    def _determine_tier(asi: float) -> ConvictionTier:
        if asi >= 85.0:
            return ConvictionTier.CRITICAL_FRAUD_COLLAPSE
        if asi >= 70.0:
            return ConvictionTier.HIGH_CONVICTION_SHORT
        if asi >= 50.0:
            return ConvictionTier.MODERATE_DISSONANCE
        if asi >= 30.0:
            return ConvictionTier.WATCHLIST
        return ConvictionTier.NEGLIGIBLE_RISK

    @staticmethod
    def _estimate_downside(asi: float, accounting: ForensicAccountingVector) -> float:
        """Estimates probable percentage downside revaluation."""
        if asi < 30.0:
            return 0.0
        base_downside = (asi / 100.0) * 65.0  # Up to -65% baseline
        if accounting.beneish_risk == "MANIPULATION_RISK":
            base_downside += 15.0
        if accounting.altman_zone == "DISTRESS":
            base_downside += 10.0
        return -round(min(95.0, base_downside), 1)

    @staticmethod
    def _structure_trade(asi: float, dtc: float, borrow_fee: float) -> tuple[TradeStructure, str]:
        """Gates short positioning against short squeezes and high borrow costs."""
        if asi < 50.0:
            return TradeStructure.NO_ACTION_AVOID, "LOW"

        is_high_dtc = dtc > CONFIG.thresholds.days_to_cover_squeeze_hazard
        is_high_borrow = borrow_fee > CONFIG.thresholds.borrow_fee_htb_hazard

        if is_high_dtc or is_high_borrow:
            squeeze_risk = "CRITICAL" if (is_high_dtc and is_high_borrow) else "HIGH"
            # High squeeze risk: use options to avoid infinite upside risk
            return TradeStructure.PUT_DEBIT_SPREAD, squeeze_risk
        elif dtc > 5.0 or borrow_fee > 15.0:
            return TradeStructure.LONG_PUT_ASYMMETRY, "MODERATE"
        else:
            return TradeStructure.OUTRIGHT_EQUITY_SHORT, "LOW"

    @staticmethod
    def _compile_catalysts(
        accounting: ForensicAccountingVector,
        acoustic: AcousticBiomarkerVector,
        linguistic: LinguisticObfuscationVector,
        insider: Optional[InsiderFlowSummary]
    ) -> List[str]:
        catalysts = []
        if accounting.beneish_risk == "MANIPULATION_RISK":
            catalysts.append(f"Beneish M-Score ({accounting.beneish_m_score}) breaches manipulation threshold (-1.78)")
        if accounting.dechow_risk_multiple > 1.85:
            catalysts.append(f"Dechow F-Score indicates {accounting.dechow_risk_multiple:.1f}x elevated misstatement risk")
        if accounting.sloan_anomaly_flag:
            catalysts.append(f"Sloan Accruals ({accounting.sloan_accrual_ratio:+.2f}) reveal cash flow divergence")
        if accounting.altman_zone == "DISTRESS":
            catalysts.append(f"Altman Z-Score ({accounting.altman_z_score}) in severe insolvency distress zone")
        if acoustic.acute_stress_flag:
            catalysts.append(f"Acoustic vocal jitter ({acoustic.jitter_z_score:+.1f}σ) signals executive deception")
        if linguistic.is_evasive_deflection:
            catalysts.append(f"Q&A semantic alignment ({linguistic.qa_semantic_alignment:.2f}) flags intentional deflection")
        if insider and insider.is_abnormal_liquidation:
            catalysts.append(f"C-suite opportunistic stock dumping (${insider.total_sales_value:,.0f} extracted)")
        return catalysts
