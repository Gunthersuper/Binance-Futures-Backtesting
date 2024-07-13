import pandas as pd
from time import sleep
import ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
from helper import get_tickers_usdt, klines, klines_extended


def bol_h(df, period=40, dev=2):
    return ta.volatility.BollingerBands(pd.Series(df), window=period, window_dev=dev).bollinger_hband()


def bol_l(df, period=40, dev=2):
    return ta.volatility.BollingerBands(pd.Series(df), window=period, window_dev=dev).bollinger_lband()


class str(Strategy):
    bol_period = 40
    bol_dev = 2

    def init(self):
        self.bol_h = self.I(bol_h, self.data.Close, self.bol_period, self.bol_dev)
        self.bol_l = self.I(bol_l, self.data.Close, self.bol_period, self.bol_dev)

    def next(self):
        if self.data.Close[-2] > self.bol_l[-2] and self.data.Close[-1] < self.bol_l[-1]:
            if not self.position:
                self.buy(size=0.5)
            if self.position.is_short:
                self.position.close()
                self.buy(size=0.5)

        if self.data.Close[-2] < self.bol_h[-2] and self.data.Close[-1] > self.bol_h[-1]:
            if not self.position:
                self.sell(size=0.5)
            if self.position.is_long:
                self.position.close()
                self.sell(size=0.5)


# symbols = get_tickers_usdt()
symbol = 'SOLUSDT'
timeframe = '1m'
interval = 3  # days
kl = klines_extended(symbol, timeframe, interval)
bt = Backtest(kl, str, cash=500, margin=1/10, commission=0.0007)

# stats = bt.run()

stats, heatmap = bt.optimize(
    bol_period=range(5, 120, 2),
    bol_dev=range(0, 10, 1),
    maximize='Equity Final [$]',
    max_tries=2000,
    random_state=0,
    return_heatmap=True)

print(stats)
bt.plot()
# print(heatmap)
result = pd.DataFrame(heatmap)
result.to_excel('heatmap.xlsx')

