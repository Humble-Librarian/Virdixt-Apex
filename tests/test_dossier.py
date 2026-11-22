"""
Unit Tests for Wave 4: Autonomous Forensic Audit Dossier Compiler
"""

import time
import pytest
from apex.core.types import (
    ActivistShortThesis,
    ConvictionTier,
    TradeStructure,
    ForensicAccountingVector,
    AcousticBiomarkerVector,
    LinguisticObfuscationVector,
    InsiderFlowSummary,
)
from apex.dossier.compiler import ForensicDossierCompiler
from apex.core.memory_watchdog import MemoryWatchdog


class TestForensicDossierCompiler:
    """Verifies speed, structure, and deterministic generation of the short thesis dossier."""

    @pytest.fixture
    def sample_thesis(self):
        acct = ForensicAccountingVector(
            altman_z_score=1.15,
            altman_zone="DISTRESS",
            beneish_m_score=-1.45,
            beneish_risk="MANIPULATION_RISK",
            dechow_f_score=0.075,
            dechow_risk_multiple=6.8,
            sloan_accrual_ratio=0.18,
            sloan_anomaly_flag=True,
        )
        acoust = AcousticBiomarkerVector(
            f0_mean_hz=165.2,
            f0_std_hz=28.4,
            jitter_z_score=3.1,
            shimmer_local_db=1.4,
            hnr_db=12.1,
            cmdi_score=8.2,
            vocal_stress_rating="PANIC_ANOMALY",
            acute_stress_flag=True,
        )
        ling = LinguisticObfuscationVector(
            gunning_fog_index=20.5,
            epistemic_hedging_score=52.0,
            qa_semantic_alignment=0.31,
            is_evasive_deflection=True,
            sentiment_bullishness=0.88,
        )
        insider = InsiderFlowSummary(
            total_sales_value=4_250_000.0,
            total_purchases_value=0.0,
            opportunistic_sales_count=2,
            c_suite_sellers=["Greg Becker (CEO) - $3.5M", "Dan Beck (CFO) - $750k"],
            dump_velocity_v=32.0,
            is_abnormal_liquidation=True,
        )

        return ActivistShortThesis(
            ticker="SIVB",
            company_name="Silicon Valley Bank Financial Group",
            analysis_date="2023-03-08",
            asi_score=88.5,
            conviction_tier=ConvictionTier.CRITICAL_FRAUD_COLLAPSE,
            downside_target_percent=-85.0,
            recommended_trade_structure=TradeStructure.PUT_DEBIT_SPREAD,
            days_to_cover=9.2,
            borrow_fee_annual_percent=42.0,
            short_squeeze_risk_level="CRITICAL",
            key_forensic_catalysts=[
                "Beneish M-Score (-1.45) indicates revenue manipulation",
                "Dechow F-Score indicates 6.8x elevated misstatement risk",
                "Acoustic vocal jitter (+3.1σ) signals unscripted panic during liquidity queries",
                "C-suite opportunistic stock dumping ($4,250,000 extracted)",
            ],
            forensic_accounting=acct,
            acoustic_biomarkers=acoust,
            linguistic_vector=ling,
            insider_dump_summary=insider,
        )

    def test_dossier_markdown_compilation(self, sample_thesis):
        md = ForensicDossierCompiler.compile_markdown(sample_thesis)

        # Structure checks
        assert "# 🦅 VIRDIXT-APEX FORENSIC SHORT THESIS: SIVB" in md
        assert "ACTIVIST SHORT INDEX (ASI) : 88.5 / 100.0" in md
        assert "CRITICAL_FRAUD_COLLAPSE" in md
        assert "-85.0%" in md
        assert "PUT_DEBIT_SPREAD" in md

        # Key Sections checks
        assert "## 1. Executive Summary & Core Short Thesis" in md
        assert "## 2. Quantitative Accounting & Misstatement Audit" in md
        assert "## 3. Unscripted Acoustic Deception & Vocal Stress Audit" in md
        assert "## 4. Linguistic Obfuscation & Evasion Analysis" in md
        assert "## 5. SEC Form 4 C-Suite Capital Outflow" in md
        assert "## 6. Asymmetric Trade Structuring & Squeeze Management" in md
        assert "## 7. Mandatory Legal Disclaimers & Non-Commercial Disclosures" in md
        assert "Research Opinion Only" in md
        assert "No Fiduciary Duty & Assumption of Risk" in md

        # Content exactness checks
        assert "-1.45" in md  # Beneish score
        assert "+3.10σ" in md  # Jitter Z-score
        assert "$4,250,000.00" in md  # Insider sales
        assert "Greg Becker (CEO)" in md

    def test_dossier_compilation_latency_under_sla(self, sample_thesis):
        watchdog = MemoryWatchdog()
        _, metrics = watchdog.monitor(
            ForensicDossierCompiler.compile_markdown,
            sample_thesis,
            max_duration_ms=50.0  # Hardware SLA from config
        )
        assert metrics.duration_ms < 15.0  # Should run in < 2ms in pure Python
