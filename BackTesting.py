import pybithumb
import numpy as np
import pandas as pd
import pprint

# Disable SettingWithCopyWarning message
pd.set_option('mode.chained_assignment', None)


def merge_candle(candle_30min, candle_5min):
    # 시간대 맞추기
    candle_30min = candle_30min[candle_30min.index >= '2024-04-12']
    candle_5min = candle_5min[candle_5min.index >= '2024-04-12']

    # 5분봉, 30분봉 합치기
    candle_30min['key'] = np.arange(len(candle_30min))
    tmpKey = np.repeat(np.arange(len(candle_5min) // 6), 6)

    # 임시 키 개수가 원본 행 개수와 맞지 않을 경우
    if tmpKey.size < len(candle_5min):
        tmpKey = np.append(tmpKey, np.repeat(tmpKey[-1], len(candle_5min) - tmpKey.size))
    candle_5min['key'] = tmpKey

    # Reset the current index 'time' and keep it as a column
    candle_30min.reset_index(inplace=True)
    candle_5min.reset_index(inplace=True)
    # Set 'key' as the new index
    candle_30min.set_index('key', inplace=True)
    candle_5min.set_index('key', inplace=True)

    # Merge the two dataframes on 'key'
    merged_df = pd.merge(candle_30min, candle_5min, on='key', how='inner')
    # 1씩 증가하도록 index 변경
    merged_df.reset_index(drop=True, inplace=True)
    return merged_df


def calculate_ror(sell_price, buy_price, fee, leverage):
    return 1 - (1 - sell_price * (1 - fee) / buy_price * (1 + fee)) * leverage


def set_ror(candle_info, leverage, k):
    # 직전 30분봉 기준 range, target 계산
    candle_info['range'] = (candle_info['high_x'] - candle_info['low_x']) * k
    candle_info['target'] = candle_info['open_x'] + candle_info['range'].shift(6)

    # 5분봉 종가 마감이 target 보다 높으면 매수
    # 즉, 이번 5분봉 마감이 직전 30분봉을 k% 장악하는 양봉일 때 매수, 이번 30분봉 마감 시 매도
    fee = 0.0004
    candle_info['buy'] = np.where(candle_info['close_y'] > candle_info['target'], 1, 0)
    candle_info['ror'] = np.where(candle_info['close_y'] > candle_info['target'],
                                  calculate_ror(candle_info['close_x'], candle_info['close_y'], fee, leverage),
                                  1)
    # 30분에 1번 거래하므로 30분봉 기준으로 누적 수익률 계산
    bought = True
    for i in range(len(candle_info)):
        # 30분봉 시작 시
        if i % 6 == 0:
            bought = False
        # 30분봉 시작 후 최초 매수일 경우
        if candle_info['buy'].iloc[i] == 1 and not bought:
            bought = True
        # 30분봉 시작 후 최초 매수가 아닐 경우 매수 신호 제거
        elif candle_info['buy'].iloc[i] == 1 and bought:
            candle_info['buy'].iloc[i] = 0
            candle_info['ror'].iloc[i] = 1

    # 누적 수익률
    candle_info['hpr'] = candle_info['ror'].cumprod()
    candle_info.to_excel("volatility_breakout.xlsx")
    strategy_ror = candle_info['hpr'].iloc[-1]
    hold_ror = candle_info['open_x'].iloc[-1] / candle_info['open_x'].iloc[0]
    return strategy_ror, hold_ror


candle_30min = pybithumb.get_candlestick("BTC", payment_currency="KRW", chart_intervals="30m")
candle_5min = pybithumb.get_candlestick("BTC", chart_intervals="5m")
merged_candle = merge_candle(candle_30min, candle_5min)

# for i in np.arange(0.1, 1.0, 0.1):
#     result = set_ror(merged_candle, 10, i)
#     print("k값 : " + str(i))
#     print("전략 수익률 : " + str(result[0]))
#     print("보유 수익률 : " + str(result[1]))

result = set_ror(merged_candle, 10, 0.5)
print("k값 : " + str(0.5))
print("전략 수익률 : " + str(result[0]))
print("보유 수익률 : " + str(result[1]))
