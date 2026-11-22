"""
Virdixt-Apex Historical "Golden Blowup" Benchmark Runner
Executes end-to-end forensic analysis against historic corporate collapses vs clean controls.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from apex.core.adapter import VirdixtCoreAdapter
from apex.screener.index import ActivistShortScreener
from apex.dossier.compiler import ForensicDossierCompiler
from apex.core.types import (
    ActivistShortThesis,
    AcousticBiomarkerVector,
    LinguisticObfuscationVector,
    InsiderFlowSummary,
)
from apex.core.memory_watchdog import MemoryWatchdog


CASES_DIR = Path(__file__).parent / "cases"


def load_case(case_path: Path) -> Dict[str, Any]:
    with open(case_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_benchmark_case(case_data: Dict[str, Any]) -> tuple[ActivistShortThesis, str]:
    adapter = VirdixtCoreAdapter()

    # 1. Forensic Accounting Vector
    acct_vec = adapter.compute_accounting_vector(case_data["financials"])

    # 2. Acoustic Vector
    acoust_raw = case_data["acoustic"]
    acoust_vec = AcousticBiomarkerVector(**acoust_raw)

    # 3. Linguistic Vector
    ling_raw = case_data["linguistic"]
    ling_vec = LinguisticObfuscationVector(
        gunning_fog_index=ling_raw["gunning_fog_index"],
        epistemic_hedging_score=ling_raw["epistemic_hedging_score"],
        qa_semantic_alignment=ling_raw["qa_semantic_alignment"],
        is_evasive_deflection=ling_raw["is_evasive_deflection"],
        sentiment_bullishness=ling_raw["sentiment_bullishness"],
    )

    # 4. Insider Vector
    insider_raw = case_data.get("insider")
    insider_summary = InsiderFlowSummary(**insider_raw) if insider_raw else None

    # 5. Activist Short Screener (ASI)
    thesis = ActivistShortScreener.evaluate(
        ticker=case_data["ticker"],
        company_name=case_data["company_name"],
        accounting=acct_vec,
        acoustic=acoust_vec,
        linguistic=ling_vec,
        insider=insider_summary,
        days_to_cover=case_data.get("days_to_cover", 3.0),
        borrow_fee_annual_percent=case_data.get("borrow_fee_annual_percent", 2.0),
        analysis_date=case_data.get("analysis_date"),
    )

    # 6. Autonomous Dossier Compiler
    dossier_md = ForensicDossierCompiler.compile_markdown(thesis)

    return thesis, dossier_md


def run_all_benchmarks() -> List[ActivistShortThesis]:
    watchdog = MemoryWatchdog()
    case_files = sorted(list(CASES_DIR.glob("*.json")))
    theses: List[ActivistShortThesis] = []

    print("\n" + "=" * 90)
    print(" 🦅 VIRDIXT-APEX: HISTORICAL 'GOLDEN BLOWUP' BENCHMARK HARNESS")
    print("=" * 90)
    print(f"{'TICKER':<8} {'COMPANY':<30} {'ASI':<8} {'CONVICTION TIER':<25} {'DOWNSIDE':<10} {'STRUCTURE':<12}")
    print("-" * 90)

    for cfile in case_files:
        cdata = load_case(cfile)
        (thesis, md), metrics = watchdog.monitor(run_benchmark_case, cdata)
        theses.append(thesis)

        print(
            f"{thesis.ticker:<8} "
            f"{thesis.company_name[:28]:<30} "
            f"{thesis.asi_score:>5.1f}   "
            f"{thesis.conviction_tier.value:<25} "
            f"{thesis.downside_target_percent:>6.1f}%   "
            f"{thesis.recommended_trade_structure.value:<12}"
        )

    peak_rss = watchdog.assert_within_budget()
    print("=" * 90)
    print(f"BENCHMARK STATUS: ALL {len(theses)} CASES PROCESSED | PEAK RAM: {peak_rss:.2f} MB (< 950 MB SLA)")
    print("=" * 90 + "\n")

    return theses


if __name__ == "__main__":
    run_all_benchmarks()
