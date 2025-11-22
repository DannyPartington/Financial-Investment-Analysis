# ROADMAP.md  
_Future development plan for the RSI Mean Reversion / Multi-Strategy Trading System_

This roadmap outlines the next stages of development for converting this project from an analytical research tool into a production-ready automated trading system.

---

# 1. Backtesting Improvements

## **1.1 Add Transaction Costs & Slippage**
- Model percentage-based fees for crypto
- Model pip spreads for FX
- Add slippage assumptions for illiquid markets and lower timeframes  
- Adjust PnL calculations accordingly  
- Add commission breakdown in results

## **1.2 Include Position Sizing & Capital Curves**
- Fixed fractional position sizing  
- Kelly fraction experiments  
- ATR-based volatility sizing  
- Track:
  - Equity curve  
  - Max drawdown  
  - Sharpe / Sortino ratios  
  - Profit factor

## **1.3 Expand Strategy Families**
Add additional strategies beyond RSI:
- Simple moving average crossovers  
- Bollinger Band Mean Reversion  
- Momentum bursts  
- MACD divergences  
- Volatility breakout models  

This will allow multi-strategy ensemble testing.

## **1.4 Walk-Forward / Out-of-Sample Testing**
- Train strategy on 70% of dataset  
- Validate on remaining 30%  
- Use rolling walk-forward windows  
- Compare in-sample vs out-of-sample performance

---

# 2. Streamlit App Enhancements

## **2.1 Multi-strategy comparison view**
Plot PnL curves for all strategies on one page.

## **2.2 Session persistence**
Allow the user to save parameter presets.

## **2.3 Live price feed mode**
Use WebSocket-based streaming data (Binance / Polygon).

## **2.4 Deploy App Online**
Deploy on:
- Streamlit Cloud  
- Render  
- Railway  
This allows recruiters and clients to use it without installing anything.

---

# 3. Data Engineering Upgrades

## **3.1 Larger Historical Downloads**
Replace current limits with:
- Binance futures API for unlimited candles  
- Polygon.io for equities  
- AlphaVantage / Oanda for FX

## **3.2 Database Storage**
Move from CSVs to:
- SQLite (simple)
- PostgreSQL (scalable)
- InfluxDB (time-series)

## **3.3 Automated Daily Data Pipeline**
Schedule data refreshes using:
- cron  
- Airflow (for more advanced pipelines)

---

# 4. Power BI Dashboard Extensions

## **4.1 Rolling PnL Curves**
Add equity curves per strategy and per market.

## **4.2 Risk Metrics Page**
Include:
- Sharpe  
- Sortino  
- Calmar  
- Max DD heatmaps  
- Consecutive win/loss distributions  

## **4.3 Market Regime Diagnostics**
Analyse how each strategy behaves in:
- trending markets  
- ranging markets  
- high volatility periods  

## **4.4 Parameter Search Explorer**
Display:
- RSI Period × Threshold optimization  
- 3D surface plots (PnL, DD, Win Rate)

---

# 5. Automated Trading Bot (Major Next Step)

## **5.1 Broker Integration**
API options:
- Binance  
- Oanda  
- Alpaca  
- Interactive Brokers  

## **5.2 Execution Engine**
Core components:
- order manager  
- position manager  
- risk manager  
- live PnL and exposure tracking  

## **5.3 Live Strategy Monitoring Dashboard**
Track:
- open positions  
- unrealized PnL  
- risk thresholds  
- trade frequency  
- alerts on anomalies  

## **5.4 Safety Features**
- Max drawdown stop  
- Daily loss limit  
- Internet disconnect fail-safe  
- API key encryption

---

# 6. Machine Learning Extensions

## **6.1 Regime Classification (Supervised)**
Train a model to classify:
- trending  
- ranging  
- volatile  

Better than heuristic tagging.

## **6.2 Signal Prediction Models**
Use ML to anticipate:
- reversals  
- volatility bursts  
- trend breakouts  

Potential models:
- Gradient boosting  
- LSTM networks  
- 1D CNN on price sequences

## **6.3 Reinforcement Learning Agent**
Train an RL agent to:
- choose thresholds dynamically  
- select which strategy to run  
- size positions optimally  

---

# 7. Packaging & Productionisation

## **7.1 Convert backtesting engine into a Python package**
Installable via:
```
pip install rsi-trader
```

## **7.2 Create CLI Tools**
Examples:
```
backtest run --market BTCUSDT --tf 1m --strategy mean_reversion
backtest grid-search --market EURUSD --rsi 7 14 21
```

## **7.3 Add Unit Tests**
Ensure stable:
- RSI calculation  
- regime tagging  
- trade lifecycle  
- PnL functions

Use `pytest` and GitHub Actions.

---

# 8. Long-Term Vision: Full Trading Platform

## **8.1 Web dashboard**
- React/Next.js or Dash  
- Real-time charts  
- Strategy selection  
- Live trades and alerts  

## **8.2 Mobile app**
For monitoring and alerts.

## **8.3 Multi-strategy portfolio**
Combine:
- trend  
- mean reversion  
- volatility  
- seasonal patterns  

## **8.4 Cloud infrastructure**
- AWS Lambda for event-driven functions  
- S3 for data storage  
- EC2 for execution engine  
- CloudWatch for monitoring  

---

#  Summary

This roadmap outlines the path from:
- **interactive research tool** →  
- **batch-tested systematic framework** →  
- **automated trading system** →  
- **AI-enhanced strategy platform**