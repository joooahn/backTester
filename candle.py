import pprint

import numpy as np
import pandas as pd

def merge_candle(candle_30min, candle_5min):
    # 시간대 맞추기
    start_dttm = get_start_dttm(candle_5min)
    candle_30min = candle_30min[candle_30min.index >= start_dttm]
    candle_5min = candle_5min[candle_5min.index >= start_dttm]

    # 5분봉, 30분봉 합치기
    candle_30min['key'] = np.arange(len(candle_30min))
    tmp_key = np.repeat(np.arange(len(candle_5min) // 6), 6)

    # 임시 키 개수가 원본 행 개수와 맞지 않을 경우
    if tmp_key.size < len(candle_5min):
        tmp_key = np.append(tmp_key, np.repeat(tmp_key[-1], len(candle_5min) - tmp_key.size))
    candle_5min['key'] = tmp_key

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


def get_start_dttm(candle_5min):
    start_dttm = candle_5min.index[0]
    if start_dttm.hour > 0:
        start_dttm = start_dttm + pd.Timedelta(days=1)
        start_dttm = start_dttm.replace(hour=0, minute=0)
    return start_dttm


def set_ema(merged_candle, target_column):
    merged_candle['ema20'] = target_column.ewm(span=20, adjust=False, min_periods=20).mean()
    merged_candle['ema50'] = target_column.ewm(span=50, adjust=False, min_periods=50).mean()
    merged_candle['ema100'] = target_column.ewm(span=100, adjust=False, min_periods=100).mean()
    return merged_candle


def set_is_bull(candle_info):
    candle_info['is_bull'] = np.where((candle_info['ema20'] > candle_info['ema50']) & (candle_info['ema50'] > candle_info['ema100']), 1, 0)
    return candle_info


def set_range_target(candle_info, k):
    # 직전 30분봉 기준 range, target 계산
    # 즉, 이번 5분봉 마감이 직전 30분봉을 k% 장악하는 양봉일 때 매수, 이번 30분봉 마감 시 매도
    candle_info['range'] = (candle_info['high_x'] - candle_info['low_x']) * k
    candle_info['target'] = candle_info['open_x'] + candle_info['range'].shift(6)
    # 필요없는 column 삭제
    candle_info.drop('time_x', axis=1, inplace=True)
    candle_info.drop('open_x', axis=1, inplace=True)
    candle_info.drop('high_x', axis=1, inplace=True)
    candle_info.drop('low_x', axis=1, inplace=True)
    candle_info.drop('close_x', axis=1, inplace=True)
    candle_info.drop('volume_x', axis=1, inplace=True)
    candle_info.drop('volume_y', axis=1, inplace=True)
    return candle_info