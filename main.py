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
# Timeframe (for example, '1m', '3m', '5m', '15m', '1h', '4h')
timeframe = '5m'
# Interval in days:
interval = 30


# symbols = get_tickers_usdt()

# RSI indicator function. Returns dataframe
def rsi(df, period=14):
    rsi = ta.momentum.RSIIndicator(pd.Series(df), window=period).rsi()
    return rsi

def ema(df, period=200):
    ema = ta.trend.EMAIndicator(pd.Series(df), period).ema_indicator()
    return ema

def macd(df):
    macd = ta.trend.MACD(pd.Series(df)).macd()
    return macd

def signal_h(df):
    return ta.volatility.BollingerBands(pd.Series(df)).bollinger_hband()
def signal_l(df):
    return ta.volatility.BollingerBands(pd.Series(df)).bollinger_lband()

class str(Strategy):
    # Any variables you want:
    ema_period = 200
    rsi_period = 14
    def init(self):
        # Take close prices as actual price
        price = self.data.Close
        # Declare indicators you will use in the strategy:
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)
        self.macd = self.I(macd, self.data.Close)
        self.ema = self.I(ema, self.data.Close, self.ema_period)
        self.bol_h = self.I(signal_h, self.data.Close)
        self.bol_l = self.I(signal_l, self.data.Close)

    def next(self):
        price = float(self.data.Close[-1])
        # Strategy example. Its simple RSI. Buy when RSI<30 and sell when RSI>70
        if not self.position and self.rsi[-2] < 30:
            # size is % of the 'cash'
            self.buy(size=0.02, tp=(1+tp)*price, sl=(1-sl)*price)
        if not self.position and self.rsi[-2] > 70:
            self.sell(size=0.02, tp=(1-tp)*price, sl=(1+sl)*price)


symbol = 'XRPUSDT'
kl = klines_extended(symbol, timeframe, interval)
# cash is initial investment in USDT, margin is leverage (1/10 is x10)
# commission is about 0.07% for Binance Futures
bt = Backtest(kl, str, cash=100, margin=1/10, commission=0.0007)
stats = bt.run()
print(stats)
bt.plot()
