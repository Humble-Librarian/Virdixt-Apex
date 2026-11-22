"""
Unit Tests for SEC Form 4 Parser & Cohen-Malloy Insider Flow Analyzer
"""

import time
import pytest
from apex.core.types import InsiderTransaction
from apex.sec.edgar_form4 import Form4Parser, InsiderTradeAnalyzer
from apex.core.memory_watchdog import MemoryWatchdog


# Realistic SEC Form 4 XML Snippet for a CEO disposing shares
SAMPLE_FORM4_XML = """<?xml version="1.0"?>
<ownershipDocument>
    <issuer>
        <issuerCik>0001067983</issuerCik>
        <issuerName>BERKSHIRE VENTURES CORP</issuerName>
        <issuerTradingSymbol>BVC</issuerTradingSymbol>
    </issuer>
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerName>Becker Gregory W</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isOfficer>1</isOfficer>
            <officerTitle>Chief Executive Officer</officerTitle>
        </reportingOwnerRelationship>
    </reportingOwner>
    <nonDerivativeTable>
        <nonDerivativeTransaction>
            <securityTitle>
                <value>Common Stock</value>
            </securityTitle>
            <transactionDate>
                <value>2023-02-27</value>
            </transactionDate>
            <transactionCoding>
                <transactionFormType>4</transactionFormType>
                <transactionCode>S</transactionCode>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares>
                    <value>12451</value>
                </transactionShares>
                <transactionPricePerShare>
                    <value>287.42</value>
                </transactionPricePerShare>
                <transactionAcquiredDisposedCode>
                    <value>D</value>
                </transactionAcquiredDisposedCode>
            </transactionAmounts>
            <postTransactionAmounts>
                <sharesOwnedFollowingTransaction>
                    <value>87200</value>
                </sharesOwnedFollowingTransaction>
            </postTransactionAmounts>
        </nonDerivativeTransaction>
    </nonDerivativeTable>
</ownershipDocument>
"""

# Purchase Form 4 XML snippet
SAMPLE_PURCHASE_XML = """<?xml version="1.0"?>
<ownershipDocument>
    <reportingOwner>
        <reportingOwnerId>
            <rptOwnerName>Chen Victoria</rptOwnerName>
        </reportingOwnerId>
        <reportingOwnerRelationship>
            <isOfficer>1</isOfficer>
            <officerTitle>Chief Financial Officer</officerTitle>
        </reportingOwnerRelationship>
    </reportingOwner>
    <nonDerivativeTable>
        <nonDerivativeTransaction>
            <transactionDate>
                <value>2023-02-15</value>
            </transactionDate>
            <transactionCoding>
                <transactionCode>P</transactionCode>
            </transactionCoding>
            <transactionAmounts>
                <transactionShares>
                    <value>5000</value>
                </transactionShares>
                <transactionPricePerShare>
                    <value>45.50</value>
                </transactionPricePerShare>
                <transactionAcquiredDisposedCode>
                    <value>A</value>
                </transactionAcquiredDisposedCode>
            </transactionAmounts>
        </nonDerivativeTransaction>
    </nonDerivativeTable>
</ownershipDocument>
"""


