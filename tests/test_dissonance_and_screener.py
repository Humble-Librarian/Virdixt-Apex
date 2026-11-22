"""
Unit Tests for Wave 3: Cross-Modal Dissonance Engine and Activist Short Screener (ASI)
"""

import pytest
from apex.core.types import (
    ConvictionTier,
    TradeStructure,
    ForensicAccountingVector,
    AcousticBiomarkerVector,
    LinguisticObfuscationVector,
    InsiderFlowSummary,
)
from apex.dissonance.cross_modal import CrossModalDissonanceCalculator
from apex.screener.index import ActivistShortScreener


class TestCrossModalDissonance:
    """Tests cognitive disconnect calculations and acoustic multiplier scaling."""

    def test_congruent_clean_firm_low_dissonance(self):
        ling = LinguisticObfuscationVector(
            gunning_fog_index=12.0,
            epistemic_hedging_score=10.0,
            qa_semantic_alignment=0.85,
            is_evasive_deflection=False,
            sentiment_bullishness=0.6,
        )
        acct = ForensicAccountingVector(
            altman_z_score=4.5,
            altman_zone="SAFE",
            beneish_m_score=-2.8,
            beneish_risk="LOW_RISK",
            dechow_f_score=0.005,
            dechow_risk_multiple=0.45,
            sloan_accrual_ratio=-0.02,
            sloan_anomaly_flag=False,
        )
        acoust = AcousticBiomarkerVector(
            cmdi_score=1.5,
            vocal_stress_rating="CALM",
            acute_stress_flag=False,
        )

        res = CrossModalDissonanceCalculator.compute(ling, acct, acoust)
        assert res.dissonance_gap < 0.2
        assert res.acoustic_multiplier < 1.2
        assert res.accounting_penalty == 0.0
        assert res.composite_dissonance_score < 25.0

    def test_acute_dissonance_on_deceptive_firm(self):
        ling = LinguisticObfuscationVector(
            gunning_fog_index=21.0,
            epistemic_hedging_score=48.0,
            qa_semantic_alignment=0.25,
            is_evasive_deflection=True,
            sentiment_bullishness=0.9,  # Euphoric executive claims
        )
        acct = ForensicAccountingVector(
            altman_z_score=1.1,
            altman_zone="DISTRESS",
            beneish_m_score=-1.2,
            beneish_risk="MANIPULATION_RISK",
            dechow_f_score=0.08,
            dechow_risk_multiple=7.2,
            sloan_accrual_ratio=0.22,
            sloan_anomaly_flag=True,
        )
        acoust = AcousticBiomarkerVector(
            cmdi_score=8.5,
            vocal_stress_rating="PANIC_ANOMALY",
            acute_stress_flag=True,
        )

        res = CrossModalDissonanceCalculator.compute(ling, acct, acoust)
        assert res.dissonance_gap > 0.6
        assert res.acoustic_multiplier > 1.8
        assert res.accounting_penalty >= 50.0
        assert res.composite_dissonance_score > 85.0


class TestActivistShortScreener:
    """Verifies Activist Short Index (ASI) conviction, downside target, and trade structuring."""

    @pytest.fixture
    def clean_vectors(self):
        return {
            "acct": ForensicAccountingVector(
                altman_z_score=5.2,
                altman_zone="SAFE",
                beneish_m_score=-2.9,
                beneish_risk="LOW_RISK",
                dechow_f_score=0.005,
                dechow_risk_multiple=0.4,
                sloan_accrual_ratio=-0.05,
                sloan_anomaly_flag=False,
            ),
            "acoust": AcousticBiomarkerVector(
                cmdi_score=1.2,
                vocal_stress_rating="CALM",
                acute_stress_flag=False,
            ),
            "ling": LinguisticObfuscationVector(
                gunning_fog_index=11.5,
                epistemic_hedging_score=8.0,
                qa_semantic_alignment=0.88,
                is_evasive_deflection=False,
                sentiment_bullishness=0.6,
            ),
            "insider": InsiderFlowSummary(
                total_sales_value=0.0,
                total_purchases_value=500_000.0,
                is_abnormal_liquidation=False,
                dump_velocity_v=0.0,
            ),
        }

    @pytest.fixture
    def collapse_vectors(self):
        return {
            "acct": ForensicAccountingVector(
                altman_z_score=1.05,
                altman_zone="DISTRESS",
                beneish_m_score=-1.35,
                beneish_risk="MANIPULATION_RISK",
                dechow_f_score=0.065,
                dechow_risk_multiple=5.9,
                sloan_accrual_ratio=0.19,
                sloan_anomaly_flag=True,
            ),
            "acoust": AcousticBiomarkerVector(
                jitter_z_score=3.2,
                cmdi_score=8.8,
                vocal_stress_rating="PANIC_ANOMALY",
                acute_stress_flag=True,
            ),
            "ling": LinguisticObfuscationVector(
                gunning_fog_index=22.4,
                epistemic_hedging_score=55.0,
                qa_semantic_alignment=0.28,
                is_evasive_deflection=True,
                sentiment_bullishness=0.85,
            ),
            "insider": InsiderFlowSummary(
                total_sales_value=8_500_000.0,
                opportunistic_sales_count=4,
                dump_velocity_v=45.0,
                is_abnormal_liquidation=True,
                c_suite_sellers=["CEO ($4.5M)", "CFO ($4.0M)"],
            ),
        }

    def test_clean_firm_outputs_negligible_risk(self, clean_vectors):
        thesis = ActivistShortScreener.evaluate(
            ticker="AAPL",
            company_name="Apple Inc.",
            accounting=clean_vectors["acct"],
            acoustic=clean_vectors["acoust"],
            linguistic=clean_vectors["ling"],
            insider=clean_vectors["insider"],
            days_to_cover=2.0,
            borrow_fee_annual_percent=0.3,
        )
        assert thesis.asi_score < 30.0
        assert thesis.conviction_tier == ConvictionTier.NEGLIGIBLE_RISK
        assert thesis.downside_target_percent == 0.0
        assert thesis.recommended_trade_structure == TradeStructure.NO_ACTION_AVOID

    def test_collapse_firm_outputs_critical_short_conviction(self, collapse_vectors):
        thesis = ActivistShortScreener.evaluate(
            ticker="FRAUD",
            company_name="Apex Collapse Corp",
            accounting=collapse_vectors["acct"],
            acoustic=collapse_vectors["acoust"],
            linguistic=collapse_vectors["ling"],
            insider=collapse_vectors["insider"],
            days_to_cover=3.2,
            borrow_fee_annual_percent=3.5,
        )
        assert thesis.asi_score >= 85.0
        assert thesis.conviction_tier == ConvictionTier.CRITICAL_FRAUD_COLLAPSE
        assert thesis.downside_target_percent <= -70.0
        assert len(thesis.key_forensic_catalysts) >= 4

    def test_short_squeeze_gating_selects_options_spread(self, collapse_vectors):
        # High Days to Cover (DTC = 12.5 days) should trigger Put Debit Spread instead of outright short
        thesis = ActivistShortScreener.evaluate(
            ticker="SQUEEZE",
            company_name="Crowded Short Inc",
            accounting=collapse_vectors["acct"],
            acoustic=collapse_vectors["acoust"],
            linguistic=collapse_vectors["ling"],
            insider=collapse_vectors["insider"],
            days_to_cover=12.5,
            borrow_fee_annual_percent=45.0,
        )
        assert thesis.short_squeeze_risk_level == "CRITICAL"
        assert thesis.recommended_trade_structure == TradeStructure.PUT_DEBIT_SPREAD
