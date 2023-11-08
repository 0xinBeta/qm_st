import ccxt
import pandas as pd


exchange = ccxt.binance({

    "enableRateLimit": True,
})

candles = exchange.fetch_ohlcv(symbol="BTC/USDT", timeframe="15m", limit=5000)
print(candles)

df = pd.DataFrame(candles, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

# Convert the timestamp to a readable date format if necessary
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

df.to_csv("bingx.csv")