# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 05:22:53 2025

@author: d_par
"""

# rsi_app_auto.py
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

st.set_page_config(layout="wide", page_title="RSI Strategy Analyzer (Auto-run)")

# -------------------------
# Helper functions
# -------------------------
@st.cache_data
def fetch_data_yfinance(ticker, period="60d", interval="1h"):
    """
    Fetch OHLCV data using yfinance.
    period examples: "60d", "180d", "730d"
    interval examples: "1m", "5m", "1h", "4h", "1d"
    Note: yfinance intraday intervals often limited to ~60 days or less.
    """
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if df.empty:
        raise ValueError("No data returned — check ticker or data availability for that interval/period.")
    df = df.dropna()
    df.rename(columns={"Adj Close": "adj_close"}, inplace=True)
    df['timestamp'] = df.index
    df = df[['Open','High','Low','Close','Volume','timestamp']]
    df.columns = ['open','high','low','close','volume','timestamp']
    return df

# -------------------------
# Streamlit UI
# -------------------------
st.title("RSI Strategy Analyzer — Multi-Market (Auto-run)")

with st.sidebar:
    st.header("Controls")
    market = st.selectbox("Choose market / ticker", options=[
        "SPY", "QQQ", "EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD", "GC=F"
    ])
    timeframe = st.selectbox("Timeframe", options=["1m","5m","15m","1h","4h","1d"], index=3)
    period_lookup = {
        "1m":"7d", "5m":"60d", "15m":"90d", "1h":"180d", "4h":"730d", "1d":"max"
    }
    period = period_lookup.get(timeframe, "90d")
    rsi_period = st.slider("RSI period", min_value=5, max_value=50, value=14)
    lower_thresh = st.slider("Lower threshold (buy for mean reversion)", 5, 45, 30)
    upper_thresh = st.slider("Upper threshold (short for reversal)", 55, 95, 70)
    exit_level = st.slider("Exit level (mid)", 30, 70, 50)

st.markdown("""
This demo evaluates **3 RSI-based strategies** across the chosen market and timeframe.
- Mean Reversion: buy when RSI < lower threshold, exit when RSI > exit level.
- Overbought Reversal: short when RSI > upper threshold, cover when RSI < exit level.
- Trend-following (RSI-based): enter on RSI cross of 50.
""")

# Auto-run: compute immediately after any input change
status_msg = st.empty()
status_msg.info("Fetching data and computing results... (this runs automatically on input changes)")

try:
    df = fetch_data_yfinance(market, period=period, interval=timeframe)
except Exception as e:
    st.error(f"Data fetch failed: {e}")
    st.stop()

df['rsi'] = rsi(df['close'], period=rsi_period)
df = df.dropna().reset_index(drop=True)

strategies = [
    {'name':'Mean Reversion', 'mode':'mean_reversion', 'lower': lower_thresh, 'exit_level': exit_level},
    {'name':'Overbought Reversal', 'mode':'overbought_reversal', 'upper': upper_thresh, 'exit_level': exit_level},
    {'name':'Trend-follow RSI', 'mode':'trend_follow_rsi'}
]

results = {}
trades_tables = {}
for s in strategies:
    cfg = s.copy()
    cfg['mode'] = s['mode']
    summary, trades_df = backtest_simple_strategy(df, df['rsi'], cfg)
    results[s['name']] = summary
    trades_tables[s['name']] = trades_df

regime, metrics = tag_market_regime(df)



# Sidebar banner (persistent while scrolling)
try:
    label = {"trending":"🟢 TRENDING", "ranging":"🔵 RANGING", "volatile":"🟡 VOLATILE"}.get(regime, "⚪ UNKNOWN")
except NameError:
    regime, metrics = tag_market_regime(df)
    label = {"trending":"🟢 TRENDING", "ranging":"🔵 RANGING", "volatile":"🟡 VOLATILE"}.get(regime, "⚪ UNKNOWN")

st.sidebar.markdown(f"**Market Regime:**  \n\n### {label}  \n\nVol: `{metrics.get('vol',0):.5f}`  \nSlope: `{metrics.get('trend',0):.6f}`")


status_msg.success("Analysis complete.")


# -------------------------
# Phase 1: Persist run summary + trade logs to CSV files
# Insert immediately AFTER computing `results`, `trades_tables`, and `regime, metrics`
# -------------------------

# ensure results folder exists
os.makedirs("results", exist_ok=True)

# Basic metadata for this run
run_meta = {
    "run_ts": datetime.utcnow().isoformat(),
    "market": market,
    "timeframe": timeframe,
    "rsi_period": int(rsi_period),
    "lower_thresh": int(lower_thresh),
    "upper_thresh": int(upper_thresh),
    "exit_level": int(exit_level),
    "regime": regime,
    "volatility": float(metrics.get("vol", np.nan)),
    "trend_slope": float(metrics.get("trend", np.nan)),
    "bars": int(len(df)),
    "start_time": df['timestamp'].iloc[0].isoformat() if len(df)>0 else None,
    "end_time": df['timestamp'].iloc[-1].isoformat() if len(df)>0 else None
}

# Build a single-row summary DataFrame for all strategies (one row per strategy)
summary_rows = []
for s_name, summ in results.items():
    row = run_meta.copy()
    row.update({
        "strategy": s_name,
        "total_trades": int(summ.get("total_trades", 0)),
        "total_pnl_pct": float(summ.get("total_pnl_pct", 0.0)),
        "avg_pnl_pct": float(summ.get("avg_pnl_pct", 0.0)),
        "win_rate_pct": float(summ.get("win_rate_pct", 0.0)),
        "max_drawdown_pct": float(summ.get("max_drawdown_pct", 0.0)),
    })
    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows)

# Append summary to master results CSV
results_path = os.path.join("results", "rsi_strategy_results.csv")
summary_df.to_csv(results_path, mode="a", index=False, header=not os.path.exists(results_path))

# Also save trade logs for each strategy (append if file exists)
for s_name, trades_df in trades_tables.items():
    # add run meta to trades table for traceability
    if not trades_df.empty:
        trades_copy = trades_df.copy()
        trades_copy["market"] = market
        trades_copy["timeframe"] = timeframe
        trades_copy["rsi_period"] = int(rsi_period)
        trades_copy["strategy"] = s_name
        trades_copy["run_ts"] = run_meta["run_ts"]
        # filename safe strategy name
        safe_name = s_name.replace(" ", "_").lower()
        trades_path = os.path.join("results", f"trade_logs_{market}_{timeframe}_{safe_name}.csv")
        trades_copy.to_csv(trades_path, mode="a", index=False, header=not os.path.exists(trades_path))

# Small UI confirmation
st.success(f"Saved run summary to `{results_path}` and trade logs to `results/`.")


# Market condition banner — high visibility

try:
    regime
except NameError:
    regime, metrics = tag_market_regime(df)

_badge_map = {
    "trending": ("🟢 TRENDING", "#2ecc71"),
    "ranging":  ("🔵 RANGING", "#3498db"),
    "volatile": ("🟡 VOLATILE", "#f1c40f"),
    "unknown":  ("⚪ UNKNOWN", "#95a5a6")
}
label, color = _badge_map.get(regime, _badge_map["unknown"])

vol_text = f"Vol (last 50): {metrics.get('vol', 0):.5f}"
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
  <div style="font-size:13px; color:#475569;">Regime uses rolling vol & trend slope heuristic</div>
</div>
"""
st.markdown(banner_html, unsafe_allow_html=True)
# -------------------------