class TestForm4Parser:
    """Verifies speed, accuracy, and parsing of SEC Form 4 XML."""

    def test_parse_ceo_sale_xml(self):
        txs = Form4Parser.parse_xml_string(SAMPLE_FORM4_XML)
        assert len(txs) == 1
        tx = txs[0]
        assert tx.insider_name == "Becker Gregory W"
        assert tx.officer_title == "Chief Executive Officer"
        assert tx.transaction_code == "S"
        assert tx.shares == 12451.0
        assert tx.price_per_share == 287.42
        assert tx.total_value == round(12451.0 * 287.42, 2)
        assert tx.filing_date == "2023-02-27"

    def test_parse_cfo_purchase_xml(self):
        txs = Form4Parser.parse_xml_string(SAMPLE_PURCHASE_XML)
        assert len(txs) == 1
        tx = txs[0]
        assert tx.insider_name == "Chen Victoria"
        assert tx.officer_title == "Chief Financial Officer"
        assert tx.transaction_code == "P"
        assert tx.shares == 5000.0
        assert tx.price_per_share == 45.50
        assert tx.total_value == 227500.0

    def test_corrupt_xml_handled_gracefully(self):
        txs = Form4Parser.parse_xml_string("<corrupt<xml>>>")
        assert txs == []

    def test_malicious_entity_expansion_blocked(self):
        # Billion Laughs / entity expansion attack payload
        evil_xml = """<?xml version="1.0"?>
        <!DOCTYPE lolz [
         <!ENTITY lol "lol">
         <!ELEMENT lolz (#PCDATA)>
         <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
        ]>
        <ownershipDocument>&lol1;</ownershipDocument>
        """
        txs = Form4Parser.parse_xml_string(evil_xml)
        assert txs == []  # Rejected by security guard before parsing

    def test_oversize_xml_payload_rejected(self):
        # Oversize payload exceeding MAX_XML_PAYLOAD_BYTES
        huge_xml = "<ownershipDocument>" + (" " * (11 * 1024 * 1024)) + "</ownershipDocument>"
        txs = Form4Parser.parse_xml_string(huge_xml)
        assert txs == []

    def test_parsing_latency_under_sla(self):
        watchdog = MemoryWatchdog()
        _, metrics = watchdog.monitor(
            Form4Parser.parse_xml_string,
            SAMPLE_FORM4_XML,
            max_duration_ms=50.0  # Hardware SLA from config
        )
        assert metrics.duration_ms < 20.0  # Expected to be < 5ms in pure Python


class TestInsiderTradeAnalyzer:
    """Verifies Cohen-Malloy routine vs opportunistic classification and V_dump calculation."""

    def test_c_suite_title_detection(self):
        assert InsiderTradeAnalyzer.is_c_suite("Chief Executive Officer") is True
        assert InsiderTradeAnalyzer.is_c_suite("CFO & Treasurer") is True
        assert InsiderTradeAnalyzer.is_c_suite("Director") is True
        assert InsiderTradeAnalyzer.is_c_suite("Executive Vice President") is False
        assert InsiderTradeAnalyzer.is_c_suite("Senior Software Engineer") is False

    def test_cohen_malloy_routine_vs_opportunistic(self):
        # Historical trades in March 2021 and March 2022
        history = [
            InsiderTransaction(
                filing_date="2021-03-15",
                insider_name="John Doe",
                officer_title="CEO",
                transaction_code="S",
                shares=1000,
                price_per_share=50.0,
                total_value=50000.0,
            ),
            InsiderTransaction(
                filing_date="2022-03-14",
                insider_name="John Doe",
                officer_title="CEO",
                transaction_code="S",
                shares=1000,
                price_per_share=55.0,
                total_value=55000.0,
            ),
        ]

        # Current trade in March 2023 (should be classified ROUTINE because same calendar month)
        routine_tx = InsiderTransaction(
            filing_date="2023-03-16",
            insider_name="John Doe",
            officer_title="CEO",
            transaction_code="S",
            shares=1200,
            price_per_share=60.0,
            total_value=72000.0,
        )

        # Current trade in November 2023 (should be classified OPPORTUNISTIC)
        opp_tx = InsiderTransaction(
            filing_date="2023-11-05",
            insider_name="John Doe",
            officer_title="CEO",
            transaction_code="S",
            shares=50000,
            price_per_share=60.0,
            total_value=3000000.0,
        )

        classified = InsiderTradeAnalyzer.classify_routine_vs_opportunistic(
            [routine_tx, opp_tx], history
        )
        assert classified[0].is_opportunistic is False  # Routine calendar sale
        assert classified[1].is_opportunistic is True   # Irregular opportunistic sale

    def test_flow_summary_abnormal_liquidation(self):
        # Simulate SVB-style liquidation: CEO selling $3.57M days before collapse
        tx = Form4Parser.parse_xml_string(SAMPLE_FORM4_XML)[0]
        tx.is_opportunistic = True

        summary = InsiderTradeAnalyzer.calculate_flow_summary(
            [tx],
            earnings_date="2023-03-08",
            lookback_days=90,
            average_daily_volume_usd=20_000_000.0
        )

        assert summary.total_sales_value == round(12451.0 * 287.42, 2)
        assert summary.total_sales_value > 3_500_000.0
        assert summary.opportunistic_sales_count == 1
        assert summary.is_abnormal_liquidation is True
        assert summary.dump_velocity_v > 15.0
        assert "Becker Gregory W (Chief Executive Officer)" in summary.c_suite_sellers
