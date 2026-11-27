"""CryptoSight — Institutional Quantitative Terminal & Market Sentiment Console."""

from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

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

# -----------------
# PAGE & QUANT TERMINAL THEME
# -----------------
st.set_page_config(
    page_title="CryptoSight | Quant Market Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background-color: #090b0e;
        color: #f4f4f5;
    }
    section[data-testid="stSidebar"] {
        background-color: #0d1015;
        border-right: 1px solid #1e242e;
    }
    div[data-testid="metric-container"] {
        background-color: #12161c;
        border: 1px solid #1e242e;
        border-top: 2px solid #f59e0b;
        border-radius: 6px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Courier New', monospace;
        font-weight: 700;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=300)
def get_crypto_data(ticker: str, period: str, interval: str) -> tuple[pd.DataFrame, bool]:
    try:
        hist = yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=True)
        if not hist.empty:
            return hist, True
    except Exception:
        pass
    return synthetic_ohlcv(ticker), False


@st.cache_data(ttl=60)
def get_live_metrics(ticker: str) -> tuple[float, float, float, float, bool]:
    for period, interval in (("2d", "15m"), ("5d", "1d")):
        try:
            data = yf.Ticker(ticker).history(period=period, interval=interval)
            if not data.empty and len(data) >= 2:
                latest = float(data["Close"].iloc[-1])
                prev = float(data["Close"].iloc[-2])
                chg = latest - prev
                pct = (chg / prev) * 100 if prev else 0.0
                vol = float(data["Volume"].sum())
                return latest, chg, pct, vol, True
        except Exception:
            continue

    fallback = synthetic_ohlcv(ticker, rows=10)
    latest = float(fallback["Close"].iloc[-1])
    prev = float(fallback["Close"].iloc[-2])
    chg = latest - prev
    return latest, chg, (chg / prev) * 100, float(fallback["Volume"].sum()), False


@st.cache_data(ttl=1800)
def get_news(ticker: str) -> list[dict]:
    try:
        raw = yf.Ticker(ticker).news or []
        return [normalize_news_article(item) for item in raw]
    except Exception:
        return []


@st.cache_data(ttl=900)
def get_ai_sentiment(headlines: list[dict], rsi_val: float | None) -> tuple[str, str, str]:
    api_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    if not api_key or not headlines:
        sent, expl = deterministic_sentiment_fallback(headlines, rsi_val)
        return sent, expl, "Quantitative Momentum Fallback"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    titles = "\n".join(f"- {h['title']}" for h in headlines[:4])
    prompt = (
        "Classify crypto market sentiment as Bullish, Bearish, or Neutral from these headlines "
        "and provide one concise sentence explanation.\n"
        f"{titles}\nFormat:\nSentiment: <Bullish|Bearish|Neutral>\nExplanation: <one sentence>"
    )
    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]}),
            timeout=6,
        )
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        if "Explanation:" in text:
            left, right = text.split("Explanation:", 1)
            sent = left.replace("Sentiment:", "").strip().split()[0]
            return sent, right.strip(), "Gemini 2.0 Flash"
    except Exception:
        pass

    sent, expl = deterministic_sentiment_fallback(headlines, rsi_val)
    return sent, expl, "Quantitative Momentum Fallback"


# -----------------
# SIDEBAR
# -----------------
store = PortfolioStore()
if "ticker" not in st.session_state:
    st.session_state.ticker = "BTC-USD"

holdings = store.load()

