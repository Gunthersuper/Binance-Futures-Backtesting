import pandas as pd
from time import sleep
import ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
from helper import get_tickers_usdt, klines, klines_extended

# Take Profit and Stop Loss. 0.03 means 3%
tp = 0.03
sl = 0.02


def rsi(df, period=14):
    rsi = ta.momentum.RSIIndicator(pd.Series(df), window=period).rsi()
    return rsi


def ema(df, period=200):
    ema = ta.trend.EMAIndicator(pd.Series(df), window=period).ema_indicator()
    return ema


def bol_h(df):
    return ta.volatility.BollingerBands(pd.Series(df)).bollinger_hband()
def bol_l(df):
    return ta.volatility.BollingerBands(pd.Series(df)).bollinger_lband()


class str(Strategy):
    rsi_period = 14
    ema_period = 200
    def init(self):
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)
        self.ema = self.I(ema, self.data.Close, self.ema_period)

        self.bol_h = self.I(bol_h, self.data.Close)
        self.bol_l = self.I(bol_l, self.data.Close)

    def next(self):
        price = float(self.data.Close[-1])
        if self.data.Close[-3] > self.bol_l[-3] and self.data.Close[-2] < self.bol_l[-2]:
            if not self.position:
                self.buy(size=0.05)
            if self.position.is_short:
                self.position.close()
                self.buy(size=0.05)

        if self.data.Close[-3] < self.bol_h[-3] and self.data.Close[-2] > self.bol_h[-2]:
            if not self.position:
                self.sell(size=0.05)
            if self.position.is_long:
                self.position.close()
                self.sell(size=0.05)



symbols = get_tickers_usdt()
timeframe = '5m'
interval = 30

data = []
for symbol in symbols:
    try:
        kl = klines_extended(symbol, timeframe, interval)
        # cash is initial investment in USDT, margin is leverage (1/10 is x10)
        # commission is about 0.07% for Binance Futures
        bt = Backtest(kl, str, cash=1000, margin=1/10, commission=0.0007)
        stats = bt.run()
        data.append([symbol, stats.iloc[6]])
    except Exception as err:
        print(err)


result = pd.DataFrame(data)
result.columns = ['Symbol', 'Return']
result.loc[len(result.index)] = ['Total', result['Return'].sum()]
result.to_excel('result.xlsx')


