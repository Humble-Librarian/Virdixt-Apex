"""
Cross-Modal Dissonance Engine
Quantifies the cognitive dissonance gap between verbal cheerleading and fundamental/acoustic reality.
"""

from typing import Dict, Any, Optional
from apex.config import CONFIG
from apex.core.types import (
    AcousticBiomarkerVector,
    ForensicAccountingVector,
    LinguisticObfuscationVector,
    DissonanceComposite,
)


class CrossModalDissonanceCalculator:
    """
    Computes cross-modal divergence:
    Dissonance = max(0, Verbal Sentiment - Fundamental Margin Trend) * (1 + CMDI / 10) + Accounting Penalty
    """

    @classmethod
    def compute(
        cls,
        linguistic: LinguisticObfuscationVector,
        accounting: ForensicAccountingVector,
        acoustic: AcousticBiomarkerVector,
    ) -> DissonanceComposite:
        # 1. Fundamental Trend (Normalized from -1.0 to 1.0)
        # Healthy firms with low accruals and safe Altman Z have high fundamental score
        fund_score = 0.5  # Neutral default
        if accounting.altman_z_score is not None:
            if accounting.altman_z_score >= 3.0:
                fund_score += 0.3
            elif accounting.altman_z_score < 1.8:
                fund_score -= 0.4

        if accounting.sloan_anomaly_flag:
            fund_score -= 0.3

        fund_score = min(1.0, max(-1.0, fund_score))

        # 2. Verbal Sentiment (0.0 Bearish to 1.0 Bullish)
        verbal_bullishness = linguistic.sentiment_bullishness

        # Gap: Executive claims are bullish while fundamentals are negative/compressing
        raw_gap = max(0.0, verbal_bullishness - max(0.0, fund_score))

        # 3. Acoustic Dissonance Multiplier (1.0 to 2.0x)
        # Hobson, Mayew, Venkatachalam (2012): vocal stress under cognitive load compounds dissonance
        cmdi_clamped = min(10.0, max(0.0, acoustic.cmdi_score))
        acoustic_multiplier = 1.0 + (cmdi_clamped / 10.0)

        # 4. Accounting Penalty
        # If Beneish indicates manipulation, add direct penalty
        acct_penalty = 0.0
        if accounting.beneish_risk == "MANIPULATION_RISK":
            acct_penalty += 25.0
        if accounting.dechow_risk_multiple > CONFIG.thresholds.dechow_f_misstatement_threshold:
            acct_penalty += 20.0
        if accounting.sloan_anomaly_flag:
            acct_penalty += 15.0

        # 5. Composite Dissonance Score (0.0 to 100.0)
        gap_component = raw_gap * 40.0 * acoustic_multiplier
        composite_score = min(100.0, max(0.0, gap_component + acct_penalty))

        return DissonanceComposite(
            dissonance_gap=round(raw_gap, 3),
            acoustic_multiplier=round(acoustic_multiplier, 2),
            accounting_penalty=round(acct_penalty, 2),
            composite_dissonance_score=round(composite_score, 2),
        )
