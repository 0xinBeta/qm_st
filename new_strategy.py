import multiprocessing as mp
import numpy as np
import ccxt
import vectorbt as vbt
import pandas as pd
from backtesting import Backtest, Strategy
from finta import TA
import pandas as pd
from main import find_pivots
from ta.trend import adx

mp.set_start_method('fork')

['ETH', 'BTC', 'BNB', 'XRP', 'LINK']


def create_df():
    df = vbt.CCXTData.download(
        symbols="BTCUSDT",
        missing_index="drop",
        exchange="binanceusdm",
        timeframe="5m",
        start="90 day ago UTC",
        end="now"
    ).get()

    df['EMA9'] = TA.EMA(df, 9, 'close')
    df['EMA21'] = TA.EMA(df, 21, 'close')
    df['EMA50'] = TA.EMA(df, 50, 'close')
    df['SMMA200'] = TA.SMMA(df, period=200)

    # Identify crossovers between EMA9 and EMA21

    df['cross_above'] = (df['EMA9'] > df['EMA21']) & (df['EMA9'
                                                         ].shift(1) < df['EMA21'].shift(1))
    df['cross_below'] = (df['EMA9'] < df['EMA21']) & (df['EMA9'
                                                         ].shift(1) > df['EMA21'].shift(1))

    # Calculate additional technical indicators

    df['ADX'] = adx(df['High'], df['Low'], df['Close'])
    df['ATR'] = TA.ATR(df, 14)
    df['RSI'] = TA.RSI(df, period=14)

    # Determine long and short trading opportunities based on set conditions

    df['long'] = (df['Close'] > df['SMMA200']) & (df['EMA9']
                                                  > df['SMMA200']) & (df['EMA21'] > df['SMMA200']) & (df['RSI'
                                                                                                         ] < 75) & (df['EMA21'] > df['EMA50']) & df['cross_above'] \
        & (df['ADX'] > 20) & (df['EMA50'] > df['SMMA200'])
    df['short'] = (df['Close'] < df['SMMA200']) & (df['EMA9']
                                                   < df['SMMA200']) & (df['EMA21'] < df['SMMA200']) & (df['RSI'
                                                                                                          ] > 20) & (df['EMA21'] < df['EMA50']) & df['cross_below'] \
        & (df['ADX'] > 20) & (df['EMA50'] < df['SMMA200'])

    return df


df = create_df()
# df.to_csv("back_test.csv")


class qm_strat(Strategy):
    tp_m = 7
    sl_m = 4

    def init(self):
        pass

    def next(self):
        buy_signal = self.data.long[-1]
        sell_signal = self.data.short[-1]
        price = self.data.Close[-1]
        atr = self.data.ATR[-1]
        tp_long = price + atr * self.tp_m
        sl_long = price - atr * self.sl_m
        tp_short = price - atr * self.tp_m
        sl_short = price + atr * self.sl_m

        distance_long = price - sl_long
        distance_short = sl_short - price

        cash = 100_000

        risk_long = (cash * 0.02) / distance_long
        risk_short = (cash * 0.02) / distance_short

        pos_size_long = ((risk_long * price) / 125) / cash
        pos_size_short = ((risk_short * price) / 125) / cash

        if buy_signal:
            if not self.position:
                if pos_size_long < 1:
                    self.buy(size=pos_size_long, sl=sl_long, tp=tp_long)
        elif sell_signal:
            if not self.position:
                if pos_size_short < 1:
                    self.sell(size=pos_size_short, sl=sl_short, tp=tp_short)

        # Check if we need to close the position
        # if self.position:
        #     if self.position.is_long and self.data.Close[-1] < self.tp_long[-1]:
        #         self.position.close()
        #     elif self.position.is_short and self.data.Close[-1] > self.tp_short[-1]:
        #         self.position.close()


# # # Initialize backtest with $100,000 cash
bt = Backtest(df, qm_strat, cash=100_000, margin=0.008)


# # # Run the backtest and generate the performance report
# stats = bt.run()
stats = bt.optimize(
    # tp_m = 7,
    tp_m=range(5, 11, 1),
    # e_2_m = 2,
    # sl_m = 4,
    sl_m=range(1, 6, 1),
    # tp_p_m = range(2, 20, 1),
    # sl_p_m = 20,
    maximize='Win Rate [%]' and 'Return (Ann.) [%]' and 'Sharpe Ratio' and 'Sortino Ratio',
    method='grid'
)
# Plot the backtest results
# bt.plot()

# # Print the performance reports
print(stats)

# Get the list of trades
# trades = stats['trades']

# # Print each trade
# for trade in trades:
#     print(trade)
