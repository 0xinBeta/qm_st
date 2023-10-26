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

def pattern(df):
    df = find_pivots(df, 5, 5, 5, 5)
    df['pattern_bull'] = False
    df['pattern_bear'] = False
    
    pattern_list = []
    bull_flag = False
    bear_flag = False
    pl_values = []  # List to store pivot lows
    ph_values = []  # List to store pivot highs

    for i in range(len(df)):
        # Check if current is a pivot low (pl)
        if not np.isnan(df['pl'][i]):
            pattern_list.append('pl')
            pl_values.append(df['pl'][i])
            bull_flag = False
            bear_flag = False
        
        # Check if current is a pivot high (ph)
        elif not np.isnan(df['ph'][i]):
            pattern_list.append('ph')
            ph_values.append(df['ph'][i])
            bull_flag = False
            bear_flag = False
            
        # Check for pattern pl-ph-pl-ph or ph-pl-ph-pl
        if len(pattern_list) >= 4 and len(pl_values) >= 2 and len(ph_values) >= 2:
            last_four = pattern_list[-4:]
            if last_four == ['pl', 'ph', 'pl', 'ph']:
                if pl_values[-2] < pl_values[-1] and ph_values[-2] < ph_values[-1]:
                    bull_flag = True
                # Remove the first elements in pattern_list, pl_values, ph_values
                pattern_list.pop(0)
                pl_values.pop(0)
                ph_values.pop(0)

            elif last_four == ['ph', 'pl', 'ph', 'pl']:
                if ph_values[-2] > ph_values[-1] and pl_values[-2] > pl_values[-1]:
                    bear_flag = True
                # Remove the first elements in pattern_list, pl_values, ph_values
                pattern_list.pop(0)
                pl_values.pop(0)
                ph_values.pop(0)
        
        if bull_flag:
            df.at[i, 'pattern_bull'] = True

        if bear_flag:
            df.at[i, 'pattern_bear'] = True

    return df

def main():
    symbol = 'BTC/USDT'
    timeframe = '15m'
    limit = 500 
    df = fetch_data(symbol, timeframe, limit)
    df_pivots = pattern(df)
    df_pivots.to_csv("df_pivots.csv")

if __name__ == "__main__":
    main()
