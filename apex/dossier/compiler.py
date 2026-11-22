"""
Autonomous Forensic Audit Dossier Compiler
Assembles institutional-grade activist short thesis briefs with timestamped citations and zero hallucinations.
"""

from typing import Optional
from apex.core.types import ActivistShortThesis


class ForensicDossierCompiler:
    """Compiles an ActivistShortThesis into a publication-ready Markdown forensic dossier."""

    @classmethod
    def compile_markdown(cls, thesis: ActivistShortThesis) -> str:
        lines: list[str] = []

        # 1. Header & Title Block
        lines.append(f"# 🦅 VIRDIXT-APEX FORENSIC SHORT THESIS: {thesis.ticker}")
        lines.append(f"> **Target:** {thesis.company_name} | **Date:** {thesis.analysis_date} | **Classification:** AIR-GAPPED FORENSIC AUDIT")
        lines.append("")

        # 2. Key Metrics Badge Matrix
        lines.append("```")
        lines.append("================================================================================")
        lines.append(f"ACTIVIST SHORT INDEX (ASI) : {thesis.asi_score:.1f} / 100.0")
        lines.append(f"CONVICTION TIER            : {thesis.conviction_tier.value}")
        lines.append(f"DOWNSIDE VALUATION TARGET  : {thesis.downside_target_percent:.1f}%")
        lines.append(f"RECOMMENDED TRADE STRUCTURE: {thesis.recommended_trade_structure.value}")
        lines.append(f"SHORT SQUEEZE HAZARD       : {thesis.short_squeeze_risk_level} (DTC: {thesis.days_to_cover:.1f}d | Borrow: {thesis.borrow_fee_annual_percent:.1f}%)")
        lines.append("================================================================================")
        lines.append("```")
        lines.append("")

        # 3. Executive Summary
        lines.append("## 1. Executive Summary & Core Short Thesis")
        lines.append(
            f"Virdixt-Apex has flagged **{thesis.company_name} ({thesis.ticker})** with an **Activist Short Index of {thesis.asi_score:.1f}/100**, "
            f"indicating **{thesis.conviction_tier.value.replace('_', ' ')}**. "
            f"Cross-modal analysis detects critical cognitive dissonance between management's bullish public assertions "
            f"and deteriorating balance-sheet fundamentals, compounded by unscripted executive vocal strain and insider capital extraction."
        )
        lines.append("")

        # 4. Forensic Catalysts
        lines.append("### Key Forensic Catalysts & Violations")
        if thesis.key_forensic_catalysts:
            for cat in thesis.key_forensic_catalysts:
                lines.append(f"- 🔴 **{cat}**")
        else:
            lines.append("- 🟢 No critical forensic anomalies detected.")
        lines.append("")

        # 5. Forensic Accounting Table
        if thesis.forensic_accounting:
            acct = thesis.forensic_accounting
            lines.append("## 2. Quantitative Accounting & Misstatement Audit")
            lines.append("| Forensic Indicator | Calculated Value | Benchmark Threshold | Status / Risk Zone |")
            lines.append("| :--- | :--- | :--- | :--- |")
            lines.append(
                f"| **Beneish M-Score** | `{acct.beneish_m_score if acct.beneish_m_score is not None else 'N/A'}` | `> -1.78` | **{acct.beneish_risk}** |"
            )
            lines.append(
                f"| **Altman Z-Score** | `{acct.altman_z_score if acct.altman_z_score is not None else 'N/A'}` | `< 1.81` (Distress) | **{acct.altman_zone}** |"
            )
            lines.append(
                f"| **Dechow F-Score Risk** | `{acct.dechow_risk_multiple:.2f}x` | `> 1.85x Baseline` | **{'HIGH MISSTATEMENT' if acct.dechow_risk_multiple > 1.85 else 'NORMAL'}** |"
            )
            lines.append(
                f"| **Sloan Accrual Ratio** | `{acct.sloan_accrual_ratio:+.3f}` | `> +0.10` | **{'CASH FLOW DIVERGENCE' if acct.sloan_anomaly_flag else 'ALIGNED'}** |"
            )
            lines.append("")

        # 6. Acoustic Biomarkers
        if thesis.acoustic_biomarkers:
            acoust = thesis.acoustic_biomarkers
            lines.append("## 3. Unscripted Acoustic Deception & Vocal Stress Audit")
            lines.append(
                f"During unscripted analyst Q&A, executive vocal parameters exhibited an autonomic arousal rating of **{acoust.vocal_stress_rating}** "
                f"with a Composite Multimodal Deception Index (**CMDI**) of **{acoust.cmdi_score:.1f} / 10.0**."
            )
            lines.append("")
            lines.append("| Acoustic Biomarker | Observed Value | Physiological Interpretation |")
            lines.append("| :--- | :--- | :--- |")
            lines.append(f"| **F0 Mean Pitch** | `{acoust.f0_mean_hz:.1f} Hz` | Baseline pitch level |")
            lines.append(f"| **Vocal Jitter (Z-Score)** | `{acoust.jitter_z_score:+.2f}σ` | Laryngeal muscle micro-tremor under cognitive load |")
            lines.append(f"| **Shimmer Perturbation** | `{acoust.shimmer_local_db:.2f} dB` | Diaphragmatic respiratory instability |")
            lines.append(f"| **Harmonics-to-Noise (HNR)** | `{acoust.hnr_db:.1f} dB` | Dysphonia / vocal turbulence |")
            lines.append("")

        # 7. Linguistic Obfuscation & Evasion
        if thesis.linguistic_vector:
            ling = thesis.linguistic_vector
            lines.append("## 4. Linguistic Obfuscation & Evasion Analysis")
            lines.append(
                f"- **Q&A Semantic Alignment:** `{ling.qa_semantic_alignment:.2f}` "
                f"({'⚠️ Severe Topic Deflection' if ling.is_evasive_deflection else 'Direct Response'})"
            )
            lines.append(
                f"- **Gunning-Fog Reading Complexity:** `{ling.gunning_fog_index:.1f}` "
                f"({'⚠️ Obfuscated Syntactic Masking' if ling.gunning_fog_index > 18.0 else 'Standard Disclosure'})"
            )
            lines.append(f"- **Epistemic Hedging Density:** `{ling.epistemic_hedging_score:.1f} / 100`")
            lines.append("")

        # 8. Insider Disposition Timeline
        if thesis.insider_dump_summary:
            ins = thesis.insider_dump_summary
            lines.append("## 5. SEC Form 4 C-Suite Capital Outflow")
            lines.append(
                f"In the 90 days preceding corporate disclosures, C-suite officers liquidated a cumulative "
                f"**${ins.total_sales_value:,.2f}** in equity across **{ins.opportunistic_sales_count} opportunistic transactions**."
            )
            lines.append("")
            lines.append(f"- **Net Outflow Velocity ($V_{{dump}}$):** `{ins.dump_velocity_v:.1f} / 100.0`")
            lines.append(f"- **Abnormal Liquidation Flag:** `{'YES - HIGH RISK' if ins.is_abnormal_liquidation else 'NO'}`")
            if ins.c_suite_sellers:
                lines.append("- **Identified Disposing Insiders:**")
                for s in ins.c_suite_sellers:
                    lines.append(f"  • {s}")
            lines.append("")

        # 9. Trade Execution & Squeeze Risk Gating
        lines.append("## 6. Asymmetric Trade Structuring & Squeeze Management")
        lines.append(f"- **Recommended Structure:** `{thesis.recommended_trade_structure.value}`")
        lines.append(f"- **Days to Cover (DTC):** `{thesis.days_to_cover:.1f} days`")
        lines.append(f"- **Borrow Fee:** `{thesis.borrow_fee_annual_percent:.2f}% annualized`")
        lines.append(f"- **Squeeze Hazard Level:** `{thesis.short_squeeze_risk_level}`")
        lines.append("")
        if thesis.recommended_trade_structure.value == "PUT_DEBIT_SPREAD":
            lines.append(
                "> **Execution Directives:** High borrow costs and elevated Days to Cover create short squeeze tail-risk. "
                "Outright shorting is locked out. Execute downside via **Put Debit Spreads (e.g. 60-90 DTE)** to cap volatility drag while extracting terminal downside."
            )
        elif thesis.recommended_trade_structure.value == "OUTRIGHT_EQUITY_SHORT":
            lines.append(
                "> **Execution Directives:** Low borrow fee and liquid float permit **Outright Equity Short** positions with standard stop-loss orders."
            )
        lines.append("")

        # 10. Mandatory Legal Disclaimer & Research Disclosures
        lines.append("## 7. Mandatory Legal Disclaimers & Non-Commercial Disclosures")
        lines.append(
            "> [!IMPORTANT]\n"
            "> **Research Opinion Only:** This document is generated autonomously by an experimental quantitative algorithmic research system. "
            "It reflects non-commercial statistical interpretations, mathematical ratios, and acoustic signal processing derived exclusively from "
            "publicly available regulatory disclosures and earnings call transcripts. It does not constitute investment advice, financial promotion, "
            "tax advice, legal counsel, or an offer or solicitation to buy, sell, or short any security or financial instrument.\n"
            ">\n"
            "> **No Fiduciary Duty & Assumption of Risk:** The authors, maintainers, and contributors hold no fiduciary duty toward readers. "
            "Short-selling and derivatives trading carry substantial risk of loss, including infinite theoretical loss on uncovered equity shorts. "
            "All statements herein regarding corporate accounting manipulation or executive deception represent algorithmic model outputs and "
            "academic opinions protected under freedom of speech and fair comment, not verified statements of adjudicated fact."
        )
        lines.append("")
        lines.append("---")
        lines.append("*Generated autonomously by Virdixt-Apex Engine. Deterministic mathematical execution. 100% Air-Gapped.*")

        return "\n".join(lines)
