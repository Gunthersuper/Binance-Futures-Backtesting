from binance.um_futures import UMFutures
import pandas as pd
from time import sleep
from time import time
from binance.error import ClientError

client = UMFutures()


def get_tickers_usdt():
    try:
        tickers = []
        resp = client.ticker_price()
        for elem in resp:
            if 'USDT' in elem['symbol']:
                tickers.append(elem['symbol'])
        return tickers
    except ClientError as error:
        print(
            f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")


intervals = {'1m': 1,
             '3m': 3,
             '5m': 5,
             '15m': 15,
             '30m': 30,
             '1h': 60,
             '2h': 120,
             '4h': 240,
             '6h': 360,
             '8h': 480,
             '12h': 720,
             '1d': 1440,
             '3d': 4320,
             '1w': 10080,
             }


def klines(symbol, timeframe='5m', limit=1500, start=None, end=None):
    try:
        resp = pd.DataFrame(client.klines(symbol, timeframe, limit=limit, startTime=start, endTime=end))
        resp = resp.iloc[:, :6]
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        resp = resp.set_index('Time')
        resp.index = pd.to_datetime(resp.index, unit='ms')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(
            f"Found error. status: {error.status_code}, error code: {error.error_code}, error message: {error.error_message}")


def klines_extended(symbol, timeframe='15m', interval_days=30):
    ms_interval = interval_days * 24 * 3600 * 1000
    limit = ms_interval / (intervals[timeframe] * 60 * 1000)
    steps = limit / 1500
    first_limit = int(steps)
    last_step = steps - int(steps)
    last_limit = round(1500 * last_step)
    current_time = time() * 1000
    p = pd.DataFrame()
    for i in range(first_limit):
        start = int(current_time - (ms_interval - i * 1500 * intervals[timeframe] * 60 * 1000))
        end = start + 1500 * intervals[timeframe] * 60 * 1000
        res = klines(symbol, timeframe = timeframe, limit=1500, start=start, end=end)
        p = pd.concat([p, res])
    p = pd.concat([p, klines(symbol, timeframe = timeframe, limit=last_limit)])
    return p