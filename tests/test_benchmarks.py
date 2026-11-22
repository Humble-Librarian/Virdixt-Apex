"""
Integration & Regression Tests for Wave 5: Historical Blowup Benchmarks
"""

import pytest
from pathlib import Path
from benchmarks.run_benchmarks import load_case, run_benchmark_case, CASES_DIR
from apex.core.types import ConvictionTier, TradeStructure
from apex.core.memory_watchdog import MemoryWatchdog


class TestGoldenBlowupBenchmarks:
    """Verifies that historic blowup cases trigger critical conviction while clean controls remain safe."""

    def test_silicon_valley_bank_collapse_detection(self):
        case_data = load_case(CASES_DIR / "svb_2023.json")
        thesis, dossier_md = run_benchmark_case(case_data)

        assert thesis.ticker == "SIVB"
        assert thesis.asi_score >= 85.0
        assert thesis.conviction_tier == ConvictionTier.CRITICAL_FRAUD_COLLAPSE
        assert thesis.downside_target_percent <= -75.0
        assert thesis.recommended_trade_structure == TradeStructure.PUT_DEBIT_SPREAD
        assert thesis.short_squeeze_risk_level in ("HIGH", "CRITICAL")

        # Dossier evidence verification
        assert "Silicon Valley Bank Financial Group" in dossier_md
        assert "Gregory W. Becker" in dossier_md
        assert "3.40σ" in dossier_md

    def test_carvana_debt_restructuring_distress(self):
        case_data = load_case(CASES_DIR / "carvana_2022.json")
        thesis, dossier_md = run_benchmark_case(case_data)

        assert thesis.ticker == "CVNA"
        assert thesis.asi_score >= 85.0
        assert thesis.conviction_tier == ConvictionTier.CRITICAL_FRAUD_COLLAPSE
        assert thesis.downside_target_percent <= -75.0
        assert thesis.forensic_accounting.beneish_risk == "MANIPULATION_RISK"
        assert "Ernie Garcia III" in dossier_md

    def test_wirecard_fraud_collapse_detection(self):
        case_data = load_case(CASES_DIR / "wirecard_2020.json")
        thesis, dossier_md = run_benchmark_case(case_data)

        assert thesis.ticker == "WDI"
        assert thesis.asi_score >= 85.0
        assert thesis.conviction_tier == ConvictionTier.CRITICAL_FRAUD_COLLAPSE
        assert thesis.forensic_accounting.sloan_anomaly_flag is True
        assert thesis.forensic_accounting.dechow_risk_multiple > 1.85
        assert "Markus Braun" in dossier_md

    def test_apple_clean_control_safety(self):
        case_data = load_case(CASES_DIR / "apple_clean_control.json")
        thesis, dossier_md = run_benchmark_case(case_data)

        assert thesis.ticker == "AAPL"
        assert thesis.asi_score <= 25.0
        assert thesis.conviction_tier == ConvictionTier.NEGLIGIBLE_RISK
        assert thesis.downside_target_percent == 0.0
        assert thesis.recommended_trade_structure == TradeStructure.NO_ACTION_AVOID
        assert thesis.insider_dump_summary.is_abnormal_liquidation is False

    def test_all_benchmarks_within_memory_budget(self):
        watchdog = MemoryWatchdog(max_memory_mb=950.0)
        current_mem = watchdog.assert_within_budget()
        assert current_mem < 950.0, f"Memory exceeded hardware limit: {current_mem:.2f} MB"
