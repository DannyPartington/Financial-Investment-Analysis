# METHODS.md  
_End-to-end workflow for the RSI Mean Reversion Trading Project_

---

## 1. Project Architecture & Timeline

This project was built in three stages:

### **1. Streamlit App (built first — interactive exploration)**  
A user-friendly interface where users can:
- Select a market and timeframe  
- Adjust RSI parameters  
- Run a backtest instantly  
- View entry/exit markers on charts  
- Inspect trade logs  
- See summary statistics and market regime detection  

This helped form intuition about how RSI-based strategies behave in different market conditions.

### **2. Batch Backtester (built second — systematic analysis)**  
After exploring the idea interactively, a full batch backtesting engine was built to:
- Loop through **multiple markets**, **multiple timeframes**, and **multiple RSI parameter grids**
- Evaluate **three RSI-based strategies**
- Produce a large structured results table
- Export detailed per-run trade logs

These batch results power the Power BI analysis.

### **3. Power BI Dashboard (built last — deep analysis)**  
The Power BI report reads the batch results CSV and performs:
- Strategy comparison
- Parameter optimisation
- Market-by-market performance analysis
- Deep dive into the Mean Reversion strategy

---

## 2. Data Acquisition

All raw market data used by the **batch backtester** comes from the `data/` folder.

Data is downloaded by `download_data.py`, which uses **two data sources**:

---

### **2.1 Crypto Data (via Binance API using `ccxt`)**

Symbols downloaded:
- BTC/USDT  
- ETH/USDT  
- SOL/USDT  
- BNB/USDT  

Timeframes:
- 1m, 5m, 15m, 1h, 4h

Process:
1. Fetch up to 1000 candles per `(symbol, timeframe)`  
2. Convert OHLCV to a pandas DataFrame  
3. Convert timestamp to datetime  
4. Save to CSV:
   ```
   BTCUSDT_1m.csv
   ETHUSDT_1h.csv
   etc.
   ```

---

### **2.2 Forex, Commodities & Indices (via Yahoo Finance)**

Assets:
- EURUSD  
- EURJPY  
- XAUUSD (Gold)  
- WTI Crude Oil  
- SPY (S&P 500 ETF)

Timeframes:
- 1m, 5m, 15m, 1h, 4h

Because Yahoo imposes limits, the script adjusts request periods:

- 1m → last 7 days  
- 5m → last 60 days  
- 15m → last 90 days  
- 1h → last 180 days  
- 4h → last ~2 years  

Files are saved using the same naming scheme:
```
EURUSD_15m.csv
XAUUSD_1h.csv
```

---

## 3. Data Structure & Preprocessing

### **3.1 File Loading**

Each CSV is loaded using `load_market_csv(path)`:

- Infers which column contains timestamps
- Renames it to `timestamp`
- Ensures six standard columns exist:

```
timestamp, open, high, low, close, volume
```

- Sorts by timestamp
- Returns a clean DataFrame

### **3.2 Market & Timeframe Inference**

The batch script loops over *all* CSVs in `data/`, and identifies the timeframe from the filename:

- Valid suffixes: `1m`, `5m`, `15m`, `1h`, `4h`
- Files without valid suffixes are skipped

Example:
```
BTCUSDT_1m.csv → market=BTCUSDT, timeframe=1m
```

---

## 4. Strategy Logic (Shared Between Streamlit & Backtester)

All RSI logic is implemented once in:
```
utils/strategies.py
```

Used by both:
- The Streamlit App  
- The Batch Backtester  

Shared functions:
- `rsi()`
- `backtest_simple_strategy()`
- `tag_market_regime()`

### **4.1 RSI Period Grid**
The batch backtester tests:
```
[7, 14, 21]
```

The Streamlit app allows interactive selection:
```
5–50
```

### **4.2 Strategies Evaluated**

Both the Streamlit App and the batch backtester evaluate **three strategies**:

1. **Mean Reversion**  
   - Buy when RSI < lower threshold  
   - Exit when RSI > exit level  

2. **Overbought Reversal**  
   - Short when RSI > upper threshold  
   - Exit when RSI < exit level  

3. **Trend-Follow RSI**  
   - Enter when RSI crosses above/below 50  

### **4.3 Market Regime Tagging**
`tag_market_regime()` returns:
- regime label: trending / ranging / volatile  
- metrics:
  - volatility estimate  
  - trend slope estimate  

Used in both Streamlit and batch results.

---

## 5. Batch Backtesting Process

The engine is implemented in:
```
backtester/batch_backtest.py
```

### **5.1 Summary Results Table**

Saved to:
```
results/rsi_strategy_results.csv
```

Contains:
```
market, timeframe, rsi_period,
lower, upper,
strategy,
total_trades, total_pnl_pct, avg_pnl_pct,
win_rate_pct, max_drawdown_pct,
regime, volatility, trend_slope,
bars, start_time, end_time
```

### **5.2 Loop Structure**
For each CSV file:

1. Load & clean the dataset  
2. For each RSI period: compute RSI  
3. Tag regime  
4. For each strategy:  
   - Apply thresholds  
   - Backtest  
   - Collect summary metrics  
   - Save trade log for that run  

### **5.3 Trade Logs**
Saved under:
```
results/trades_<market>_<timeframe>_<strategy>_RSI<period>.csv
```

Contain:
- entry_time  
- exit_time  
- side  
- entry_price  
- exit_price  
- pnl_pct  
- cumulative_pnl_pct  

These are used for validation and parameter tuning.

---

## 6. Streamlit App (Interactive Exploration)

Location:
```
streamlit_app/app.py
```

The app was built **first**, and provides an intuitive UI to understand the strategy.

### **Features**
- Select market, timeframe, RSI period, thresholds  
- Fetches **live Yahoo Finance data** (NOT CSVs)  
- Computes RSI in real time  
- Evaluates **all three strategies simultaneously**  
- Displays:
  - Price chart with entry/exit markers  
  - RSI chart  
  - Market regime banner  
  - Summary statistics  
  - Downloadable trade logs  
- No files are written to disk (`SAVE_OUTPUTS=False`)

### **Purpose**
- Build intuition  
- Demonstrate real-time backtesting  
- Serve as the “front-end explorer” for the strategy logic  

---

## 7. Power BI Workflow

Power BI loads:
```
results/rsi_strategy_results.csv
```

The report includes:
- Strategy comparison dashboards  
- Mean Reversion deep dive  
- Heatmaps for parameter optimisation  
- Win rate vs Drawdown relationships  
- Market-by-market performance  
- Timeframe analysis  
- Trend vs Range regime performance  

The `.pbix` and `.pdf` are stored in the `powerbi/` folder.

---

## 8. Limitations

Current version intentionally keeps things simple:

- Only ~1000 candles per (market, timeframe)
- No slippage / commission modelling
- No leverage or position sizing
- RSI only (no multi-indicator confirmation)
- No walk-forward or live trading validation
- Streamlit uses Yahoo Finance, batch uses CSVs (different data vendors)

These limitations become opportunities in the roadmap.

---

## 9. Next Steps

A detailed roadmap is available in `docs/ROADMAP.md`.  
Key future improvements include:
- Adding slippage & costs  
- Capital curve & drawdown modelling  
- Larger historical datasets  
- Portfolio testing  
- Broker API integration  
- AI/ML-based optimisation  
- Automated trading bot  

---

