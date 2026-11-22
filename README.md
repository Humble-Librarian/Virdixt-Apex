# 🦅 Virdixt-Apex

> **Air-Gapped Activist Short-Seller & Forensic Deception Alpha Engine**  
> *Multimodal Cross-Examination: SEC Financials + Unscripted Q&A Acoustics + Form 4 Insider Dumping*

[![Tests](https://img.shields.io/badge/Tests-32%20Passed%20%7C%200.9s-brightgreen?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)
[![Hardware Profile](https://img.shields.io/badge/RAM-164%20MB%20Peak%20(i5%20CPU)-blue?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)
[![Air-Gapped](https://img.shields.io/badge/Security-100%25%20Air--Gapped-red?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge)](https://github.com/Humble-Librarian/Virdixt-Apex)

---

## What It Is

Most equity analysis tools evaluate corporate distress in silos:
- Quant funds track historical balance sheets and pricing factors.
- Sentiment models read PR-sanitized press releases.
- Acoustic tools measure speech tone without accounting context.

**Virdixt-Apex exploits the dissonance between these modalities.** It operates like an algorithmic activist short-seller (Hindenburg Research / Muddy Waters running on local silicon) by cross-examining:

1. **Accounting Truth:** Beneish M-Score (8-variable manipulation index), Dechow F-Score (7-variable misstatement logit model), and Sloan Accrual anomalies.
2. **Unscripted Acoustic Biomarkers:** Vocal micro-tremors, F0 pitch drift, and cycle-to-cycle jitter ($>2.5\sigma$) extracted from earnings call Q&A sessions.
3. **Linguistic Evasion:** Cosine semantic deflection ($<0.42$) between analyst questions and executive responses, alongside Gunning-Fog obfuscation.
4. **Insider Capital Outflow:** Opportunistic SEC Form 4 sales from C-suite officers ($CEO, CFO, COO$) filtered using the Cohen-Malloy-Pomorski (2012) framework.

When executive voices show acute autonomic stress during unscripted grilling, while accruals mask margin erosion and insiders liquidate stock, **Apex triggers an asymmetric short thesis.**

---

## Benchmark Results ("Golden Blowup" Suite)

Virdixt-Apex was evaluated against landmark historical collapses alongside an investment-grade control firm. Every run is deterministic, CPU-only, and fully air-gapped:

| Ticker | Company | Activist Short Index (ASI) | Conviction Tier | Downside Target | Trade Structure | Squeeze Risk |
| :--- | :--- | :---: | :--- | :---: | :--- | :---: |
| **SIVB** | Silicon Valley Bank (Q1 '23) | **100.0 / 100** | `CRITICAL_FRAUD_COLLAPSE` | **-90.0%** | `PUT_DEBIT_SPREAD` | CRITICAL |
| **WDI** | Wirecard AG (2020) | **100.0 / 100** | `CRITICAL_FRAUD_COLLAPSE` | **-90.0%** | `PUT_DEBIT_SPREAD` | CRITICAL |
| **CVNA** | Carvana Co. (Q2 '22) | **97.0 / 100** | `CRITICAL_FRAUD_COLLAPSE` | **-88.0%** | `PUT_DEBIT_SPREAD` | HIGH |
| **AAPL** | Apple Inc. (Control) | **13.2 / 100** | `NEGLIGIBLE_RISK` | **0.0%** | `NO_ACTION_AVOID` | LOW |

> **Telemetry:** All four benchmark targets processed sequentially in **< 4.5 seconds** with a peak memory working set of **164.4 MB RAM** (well below the 950 MB hardware ceiling).

---

## System Architecture

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
   │  Accounting Engine│             │  Acoustic Engine  │            │  apex/sec/        │
   │  • Beneish M-Score│             │  • openSMILE eGeMAPS│          │  • Form 4 Parser   │
   │  • Dechow F-Score │             │  • Pitch Jitter   │            │  • Cohen-Malloy   │
   │  • Sloan Accruals │             │  • Vocal Tremors  │            │  • Dump Velocity  │
   └─────────┬─────────┘             └─────────┬─────────┘            └─────────┬─────────┘
             │                                 │                                │
             └─────────────────────────────────┼────────────────────────────────┘
                                               ▼
                               ┌────────────────────────────────┐
                               │   apex/dissonance/             │
                               │  Cross-Modal Dissonance Vector │
                               │  Divergence = Reality - Bravado│
                               └───────────────┬────────────────┘
                                               ▼
                               ┌────────────────────────────────┐
                               │   apex/screener/               │
                               │   Activist Short Index (ASI)   │
                               │   Downside Skew & Squeeze Gate │
                               └───────────────┬────────────────┘
                                               ▼
                               ┌────────────────────────────────┐
                               │   apex/dossier/                │
                               │   Forensic Audit Dossier       │
                               │   (Markdown / Timestamped Cit.)│
                               └────────────────────────────────┘
```

---

## Mathematical Formulation

### 1. Activist Short Index (ASI)
The core screener binds the four investigative pillars into a bounded index ($\text{ASI} \in [0, 100]$):

$$\text{ASI} = 100 \times \sigma\left( w_{\text{acct}} \cdot \mathcal{S}_{\text{Accounting}} + w_{\text{acoust}} \cdot \mathcal{S}_{\text{Acoustic}} + w_{\text{ling}} \cdot \mathcal{S}_{\text{Linguistic}} + w_{\text{insider}} \cdot \mathcal{S}_{\text{Insider}} + \Delta_{\text{Dissonance}} \right)$$

- $w_{\text{acct}} = 0.35$: Beneish manipulation ($M > -1.78$), Dechow misstatement risk ($F > 1.85$), and Sloan accrual divergence.
- $w_{\text{acoust}} = 0.25$: Composite Multimodal Deception Index ($\text{CMDI} \ge 5.0$) and vocal fold jitter ($> 2.5\sigma$).
- $w_{\text{ling}} = 0.20$: Epistemic hedging density, Gunning-Fog index ($> 18.0$), and semantic deflection.
- $w_{\text{insider}} = 0.20$: Net opportunistic disposition velocity ($V_{\text{dump}}$) over the 90-day pre-earnings window.
- $\Delta_{\text{Dissonance}}$: Non-linear multiplier penalizing instances where verbal bravado conflicts directly with balance-sheet erosion.

### 2. Squeeze Risk & Trade Structuring
Activist short positions fail when forced short squeezes liquidate the trade before fundamentals assert themselves:
- **Days to Cover (DTC) $> 8.0$ or Borrow Fee $> 40\%$:** Flags critical squeeze hazard $\rightarrow$ Outright equity shorting is blocked $\rightarrow$ Automatically routes execution to **Put Debit Spreads (60-90 DTE)** to cap volatility drag.
- **DTC $< 4.0$ and Borrow Fee $< 10\%$:** Low squeeze friction $\rightarrow$ Directs **Outright Equity Short**.

---

## Quickstart

### Installation
Clone the repository and install dependencies in an isolated virtual environment:

```bash
git clone https://github.com/Humble-Librarian/Virdixt-Apex.git
cd Virdixt-Apex
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Run Tests
Execute the 30-test suite across all 5 architectural waves:

```bash
pytest tests/ -v
```

### Run Historical Benchmark Harness
Reproduce the SVB, Carvana, Wirecard, and Apple benchmark runs:

```bash
python benchmarks/run_benchmarks.py
```

---

## Python API Example

```python
from apex.core.adapter import VirdixtCoreAdapter
from apex.screener.index import ActivistShortScreener
from apex.dossier.compiler import ForensicDossierCompiler
from apex.core.types import (
    AcousticBiomarkerVector,
    LinguisticObfuscationVector,
    InsiderFlowSummary,
)

# 1. Compute accounting benchmarks from raw balance sheet metrics
adapter = VirdixtCoreAdapter()
accounting_vec = adapter.compute_accounting_vector({
    "total_assets": 211_000_000_000,
    "net_income": 1_500_000_000,
    "operating_cash_flow": -4_200_000_000,  # Negative cash flow vs positive income
    "dsri": 1.45,
    "gmi": 1.85,
    "aqi": 1.60,
    "sgi": 1.15,
    "rsst_accrual": 0.95,
})

# 2. Supply unscripted vocal and linguistic vectors
acoustic_vec = AcousticBiomarkerVector(
    jitter_z_score=3.4,
    cmdi_score=8.9,
    vocal_stress_rating="PANIC_ANOMALY",
    acute_stress_flag=True,
)

linguistic_vec = LinguisticObfuscationVector(
    gunning_fog_index=21.8,
    epistemic_hedging_score=54.0,
    qa_semantic_alignment=0.26,  # Evasive deflection
    is_evasive_deflection=True,
    sentiment_bullishness=0.82,
)

# 3. Supply Form 4 insider flow summary
insider_vec = InsiderFlowSummary(
    total_sales_value=3_570_000.0,
    opportunistic_sales_count=1,
    dump_velocity_v=35.7,
    is_abnormal_liquidation=True,
    c_suite_sellers=["Gregory W. Becker (CEO) - $3.57M"],
)

# 4. Evaluate Activist Short Index
thesis = ActivistShortScreener.evaluate(
    ticker="SIVB",
    company_name="Silicon Valley Bank",
    accounting=accounting_vec,
    acoustic=acoustic_vec,
    linguistic=linguistic_vec,
    insider=insider_vec,
    days_to_cover=9.4,
    borrow_fee_annual_percent=38.5,
)

# 5. Compile institutional markdown dossier
dossier_markdown = ForensicDossierCompiler.compile_markdown(thesis)
print(dossier_markdown)
```

---

## Hardware Envelope

| Dimension | Specification | Enforced By |
| :--- | :--- | :--- |
| **Target CPU** | Intel Core i5 (8th Gen or higher) | Single-pass vectorization & Polars |
| **RAM Ceiling** | $\le 950\text{ MB}$ working set (Actual: $\sim 165\text{ MB}$) | `apex.core.memory_watchdog.MemoryWatchdog` |
| **GPU / VRAM** | **0 VRAM** (No CUDA or GPU required) | CPU execution only |
| **Air-Gap** | 100% offline, zero runtime HTTP requests | Local fixture integration |

---

## License

MIT License. Designed and engineered by [Humble-Librarian](https://github.com/Humble-Librarian).