# Layout: top summary cards
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Market")
    st.write(market)
    st.write("Regime:", regime)
    st.write(f"Volatility (last 50 bars std): {metrics['vol']:.5f}")
    st.write(f"Trend slope (log-price): {metrics['trend']:.6f}")

with col2:
    st.subheader("RSI Params")
    st.write(f"Period: {rsi_period}")
    st.write(f"Lower: {lower_thresh}  Upper: {upper_thresh}  Exit: {exit_level}")

with col3:
    st.subheader("Data")
    st.write(f"Timeframe: {timeframe}  Period: {period}")
    st.write(f"Bars: {len(df)}")

st.markdown("---")

# Three strategy result boxes
strat_cols = st.columns(3)
for i, s in enumerate(strategies):
    name = s['name']
    summ = results[name]
    with strat_cols[i]:
        st.metric(label=name + " — Total Trades", value=int(summ['total_trades']))
        st.metric(label="Total PnL (%)", value=f"{summ['total_pnl_pct']:.2f}")
        st.metric(label="Win Rate (%)", value=f"{summ['win_rate_pct']:.2f}")
        st.write(f"Avg trade PnL (%): {summ['avg_pnl_pct']:.2f}")
        st.write(f"Max Drawdown (%): {summ['max_drawdown_pct']:.2f}")

