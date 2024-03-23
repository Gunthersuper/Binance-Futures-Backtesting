**Binance Futures backtesting Python script (bactesting.py)**

It doesn't matter which platform you trade on, it just uses binance as the provider (receiving candles).

**Installing**:
1. Download the repo, unpack it
2. Use installing command to get all the needed packages:
   ```
   pip install -r requirements.txt
   ```

**Usage:**
1. Add indicators you want to use. Add it as function that returns dataframe. For example:
   ```
   def rsi(df, period=14):
      rsi = ta.momentum.RSIIndicator(pd.Series(df), window=period).rsi()
      return rsi
   ```
   I use [TA library](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html) for technical analysis.

2. In the strategy class declare all variables (like periods for RSi and EMA), and indicators:
   ```
   class str(Strategy):
      ema_period = 200
      rsi_period = 14
      def init(self):
          self.rsi = self.I(rsi, self.data.Close, self.rsi_period)
          self.macd = self.I(macd, self.data.Close)
   ```

3. In the `next` function describe your strategy:
   ```
   def next(self):
      price = float(self.data.Close[-1])
      if not self.position and self.rsi[-2] < 30:
          self.buy(size=0.02, tp=(1+tp)*price, sl=(1-sl)*price)
      if not self.position and self.rsi[-2] > 70:
          self.sell(size=0.02, tp=(1-tp)*price, sl=(1+sl)*price)
   ```
   We take candles close prices as actual price. Its simple RSI strategy. Buy when RSI<30 and sell when RSI>70.
   `size` is % of the investment that will be used for one order. If investment is 100 and size is 0.02, all orders will use $2 margin.

4. Make a config (TP, SL, Timeframe, and Interval)
   ```
   tp = 0.03
   sl = 0.02
   timeframe = '5m'
   interval = 30
   ```
   `tp` and `sl` is a %. For example, 0.03 is 3% of price changing. `timeframe` is any timeframe available on the binance Futures (1m, 5m, 15m, 1h, 4h).
   `interval` is time interval in days (there are some restrictions, like you cant get 5m klines for more than 30 days).

5. Run the backtesting:
   ```
   symbol = 'XRPUSDT'
   kl = klines_extended(symbol, timeframe, interval)
   bt = Backtest(kl, str, cash=100, margin=1/10, commission=0.0007)
   stats = bt.run()
   print(stats)
   bt.plot()
   ```
   `symbol` is any symbol you want. You can get all symbols using `symbols = get_tickers_usdt()`.

   `cash` is some investment. `margin` is leverage, 1/10 is x10. commission is a broker commisson. Binance takes 0.02% + 0.05%

   `print(stats)` shows all the needed statistics in the console, like this:
   ```
    Start                     2024-02-22 11:15:00
    End                       2024-03-23 11:10:00
    Duration                     29 days 23:55:00
    Exposure Time [%]                   79.351852
    Equity Final [$]                   101.698555
    Equity Peak [$]                    102.287638
    Return [%]                           1.698555
    Buy & Hold Return [%]               13.503115
    Return (Ann.) [%]                   21.934238
    Volatility (Ann.) [%]               18.247439
    Sharpe Ratio                         1.202045
    Sortino Ratio                         2.18934
    Calmar Ratio                         6.605664
    Max. Drawdown [%]                    -3.32052
    Avg. Drawdown [%]                   -0.329843
    Max. Drawdown Duration       11 days 09:30:00
    Avg. Drawdown Duration        0 days 15:25:00
    # Trades                                  101
    Win Rate [%]                        43.564356
    Best Trade [%]                       2.948099
    Worst Trade [%]                     -2.088616
    Avg. Trade [%]                       0.059854
    Max. Trade Duration           2 days 20:55:00
    Avg. Trade Duration           0 days 05:35:00
    Profit Factor                        1.077106
    Expectancy [%]                       0.090063
    SQN                                  0.347798
   ```

   And `bt.plot()` makes a chart as html page:
   ![1](https://i.imgur.com/Abxgz2B.png)

