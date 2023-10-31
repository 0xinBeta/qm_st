import multiprocessing as mp
import numpy as np
import ccxt
import vectorbt as vbt
import pandas as pd
from backtesting import Backtest, Strategy
from finta import TA


# TOKEN = "e3c1b16fcd75a51afb4d06f1f7fe60cb-8d9f5eefaaf4502653a6ed827361f97f"
# api = API(access_token=TOKEN)
# params = {"count": 5000,"granularity": "M3"} # 5000 data points with 5 minute granularity

# r = instruments.InstrumentsCandles(instrument="EUR_USD", params=params)
# response = api.request(r)
# data = response["candles"]

# # Create a list to store the data
# data_list = []

# for candle in data:
#     time = pd.to_datetime(candle["time"])
#     volume = candle["volume"]
#     o = float(candle["mid"]["o"])
#     h = float(candle["mid"]["h"])
#     l = float(candle["mid"]["l"])
#     c = float(candle["mid"]["c"])

#     # Append this data to the list as a dictionary
#     data_list.append({"time": time, "open": o, "high": h, "low": l, "close": c, "volume": volume})

# # Convert the list of dictionaries into a DataFrame
# df = pd.DataFrame(data_list)

# # Set "time" as the index
# df.set_index("time", inplace=True)


mp.set_start_method('fork')


symbol = "BTCUSD"
timeframe = "15m"
limit = 1500


def create_df(tf):
    # Load historical data
    # TOKEN = "e3c1b16fcd75a51afb4d06f1f7fe60cb-8d9f5eefaaf4502653a6ed827361f97f"
    # api = API(access_token=TOKEN)
    # params = {"count": 5000,"granularity": "H1"} # end of the date range # 5000 data points with 5 minute granularity

    # r = instruments.InstrumentsCandles(instrument="EUR_USD", params=params)
    # response = api.request(r)
    # data = response["candles"]

    # # Create a list to store the data
    # data_list = []

    # for candle in data:
    #     time = pd.to_datetime(candle["time"])
    #     volume = candle["volume"]
    #     o = float(candle["mid"]["o"])
    #     h = float(candle["mid"]["h"])
    #     l = float(candle["mid"]["l"])
    #     c = float(candle["mid"]["c"])

    #     # Append this data to the list as a dictionary
    #     data_list.append({"time": time, "Open": o, "High": h, "Low": l, "Close": c, "volume": volume})

    # # Convert the list of dictionaries into a DataFrame
    # df = pd.DataFrame(data_list)

    # # Set "time" as the index
    # df.set_index("time", inplace=True)


    # exchange = ccxt.phemex(
    # {
    #     "enableRateLimit": True,
    # })

    # candles = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe,
    #                                limit=limit)

    # # Convert data to pandas DataFrame

    # df = pd.DataFrame(candles, columns=[
    #     'DateTime',
    #     'Open',
    #     'High',
    #     'Low',
    #     'Close',
    #     'Volume',
    #     ])
    df = vbt.CCXTData.download(
        symbols="BTCUSDT",
        missing_index="drop",
        exchange="binanceusdm",
        timeframe= tf,
        start="2 day ago UTC",
        end="now UTC"
    ).get()

    # df['EMA9'] = TA.EMA(df, 9, 'close')
    # df['EMA21'] = TA.EMA(df, 21, 'close')
    # df['EMA50'] = TA.EMA(df, 50, 'close')
    # pivots = TA.PIVOT_FIB(df)
    # print(df)
    # print(pivots)
    # df['EMA50'] = TA.EMA(df, 50, 'close')
    # df['SMMA200'] = TA.SMMA(df, period=100)
    df_bb_8 = TA.BBANDS(df, period=20, std_multiplier=0.8)
    

    df = pd.concat([df, df_bb_8], axis=1)

    df['BB_UPPER_8'], df['BB_MIDDLE_8'], df['BB_LOWER_8'] = round(df['BB_UPPER'], 1), round(df['BB_MIDDLE'], 1), round(df['BB_LOWER'], 1)
    
    columns_to_delete = ['BB_UPPER', 'BB_MIDDLE', 'BB_LOWER']
    df.drop(columns=columns_to_delete, inplace=True)

    df_bb_9 = TA.BBANDS(df, period=20, std_multiplier=0.9)
    df = pd.concat([df, df_bb_9], axis=1)

    df['BB_UPPER_9'], df['BB_MIDDLE_9'], df['BB_LOWER_9'] = round(df['BB_UPPER'], 1), round(df['BB_MIDDLE'], 1), round(df['BB_LOWER'], 1)

    columns_to_delete = ['BB_UPPER', 'BB_MIDDLE', 'BB_LOWER']
    df.drop(columns=columns_to_delete, inplace=True)

    # df = df.dropna(how='any')
    # df['ATR'] = TA.ATR(df)
    # # Compute the ATR values for the given period
    # df['ADX'] = trend.adx(df['High'], df['Low'], df['Close'])
    # df['ATR'] = average_true_range(df['High'], df['Low'], df['Close'])
    
    

    # Update cross_above and cross_below calculations to consider the tolerance values
    # df['cross_above'] = (df['EMA9'] > df['EMA21']) & (df['EMA9'].shift(1) < df['EMA21'].shift(1)) 
    # df['cross_below'] = (df['EMA9'] < df['EMA21']) & (df['EMA9'].shift(1) > df['EMA21'].shift(1)) 

    # df['RSI'] = TA.RSI(df, period=14)
    # df['diff_from_smma'] = abs(((df['Close'] - df['SMMA200']) / df['SMMA200']) * 100)


    
    # df['long'] = (df['Close'] > df['SMMA200']) & (df['EMA9'] > df['SMMA200']) & (df['EMA21'] > df['SMMA200']) & (df['EMA21'] > df['EMA50']) & (df['cross_above']) & (df['EMA50'] > df['SMMA200']) & (df['ADX'] > 20) & (df['RSI'] < 75)
    # df['short'] = (df['Close'] < df['SMMA200']) & (df['EMA9'] < df['SMMA200']) & (df['EMA21'] < df['SMMA200']) & (df['EMA21'] < df['EMA50']) & (df['cross_below']) & (df['EMA50'] < df['SMMA200']) & (df['ADX'] > 20) & (df['RSI'] > 20)
    # & (df['ADX'] > 20)
    # df['long'] = (df['Close'] > df['SMMA200']) & (df['EMA9'] > df['SMMA200']) & (df['EMA21'] > df['SMMA200']) & (df['cross_above'])  & (df['EMA50'] > df['SMMA200']) & (df['EMA21'] > df['EMA50']) & (df['ADX'] > 20) & (df['RSI'] < 75)
    # df['short'] = (df['Close'] < df['SMMA200']) & (df['EMA9'] < df['SMMA200']) & (df['EMA21'] < df['SMMA200'])  & (df['cross_below'])  & (df['EMA50'] < df['SMMA200']) & (df['EMA21'] < df['EMA50']) & (df['ADX'] > 20) & (df['RSI'] > 20)

    df['long'] = (df['Close'] > df['BB_UPPER_8']) & (df['Close'].shift(1) < df['BB_UPPER_8'].shift(1))
    df['short'] = (df['Close'] < df['BB_LOWER_8']) & (df['Close'].shift(1) > df['BB_LOWER_8'].shift(1))
    


    df = df.dropna(how='any')


    return df


