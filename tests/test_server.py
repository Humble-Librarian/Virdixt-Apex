"""
Unit & Integration Tests for Virdixt-Apex Standalone Web Server
"""

import pytest
from fastapi.testclient import TestClient
from apex.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_status_endpoint(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["engine"] == "Virdixt-Apex"
    assert data["air_gapped"] is True
    assert data["status"] == "ONLINE_STANDALONE"
    assert data["rss_memory_mb"] > 0.0


def test_benchmarks_endpoint(client):
    res = client.get("/api/benchmarks")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 4
    tickers = [c["ticker"] for c in data["cases"]]
    assert "SIVB" in tickers
    assert "AAPL" in tickers
    assert "CVNA" in tickers
    assert "WDI" in tickers


def test_benchmark_detail_endpoint(client):
    res = client.get("/api/benchmarks/SIVB")
    assert res.status_code == 200
    data = res.json()
    assert data["ticker"] == "SIVB"
    assert "Silicon Valley Bank" in data["dossier_markdown"]
    assert data["thesis"]["asi_score"] >= 85.0


def test_static_dashboard_mounted(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "VIRDIXT-APEX" in res.text
    assert "Historical" in res.text
    assert "Golden Blowup" in res.text
