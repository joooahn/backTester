import pybithumb
import candle
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pprint


# Disable SettingWithCopyWarning message
pd.set_option('mode.chained_assignment', None)

def set_ema(df):
    df['ema20'] = df['close_y'].ewm(span=20, adjust=False, min_periods=20).mean()
    df['ema50'] = df['close_y'].ewm(span=50, adjust=False, min_periods=50).mean()
    df['ema100'] = df['close_y'].ewm(span=100, adjust=False, min_periods=100).mean()
    return df
