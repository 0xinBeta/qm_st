import multiprocessing as mp
import numpy as np
import ccxt
import vectorbt as vbt
import pandas as pd
from backtesting import Backtest, Strategy
from finta import TA
import pandas as pd
from main import find_pivots

mp.set_start_method('fork')


def create_df():
    df = vbt.CCXTData.download(
        symbols="ATOMUSDT",
        missing_index="drop",
        exchange="binanceusdm",
        timeframe= "15m",
        start="30 day ago UTC",
        end="now UTC"
    ).get()

    df.reset_index(drop=False, inplace=True)

    df = find_pivots(df, 5,5,5,5)
    df['RSI'] = TA.RSI(df)

    filtered_df = df[df['ph'].notna() | df['pl'].notna()].copy()

    last_ph_idx = filtered_df[filtered_df['ph'].notna()].index[-1] if not filtered_df[filtered_df['ph'].notna()].empty else None
    last_pl_idx = filtered_df[filtered_df['pl'].notna()].index[-1] if not filtered_df[filtered_df['pl'].notna()].empty else None

    ph_rows = filtered_df[filtered_df['ph'].notna()]
    if len(ph_rows) >= 3:
        last_three_ph = ph_rows.iloc[-3:]['ph'].values
        last_three_ph_rsi = ph_rows.iloc[-3:]['RSI'].values

        if all(x < y for x, y in zip(last_three_ph, last_three_ph[1:])) and all(x > y for x, y in zip(last_three_ph_rsi, last_three_ph_rsi[1:])):
            # Your condition for ph is met
            condition_ph_met = True
        else:
            condition_ph_met = False
    else:
        condition_ph_met = False

    
    df['Condition_met'] = False
    if condition_ph_met:
        df.loc[last_ph_idx, 'Condition_met'] = True

    df.to_csv("three-push.csv")

    df.set_index('Open time', inplace=True)

    
    return df


df = create_df()
# df.to_csv("back_test.csv")

# class qm_strat(Strategy):

#     def init(self):
#         pass

#     def next(self):
#         buy_signal = self.data.long[-1]
#         sell_signal = self.data.short[-1]
#         entry_long = float(self.data.entry_long[-1])
#         entry_short = float(self.data.entry_short[-1])
#         sl_long = float(self.data.sl_long[-1])
#         sl_short = float(self.data.sl_short[-1])
#         tp_long = float(round(((entry_long - sl_long) * 2) + entry_long, 2))
#         tp_short = float(round(entry_short - (abs(entry_short - sl_short) * 2), 2))
#         date = self.data.index[-1]


#         if buy_signal:
#             print("buy")
#             print(date, entry_long, tp_long, sl_long)

#             if not self.position:
#                 self.buy(limit=entry_long, sl=sl_long, tp=tp_long)
#         elif sell_signal:
#             print("sell")
#             print(date, entry_short, tp_short, sl_short)
#             if not self.position:
#                 self.sell(limit=entry_short, sl=sl_short, tp=tp_short)

        
#         # Check if we need to close the position
#         # if self.position:
#         #     if self.position.is_long and self.data.Close[-1] < self.tp_long[-1]:
#         #         self.position.close()
#         #     elif self.position.is_short and self.data.Close[-1] > self.tp_short[-1]:
#         #         self.position.close()


# # # # Initialize backtest with $100,000 cash
# bt = Backtest(df, qm_strat, cash=100_000)


# # # # Run the backtest and generate the performance report
# stats = bt.run()
# # stats = bt.optimize(
# #     # tp_m = 9,
# #     tp_m = range(3,11,1),
# #     # e_2_m = 2,
# #     # sl_m = 7,
# #     sl_m = range(3, 11, 1),
# #     # tp_p_m = range(2, 20, 1),
# #     # sl_p_m = 20,
# #     maximize='Win Rate [%]' and 'Return (Ann.) [%]'
# #     )
# # # Plot the backtest results
# bt.plot()

# # # Print the performance reports
# print(stats)

# # Get the list of trades
# trades = stats['trades']

# # Print each trade
# for trade in trades:
#     print(trade)