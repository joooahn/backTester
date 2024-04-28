import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pybithumb
import candle
import trading
import pprint
import numpy as np

# Disable SettingWithCopyWarning message
pd.set_option('mode.chained_assignment', None)


def show_chart(df):
    plt.plot(df['time_y'], df['hpr'], label='strategy')
    # Format x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %H:%M'))
    # Autoformat the date labels. It rotates the labels by 30 degrees.
    plt.gcf().autofmt_xdate()
    plt.legend()
    plt.show()


candle_30min = pybithumb.get_candlestick("BTC", payment_currency="KRW", chart_intervals="30m")
candle_5min = pybithumb.get_candlestick("BTC", chart_intervals="5m")
merged_candle = candle.merge_candle(candle_30min, candle_5min)

# for i in np.arange(0.1, 1.0, 0.1):
#     result = set_ror(merged_candle, 20, 0.0004, 2, i)
#     print("k값 : " + str(i))
#     print("전략 수익률 : " + str(result[1]))
#     print("보유 수익률 : " + str(result[2]))

result = trading.set_ror(merged_candle, 20, 0.0005, 2, 0.1)
df = result[0]
print("k값 : " + str(0.5))
print("전략 적용 시 수익률 : " + str(result[1]))
print("보유 시 수익률 : " + str(result[2]))
show_chart(merged_candle)