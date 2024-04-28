import pybithumb
import candle
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pprint


# Disable SettingWithCopyWarning message
pd.set_option('mode.chained_assignment', None)

candle_30min = pybithumb.get_candlestick("BTC", payment_currency="KRW", chart_intervals="30m")
candle_5min = pybithumb.get_candlestick("BTC", chart_intervals="5m")
merged_candle = candle.merge_candle(candle_30min, candle_5min)
merged_candle['ema20'] = merged_candle['close_y'].ewm(span=20, adjust=False, min_periods=20).mean()
merged_candle['ema50'] = merged_candle['close_y'].ewm(span=50, adjust=False, min_periods=50).mean()
merged_candle['ema100'] = merged_candle['close_y'].ewm(span=100, adjust=False, min_periods=100).mean()
merged_candle.to_excel("ema.xlsx")
