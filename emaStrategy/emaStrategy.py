import pprint

import pybithumb
import candle
import trading

candles = pybithumb.get_candlestick("BTC", chart_intervals="5m")
candles = candle.set_ema(candles, candles['close'])
candles = candle.set_is_bull(candles)

candles = trading.trade(candles, 100, 1, 2, fee = 0.0004)

buy_count = candles['buy'].sum()
take_profit_count = candles['take_profit'].sum()
stop_loss_count = candles['stop_loss'].sum()

print(f"Buy Count: {buy_count}")
print(f"Take Profit Count: {take_profit_count}")
print(f"Stop Loss Count: {stop_loss_count}")
print(f"전략 수익률: {candles.iloc[-1]['hpr']}")
print(f"보유 수익률: {candles.iloc[-1]['hold_ror']}")
candles.to_excel("result.xlsx")