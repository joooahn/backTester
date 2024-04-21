import pybithumb
import numpy as np
import pprint


def get_ror(k):
    df = pybithumb.get_ohlcv("BTC")
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)
    df['ror2'] = df['ror'].apply(lambda x: 0.99 if x < 0.99 else x)
    df['hpr'] = df['ror'].cumprod()
    df['hpr2'] = df['ror2'].cumprod()
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
    df['dd2'] = (df['hpr2'].cummax() - df['hpr2']) / df['hpr2'].cummax() * 100
    print("MDD(%): ", df['dd'].max())
    print("MDD2(%): ", df['dd2'].max())
    print("HPR: ", df['hpr'][-1])
    print("HPR2: ", df['hpr2'][-1])
    df.to_excel("trade.xlsx")
    return max(df['hpr'].iloc[-1], df['hpr2'].iloc[-1])


# for k in np.arange(0.1, 1.0, 0.1):
#     ror = get_ror(k)
#     print("%.1f %f" % (k, ror))

get_ror(0.1)