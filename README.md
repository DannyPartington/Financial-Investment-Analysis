#  RSI Mean Reversion Trading Strategy  
### *End-to-End Data Analytics | Backtesting | Power BI | Streamlit*

This project explores the performance of **RSI-based trading strategies** across multiple markets and timeframes using:

- **Python (Backtesting Engine)**
- **Streamlit Web App**
- **Power BI Analytics Dashboard**

It demonstrates an end-to-end workflow from **data collection → backtesting → visual exploration → systematic analysis**, using data analytics, quant, and financial engineering.

---

# 🔍 Project Overview

This repo contains:

###  **Interactive Streamlit App**
Run RSI strategies on live data and view:
- Entry/exit markers  
- RSI overlays  
- Performance metrics  
- Market regime classification  
- Downloadable trade logs  

###  **Batch Backtester (Python)**
Systematically tests:
- 3 RSI-based strategies (Mean Reversion, Overbought Reversal, Trend-Follow RSI)  
- Multiple markets  
- Multiple timeframes  
- Multiple RSI periods & thresholds  

Generates a unified results table for Power BI.

###  **Power BI Report**
A multi-page dashboard analyzing:
- Performance distributions  
- Parameter sensitivity  
- Strategy comparison  
- Deep dive into Mean Reversion  

---

# 📂 Project Structure

```
Financial Markets Analysis/
│
├─ streamlit_app/
│   └─ app.py
│
├─ backtester/
│   ├─ batch_backtest.py
│   └─ download_data.py
│
├─ powerbi/
│   ├─ Trading_Strategy_Analysis.pbix
│   └─ Trading_Strategy_Analysis.pdf
│
├─ data
│                   # Full raw data (ignored in GitHub)
├─ data_sample/
│   └─ rsi_strategy_results_sample.csv
│
├─ results/
│   └─ rsi_strategy_results.csv (generated)
│
├─ docs/
│   ├─ METHODS.md
│   ├─ ROADMAP.md
│   └─ screenshots/
│       ├─ pbi_overview.png
│       ├─ pbi_distribution_analysis.png
│       ├─ pbi_rsi_parameter_analysis.png
│       ├─ pbi_mean_reversion_deep_dive.png
│       ├─ streamlit_controls.png
│       ├─ streamlit_banner_and_summary.png
│       ├─ streamlit_price_chart.png
│       ├─ streamlit_strategy_metrics.png
│       └─ streamlit_trades_table.png
│
├─ LICENSE
└─ README.md
```

---

# 🚀 Running the Streamlit App

### 1. Install dependencies
From project root:

```bash
pip install -r requirements.txt
```

### 2. Launch the app
```bash
streamlit run streamlit_app/app.py
```

### Features
- Live data via Yahoo Finance  
- 3 RSI strategies evaluated simultaneously
- Adjustable controls panel to modify strategy paramters
- Entry/exit visualisation  
- Trade logs with downloadable CSV  
- Market regime detection (trending, ranging, volatile)  
- No files written to disk (portfolio-safe)

---

# 📊 Power BI Dashboard

Located in `powerbi/`.

### Pages include:

#### **1. Overview**
KPIs, filters, market summaries  
![Overview](docs/screenshots/pbi_overview.png)

#### **2. Distribution Analysis**
PnL histograms for each strategy  
![Distribution](docs/screenshots/pbi_distribution_analysis.png)

#### **3. RSI Parameter Analysis**
Performance impact of RSI periods & thresholds  
![Parameters](docs/screenshots/pbi_rsi_parameter_analysis.png)

#### **4. Mean Reversion deep dive**
Full breakdown of the strongest-performing strategy  
![Mean Reversion Deep Dive](docs/screenshots/pbi_mean_reversion_deep_dive.png)

---

# 💻 Streamlit App Preview

### Controls & Inputs
![Streamlit Controls](docs/screenshots/streamlit_controls.png)

### Strategy Summary & Regime Banner
![Banner Summary](docs/screenshots/streamlit_banner_and_summary.png)

### Interactive Price Chart
![Price Chart](docs/screenshots/streamlit_price_chart.png)

### Strategy Metrics
![Metrics](docs/screenshots/streamlit_strategy_metrics.png)

### Trades Table
![Trades Table](docs/screenshots/streamlit_trades_table.png)

---

# ⚙️  Methodology

A full explanation of the workflow (data acquisition, preprocessing, RSI logic, strategy grid, regime tagging, metrics and outputs) is in:

📄 **`docs/METHODS.md`**

---

# 🧭 Future Development Roadmap

Planned upgrades include:

- Transaction costs & slippage  
- Position sizing models    
- Larger historical datasets  
- Multi-strategy portfolios  
- Broker API integration  
- AI/ML-based optimisation  
- Automated trading bot  

See the full document:

📄 **`docs/ROADMAP.md`**

---

# 🧠 Key Insights

Across all experiments:

- **Mean Reversion** is the most stable strategy  
- Performs best in **ranging markets**  
- Lower-entry thresholds (20–30) yield stronger reversion  
- Trend-follow RSI has higher trade frequency but lower consistency  
- Overbought reversal has volatile outcomes and left-skewed distributions  

The analysis provides a base for next steps toward automation or AI signal generation.

---

# 📝 License

MIT License © 2025

---

# 📬 Contact

- GitHub: *DannyPartington*  
- Email: *d_partington@hotmail.com*  
- Portfolio website:   