print(create_df(timeframe))

df = create_df(timeframe)
# df.to_csv("test_02_04_1_1.csv")

# class mkb_strat(Strategy):

#     def init(self):
#         pass

#     def next(self):
#         buy_signal = self.data.long[-1]
#         sell_signal = self.data.short[-1]


#         if buy_signal == True:
#             if not self.position:
#                 # price = self.data.Close[-1]
#                 # # tp_long = (atr * self.tp_m) + price + 0.0007
#                 # # sl_long = price - (atr * self.sl_m) 
#                 # tp_long = price + atr * self.tp_m
#                 # sl_long = price - atr * self.sl_m
#                 self.buy()
#                 # self.buy(limit=price - atr * self.e_2_m, tp=tp_long, sl=sl_long, size=0.03)
                

#         elif sell_signal == True:
#             if not self.position:
#                 # price = self.data.Close[-1]
#                 # # sl_short = (atr * self.sl_m) + price
#                 # # tp_short = price - (atr * self.tp_m) - 0.0007
#                 # sl_short = price + atr * self.sl_m
#                 # tp_short = price - atr * self.tp_m
#                 self.sell()
#                 # self.sell(limit=price + atr * self.e_2_m ,tp=tp_short, sl=sl_short, size=0.03)
#         for trade in self.trades:
#             if trade.is_long:
#                 trade.sl = 

class mkb_strat(Strategy):

    def init(self):
        self.tp_long = self.data.BB_UPPER_9
        self.tp_short = self.data.BB_LOWER_9

    def next(self):
        buy_signal = self.data.long[-1]
        sell_signal = self.data.short[-1]
        sl_long = self.data.BB_UPPER_8[-1]
        sl_short = self.data.BB_LOWER_8[-1]

        if buy_signal == True:
            if not self.position:
                self.buy(sl=sl_long)
        elif sell_signal == True:
            if not self.position:
                self.sell(sl=sl_short)

        # Check if we need to close the position
        if self.position:
            if self.position.is_long and self.data.Close[-1] < self.tp_long[-1]:
                self.position.close()
            elif self.position.is_short and self.data.Close[-1] > self.tp_short[-1]:
                self.position.close()
    
        


# Initialize backtest with $100,000 cash
bt = Backtest(df, mkb_strat, cash=100_000)


# Run the backtest and generate the performance report
stats = bt.run()
# stats = bt.optimize(
#     # tp_m = 9,
#     tp_m = range(3,11,1),
#     # e_2_m = 2,
#     # sl_m = 7,
#     sl_m = range(3, 11, 1),
#     # tp_p_m = range(2, 20, 1),
#     # sl_p_m = 20,
#     maximize='Win Rate [%]' and 'Return (Ann.) [%]'
#     )
# Plot the backtest results
bt.plot()

# Print the performance reports
print(stats)

# # Get the list of trades
# trades = stats['trades']

# # Print each trade
# for trade in trades:
#     print(trade)