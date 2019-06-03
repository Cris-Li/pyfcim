from __future__ import print_function

import pybacktest  # obviously, you should install pybacktest before importing it
import pandas as pd

from scripts.波动率计算 import *

df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113009广汽转债").fillna(method='ffill')


def convert_f(_df):
    _df.index = pd.to_datetime(_df.time)
    _df.index = _df.index.tz_localize('UTC')
    _df.index.name = 'Date'
    _df['upper'], _df['middle'], _df['lower'] = talib.BBANDS(_df.close, matype=talib.MA_Type.T3)
    _df['CCI'] = talib.CCI(_df.high, _df.low, _df.close, timeperiod=24)
    _df['macd'], macdsignal, macdhist = talib.MACD(_df.close)
    _df['HT_DCPERIOD'] = talib.HT_DCPERIOD(_df.close)
    _df['buy_point'] = (_df.high > _df.lower) & (_df.low < _df.lower).shift(1) & (
            (_df.CCI >= 0) & (_df.CCI < 200) | (_df.CCI < -200)) & (_df.macd > -0.05) & (_df['HT_DCPERIOD'] > 20)
    _df['sell_point'] = (_df.high > _df.upper)
    _df.rename(columns={'open': 'O', 'high': 'H', 'low': 'L', 'close': 'C'}, inplace=True)
    return _df


ohlc = convert_f(df)
buy = ohlc.buy_point
sell = ohlc.sell_point

short_ma = 50
long_ma = 200

ms = ohlc.C.rolling(short_ma).mean()
ml = ohlc.C.rolling(long_ma).mean()

buy = cover = (ms > ml) & (ms.shift() < ml.shift())  # ma cross up
sell = short = (ms < ml) & (ms.shift() > ml.shift())  # ma cross down

print('>  Short MA\n%s\n' % ms.tail())
print('>  Long MA\n%s\n' % ml.tail())
print('>  Buy/Cover signals\n%s\n' % buy.tail())
print('>  Short/Sell signals\n%s\n' % sell.tail())
bt = pybacktest.Backtest(locals(), 'ma_cross')
print(list(filter(lambda x: not x.startswith('_'), dir(bt))))
print('\n>  bt.signals\n%s' % bt.signals.tail())
print('\n>  bt.trades\n%s' % bt.trades.tail())
print('\n>  bt.positions\n%s' % bt.positions.tail())
print('\n>  bt.equity\n%s' % bt.equity.tail())
print('\n>  bt.trade_price\n%s' % bt.trade_price.tail())

bt.summary()

# matplotlib inline
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['figure.figsize'] = (15.0, 8.0)

bt.plot_equity()
plt.show()

bt.plot_trades()
ohlc.C.rolling(short_ma).mean().plot(c='green')
ohlc.C.rolling(long_ma).mean().plot(c='blue')
plt.legend(loc='upper left')
plt.show()
pass