with st.sidebar:
    st.title("📈 CryptoSight")
    st.caption("Institutional Quant Terminal")
    st.divider()

    quick_pick = st.selectbox("Quick Asset", ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD"])
    custom_ticker = st.text_input("Custom Ticker", value=st.session_state.ticker)
    if st.button("Load Market Ticker", type="primary", use_container_width=True):
        st.session_state.ticker = (custom_ticker or quick_pick).strip().upper()
        st.rerun()

    selected_ticker = st.session_state.ticker
    st.divider()
    st.subheader("Saved Portfolio (SQLite)")
    for asset, qty in holdings.items():
        new_qty = st.number_input(
            f"{asset.replace('-USD', '')} Qty",
            min_value=0.0,
            value=float(qty),
            step=0.05,
            format="%.4f",
            key=f"hold_{asset}",
        )
        if new_qty != qty:
            store.save(asset, new_qty)
            holdings[asset] = new_qty


# -----------------
# MAIN TERMINAL VIEW
# -----------------
latest_price, change, change_pct, volume, is_live = get_live_metrics(selected_ticker)
feed_tag = "LIVE YFINANCE FEED" if is_live else "OFFLINE QUANT SIMULATION"

st.title(f"{selected_ticker} · Market Terminal")
st.caption(f"{feed_tag} · Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Spot Price", f"${latest_price:,.2f}")
c2.metric("24h Change", f"${change:+,.2f}", f"{change_pct:+.2f}%")
c3.metric("24h Volume", f"{volume:,.0f}")

time_map = {
    "1M": ("1mo", "1d"),
    "3M": ("3mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Y": ("1y", "1d"),
}

hist_data, _ = get_crypto_data(selected_ticker, "1mo", "1d")
rsi_series = compute_rsi(hist_data["Close"]) if not hist_data.empty else pd.Series(dtype=float)
latest_rsi = float(rsi_series.dropna().iloc[-1]) if not rsi_series.dropna().empty else None
c4.metric("RSI (14D)", f"{latest_rsi:.1f}" if latest_rsi is not None else "N/A")

news_articles = get_news(selected_ticker)
sentiment, explanation, engine_label = get_ai_sentiment(news_articles, latest_rsi)
st.info(f"**Market Sentiment ({engine_label}): {sentiment}** — {explanation}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Candlestick & Indicators",
    "Relative Performance",
    "Portfolio Valuation",
    "Headlines",
    "Quant Backtest Lab",
])

with tab1:
    ctl1, ctl2, ctl3 = st.columns([1, 1, 1.5])
    time_range = ctl1.selectbox("Range", list(time_map.keys()), index=1)
    show_sma20 = ctl2.checkbox("20-Day SMA + Bollinger", value=True)
    period_arg, interval_arg = time_map[time_range]
    chart_df, _ = get_crypto_data(selected_ticker, period_arg, interval_arg)

    if not chart_df.empty:
        chart_df["RSI"] = compute_rsi(chart_df["Close"])
        bb_up, bb_mid, bb_low = compute_bollinger_bands(chart_df["Close"])
        macd_line, macd_sig, macd_hist = compute_macd(chart_df["Close"])
        risk = compute_risk_metrics(chart_df["Close"])
        ctl3.caption(f"Max Drawdown: **{risk['max_drawdown_pct']}%** · Sharpe Est: **{risk['sharpe_ratio']}** · Latest MACD: **{macd_line.iloc[-1]:+.1f}**")
        fig = make_subplots(
            rows=4,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.045,
            row_heights=[0.46, 0.16, 0.19, 0.19],
        )
        fig.add_trace(
            go.Candlestick(
                x=chart_df.index,
                open=chart_df["Open"],
                high=chart_df["High"],
                low=chart_df["Low"],
                close=chart_df["Close"],
                name="Price",
                increasing_line_color="#10b981",
                decreasing_line_color="#f43f5e",
            ),
            row=1,
            col=1,
        )
        if show_sma20:
            fig.add_trace(go.Scatter(x=chart_df.index, y=bb_mid, mode="lines", name="SMA 20", line=dict(color="#f59e0b", width=1.6)), row=1, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=bb_up, mode="lines", name="BB Upper", line=dict(color="rgba(56,189,248,0.45)", width=1, dash="dot")), row=1, col=1)
            fig.add_trace(go.Scatter(x=chart_df.index, y=bb_low, mode="lines", name="BB Lower", line=dict(color="rgba(56,189,248,0.45)", width=1, dash="dot")), row=1, col=1)
        vol_colors = ["#10b981" if c >= o else "#f43f5e" for o, c in zip(chart_df["Open"], chart_df["Close"])]
        fig.add_trace(go.Bar(x=chart_df.index, y=chart_df["Volume"], marker_color=vol_colors, name="Volume"), row=2, col=1)
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["RSI"], mode="lines", name="RSI 14", line=dict(color="#38bdf8", width=1.6)), row=3, col=1)
        fig.add_hrect(y0=30, y1=70, fillcolor="rgba(56,189,248,0.08)", line_width=0, row=3, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#f43f5e", row=3, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#10b981", row=3, col=1)
        hist_colors = ["#10b981" if v >= 0 else "#f43f5e" for v in macd_hist.fillna(0.0)]
        fig.add_trace(go.Bar(x=chart_df.index, y=macd_hist, marker_color=hist_colors, name="MACD Hist"), row=4, col=1)
        fig.add_trace(go.Scatter(x=chart_df.index, y=macd_line, mode="lines", name="MACD", line=dict(color="#a78bfa", width=1.5)), row=4, col=1)
        fig.add_trace(go.Scatter(x=chart_df.index, y=macd_sig, mode="lines", name="Signal", line=dict(color="#f59e0b", width=1.2)), row=4, col=1)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#090b0e",
            plot_bgcolor="#12161c",
            height=720,
            xaxis_rangeslider_visible=False,
            margin=dict(l=16, r=16, t=20, b=16),
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    compare_assets = st.multiselect("Compare Assets", ["BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "XRP-USD"], default=["BTC-USD", "ETH-USD", "SOL-USD"])
    if compare_assets:
        comp_fig = go.Figure()
        for asset in compare_assets:
            adf, _ = get_crypto_data(asset, "3mo", "1d")
            if not adf.empty:
                norm = (adf["Close"] / adf["Close"].iloc[0]) * 100
                comp_fig.add_trace(go.Scatter(x=norm.index, y=norm, mode="lines", name=asset))
        comp_fig.update_layout(
            title="Indexed Performance (Base 100)",
            template="plotly_dark",
            paper_bgcolor="#090b0e",
            plot_bgcolor="#12161c",
        )
        st.plotly_chart(comp_fig, use_container_width=True)

with tab3:
    detailed_holdings = store.load_detailed()
    rows = []
    for item in detailed_holdings:
        qty = item["quantity"]
        asset = item["ticker"]
        basis = item["avg_buy_price"]
        if qty > 0:
            p, _, _, _, _ = get_live_metrics(asset)
            val = qty * p
            pnl_pct = ((p - basis) / basis * 100.0) if basis > 0 else 0.0
            rows.append(
                {
                    "Asset": asset.replace("-USD", ""),
                    "Quantity": qty,
                    "Avg Basis": round(basis, 2),
                    "Price (USD)": round(p, 2),
                    "Value (USD)": round(val, 2),
                    "Unrealized %": f"{pnl_pct:+.1f}%",
                }
            )
    if rows:
        pdf = pd.DataFrame(rows)
        total_val = float(pdf["Value (USD)"].sum())
        total_cost = sum(item["quantity"] * item["avg_buy_price"] for item in detailed_holdings if item["quantity"] > 0 and item["avg_buy_price"] > 0)
        unreal_pnl = total_val - total_cost if total_cost > 0 else 0.0
        pv1, pv2 = st.columns(2)
        pv1.metric("Total Portfolio Valuation", f"${total_val:,.2f}")
        pv2.metric("Unrealized P&L", f"${unreal_pnl:+,.2f}")
        c_pie, c_tbl = st.columns([1, 1.4])
        with c_pie:
            pie = go.Figure(data=[go.Pie(labels=pdf["Asset"], values=pdf["Value (USD)"], hole=0.45)])
            pie.update_layout(template="plotly_dark", paper_bgcolor="#090b0e", margin=dict(t=10, b=10))
            st.plotly_chart(pie, use_container_width=True)
        with c_tbl:
            st.dataframe(pdf, use_container_width=True, hide_index=True)
            st.download_button(
                "Export Portfolio CSV",
                data=pdf.to_csv(index=False).encode("utf-8"),
                file_name="cryptosight_portfolio.csv",
                mime="text/csv",
            )
        with st.expander("Update Average Buy Basis ($)"):
            basis_opts = [item["ticker"] for item in detailed_holdings]
            b_col1, b_col2, b_col3 = st.columns([1.2, 1.2, 1])
            b_asset = b_col1.selectbox("Asset", basis_opts, key="basis_asset")
            cur_item = next(i for i in detailed_holdings if i["ticker"] == b_asset)
            new_basis = b_col2.number_input("Avg Buy Basis ($)", min_value=0.0, value=float(cur_item["avg_buy_price"]), step=10.0)
            if b_col3.button("Save Basis", use_container_width=True):
                store.save(b_asset, cur_item["quantity"], avg_buy_price=float(new_basis))
                st.rerun()
    else:
        st.info("Set asset quantities in the sidebar to inspect portfolio allocation.")

with tab4:
    if news_articles:
        for art in news_articles[:8]:
            st.markdown(f"**[{art['title']}]({art['link']})** — _{art['publisher']}_")
    else:
        st.info("No live news headlines available for this ticker right now.")

with tab5:
    st.subheader(f"{selected_ticker} · SMA Crossover Backtest Lab")
    bc1, bc2 = st.columns(2)
    fast_win = bc1.slider("Fast SMA Window", 5, 20, 10)
    slow_win = bc2.slider("Slow SMA Window", 15, 50, 20)
    bt_df, _ = get_crypto_data(selected_ticker, "6mo", "1d")
    bt = run_sma_crossover_backtest(bt_df, fast=fast_win, slow=slow_win)
    bk1, bk2, bk3, bk4 = st.columns(4)
    bk1.metric("Strategy Return", f"{bt['strategy_return_pct']:+.2f}%")
    bk2.metric("Buy & Hold Return", f"{bt['buy_hold_return_pct']:+.2f}%")
    bk3.metric("Signal Trades", bt["trades_count"])
    bk4.metric("Active-Day Win Rate", f"{bt['win_rate_pct']:.1f}%")
    eq_df = bt["equity_df"]
    if not eq_df.empty:
        bt_fig = go.Figure()
        bt_fig.add_trace(go.Scatter(x=eq_df.index, y=eq_df["Strategy"], mode="lines", name="SMA Strategy", line=dict(color="#10b981", width=2.2)))
        bt_fig.add_trace(go.Scatter(x=eq_df.index, y=eq_df["BuyHold"], mode="lines", name="Buy & Hold", line=dict(color="#94a3b8", width=1.6, dash="dot")))
        bt_fig.update_layout(title="Equity Curve Comparison (Base 100)", template="plotly_dark", paper_bgcolor="#090b0e", plot_bgcolor="#12161c")
        st.plotly_chart(bt_fig, use_container_width=True)
