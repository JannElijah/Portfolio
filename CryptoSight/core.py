"""Pure analytics & portfolio persistence helpers for CryptoSight."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

DB_PATH = Path(__file__).parent / "cryptosight.db"
DEFAULT_ASSETS = {"BTC-USD": 0.25, "ETH-USD": 1.5, "SOL-USD": 12.0, "ADA-USD": 450.0}


class PortfolioStore:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS holdings (
                    ticker TEXT PRIMARY KEY,
                    quantity REAL NOT NULL,
                    avg_buy_price REAL NOT NULL DEFAULT 0.0
                )
                """
            )
            try:
                conn.execute("ALTER TABLE holdings ADD COLUMN avg_buy_price REAL NOT NULL DEFAULT 0.0")
            except sqlite3.OperationalError:
                pass
            count = conn.execute("SELECT COUNT(*) FROM holdings").fetchone()[0]
            if count == 0:
                defaults = [
                    ("BTC-USD", 0.25, 68500.0),
                    ("ETH-USD", 1.5, 2650.0),
                    ("SOL-USD", 12.0, 145.0),
                    ("ADA-USD", 450.0, 0.52),
                ]
                conn.executemany(
                    "INSERT INTO holdings (ticker, quantity, avg_buy_price) VALUES (?, ?, ?)",
                    defaults,
                )

    def load(self) -> dict[str, float]:
        with self._connect() as conn:
            rows = conn.execute("SELECT ticker, quantity FROM holdings ORDER BY ticker").fetchall()
        return {t: float(q) for t, q in rows}

    def load_detailed(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT ticker, quantity, avg_buy_price FROM holdings ORDER BY ticker").fetchall()
        return [{"ticker": t, "quantity": float(q), "avg_buy_price": float(p)} for t, q, p in rows]

    def save(self, ticker: str, quantity: float, avg_buy_price: float | None = None) -> None:
        with self._connect() as conn:
            if avg_buy_price is None:
                row = conn.execute("SELECT avg_buy_price FROM holdings WHERE ticker = ?", (ticker,)).fetchone()
                avg_buy_price = float(row[0]) if row else 0.0
            conn.execute(
                "INSERT INTO holdings (ticker, quantity, avg_buy_price) VALUES (?, ?, ?) "
                "ON CONFLICT(ticker) DO UPDATE SET quantity = excluded.quantity, avg_buy_price = excluded.avg_buy_price",
                (ticker, float(quantity), float(avg_buy_price)),
            )


def normalize_news_article(article: dict) -> dict:
    """Handle both legacy flat yfinance news dicts and modern nested content dicts."""
    if not isinstance(article, dict):
        return {"title": "Market Update", "link": "#", "publisher": "Market Feed"}
    if "content" in article and isinstance(article["content"], dict):
        content = article["content"]
        provider = content.get("provider") or {}
        canon = content.get("canonicalUrl") or {}
        return {
            "title": content.get("title") or "Market Headline",
            "link": canon.get("url") or "#",
            "publisher": provider.get("displayName") or "Financial Feed",
        }
    return {
        "title": article.get("title") or "Market Headline",
        "link": article.get("link") or "#",
        "publisher": article.get("publisher") or "Financial Feed",
    }


def synthetic_ohlcv(ticker: str, rows: int = 60) -> pd.DataFrame:
    """Deterministic fallback OHLCV series when upstream market feed is offline."""
    seed = sum(ord(c) for c in ticker)
    rng = np.random.default_rng(seed)
    base = 86000.0 if "BTC" in ticker else 3100.0 if "ETH" in ticker else 175.0
    dates = pd.date_range(end=datetime.now(), periods=rows, freq="D")
    returns = rng.normal(0.002, 0.025, size=rows)
    closes = base * np.cumprod(1 + returns)
    opens = np.roll(closes, 1)
    opens[0] = base
    highs = np.maximum(opens, closes) * (1 + rng.uniform(0.003, 0.02, size=rows))
    lows = np.minimum(opens, closes) * (1 - rng.uniform(0.003, 0.02, size=rows))
    volumes = rng.integers(150_000, 950_000, size=rows)
    return pd.DataFrame(
        {"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": volumes},
        index=dates,
    )


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute MACD line, signal line, and histogram."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line, macd_line - signal_line


def compute_bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Compute Bollinger upper band, middle SMA, and lower band."""
    mid = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    return mid + (std * num_std), mid, mid - (std * num_std)


def compute_risk_metrics(series: pd.Series) -> dict[str, float]:
    """Compute Max Drawdown (%) and annualized Sharpe Estimate from daily closes."""
    clean = series.dropna()
    if len(clean) < 2:
        return {"max_drawdown_pct": 0.0, "sharpe_ratio": 0.0}
    running_max = clean.cummax()
    drawdown = ((clean - running_max) / running_max.replace(0, np.nan)).min() * 100.0
    daily_ret = clean.pct_change().dropna()
    std = float(daily_ret.std())
    sharpe = (float(daily_ret.mean()) / std) * float(np.sqrt(252)) if std > 1e-12 else 0.0
    return {"max_drawdown_pct": round(float(drawdown), 2), "sharpe_ratio": round(sharpe, 2)}


def deterministic_sentiment_fallback(headlines: list[dict], rsi_val: float | None) -> tuple[str, str]:
    """Rule-based headline + RSI fallback when Gemini key is absent or rate-limited."""
    bull_words = {"surge", "rally", "gain", "etf", "adoption", "record", "inflow", "bull", "upgrade"}
    bear_words = {"drop", "crash", "hack", "lawsuit", "outflow", "bear", "ban", "selloff", "slump"}
    score = 0
    for item in headlines[:5]:
        words = set(item["title"].lower().split())
        score += len(words & bull_words) - len(words & bear_words)
    if rsi_val is not None:
        if rsi_val >= 62:
            score += 1
        elif rsi_val <= 38:
            score -= 1
    if score > 0:
        return "Bullish", "Positive headline momentum and technical strength detected (Local Quant Engine)."
    if score < 0:
        return "Bearish", "Cautionary headline signals or downward momentum detected (Local Quant Engine)."
    return "Neutral", "Balanced news flow and neutral RSI range (Local Quant Engine)."
