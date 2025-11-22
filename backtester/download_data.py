import os
import pandas as pd
import ccxt
import yfinance as yf
from time import sleep

# === SETUP ===
os.makedirs("data", exist_ok=True)

# ---- 1. CRYPTO MARKETS (from Binance via ccxt) ----
crypto_markets = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT"
]
timeframes = ["1m", "5m", "15m", "1h", "4h"]

print("\n📊 Downloading crypto data from Binance...")
exchange = ccxt.binance()
limit = 1000  # number of candles per request

for symbol in crypto_markets:
    for tf in timeframes:
        print(f"Fetching {symbol} ({tf})...")
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            file_name = f"{symbol.replace('/', '')}_{tf}.csv"
            df.to_csv(f"data/{file_name}", index=False)
            sleep(1)
        except Exception as e:
            print(f"⚠️ Error fetching {symbol} ({tf}): {e}")

# ---- 2. FOREX & COMMODITIES (from Yahoo Finance) ----
print("\n💱 Downloading forex & commodities data from Yahoo Finance...")

yahoo_markets = {
    "EURUSD": "EURUSD=X",   # Euro / US Dollar
    "EURJPY": "EURJPY=X",   # Euro / Japanese Yen
    "XAUUSD": "GC=F",       # Gold futures
    "WTIUSD": "CL=F",        # WTI Crude Oil futures
    "SPY": "SPY"            # S&P 500 ETF (US Stock Market)
}

for label, ticker in yahoo_markets.items():
    for interval in timeframes:
        print(f"Downloading {label} ({interval})...")
        try:
            # Note: Yahoo only supports 1m data for 7 days, higher intervals have longer history
            period = "7d" if interval == "1m" else "60d"
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            df.reset_index(inplace=True)
            df.rename(columns={"Datetime": "timestamp"}, inplace=True)
            df = df[["timestamp", "Open", "High", "Low", "Close", "Volume"]]
            df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
            file_name = f"{label}_{interval}.csv"
            df.to_csv(f"data/{file_name}", index=False)
        except Exception as e:
            print(f"⚠️ Error downloading {label} ({interval}): {e}")

print("\n✅ Done! All crypto, forex, and commodity data saved in /data")
