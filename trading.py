def is_bull(candle):
    return candle['ema20'] > candle['ema50'] > candle['ema100']


def calculate_ror(sell_price, buy_price, fee, leverage):
    buy_price = buy_price * (1 + fee)
    sell_price = sell_price * (1 - fee)
    loss_rate = (1 - sell_price / buy_price) * leverage
    return 1 - loss_rate


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
        bull = is_bull(current_candle)
        # 30분봉 시작
        if i % 6 == 0:
            bought = False
        # 5분봉 종가 마감이 target 보다 높으면 매수
        if not bought and bull and current_price > target_price:
            # 30분봉 마감 시 매수하지 않음
            if i % 6 == 5:
                continue
            candle_info.loc[i, 'buy'] = 1
            bought = True
            buy_price = current_price
            continue
        # 2% 하락 시 손절
        if bought and calculate_ror(current_price, buy_price, fee, leverage) <= stop_loss:
            candle_info.loc[i, 'sell'] = 1
            candle_info.loc[i, 'stop_loss'] = 1
            candle_info.loc[i, 'ror'] = 1 - loss_cut / 100
            bought = False
            continue
        # 30분봉 마감 시 매도
        if bought and i % 6 == 5:
            candle_info.loc[i, 'sell'] = 1
            candle_info.loc[i, 'ror'] = calculate_ror(current_price, buy_price, fee, leverage)
            continue

    # 보유 수익률
    candle_info['hold_ror'] = candle_info['close_y'] / candle_info['open_y']

    # 누적 수익률
    candle_info['hpr'] = candle_info['ror'].cumprod()
    candle_info.to_excel("volatility_breakout.xlsx")
    strategy_ror = candle_info['hpr'].iloc[-1]
    hold_ror = candle_info['open_x'].iloc[-1] / candle_info['open_x'].iloc[0]
    return candle_info, strategy_ror, hold_ror