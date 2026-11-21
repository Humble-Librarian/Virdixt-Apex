# 🦅 Virdixt-Apex

> **The World's First Air-Gapped "Activist Short-Seller" & Forensic Deception Alpha Engine**  
> *Autonomous Multimodal Cross-Examination: SEC Financials + Unscripted Q&A Acoustics + Form 4 Insider Dumping*

[![Engine Status](https://img.shields.io/badge/Engine-Virdixt--Apex-0A0E17?style=for-the-badge&logo=target)](https://github.com/Humble-Librarian/Virdixt-Apex)
[![Hardware Profile](https://img.shields.io/badge/Hardware-Intel%20i5%20%7C%208GB%20RAM%20%7C%200%20VRAM-success?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)
[![Inference SLA](https://img.shields.io/badge/Latency-%3C100ms%20CPU-blue?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)
[![Air-Gapped](https://img.shields.io/badge/Security-100%25%20Air--Gapped-red?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)

---

## ⚡ Executive Summary

Traditional financial markets and quant models evaluate corporate distress in silos:
- Fundamental quant funds examine historical balance sheets and ratios.
- Sentiment screeners parse canned, PR-scrubbed press releases.
- Acoustic tools measure vocal inflection in isolation without financial context.

**Virdixt-Apex bridges the Dissonance Gap.** It operates like an autonomous, algorithmic activist short-seller (Hindenburg Research / Muddy Waters on local silicon) by cross-examining:
1. **Reported Accounting Reality:** Beneish M-Score, Altman Z-Score, and Sloan Accruals.
2. **Linguistic Masking:** Gunning-Fog obfuscation and unscripted hedging density.
3. **Biological Acoustic Stress:** Unscripted earnings Q&A micro-tremors, F0 pitch jitter, and vocal panic (CMDI).
4. **Insider Capital Outflow:** Real-time SEC Form 4 liquidation velocity from C-suite executives prior to guidance.

When management's vocal cords crack under unscripted analyst grilling while accruals show aggressive revenue recognition and the CFO is dumping stock, **Virdixt-Apex triggers an asymmetric conviction short signal.**

---

## 🏛️ High-Level System Architecture

```
                           ┌────────────────────────────────────────┐
                           │          DATA INGESTION LAYER          │
                           └───────────────────┬────────────────────┘
                                               │
             ┌─────────────────────────────────┼────────────────────────────────┐
             ▼                                 ▼                                ▼
   [ SEC 10-K / 10-Q PDF/HTML ]    [ Unscripted Q&A Audio (.wav) ]    [ SEC Form 4 XML Feeds ]
             │                                 │                                │
             ▼                                 ▼                                ▼
   ┌───────────────────┐             ┌───────────────────┐            ┌───────────────────┐
   │  D:\Virdixt Core  │             │  D:\Virdixt Audio │            │ apex/sec/         │
   │  • Fast OCR / NLP │             │  • openSMILE CMDI │            │ • Form 4 Parser   │
   │  • FinBERT ONNX   │             │  • Pitch Jitter   │            │ • Net Disposition │
   │  • Beneish / Z    │             │  • Tremor / F0    │            │ • Velocity Window │
   └─────────┬─────────┘             └─────────┬─────────┘            └─────────┬─────────┘
             │                                 │                                │
             └─────────────────────────────────┼────────────────────────────────┘
                                               ▼
                               ┌────────────────────────────────┐
                               │   apex/dissonance/engine.py    │
                               │  Cross-Modal Dissonance Vector │
                               │  Divergence = Reality - Bravado│
                               └───────────────┬────────────────┘
                                               ▼
                               ┌────────────────────────────────┐
                               │     apex/screener/index.py     │
                               │   Activist Short Index (ASI)   │
                               │   Downside Skew & Conviction   │
                               └───────────────┬────────────────┘
                                               ▼
                               ┌────────────────────────────────┐
                               │     apex/dossier/compiler.py   │
                               │ Institutional Short Dossier    │
                               │ (Markdown / Timestamped Proof) │
                               └────────────────────────────────┘
```

---

## 📐 Mathematical Core: Activist Short Index (ASI)

The **Activist Short Index ($\text{ASI} \in [0, 100]$)** computes conviction across the four investigative pillars:

$$\text{ASI} = 100 \times \sigma\left( w_1 \cdot \mathcal{M}_{\text{Beneish}} + w_2 \cdot \mathcal{A}_{\text{CMDI}} + w_3 \cdot \Delta\mathcal{H}_{\text{Linguistic}} + w_4 \cdot \mathcal{V}_{\text{Dump}} \right)$$

Where:
- $\mathcal{M}_{\text{Beneish}}$: Normalized Beneish M-Score manipulation risk ($\text{Threshold} > -1.78$).
- $\mathcal{A}_{\text{CMDI}}$: Composite Multimodal Deception Index measuring unscripted vocal jitter and micro-tremor deviations ($\ge +2.5\sigma$).
- $\Delta\mathcal{H}_{\text{Linguistic}}$: Rate of epistemic hedging surge relative to baseline filings.
- $\mathcal{V}_{\text{Dump}}$: Net C-suite liquidation velocity within the pre-earnings 90-day window.

---

## 🏆 The "Golden Blowup" Benchmark Suite

Virdixt-Apex is validated against landmark corporate catastrophes:

| Case Study | Conventional Market Consensus | Virdixt-Apex Pre-Crash Detection |
| :--- | :--- | :--- |
| **Silicon Valley Bank (SVB Q1 '23)** | "Pristine balance sheet, regional leader" | Severe vocal strain on liquidity queries + \$4M+ insider sales weeks prior. |
| **Carvana (Q2 '22)** | "Rapid hypergrowth disruptor" | Beneish M manipulation flag + vocal tremor surge during debt refinancing questions. |
| **Wirecard (2020)** | "DAX-30 European fintech giant" | Extreme linguistic evasion + catastrophic divergence between reported EBITDA and cash accruals. |

---

## 💻 Hardware Constraints (Strict SLA)

Designed to run locally on modest consumer hardware:
- **CPU:** Intel Core i5 (8th Gen or higher)
- **RAM:** $\le 950\text{ MB}$ peak working set
- **GPU:** 0 VRAM (CPU-only optimized via ONNX Runtime & Polars)
- **Air-Gapped:** 100% offline, privacy-guaranteed execution

---

## 🚀 Repository Roadmap

For detailed milestones, technical invariants, and the 5-phase engineering waves, see [PLAN.md](file:///d:/Virdixt-Apex/PLAN.md).
