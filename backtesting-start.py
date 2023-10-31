import multiprocessing as mp
import numpy as np
import ccxt
import vectorbt as vbt
import pandas as pd
from backtesting import Backtest, Strategy
from finta import TA
import pandas as pd
from main import pattern


mp.set_start_method('fork')


def create_df():
    df = vbt.CCXTData.download(
        symbols="BTCUSDT",
        missing_index="drop",
        exchange="binanceusdm",
        timeframe= "15m",
        start="90 day ago UTC",
        end="now UTC"
    ).get()

    df.reset_index(drop=False, inplace=True)

    df = pattern(df=df)

    df.set_index('Open time', inplace=True)

    df['long'] = (df['CHoCH'] == True) & (df['ph'] > 0)
    df['short'] = (df['CHoCH'] == True) & (df['pl'] > 0)

    df['Open_values'] = df['OHCL'].apply(lambda x: x.get('Open', None) if x is not None else None)
    df['Close_values'] = df['OHCL'].apply(lambda x: x.get('Close', None) if x is not None else None)

    # Adding new columns 'entry_short' and 'entry_long' based on conditions
    df['entry_short'] = np.where(df['Open_values'] > df['Close_values'], df['Open_values'], df['Close_values'])
    df['entry_long'] = np.where(df['Open_values'] < df['Close_values'], df['Open_values'], df['Close_values'])

    def last_ph_high(row_idx, df):
        previous_rows = df.iloc[:row_idx]
        ph_series = previous_rows.get('ph', None)
        if ph_series is not None:
            valid_ph_rows = ph_series.dropna()
            if not valid_ph_rows.empty:
                last_ph_row = previous_rows.loc[valid_ph_rows.index[-1]]
                return last_ph_row['High']
        return None

    def last_pl_low(row_idx, df):
        previous_rows = df.iloc[:row_idx]
        pl_series = previous_rows.get('pl', None)
        if pl_series is not None:
            valid_pl_rows = pl_series.dropna()
            if not valid_pl_rows.empty:
                last_pl_row = previous_rows.loc[valid_pl_rows.index[-1]]
                return last_pl_row['Low']
        return None

    df['sl_short'] = [last_ph_high(idx, df) for idx in range(len(df))]
    df['sl_long'] = [last_pl_low(idx, df) for idx in range(len(df))]

    return df


df = create_df()
# df.to_csv("back_test.csv")

class qm_strat(Strategy):

    def init(self):
        pass

    def next(self):
        buy_signal = self.data.long[-1]
        sell_signal = self.data.short[-1]
        entry_long = float(self.data.entry_long[-1])
        entry_short = float(self.data.entry_short[-1])
        sl_long = float(self.data.sl_long[-1])
        sl_short = float(self.data.sl_short[-1])
        tp_long = float(round(((entry_long - sl_long) * 2) + entry_long, 2))
        tp_short = float(round(entry_short - (abs(entry_short - sl_short) * 2), 2))
        date = self.data.index[-1]


        if buy_signal:
            print("buy")
            print(date, entry_long, tp_long, sl_long)

            if not self.position:
                self.buy(limit=entry_long, sl=sl_long, tp=tp_long)
        elif sell_signal:
            print("sell")
            print(date, entry_short, tp_short, sl_short)
            if not self.position:
                self.sell(limit=entry_short, sl=sl_short, tp=tp_short)

        
        # Check if we need to close the position
        # if self.position:
        #     if self.position.is_long and self.data.Close[-1] < self.tp_long[-1]:
        #         self.position.close()
        #     elif self.position.is_short and self.data.Close[-1] > self.tp_short[-1]:
        #         self.position.close()


# # # Initialize backtest with $100,000 cash
bt = Backtest(df, qm_strat, cash=100_000)


# # # Run the backtest and generate the performance report
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
# # Plot the backtest results
bt.plot()

# # Print the performance reports
print(stats)

# # Get the list of trades
# trades = stats['trades']

# # Print each trade
# for trade in trades:
#     print(trade)