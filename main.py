import ccxt
import pandas as pd
import numpy as np

def fetch_data(symbol, timeframe, limit):
    binance = ccxt.binanceusdm()
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def find_pivots(df, leftLenH, rightLenH, leftLenL, rightLenL):
    df['ph'] = np.nan
    df['pl'] = np.nan

    for i in range(leftLenH, len(df) - rightLenH):
        # Pivot High
        if df['High'][i] == max(df['High'][i - leftLenH:i + rightLenH + 1]):
            df.at[i + rightLenH, 'ph'] = df['High'][i]
        
        # Pivot Low
        if df['Low'][i] == min(df['Low'][i - leftLenL:i + rightLenL + 1]):
            df.at[i + rightLenL, 'pl'] = df['Low'][i]

    return df

# def pattern(df):
#     df = find_pivots(df, 5, 5, 5, 5)
    
#     # Identify the Zigzag pattern
#     df['Pattern'] = False
#     for i in range(3, len(df)):
#         if (not np.isnan(df['pl'][i-3])) and (not np.isnan(df['ph'][i-2])) and (not np.isnan(df['pl'][i-1])) and (not np.isnan(df['ph'][i])):
#             if (df['pl'][i-3] < df['pl'][i-1]) and (df['ph'][i-2] < df['ph'][i]):
#                 df.at[i, 'Pattern'] = True

#     return df

def main():
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 100 
    df = fetch_data(symbol, timeframe, limit)
    # df_with_patterns = pattern(df)
    # df_with_patterns.to_csv("df_test.csv")

if __name__ == "__main__":
    main()
