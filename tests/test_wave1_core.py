"""
Unit & Integration Tests for Wave 1 Core Infrastructure
Verifies memory watchdog, domain models, forensic math, and core adapter.
"""

import pytest
from apex.config import CONFIG, ApexConfig
from apex.core.memory_watchdog import (
    MemoryWatchdog,
    MemoryBudgetExceededError,
    LatencyBudgetExceededError,
)
from apex.core.types import (
    ConvictionTier,
    TradeStructure,
    ForensicAccountingVector,
    AcousticBiomarkerVector,
    LinguisticObfuscationVector,
    ActivistShortThesis,
)
from apex.core.adapter import VirdixtCoreAdapter


class TestConfigAndHardwareEnvelope:
    """Verifies that all global constraints and scientific thresholds are loaded."""

    def test_hardware_limits_loaded(self):
        assert CONFIG.hardware.max_memory_mb == 950.0
        assert CONFIG.hardware.max_xml_parse_ms == 50.0
        assert CONFIG.hardware.max_asi_calc_ms == 5.0
        assert CONFIG.hardware.target_device == "cpu"

    def test_forensic_thresholds_match_research(self):
        assert CONFIG.thresholds.beneish_m_manipulation_threshold == -1.78
        assert CONFIG.thresholds.dechow_f_misstatement_threshold == 1.85
        assert CONFIG.thresholds.jitter_sigma_stress_threshold == 2.5
        assert CONFIG.thresholds.qa_semantic_alignment_min == 0.42
        assert CONFIG.thresholds.days_to_cover_squeeze_hazard == 8.0


class TestMemoryWatchdog:
    """Tests memory tracking, ceiling enforcement, and latency budgets."""

    def test_current_rss_within_hardware_budget(self):
        watchdog = MemoryWatchdog(max_memory_mb=950.0)
        current_mb = watchdog.assert_within_budget()
        assert current_mb > 0.0
        assert current_mb < 950.0, f"Process is using {current_mb} MB, exceeding 950 MB budget"

    def test_monitor_measures_latency_and_delta(self):
        watchdog = MemoryWatchdog()

        def dummy_calculation():
            return sum(i * i for i in range(10_000))

        result, metrics = watchdog.monitor(dummy_calculation, max_duration_ms=500.0)
        assert result > 0
        assert metrics.duration_ms < 500.0
        assert metrics.peak_memory_mb <= 950.0

    def test_memory_budget_exceeded_raises(self):
        # Artificially tiny ceiling to trigger watchdog
        strict_watchdog = MemoryWatchdog(max_memory_mb=1.0)
        with pytest.raises(MemoryBudgetExceededError):
            strict_watchdog.assert_within_budget()

    def test_latency_budget_exceeded_raises(self):
        watchdog = MemoryWatchdog()

        def slow_func():
            import time
            time.sleep(0.05)

        with pytest.raises(LatencyBudgetExceededError):
            watchdog.monitor(slow_func, max_duration_ms=5.0)


class TestCoreAdapterAndForensics:
    """Tests the deterministic accounting, linguistic, and acoustic engines."""

    @pytest.fixture
    def adapter(self):
        return VirdixtCoreAdapter()

    def test_altman_z_distress_detection(self, adapter):
        distressed_firm = {
            "working_capital": -50_000_000,
            "retained_earnings": -120_000_000,
            "ebit": -30_000_000,
            "market_cap": 20_000_000,
            "total_liabilities": 200_000_000,
            "sales": 80_000_000,
            "total_assets": 100_000_000,
        }
        vec = adapter.compute_accounting_vector(distressed_firm)
        assert vec.altman_z_score is not None
        assert vec.altman_z_score < 1.81
        assert vec.altman_zone == "DISTRESS"

    def test_beneish_m_manipulation_detection(self, adapter):
        manipulated_firm = {
            "dsri": 2.8,  # Huge surge in receivables vs sales (channel stuffing)
            "gmi": 1.6,   # Deteriorating gross margin
            "aqi": 1.5,
            "sgi": 1.8,
            "depi": 0.8,
            "sgai": 1.2,
            "lvgi": 1.4,
            "tata": 0.15, # High positive accruals
            "total_assets": 1_000_000,
        }
        vec = adapter.compute_accounting_vector(manipulated_firm)
        assert vec.beneish_m_score is not None
        assert vec.beneish_m_score > -1.78
        assert vec.beneish_risk == "MANIPULATION_RISK"

    def test_dechow_f_score_and_sloan_accruals(self, adapter):
        suspicious_accruals = {
            "total_assets": 500_000_000,
            "net_income": 80_000_000,
            "operating_cash_flow": -10_000_000,  # Cash flow is negative while net income is positive!
            "rsst_accrual": 1.10,
            "delta_receivables": 0.40,
            "delta_inventory": 0.25,
            "soft_assets_ratio": 0.85,
            "delta_cash_sales": -0.15,
            "delta_roa": -0.20,
            "securities_issued": True,
        }
        vec = adapter.compute_accounting_vector(suspicious_accruals)
        assert vec.sloan_accrual_ratio > 0.10
        assert vec.sloan_anomaly_flag is True
        assert vec.dechow_f_score is not None
        assert vec.dechow_risk_multiple > 1.85

    def test_linguistic_evasion_and_deflection(self, adapter):
        analyst_question = "Can you explain why Days Sales Outstanding increased from 42 days to 89 days in Europe?"
        evasive_answer = (
            "We are extraordinarily confident in our long-term secular runway and global momentum. "
            "Our market opportunities continue to expand and our teams are executing with excellence across all geographies."
        )
        ling_vec = adapter.analyze_linguistic_evasion(analyst_question, evasive_answer)
        assert ling_vec.is_evasive_deflection is True
        assert ling_vec.qa_semantic_alignment < 0.42
        assert ling_vec.gunning_fog_index > 10.0

    def test_acoustic_extraction_fallback(self, adapter):
        vec = adapter.extract_audio_biomarkers(None)
        assert isinstance(vec, AcousticBiomarkerVector)
        assert vec.f0_mean_hz > 0
        assert vec.jitter_local_percent > 0
        assert vec.cmdi_score >= 0.0