st.markdown("### Price & RSI chart (interactive)")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['close'], name='Price (close)'))
fig.update_layout(height=500, xaxis_title="Time", yaxis_title="Price")

selected_strategy_for_plot = st.selectbox("Select strategy to show trade markers", options=[s['name'] for s in strategies])
trades_df_plot = trades_tables[selected_strategy_for_plot]
if not trades_df_plot.empty:
    entry_markers = go.Scatter(
        x=trades_df_plot['entry_time'],
        y=trades_df_plot['entry_price'],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10),
        name='Entries'
    )
    exit_markers = go.Scatter(
        x=trades_df_plot['exit_time'],
        y=trades_df_plot['exit_price'],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10),
        name='Exits'
    )
    fig.add_trace(entry_markers)
    fig.add_trace(exit_markers)
st.plotly_chart(fig, use_container_width=True)

# RSI panel
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI'))
fig2.add_hline(y=lower_thresh, line_dash="dash", annotation_text="Lower")
fig2.add_hline(y=upper_thresh, line_dash="dash", annotation_text="Upper")
fig2.add_hline(y=exit_level, line_dash="dot", annotation_text="Exit")
fig2.update_layout(height=250, yaxis_title="RSI")
st.plotly_chart(fig2, use_container_width=True)


# --- Market condition tagging ---
import numpy as np

# logic for tagging
price_changes = df['close'].pct_change().dropna()
volatility = price_changes.std() * 100  # percentage volatility
rsi_mean = df['rsi'].mean()

if volatility < 0.8 and 40 < rsi_mean < 60:
    market_condition = "Ranging"
    color = "secondary"
elif volatility >= 0.8 and (rsi_mean > 60 or rsi_mean < 40):
    market_condition = "Trending"
    color = "success"
else:
    market_condition = "Volatile"
    color = "warning"

st.markdown(f"### Current Market Condition (based on last 50 candles): "
            f"<span class='badge bg-{color}'>{market_condition}</span>", 
            unsafe_allow_html=True)


st.markdown("### Trades table and details")
tabs = st.tabs([s['name'] for s in strategies])
for idx, s in enumerate(strategies):
    with tabs[idx]:
        tdf = trades_tables[s['name']]
        if tdf.empty:
            st.info("No trades for this strategy with current parameters.")
        else:
            st.dataframe(tdf[['entry_time','exit_time','side','entry_price','exit_price','pnl_pct','cumulative_pnl_pct']])
            st.download_button(
                label=f"Download {s['name']} trades CSV",
                data=tdf.to_csv(index=False),
                file_name=f"{market}_{timeframe}_{s['name'].replace(' ','_')}_trades.csv",
                mime="text/csv"
            )

st.markdown("---")
st.write("Notes & limitations:")
st.write("""
- Data availability for intraday intervals depends on the data provider (yfinance may have limitations).
- Slippage, commissions, and execution constraints are NOT modelled — treat backtest PnL as indicative only.
- Strategy definitions are intentionally simple; you can extend them to include stop-losses, take-profits, position-sizing, and more robust signal filters.
""")
