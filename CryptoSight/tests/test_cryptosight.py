"""Unit tests for CryptoSight news parser, RSI indicator, sentiment fallback, and SQLite store."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import (
    PortfolioStore,
    compute_bollinger_bands,
    compute_macd,
    compute_risk_metrics,
    compute_rsi,
    deterministic_sentiment_fallback,
    normalize_news_article,
    run_sma_crossover_backtest,
    synthetic_ohlcv,
)


def test_normalize_nested_and_flat_yfinance_news() -> None:
    nested = {
        "content": {
            "title": "Bitcoin ETF inflows hit weekly record",
            "canonicalUrl": {"url": "https://example.com/btc"},
            "provider": {"displayName": "Reuters"},
        }
    }
    flat = {"title": "ETH upgrade scheduled", "link": "https://example.com/eth", "publisher": "CoinDesk"}

    n_res = normalize_news_article(nested)
    f_res = normalize_news_article(flat)
    assert n_res["title"] == "Bitcoin ETF inflows hit weekly record"
    assert n_res["publisher"] == "Reuters"
    assert f_res["link"] == "https://example.com/eth"


def test_rsi_and_sentiment_fallback() -> None:
    df = synthetic_ohlcv("BTC-USD", rows=40)
    rsi = compute_rsi(df["Close"]).dropna()
    assert not rsi.empty
    assert (rsi >= 0).all() and (rsi <= 100).all()

    bull_sent, _ = deterministic_sentiment_fallback([{"title": "ETF adoption surge and rally"}], 68.0)
    bear_sent, _ = deterministic_sentiment_fallback([{"title": "Exchange hack causes market crash"}], 30.0)
    assert bull_sent == "Bullish"
    assert bear_sent == "Bearish"


def test_portfolio_store_persistence(tmp_path) -> None:
    store = PortfolioStore(tmp_path / "cs.db")
    initial = store.load()
    assert "BTC-USD" in initial
    store.save("BTC-USD", 1.75, avg_buy_price=72000.0)
    assert store.load()["BTC-USD"] == 1.75
    det = {d["ticker"]: d for d in store.load_detailed()}
    assert det["BTC-USD"]["avg_buy_price"] == 72000.0


def test_macd_bollinger_and_risk_metrics() -> None:
    df = synthetic_ohlcv("ETH-USD", rows=60)
    macd_line, sig_line, hist = compute_macd(df["Close"])
    up, mid, low = compute_bollinger_bands(df["Close"])
    risk = compute_risk_metrics(df["Close"])
    assert len(macd_line) == 60 and len(sig_line) == 60 and len(hist) == 60
    assert (up.dropna() >= mid.dropna()).all()
    assert (mid.dropna() >= low.dropna()).all()
    assert risk["max_drawdown_pct"] <= 0.0
    assert isinstance(risk["sharpe_ratio"], float)

    bt = run_sma_crossover_backtest(df, fast=10, slow=20)
    assert len(bt["equity_df"]) == len(df)
    assert isinstance(bt["strategy_return_pct"], float)
    assert isinstance(bt["buy_hold_return_pct"], float)
    assert bt["trades_count"] >= 0 and 0.0 <= bt["win_rate_pct"] <= 100.0
