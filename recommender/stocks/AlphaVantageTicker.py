'''
Defines the stock ticker for the Alpha Vantage API.

'''

from alpha_vantage.timeseries import TimeSeries
from .Ticker import Ticker, TickerResolution, TickerGranularity
from recommender import utils

from datetime import datetime
import pytz
import re

class AlphaVantageTicker(Ticker):
  '''Ticker implementation for the Alpha-Vantage API.

  Example:
    ```
    ticker = AlphaVantageTicker('<KEY>')
    data = ticker.historic('MSFT', start=None)
    ```

  Args:
    key: `str` key for the alpha vantage API (if None try to load through `utils.read_keys()`)
    outputsize: `str` of either `full` or `compact` that defines the return values from the API.
  '''
  def __init__(self, key=None, outputsize='full'):
    # check if key should be updated
    if key is None:
      key = utils.read_keys()['alphavantage']
    # retrieve the data
    self.__key = key
    self.ts = TimeSeries(key=self.__key, output_format='pandas')
    self._out = outputsize

  def price(self, symbol):
    '''Retrieves the current price of the given stock.

    Args:
      symbol: `str` of the symbol name

    Returns:
      `dict` that contains open, close, volume, high, low, timestamp
    '''
    # retrieve the data
    data, meta_data = self.ts.get_intraday(symbol, interval='1min', outputsize='compact')
    price = data[-1:]

    # adjust time
    tz = utils.parse_time(price.index[0], "%Y-%m-%d %H:%M:%S", meta_data["6. Time Zone"])
    # TODO: adjust to current timezone?

    # generate the output
    return {'timestamp': tz,
            'open': price['1. open'][0], 'close': price['4. close'][0],
            'high': price['2. high'][0], 'low': price['3. low'][0],
            'volume': price['5. volume'][0]}

  def __search_key(self, dic, str):
    '''Helper function to find an entry in dicts.'''
    p = re.compile('.*{}.*'.format(str), re.IGNORECASE)
    for key in dic:
      m = p.match(key)
      if m is not None:
        return key

  def historic(self, symbol, start, end=None, resolution="daily"):
    '''Retrieves the historic prices from

    Args:
      symbol: `str` of the symbol name
      start: `datetime` or `long` of the starting point (`None` = from earliest)
      end: `datetime` or `long` of the ending point (`None` = up to current)
      resolution: `TickerResolution` or `str` on the resolution of the data. (strings can be `weekly`, `monthly`, `daily`,
        '<X>min', whereby X is replaced by a number)

    Returns:
      `pd.dataframe` with a `pd.DatetimeIndex` and columns `open`, `close`, `low`, `high`, `volume`.
    '''
    # safty: covnert input data
    start = utils.safe_datetime(start)
    end = utils.safe_datetime(end)
    # safty: check input data
    if (start is not None and start.tzinfo is None) or (end is not None and end.tzinfo is None):
      print("WARNING: `start` and/or `end` timestamps appear not to have a timezone!")

    # handle resolution
    if isinstance(resolution, str):
      resolution = TickerResolution.from_string(resolution)
    time_format = '%Y-%m-%d'

    # check for correct granularity
    if resolution.granularity == TickerGranularity.DAILY:
      if resolution.adjusted:
        data, md = self.ts.get_daily_adjusted(symbol, outputsize=self._out)
      else:
        data, md = self.ts.get_daily(symbol, outputsize=self._out)
    elif resolution.granularity == TickerGranularity.WEEKLY:
      if resolution.adjusted:
        data, md = self.ts.get_weekly_adjusted(symbol)
      else:
        data, md = self.ts.get_weekly(symbol)
    elif resolution.granularity == TickerGranularity.MONTHLY:
      if resolution.adjusted:
        data, md = self.ts.get_monthly_adjusted(symbol)
      else:
        data, md = self.ts.get_monthly(symbol)
    else:
      # retrieve number closed to predef minute intervals
      mins = utils.math.take_smallest_closest(resolution.min_interval, [1,5,15,30,60])
      time_format = '%Y-%m-%d %H:%M:%S'
      # retrieve the data
      data, md = self.ts.get_intraday(symbol, interval="{}min".format(mins), outputsize=self._out)
      # TODO: filter the data in pandas (according to actual resolution data)

    # format the data
    tz = pytz.timezone(md[self.__search_key(md, "Time Zone")])
    data.rename(columns={'1. open':'open', '2. high':'high', '3. low':'low', '4. close': 'close', '5. volume': 'volume'}, inplace=True)
    data.index = data.index.map( lambda x:tz.localize( x ) )

    # filter on the given time series
    if end is not None:
      data = data.loc[start:end]
    else:
      data = data.loc[start:]

    return data
