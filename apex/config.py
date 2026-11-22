"""
Virdixt-Apex Global Configuration & Hardware Boundaries
Enforces deterministic runtime invariants and hardware ceilings for Intel i5 / 8GB RAM execution.
"""

from pathlib import Path
from pydantic import BaseModel, Field


class HardwareEnvelopeConfig(BaseModel):
    """Strict hardware constraints to prevent out-of-memory or thermal throttling."""
    max_memory_mb: float = Field(default=950.0, description="Hard ceiling for working set RAM in MB")
    max_xml_parse_ms: float = Field(default=50.0, description="Max acceptable latency per Form 4 XML parse")
    max_asi_calc_ms: float = Field(default=5.0, description="Max acceptable latency for ASI index calculation")
    max_dossier_gen_ms: float = Field(default=50.0, description="Max acceptable latency for dossier compilation")
    target_device: str = Field(default="cpu", description="Execution device (strictly cpu)")


class SecEdgarConfig(BaseModel):
    """SEC EDGAR API parameters and rate limit controls."""
    user_agent: str = Field(
        default="VirdixtApexResearch research@virdixt-apex.internal",
        description="Mandatory descriptive User-Agent header required by SEC"
    )
    submissions_endpoint: str = Field(
        default="https://data.sec.gov/submissions/CIK{cik_10}.json",
        description="Submissions JSON endpoint template"
    )
    facts_endpoint: str = Field(
        default="https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_10}.json",
        description="XBRL Company Facts endpoint template"
    )
    rate_limit_per_second: int = Field(default=5, description="Safe rate limit (<10 req/s ceiling)")
    pre_earnings_window_days: int = Field(default=90, description="Lookback window for Form 4 insider dumping")


class ForensicThresholds(BaseModel):
    """Empirical thresholds grounded in accounting and acoustic research literature."""
    # Forensic Accounting
    beneish_m_manipulation_threshold: float = Field(default=-1.78, description="Beneish M-Score fraud threshold")
    dechow_f_misstatement_threshold: float = Field(default=1.85, description="Dechow F-Score relative risk threshold")
    sloan_accrual_anomaly_threshold: float = Field(default=0.10, description="Excess accruals vs CFO threshold")

    # Acoustic Biomarkers (Hobson, Mayew & Venkatachalam 2012)
    jitter_sigma_stress_threshold: float = Field(default=2.5, description="Vocal jitter Z-score deviation")
    shimmer_sigma_stress_threshold: float = Field(default=2.0, description="Vocal shimmer amplitude perturbation")
    cmdi_high_dissonance_threshold: float = Field(default=5.0, description="Cross-Modal Dissonance Index threshold")

    # Linguistic Obfuscation & Evasion (DualEvasion ACL 2024)
    qa_semantic_alignment_min: float = Field(default=0.42, description="Min cosine similarity between Q and A")
    gunning_fog_obfuscation_threshold: float = Field(default=18.0, description="Gunning-Fog reading complexity index")
    hedging_score_high_threshold: float = Field(default=35.0, description="Linguistic hedging density score")

    # Short Squeeze & Borrow Risk Gating
    days_to_cover_squeeze_hazard: float = Field(default=8.0, description="Days to Cover squeeze risk threshold")
    borrow_fee_htb_hazard: float = Field(default=40.0, description="Annualized borrow fee % threshold")


class ApexConfig(BaseModel):
    """Master configuration container for Virdixt-Apex."""
    hardware: HardwareEnvelopeConfig = Field(default_factory=HardwareEnvelopeConfig)
    sec: SecEdgarConfig = Field(default_factory=SecEdgarConfig)
    thresholds: ForensicThresholds = Field(default_factory=ForensicThresholds)
    virdixt_base_dir: Path = Field(default=Path("D:/Virdixt"), description="Path to upstream Virdixt core")


# Global singleton instance
CONFIG = ApexConfig()
