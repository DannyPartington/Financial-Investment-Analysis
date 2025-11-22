# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 15:15:38 2025

@author: d_par
"""

"""
Batch backtester for RSI-based strategies
Uses shared logic from utils/strategies.py to stay consistent with Streamlit app.
"""

import os, glob
import pandas as pd
import numpy as np
from itertools import product
from datetime import datetime
from tqdm import tqdm

from utils.strategies import rsi, backtest_simple_strategy, tag_market_regime

DATA_DIR = "data"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

summary_path = os.path.join(RESULTS_DIR, "rsi_strategy_results.csv")
summary_cols = [
    "run_ts","market","timeframe","rsi_period","lower","upper",
    "strategy","total_trades","total_pnl_pct","avg_pnl_pct",
    "win_rate_pct","max_drawdown_pct","regime","volatility","trend_slope",
    "bars","start_time","end_time"
]
if not os.path.exists(summary_path):
    pd.DataFrame(columns=summary_cols).to_csv(summary_path, index=False)

# Config
rsi_periods       = [7, 14, 21]
lower_thresholds  = [30, 25, 20, 15]   # vary only for mean_reversion
upper_thresholds  = [70, 75, 80, 85]   # vary only for overbought_reversal
exit_level        = 50
allowed_timeframes = ["1m","5m","15m","1h","4h"]

strategies = [
    {"name": "Mean Reversion",      "mode": "mean_reversion"},
    {"name": "Overbought Reversal", "mode": "overbought_reversal"},
    {"name": "Trend-follow RSI",    "mode": "trend_follow_rsi"},
]

def load_market_csv(path):
    df = pd.read_csv(path)
    # detect timestamp col
    for c in df.columns:
        if c.lower() in ("timestamp","datetime","date","time"):
            df[c] = pd.to_datetime(df[c])
            df = df.rename(columns={c:"timestamp"})
            break
    required = ["timestamp","open","high","low","close","volume"]
    for r in required:
        if r not in df.columns:
            df[r] = np.nan
    return df[required].sort_values("timestamp").reset_index(drop=True)

csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
if not csv_files:
    print("No CSVs found in /data. Run your downloader first.")
    raise SystemExit(1)

print(f"Found {len(csv_files)} files. Starting backtest...\n")

for fpath in tqdm(csv_files, desc="Files"):
    fname = os.path.basename(fpath)
    base  = fname.rsplit(".", 1)[0]

    # infer timeframe and market
    timeframe = None
    for tf in allowed_timeframes:
        if base.endswith(tf):
            timeframe = tf
            market = base[:-len(tf)].replace("_","").replace("-","").replace("/","")
            break
    if timeframe is None:
        print(f"⚠️ Skipping {fname}: timeframe not detected.")
        continue

    # load data for this file
    try:
        df = load_market_csv(fpath)
    except Exception as e:
        print(f"Error loading {fname}: {e}")
        continue

    # -----------------------------
    # IMPORTANT: all loops below are INSIDE the per-file loop
    # -----------------------------
    for rsi_period in rsi_periods:
        df2 = df.copy().dropna().reset_index(drop=True)
        df2["rsi"] = rsi(df2["close"], period=rsi_period)
        df2 = df2.dropna().reset_index(drop=True)
        if len(df2) < 20:
            continue

        regime, metrics = tag_market_regime(df2)

        for strat in strategies:
            mode = strat["mode"]

            if mode == "mean_reversion":
                # Only vary lower threshold
                for lower in lower_thresholds:
                    cfg = {"mode": mode, "lower": lower, "exit_level": exit_level}
                    summary, trades_df = backtest_simple_strategy(df2, df2["rsi"], cfg)

                    row = {
                        "run_ts": datetime.utcnow().isoformat(),
                        "market": market,
                        "timeframe": timeframe,
                        "rsi_period": rsi_period,
                        "lower": lower,
                        "upper": np.nan,
                        "strategy": strat["name"],
                        "total_trades": summary.get("total_trades", 0),
                        "total_pnl_pct": summary.get("total_pnl_pct", 0.0),
                        "avg_pnl_pct": summary.get("avg_pnl_pct", 0.0),
                        "win_rate_pct": summary.get("win_rate_pct", 0.0),
                        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
                        "regime": regime,
                        "volatility": metrics.get("vol", np.nan),
                        "trend_slope": metrics.get("trend", np.nan),
                        "bars": len(df2),
                        "start_time": df2["timestamp"].iloc[0].isoformat(),
                        "end_time": df2["timestamp"].iloc[-1].isoformat(),
                    }
                    pd.DataFrame([row]).to_csv(summary_path, mode="a", index=False, header=False)

                    if not trades_df.empty:
                        trades_file = os.path.join(
                            RESULTS_DIR,
                            f"trades_{market}_{timeframe}_{strat['name'].replace(' ','_')}_RSI{rsi_period}_L{lower}.csv"
                        )
                        trades_df.to_csv(trades_file, index=False)

            elif mode == "overbought_reversal":
                # Only vary upper threshold
                for upper in upper_thresholds:
                    cfg = {"mode": mode, "upper": upper, "exit_level": exit_level}
                    summary, trades_df = backtest_simple_strategy(df2, df2["rsi"], cfg)

                    row = {
                        "run_ts": datetime.utcnow().isoformat(),
                        "market": market,
                        "timeframe": timeframe,
                        "rsi_period": rsi_period,
                        "lower": np.nan,
                        "upper": upper,
                        "strategy": strat["name"],
                        "total_trades": summary.get("total_trades", 0),
                        "total_pnl_pct": summary.get("total_pnl_pct", 0.0),
                        "avg_pnl_pct": summary.get("avg_pnl_pct", 0.0),
                        "win_rate_pct": summary.get("win_rate_pct", 0.0),
                        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
                        "regime": regime,
                        "volatility": metrics.get("vol", np.nan),
                        "trend_slope": metrics.get("trend", np.nan),
                        "bars": len(df2),
                        "start_time": df2["timestamp"].iloc[0].isoformat(),
                        "end_time": df2["timestamp"].iloc[-1].isoformat(),
                    }
                    pd.DataFrame([row]).to_csv(summary_path, mode="a", index=False, header=False)

                    if not trades_df.empty:
                        trades_file = os.path.join(
                            RESULTS_DIR,
                            f"trades_{market}_{timeframe}_{strat['name'].replace(' ','_')}_RSI{rsi_period}_U{upper}.csv"
                        )
                        trades_df.to_csv(trades_file, index=False)

            elif mode == "trend_follow_rsi":
                cfg = {"mode": mode}
                summary, trades_df = backtest_simple_strategy(df2, df2["rsi"], cfg)

                row = {
                    "run_ts": datetime.utcnow().isoformat(),
                    "market": market,
                    "timeframe": timeframe,
                    "rsi_period": rsi_period,
                    "lower": np.nan,
                    "upper": np.nan,
                    "strategy": strat["name"],
                    "total_trades": summary.get("total_trades", 0),
                    "total_pnl_pct": summary.get("total_pnl_pct", 0.0),
                    "avg_pnl_pct": summary.get("avg_pnl_pct", 0.0),
                    "win_rate_pct": summary.get("win_rate_pct", 0.0),
                    "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
                    "regime": regime,
                    "volatility": metrics.get("vol", np.nan),
                    "trend_slope": metrics.get("trend", np.nan),
                    "bars": len(df2),
                    "start_time": df2["timestamp"].iloc[0].isoformat(),
                    "end_time": df2["timestamp"].iloc[-1].isoformat(),
                }
                pd.DataFrame([row]).to_csv(summary_path, mode="a", index=False, header=False)

                if not trades_df.empty:
                    trades_file = os.path.join(
                        RESULTS_DIR,
                        f"trades_{market}_{timeframe}_{strat['name'].replace(' ','_')}_RSI{rsi_period}.csv"
                    )
                    trades_df.to_csv(trades_file, index=False)

print("\n✅ Batch backtest complete!")
print(f"Summary saved to: {summary_path}")
print(f"Trade logs saved to: {RESULTS_DIR}/")
