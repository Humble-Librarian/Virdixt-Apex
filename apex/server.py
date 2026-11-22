"""
Virdixt-Apex Standalone Forensic Deception Alpha Engine Server
Air-gapped, high-throughput REST API and Interactive Forensic Dashboard.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import psutil

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from apex.core.adapter import VirdixtCoreAdapter
from apex.screener.index import ActivistShortScreener
from apex.dossier.compiler import ForensicDossierCompiler
from apex.sec.edgar_form4 import Form4Parser, InsiderTradeAnalyzer
from apex.core.memory_watchdog import MemoryWatchdog
from apex.core.types import (
    ActivistShortThesis,
    AcousticBiomarkerVector,
    ForensicAccountingVector,
    LinguisticObfuscationVector,
    InsiderFlowSummary,
    ConvictionTier,
    TradeStructure,
)
from benchmarks.run_benchmarks import CASES_DIR, load_case, run_benchmark_case

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="🦅 Virdixt-Apex Forensic Alpha Engine",
    description="Air-Gapped Activist Short-Seller & Multimodal Forensic Deception Intelligence Platform",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_adapter = VirdixtCoreAdapter()
_start_time = time.time()


class AnalysisRequest(BaseModel):
    ticker: str = "TICKER"
    company_name: str = "Target Corporation"
    analysis_date: Optional[str] = None
    financials: Dict[str, Any] = Field(default_factory=dict)
    acoustic: Dict[str, Any] = Field(default_factory=dict)
    linguistic: Dict[str, Any] = Field(default_factory=dict)
    insider: Optional[Dict[str, Any]] = None
    days_to_cover: float = 3.0
    borrow_fee_annual_percent: float = 2.0


class Form4ParseRequest(BaseModel):
    xml_content: str
    target_ticker: Optional[str] = None


@app.get("/api/status")
async def get_status():
    process = psutil.Process()
    rss_mb = process.memory_info().rss / (1024 * 1024)
    return {
        "engine": "Virdixt-Apex",
        "version": "0.2.0",
        "status": "ONLINE_STANDALONE",
        "air_gapped": True,
        "rss_memory_mb": round(rss_mb, 2),
        "rss_limit_mb": 950.0,
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


@app.get("/api/benchmarks")
async def get_benchmarks():
    cases = []
    case_files = sorted(list(CASES_DIR.glob("*.json")))
    for cfile in case_files:
        cdata = load_case(cfile)
        thesis, dossier_md = run_benchmark_case(cdata)
        cases.append({
            "ticker": thesis.ticker,
            "company_name": thesis.company_name,
            "asi_score": thesis.asi_score,
            "conviction_tier": thesis.conviction_tier.value,
            "downside_target_percent": thesis.downside_target_percent,
            "recommended_trade_structure": thesis.recommended_trade_structure.value,
            "short_squeeze_risk_level": thesis.short_squeeze_risk_level,
            "days_to_cover": thesis.days_to_cover,
            "borrow_fee_annual_percent": thesis.borrow_fee_annual_percent,
            "key_catalysts": thesis.key_forensic_catalysts,
            "case_data": cdata,
        })
    return {"count": len(cases), "cases": cases}


@app.get("/api/benchmarks/{ticker}")
async def get_benchmark_by_ticker(ticker: str):
    ticker_upper = ticker.upper()
    case_files = list(CASES_DIR.glob("*.json"))
    for cfile in case_files:
        cdata = load_case(cfile)
        if cdata.get("ticker", "").upper() == ticker_upper:
            thesis, dossier_md = run_benchmark_case(cdata)
            return {
                "ticker": thesis.ticker,
                "company_name": thesis.company_name,
                "thesis": thesis.model_dump(),
                "dossier_markdown": dossier_md,
                "raw_inputs": cdata,
            }
    raise HTTPException(status_code=404, detail=f"Benchmark target '{ticker_upper}' not found.")


@app.post("/api/analyze")
async def run_analysis(req: AnalysisRequest):
    try:
        # 1. Forensic Accounting Vector
        acct_vec = _adapter.compute_accounting_vector(req.financials)

        # 2. Acoustic Vector
        acoust_vec = (
            AcousticBiomarkerVector(**req.acoustic)
            if req.acoustic
            else AcousticBiomarkerVector()
        )

        # 3. Linguistic Vector
        ling_vec = (
            LinguisticObfuscationVector(
                gunning_fog_index=req.linguistic.get("gunning_fog_index", 14.0),
                epistemic_hedging_score=req.linguistic.get("epistemic_hedging_score", 20.0),
                qa_semantic_alignment=req.linguistic.get("qa_semantic_alignment", 0.75),
                is_evasive_deflection=req.linguistic.get("is_evasive_deflection", False),
                sentiment_bullishness=req.linguistic.get("sentiment_bullishness", 0.5),
            )
            if req.linguistic
            else LinguisticObfuscationVector()
        )

        # 4. Insider Vector
        insider_summary = (
            InsiderFlowSummary(**req.insider)
            if req.insider
            else None
        )

        # 5. Activist Short Screener
        thesis = ActivistShortScreener.evaluate(
            ticker=req.ticker,
            company_name=req.company_name,
            accounting=acct_vec,
            acoustic=acoust_vec,
            linguistic=ling_vec,
            insider=insider_summary,
            days_to_cover=req.days_to_cover,
            borrow_fee_annual_percent=req.borrow_fee_annual_percent,
            analysis_date=req.analysis_date,
        )

        # 6. Dossier Compilation
        dossier_md = ForensicDossierCompiler.compile_markdown(thesis)

        return {
            "thesis": thesis.model_dump(),
            "dossier_markdown": dossier_md,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/parse-form4")
async def parse_form4_xml(payload: Form4ParseRequest):
    txs = Form4Parser.parse_xml_string(payload.xml_content)
    if not txs:
        raise HTTPException(
            status_code=400,
            detail="Unable to parse Form 4 XML or payload violated security limits (size / entity expansion).",
        )
    summary = InsiderTradeAnalyzer.summarize_flow(txs)
    return {
        "transaction_count": len(txs),
        "transactions": [t.model_dump() for t in txs],
        "summary": summary.model_dump(),
    }


# Static Frontend Mounting
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


def main():
    import uvicorn
    host = os.getenv("APEX_HOST", "127.0.0.1")
    port = int(os.getenv("APEX_PORT", 8000))
    print(f"🦅 Launching Virdixt-Apex Forensic Alpha Server on http://{host}:{port}")
    uvicorn.run("apex.server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
