"""
SEC EDGAR Data Ingestion and Form 4 Module
"""

from .edgar_form4 import Form4Parser, InsiderTradeAnalyzer

__all__ = ["Form4Parser", "InsiderTradeAnalyzer"]
