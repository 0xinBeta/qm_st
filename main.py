import ccxt
import pandas as pd
import numpy as np


def fetch_data(symbol, timeframe, limit):
    binance = ccxt.binanceusdm()
    ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(
        ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def find_pivots(df, leftLenH, rightLenH, leftLenL, rightLenL):
    df['ph'] = np.nan
    df['pl'] = np.nan

    for i in range(leftLenH, len(df) - rightLenH):

        if df['High'].iloc[i] == max(df['High'].iloc[i - leftLenH:i + rightLenH + 1]):
            target_index = i + rightLenH - 5  # Shift 5 candles backward
            if target_index >= 0:  # Check to avoid negative index
                df.at[target_index, 'ph'] = df['High'].iloc[i]

        if df['Low'].iloc[i] == min(df['Low'].iloc[i - leftLenL:i + rightLenL + 1]):
            target_index = i + rightLenL - 5  # Shift 5 candles backward
            if target_index >= 0:  # Check to avoid negative index
                df.at[target_index, 'pl'] = df['Low'].iloc[i]

    return df


def pattern(df):
    df = find_pivots(df, 5, 5, 5, 5)
    df['pattern_bull'] = False
    df['pattern_bear'] = False
    df['CHoCH'] = False  # Initialize the new column
    df['OHCL'] = None

    pattern_list = []
    bull_flag = False
    bear_flag = False
    prev_pl = None  # Store the previous pivot low
    prev_ph = None  # Store the previous pivot high
    pl_values = []  # List to store pivot lows
    ph_values = []  # List to store pivot highs
    pivots_indices = []

    for i in range(len(df)):
        if not np.isnan(df['pl'].iloc[i]):
            pattern_list.append('pl')
            pivots_indices.append(i)
            pl_values.append(df['pl'].iloc[i])

            if bull_flag:
                if prev_pl is not None and df['pl'].iloc[i] < prev_pl:
                    df.at[i, 'CHoCH'] = True

            prev_pl = df['pl'].iloc[i]
            bull_flag = False
            bear_flag = False

        elif not np.isnan(df['ph'].iloc[i]):
            pattern_list.append('ph')
            pivots_indices.append(i)
            ph_values.append(df['ph'].iloc[i])
            if bear_flag:
                if prev_ph is not None and df['ph'].iloc[i] > prev_ph:
                    df.at[i, 'CHoCH'] = True

            prev_ph = df['ph'].iloc[i]
            bull_flag = False
            bear_flag = False

        if len(pattern_list) >= 4 and len(pl_values) >= 2 and len(ph_values) >= 2:
            last_four = pattern_list[-4:]
            if last_four == ['pl', 'ph', 'pl', 'ph']:
                if pl_values[-2] < pl_values[-1] and ph_values[-2] < ph_values[-1]:
                    bull_flag = True

            elif last_four == ['ph', 'pl', 'ph', 'pl']:
                if ph_values[-2] > ph_values[-1] and pl_values[-2] > pl_values[-1]:
                    bear_flag = True

            if df['CHoCH'].iloc[i]:
                if len(pivots_indices) >= 5:
                    fourth_pivot_index = pivots_indices[-4]
                    base_candle = df.iloc[fourth_pivot_index]
                    df.at[i, 'OHCL'] = base_candle[['Open', 'High', 'Low', 'Close']].to_dict()

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
