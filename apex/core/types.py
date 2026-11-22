"""
Virdixt-Apex Domain Types & Data Contracts
Immutable, verified data structures defining the multimodal forensic pipeline.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConvictionTier(str, Enum):
    """Institutional Activist Short Conviction Levels."""
    NEGLIGIBLE_RISK = "NEGLIGIBLE_RISK"        # ASI < 30 (Clean, strong fundamentals)
    WATCHLIST = "WATCHLIST"                    # 30 <= ASI < 50 (Mild anomalies)
    MODERATE_DISSONANCE = "MODERATE_DISSONANCE"# 50 <= ASI < 70 (Material gaps)
    HIGH_CONVICTION_SHORT = "HIGH_CONVICTION_SHORT" # 70 <= ASI < 85 (Aggressive red flags)
    CRITICAL_FRAUD_COLLAPSE = "CRITICAL_FRAUD_COLLAPSE" # ASI >= 85 (Imminent failure / blowup)


class TradeStructure(str, Enum):
    """Execution strategy recommendations based on borrow & squeeze metrics."""
    OUTRIGHT_EQUITY_SHORT = "OUTRIGHT_EQUITY_SHORT"     # Low DTC, low borrow fee
    PUT_DEBIT_SPREAD = "PUT_DEBIT_SPREAD"               # Defined risk, elevated DTC
    LONG_PUT_ASYMMETRY = "LONG_PUT_ASYMMETRY"           # High squeeze hazard, high borrow
    NO_ACTION_AVOID = "NO_ACTION_AVOID"                 # Not actionable


class InsiderTransaction(BaseModel):
    """Individual SEC Form 4 transaction."""
    filing_date: str
    insider_name: str
    officer_title: str
    transaction_code: str  # P = Purchase, S = Sale, M = Option
    shares: float
    price_per_share: float
    total_value: float
    is_opportunistic: bool = True  # Cohen-Malloy classification


class InsiderFlowSummary(BaseModel):
    """Aggregated insider activity within the pre-earnings 90-day window."""
    total_sales_value: float = 0.0
    total_purchases_value: float = 0.0
    net_outflow_usd: float = 0.0
    opportunistic_sales_count: int = 0
    routine_sales_count: int = 0
    c_suite_sellers: List[str] = Field(default_factory=list)
    dump_velocity_v: float = 0.0  # V_dump score (0.0 to 100.0 normalized)
    is_abnormal_liquidation: bool = False


class AcousticBiomarkerVector(BaseModel):
    """Acoustic prosody and vocal stress parameters extracted from Q&A audio."""
    f0_mean_hz: float = 0.0
    f0_std_hz: float = 0.0
    jitter_local_percent: float = 0.0
    jitter_z_score: float = 0.0
    shimmer_local_db: float = 0.0
    shimmer_z_score: float = 0.0
    hnr_db: float = 0.0
    cmdi_score: float = 0.0  # Composite Multimodal Deception Index (0.0 to 10.0)
    vocal_stress_rating: str = "CALM"  # CALM, ELEVATED, PANIC_ANOMALY
    acute_stress_flag: bool = False


class ForensicAccountingVector(BaseModel):
    """Deterministic quantitative accounting benchmarks."""
    altman_z_score: Optional[float] = None
    altman_zone: str = "N/A"  # SAFE, GREY, DISTRESS
    beneish_m_score: Optional[float] = None
    beneish_risk: str = "N/A"  # LOW_RISK, MANIPULATION_RISK
    dechow_f_score: Optional[float] = None
    dechow_risk_multiple: float = 1.0  # Relative to 0.011 market baseline
    sloan_accrual_ratio: Optional[float] = None
    sloan_anomaly_flag: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class LinguisticObfuscationVector(BaseModel):
    """NLP deception and evasion metrics from unscripted conference call text."""
    gunning_fog_index: float = 0.0
    epistemic_hedging_score: float = 0.0  # 0.0 to 100.0
    qa_semantic_alignment: float = 1.0  # 0.0 to 1.0 (Cosine similarity)
    is_evasive_deflection: bool = False
    pronoun_depersonalization_ratio: float = 0.0
    sentiment_bullishness: float = 0.5  # 0.0 (Bearish) to 1.0 (Euphoric)


class DissonanceComposite(BaseModel):
    """Cross-modal delta measuring gap between verbal claims and fundamental/acoustic reality."""
    dissonance_gap: float = 0.0  # Raw divergence
    acoustic_multiplier: float = 1.0
    accounting_penalty: float = 0.0
    composite_dissonance_score: float = 0.0  # 0.0 to 100.0


class ActivistShortThesis(BaseModel):
    """Final institutional short report data package."""
    ticker: str
    company_name: str
    analysis_date: str
    asi_score: float = Field(ge=0.0, le=100.0, description="Activist Short Index 0-100")
    conviction_tier: ConvictionTier
    downside_target_percent: float = 0.0  # Expected downside e.g. -45%
    recommended_trade_structure: TradeStructure
    days_to_cover: float = 0.0
    borrow_fee_annual_percent: float = 0.0
    short_squeeze_risk_level: str = "LOW"
    key_forensic_catalysts: List[str] = Field(default_factory=list)
    timestamped_audio_citations: List[Dict[str, Any]] = Field(default_factory=list)
    insider_dump_summary: Optional[InsiderFlowSummary] = None
    forensic_accounting: Optional[ForensicAccountingVector] = None
    acoustic_biomarkers: Optional[AcousticBiomarkerVector] = None
    linguistic_vector: Optional[LinguisticObfuscationVector] = None
