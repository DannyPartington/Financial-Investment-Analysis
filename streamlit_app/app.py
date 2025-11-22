# -*- coding: utf-8 -*-
"""
RSI Strategy Analyzer (Portfolio Version)
------------------------------------------
- Downloads OHLCV data from Yahoo Finance using yfinance.
- Evaluates 3 RSI-based strategies.
- Displays results, charts, and downloadable trade logs.
- Does NOT write any files to disk (clean for portfolio/demo use).
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objs as go
import os
from datetime import datetime, timedelta

from utils.strategies import (
    rsi,
    compute_returns_from_trades,
    backtest_simple_strategy,
    tag_market_regime,
)

# -------------------------
# SETTINGS
# -------------------------
SAVE_OUTPUTS = False  # prevent writing to local disk
st.set_page_config(layout="wide", page_title="RSI Strategy Analyzer")

# -------------------------
# Helper function
# -------------------------
@st.cache_data
def fetch_data_yfinance(ticker, period="60d", interval="1h"):
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if df.empty:
        raise ValueError("No data returned — check ticker or data availability.")
    df = df.dropna()
    df.rename(columns={"Adj Close": "adj_close"}, inplace=True)
    df["timestamp"] = df.index
    df = df[["Open", "High", "Low", "Close", "Volume", "timestamp"]]
    df.columns = ["open", "high", "low", "close", "volume", "timestamp"]
    return df

# -------------------------
# UI
# -------------------------
st.title("RSI Strategy Analyzer")

with st.sidebar:
    st.header("Controls")
    market = st.selectbox(
        "Choose Market / Ticker",
        ["SPY", "QQQ", "EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD", "GC=F"],
    )
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    period_lookup = {
        "1m": "7d",
        "5m": "60d",
        "15m": "90d",
        "1h": "180d",
        "4h": "730d",
        "1d": "max",
    }
    period = period_lookup.get(timeframe, "90d")
    rsi_period = st.slider("RSI Period", 5, 50, 14)
    lower_thresh = st.slider("Lower Threshold (Buy)", 5, 45, 30)
    upper_thresh = st.slider("Upper Threshold (Short)", 55, 95, 70)
    exit_level = st.slider("Exit Level (Mid)", 30, 70, 50)

st.markdown("""
Evaluates **3 RSI-based strategies**:
- *Mean Reversion:* Buy when RSI < lower, sell when RSI > exit level  
- *Overbought Reversal:* Short when RSI > upper, cover when RSI < exit level  
- *Trend-following RSI:* Enter on RSI cross of 50
""")

status_msg = st.empty()
status_msg.info("Fetching data...")

try:
    df = fetch_data_yfinance(market, period=period, interval=timeframe)
except Exception as e:
    st.error(f"Data fetch failed: {e}")
    st.stop()

df["rsi"] = rsi(df["close"], period=rsi_period)
df = df.dropna().reset_index(drop=True)

strategies = [
    {"name": "Mean Reversion", "mode": "mean_reversion", "lower": lower_thresh, "exit_level": exit_level},
    {"name": "Overbought Reversal", "mode": "overbought_reversal", "upper": upper_thresh, "exit_level": exit_level},
    {"name": "Trend-follow RSI", "mode": "trend_follow_rsi"},
]

results, trades_tables = {}, {}
for s in strategies:
    summary, trades_df = backtest_simple_strategy(df, df["rsi"], s)
    results[s["name"]] = summary
    trades_tables[s["name"]] = trades_df

regime, metrics = tag_market_regime(df)
status_msg.success("Analysis complete.")

# -------------------------
# Market Regime Banner
# -------------------------
_badge_map = {
    "trending": ("🟢 TRENDING", "#2ecc71"),
    "ranging": ("🔵 RANGING", "#3498db"),
    "volatile": ("🟡 VOLATILE", "#f1c40f"),
    "unknown": ("⚪ UNKNOWN", "#95a5a6"),
}
label, color = _badge_map.get(regime, _badge_map["unknown"])
vol_text = f"Volatility: {metrics.get('vol', 0):.5f}"
trend_text = f"Slope: {metrics.get('trend', 0):.6f}"

banner_html = f"""
<div style="width:100%; padding:10px 12px; border-radius:8px; margin-bottom:12px;
            display:flex; align-items:center; justify-content:space-between;
            background:linear-gradient(90deg, rgba(0,0,0,0.03), rgba(0,0,0,0.01));">
  <div style="display:flex; gap:12px; align-items:center;">
    <div style="padding:10px 14px; border-radius:10px; background:{color}; color:#071013; font-weight:700; font-size:16px;">
      {label}
    </div>
    <div style="font-size:14px; color:#334155;">
      <strong>{vol_text}</strong> &nbsp; · &nbsp; <strong>{trend_text}</strong>
    </div>
  </div>
  <div style="font-size:13px; color:#475569;">(Rolling volatility & trend slope heuristic)</div>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)

