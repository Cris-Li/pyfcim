# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, show
import talib
import pybacktest
from WindPy import w

df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113013国君转债").fillna(method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113009广汽转债").fillna(method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113021中信转债").fillna(method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110053苏银转债").fillna(method='ffill')

df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="127012招路转债").fillna(method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113011光大转债").fillna(method='ffill')
df5 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="113013国君转债").fillna(method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110046圆通转债").fillna(method='ffill')
df7 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\转债分钟行情数据.xlsx", sheet_name="110051中天转债").fillna(method='ffill')

df832 = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\000832-D.xlsx", sheet_name="file")

df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\国君转债1min2018.xlsx", sheet_name="国君转债1min2018").fillna(
    method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\广汽转债1min2018.xlsx", sheet_name="广汽转债1min2018").fillna(
    method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\海印转债1min2018.xlsx", sheet_name="海印转债1min2018").fillna(
    method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\杭电转债1min2018.xlsx", sheet_name="杭电转债1min2018").fillna(
    method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\生益转债1min2018.xlsx", sheet_name="生益转债1min2018").fillna(
    method='ffill')
df = pd.read_excel("C:\\Users\\Lenovo\\Desktop\\data\\hs300.xlsx", sheet_name="hs300").fillna(method='ffill')


# %%
# df = w.wsi("127003.SZ", "open,high,low,close", "2018-06-12 09:00:00", "2019-06-12 10:05:00", "",usedf=True)


# %%

def intensity(lnchg, params):
    idx, = np.where(lnchg > params['threshold'])
    back_la = np.zeros(len(lnchg))
    for j in np.arange(len(lnchg)):
        _idx = idx[idx < j]
        if len(_idx) > 0:
            back_la[j] = np.sum(np.exp(-params['gama'] * (j - _idx)) * params['b'] * np.exp(
                params['a'] * (lnchg[_idx] - params['threshold'])))
    return params['la0'] + back_la


def cal_sell(_idx, _df1):
    for i in np.arange(_idx, _idx + 400):
        if np.all([i < _df1.shape[0], _df1.close[i] >= _df1.close[_idx] + 0.04, _df1.close[i] < _df1.middle[i]]):
            _df1.loc[i, 'sell_point'] = True
            break


def convert_f(_df):
    _df.index = pd.to_datetime(_df.time)
    _df.index = _df.index.tz_localize('UTC')
    _df.index.name = 'Date'
    _df['MA5'] = talib.MA(_df.close, timeperiod=5)
    _df['upper'], _df['middle'], _df['lower'] = talib.BBANDS(_df.close, matype=talib.MA_Type.T3)
    _df['CCI'] = talib.CCI(_df.high, _df.low, _df.close, timeperiod=24)
    _df['macd'], macdsignal, macdhist = talib.MACD(_df.close)
    _df['HT_DCPERIOD'] = talib.HT_DCPERIOD(_df.close)
    _df['buy_point'] = (_df.close > _df.MA5 - 0.02) & (_df.close < _df.MA5 - 0.02).shift(1) & (
                _df.close < _df.MA5 + 0.02)  # & (_df.intensity < 0.2)
    _df['sell_point'] = ((_df.close > _df.middle).shift(1) & (_df.close < _df.middle)) | (
            (_df.close > _df.upper).shift(1) & (_df.close < _df.upper)) | ((_df.close > _df.lower).shift(1) & (
                _df.close < _df.lower))  # | (_df.intensity > 0.25)
    # _df['buy_point'] = (_df.close > _df.MA5 - 0.02) & (_df.close < _df.MA5 - 0.02).shift(1) & (
    #             _df.close < _df.MA5 + 0.02)
    # _df['sell_point'] = ((_df.close > _df.middle).shift(1) & (_df.close < _df.middle)) | (
    #         (_df.close > _df.upper).shift(1) & (_df.close < _df.upper))
    # 生成sell_point序列
    # idx, = np.where(_df['buy_point'] == True)
    # for j in idx:
    #     cal_sell(j, _df)

    _df.rename(columns={'open': 'O', 'high': 'H', 'low': 'L', 'close': 'C'}, inplace=True)
    return _df


# %%
params = {'la0': 0.004, 'a': 10.161, 'b': 0.055, 'gama': 0.055, 'threshold': 0.0041}
lnchg = -df832.lnchg.dropna().values

intes = intensity(lnchg, params)
df832['intensity'] = np.nan
df832.loc[1:, 'intensity'] = intes

df['DateStr'] = df.time.apply(lambda x: x.strftime("%Y-%m-%d"))
df832['DateStr'] = df832['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
df_new = pd.merge(df, df832[['DateStr', 'intensity']], how='left', on='DateStr')
# df_new.open = df_new.close.shift(1)
# %%
ohlc = convert_f(df_new.copy())
buy = ohlc.buy_point
sell = ohlc.sell_point

cover = False
short = False

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

# %%
# matplotlib inline
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['figure.figsize'] = (15.0, 8.0)

bt.plot_equity()
plt.show()

bt.plot_trades()

plt.legend(loc='upper left')
plt.show()
pass

# %%
temp = bt.trades[1::2].price.values - bt.trades[::2].price.values
plt.hist(temp, 100)
plt.show()
plot(temp)
show()
