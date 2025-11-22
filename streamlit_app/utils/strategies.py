# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 09:30:07 2025

@author: d_par
"""

import numpy as np
import pandas as pd

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/period, adjust=False).mean()
    ma_down = down.ewm(alpha=1/period, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))

def compute_returns_from_trades(trades, df):
    rows = []
    for t in trades:
        entry_price = df.iloc[t['entry_idx']]['close']
        exit_price  = df.iloc[t['exit_idx']]['close']
        pnl = (exit_price - entry_price) / entry_price if t['side']=='long' else (entry_price - exit_price) / entry_price
        rows.append({
            'entry_time':  df.iloc[t['entry_idx']]['timestamp'],
            'exit_time':   df.iloc[t['exit_idx']]['timestamp'],
            'entry_price': entry_price,
            'exit_price':  exit_price,
            'side':        t['side'],
            'pnl_pct':     pnl * 100
        })
    trades_df = pd.DataFrame(rows)
    if trades_df.empty:
        trades_df = pd.DataFrame(columns=['entry_time','exit_time','entry_price','exit_price','side','pnl_pct'])
    trades_df['cumulative_pnl_pct'] = trades_df['pnl_pct'].cumsum()
    return trades_df

def backtest_simple_strategy(df, rsi_series, strategy_cfg):
    lower = strategy_cfg.get('lower', 30)
    upper = strategy_cfg.get('upper', 70)
    exit_level = strategy_cfg.get('exit_level', 50)
    mode = strategy_cfg.get('mode', 'mean_reversion')
    trades, position, entry_idx = [], None, None

    import numpy as np
    for i in range(1, len(df)):
        r = rsi_series.iloc[i]
        if np.isnan(r):
            continue
        if mode == 'mean_reversion':
            if position is None:
                if r < lower:
                    position, entry_idx = 'long', i
            elif position == 'long' and r > exit_level:
                trades.append({'entry_idx': entry_idx, 'exit_idx': i, 'side': 'long'})
                position, entry_idx = None, None

        elif mode == 'overbought_reversal':
            if position is None:
                if r > upper:
                    position, entry_idx = 'short', i
            elif position == 'short' and r < exit_level:
                trades.append({'entry_idx': entry_idx, 'exit_idx': i, 'side': 'short'})
                position, entry_idx = None, None

        elif mode == 'trend_follow_rsi':
            prev = rsi_series.iloc[i-1]
            if position is None:
                if prev < 50 and r > 50:
                    position, entry_idx = 'long', i
                elif prev > 50 and r < 50:
                    position, entry_idx = 'short', i
            else:
                if position == 'long' and r < 50:
                    trades.append({'entry_idx': entry_idx, 'exit_idx': i, 'side': 'long'})
                    position, entry_idx = None, None
                elif position == 'short' and r > 50:
                    trades.append({'entry_idx': entry_idx, 'exit_idx': i, 'side': 'short'})
                    position, entry_idx = None, None

        if i == len(df)-1 and position is not None and entry_idx is not None:
            trades.append({'entry_idx': entry_idx, 'exit_idx': i, 'side': position})
            position, entry_idx = None, None

    trades_df = compute_returns_from_trades(trades, df)
    summary = {
        'total_trades': len(trades_df),
        'total_pnl_pct': trades_df['pnl_pct'].sum() if not trades_df.empty else 0.0,
        'avg_pnl_pct': trades_df['pnl_pct'].mean() if not trades_df.empty else 0.0,
        'win_rate_pct': (trades_df['pnl_pct'] > 0).mean()*100 if not trades_df.empty else 0.0,
        'max_drawdown_pct': 0.0
    }
    if not trades_df.empty:
        equity = (1 + trades_df['pnl_pct']/100).cumprod()
        peak = equity.cummax()
        drawdowns = (equity - peak) / peak
        summary['max_drawdown_pct'] = drawdowns.min() * 100
    return summary, trades_df

def tag_market_regime(df):
    import numpy as np
    df = df.copy()
    df['ret'] = df['close'].pct_change().fillna(0)
    vol = df['ret'].rolling(50).std().iloc[-1] if len(df) >= 50 else df['ret'].std()
    window = min(50, len(df))
    y = np.log(df['close'].iloc[-window:].values)
    x = np.arange(window)
    if len(x) < 3:
        return 'unknown', {'vol': vol, 'trend': 0.0}
    slope = np.polyfit(x, y, 1)[0]
    trend_threshold = 0.0005
    vol_threshold = 0.005
    if abs(slope) > trend_threshold:
        regime = 'trending'
    elif vol > vol_threshold:
        regime = 'volatile'
    else:
        regime = 'ranging'
    return regime, {'vol': vol, 'trend': slope}