# -------------------------
# Summary Cards
# -------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Market Info")
    st.write(f"**Ticker:** {market}")
    st.write(f"**Regime:** {regime}")
    st.write(f"Volatility: {metrics['vol']:.5f}")
    st.write(f"Trend slope: {metrics['trend']:.6f}")

with col2:
    st.subheader("RSI Parameters")
    st.write(f"Period: {rsi_period}")
    st.write(f"Lower: {lower_thresh}  |  Upper: {upper_thresh}  |  Exit: {exit_level}")

with col3:
    st.subheader("Data Info")
    st.write(f"Timeframe: {timeframe}")
    st.write(f"Bars: {len(df)}")
    st.write(f"From {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")

st.markdown("---")

# -------------------------
# Strategy Result Boxes
# -------------------------
strat_cols = st.columns(3)
for i, s in enumerate(strategies):
    name = s["name"]
    summ = results[name]
    with strat_cols[i]:
        st.metric(label=name + " — Total Trades", value=int(summ["total_trades"]))
        st.metric(label="Total PnL (%)", value=f"{summ['total_pnl_pct']:.2f}")
        st.metric(label="Win Rate (%)", value=f"{summ['win_rate_pct']:.2f}")
        st.write(f"Avg trade PnL (%): {summ['avg_pnl_pct']:.2f}")
        st.write(f"Max Drawdown (%): {summ['max_drawdown_pct']:.2f}")

st.markdown("### Price & RSI Chart (Interactive)")

# -------------------------
# Price Chart + Markers
# -------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["timestamp"], y=df["close"], name="Price (Close)"))
fig.update_layout(height=500, xaxis_title="Time", yaxis_title="Price")

selected_strategy = st.selectbox("Select strategy for trade markers", [s["name"] for s in strategies])
trades_df_plot = trades_tables[selected_strategy]
if not trades_df_plot.empty:
    fig.add_trace(go.Scatter(
        x=trades_df_plot["entry_time"],
        y=trades_df_plot["entry_price"],
        mode="markers",
        marker=dict(symbol="triangle-up", size=10, color="green"),
        name="Entries",
    ))
    fig.add_trace(go.Scatter(
        x=trades_df_plot["exit_time"],
        y=trades_df_plot["exit_price"],
        mode="markers",
        marker=dict(symbol="triangle-down", size=10, color="red"),
        name="Exits",
    ))
st.plotly_chart(fig, use_container_width=True)

# RSI Panel
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], name="RSI"))
fig2.add_hline(y=lower_thresh, line_dash="dash", annotation_text="Lower")
fig2.add_hline(y=upper_thresh, line_dash="dash", annotation_text="Upper")
fig2.add_hline(y=exit_level, line_dash="dot", annotation_text="Exit")
fig2.update_layout(height=250, yaxis_title="RSI")
st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Trades Tables (no disk writes)
# -------------------------
st.markdown("### Trades Table and Downloads")
tabs = st.tabs([s["name"] for s in strategies])
for idx, s in enumerate(strategies):
    with tabs[idx]:
        tdf = trades_tables[s["name"]]
        if tdf.empty:
            st.info("No trades for this strategy with current parameters.")
        else:
            st.dataframe(
                tdf[["entry_time", "exit_time", "side", "entry_price", "exit_price", "pnl_pct", "cumulative_pnl_pct"]]
            )
            st.download_button(
                label=f"Download {s['name']} Trades CSV",
                data=tdf.to_csv(index=False),
                file_name=f"{market}_{timeframe}_{s['name'].replace(' ','_')}_trades.csv",
                mime="text/csv",
            )

st.markdown("---")
st.write("**Notes:**")
st.write("""
- Uses live data via Yahoo Finance (no local storage).  
- Slippage, commissions, and execution constraints are NOT modeled.  
- Strategy logic is simplified for demonstration.  
- Safe for recruiters and portfolio viewers — no files are written locally.
""")
