def trade(candles, ema_duration, tp, sl, fee):
    candles['buy'] = 0
    candles['sell'] = 0
    candles['take_profit'] = 0
    candles['stop_loss'] = 0
    candles['ror'] = 1.0
    bought = False
    buy_price = 0

    for i, current_candle in candles.iterrows():
        current_price = current_candle['close']
        is_bull = current_candle['is_bull']
        ema = "ema" + str(ema_duration)
        # ema 50선에 닿았을 때 매수
        if not bought and is_bull and current_price <= current_candle[ema]:
            candles.loc[i, 'buy'] = 1
            bought = True
            buy_price = current_price
            continue
        # tp
        if bought and calc_ror(current_price, buy_price, fee) >= tp_ratio(tp):
            candles.loc[i, 'sell'] = 1
            candles.loc[i, 'take_profit'] = 1
            candles.loc[i, 'ror'] = tp_ratio(tp)
            bought = False
            buy_price = 0
            continue
        # sl
        if bought and calc_ror(current_price, buy_price, fee) <= sl_ratio(sl):
            candles.loc[i, 'sell'] = 1
            candles.loc[i, 'stop_loss'] = 1
            candles.loc[i, 'ror'] = sl_ratio(sl)
            bought = False
            buy_price = 0
            continue
    candles['hpr'] = candles['ror'].cumprod()
    candles['hold_ror'] = candles['close'] / candles['close'].iloc[0]
    return candles


def tp_ratio(take_profit):
    return 1 + take_profit / 100


def sl_ratio(stop_loss):
    return 1 - stop_loss / 100


def calc_ror(sell_price, buy_price, fee):
    buy_price = buy_price * (1 + fee)
    sell_price = sell_price * (1 - fee)
    loss_rate = (1 - sell_price / buy_price)
    return 1 - loss_rate
