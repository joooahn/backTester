import numpy as np
import pybithumb
import candle
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import pprint

# Disable SettingWithCopyWarning message
pd.set_option('mode.chained_assignment', None)


def is_bull(candle):
    return candle['ema20'] > candle['ema50'] > candle['ema100']

def calculate_ror(sell_price, buy_price, fee, leverage):
    return 1 - (1 - sell_price * (1 - fee) / buy_price * (1 + fee)) * leverage


def set_ror(candle_info, leverage, fee, loss_cut, k):
    # 직전 30분봉 기준 range, target 계산
    # 즉, 이번 5분봉 마감이 직전 30분봉을 k% 장악하는 양봉일 때 매수, 이번 30분봉 마감 시 매도
    candle_info['range'] = (candle_info['high_x'] - candle_info['low_x']) * k
    candle_info['target'] = candle_info['open_x'] + candle_info['range'].shift(6)

    # 거래 진행 정보
    candle_info['buy'] = 0
    candle_info['sell'] = 0
    candle_info['ror'] = 1.0
    candle_info['stop_loss'] = 0
    stop_loss = 1 - loss_cut / 100
    buy_price = 0
    # 이번 30분봉 내 매수 여부 판별하는 flag
    bought = False

    # 거래 진행
    for i in range(len(candle_info)):
        current_candle = candle_info.iloc[i]
        current_price = current_candle['close_y']
        target_price = current_candle['target']
        # 30분봉 시작 시
        if i % 6 == 0:
            bought = False
        # 5분봉 종가 마감이 target 보다 높으면 매수
        if not bought and current_price > target_price:
            candle_info.loc[i, 'buy'] = 1
            bought = True
            buy_price = current_price
            continue
        # 2% 하락 시 손절
        if bought and calculate_ror(current_price, buy_price, fee, leverage) <= stop_loss:
            candle_info.loc[i, 'sell'] = 1
            candle_info.loc[i, 'stop_loss'] = 1
            candle_info.loc[i, 'ror'] = 0.98
            bought = False
            continue
        # 30분봉 마감 시 매도
        if bought and i % 6 == 5:
            candle_info.loc[i, 'sell'] = 1
            candle_info.loc[i, 'ror'] = calculate_ror(current_price, buy_price, fee, leverage)
            continue

    # 누적 수익률
    candle_info['hpr'] = candle_info['ror'].cumprod()
    candle_info.to_excel("volatility_breakout.xlsx")
    strategy_ror = candle_info['hpr'].iloc[-1]
    hold_ror = candle_info['open_x'].iloc[-1] / candle_info['open_x'].iloc[0]
    return candle_info, strategy_ror, hold_ror


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

result = set_ror(merged_candle, 20, 0.0005, 2, 0.1)
df = result[0]
print("k값 : " + str(0.5))
print("전략 적용 시 수익률 : " + str(result[1]))
print("보유 시 수익률 : " + str(result[2]))
show_chart(merged_candle)