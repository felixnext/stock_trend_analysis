'''Base Class for stock price collectors.abs

Use Cases:
- Retrieve historic data about a specific stock (e.g. symbol "XX" timespan YY)
- Retrieve current stock price
'''

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import re
import tzlocal, time

class TickerGranularity(Enum):
  '''Defines the resolution of the stock ticker.'''
  INTRADAY = 0
  DAILY = 1
  WEEKLY = 2
  MONTHLY = 3

class TickerResolution():
  '''Storage class for resolution.'''
  def __init__(self, granularity=TickerGranularity.INTRADAY, min_interval=15, adjusted=False):
    '''Creates the resolution method.

    Args:
      res: `TickerGranularity` to define the raw resolution
      min_interval: `int` to define the number of minutes for `INTRADAY` granularity
      adjusted: `bool` defines if closing prices should be adjusted
    '''
    self.granularity = granularity
    self.min_interval = min_interval
    self.adjusted = adjusted

  def from_string(str):
    '''Generates a Resolution from string.'''
    str = str.lower()
    if str == 'daily':
      return TickerResolution(TickerGranularity.DAILY)
    if str == 'daily_adjusted':
      return TickerResolution(TickerGranularity.DAILY, adjusted=True)
    if str == 'weekly':
      return TickerResolution(TickerGranularity.WEEKLY)
    if str == 'weekly_adjusted':
      return TickerResolution(TickerGranularity.WEEKLY, adjusted=True)
    if str == 'monthly':
      return TickerResolution(TickerGranularity.MONTHLY)
    if str == 'monthly_adjusted':
      return TickerResolution(TickerGranularity.MONTHLY, adjusted=True)
    p = re.compile('([0-9]+)min', re.IGNORECASE)
    m = p.match(str)
    if m is not None:
      return TickerResolution(TickerGranularity.INTRADAY, min_interval=int(m.group(1)))
    raise ValueError("Unable to parse string ({}) into valid resolution!".format(str))

class RepeatMode(Enum):
  '''Defines the types of repeat modes for the generator.'''
  LAST = 0, # reuse the last value on next call
  NONE = 1, # return none if no new value available
  WAIT = 2, # sleep to reduce load
  LOOP = 3  # simple retry (might be spamming and gets blocked)

class Ticker():
  '''Interface for any ticker information API.'''

  @abstractmethod
  def price(self, symbol):
    '''Retrieves the current price of the given stock.

    Args:
      symbol: `str` of the symbol name

    Returns:
      `dict` that contains open, close, volume, high, low, timestamp
    '''
    pass

  def price_simple(self, symbol):
    '''Retrieves the current price of the given stock.

    Args:
      symbol: `str` of the symbol name

    Returns:
      `tuple` in format (closing price, datetime)
    '''
    data = self.price(symbol)
    return data["close"], data["timestamp"]


  @abstractmethod
  def historic(self, symbol, start, end=None, resolution='daily'):
    '''Retrieves the historic prices from the API.

    Args:
      symbol: `str` of the symbol name
      start: `datetime` or `long` of the starting point (`None` = from earliest)
      end: `datetime` or `long` of the ending point (`None` = up to current)
      resolution: `TickerResolution` or `str` on the resolution of the data. (strings can be `weekly`, `monthly`, `daily`,
        '<X>min', whereby X is replaced by a number)

    Returns:
      `pd.dataframe` with a `pd.DatetimeIndex` and columns `open`, `close`, `low`, `high`, `volume`.
    '''
    pass

  def generator(self, symbol, repeat=RepeatMode.WAIT, sleep_time=0.01):
    '''Creates a generator for the stock data, allowing to retrieve the newest values if possible (otherwise yield None).

    Note that the usage of a `RepeatMode` other than `WAIT` might result in a endless loop that consumes all resources!

    Args:
      symbol: `str` name of the symbol to retrieve
      repeat: `bool` that shows if the last value should be repeated if no new value is available

    Returns:
      Generator that has the same output format as `price`
    '''
    last = None
    while True:
      # check if enough time has passed
      tz = tzlocal.get_localzone()
      if last is None or (tz.localize(datetime.now()) - last['timestamp']).total_seconds() > 60:
        # retrieve new data
        old_ts = 0 if last is None else last['timestamp']
        try:
          last = self.price(symbol)
          # check if different from old
          if old_ts != last['timestamp']:
            yield last
            continue
        except:
          time.sleep(sleep_time)
          continue
      # different repeat strategies
      if repeat == RepeatMode.LAST: yield last
      elif repeat == RepeatMode.NONE: yield None
      elif repeat == RepeatMode.WAIT: time.sleep(sleep_time)


  # TODO: which types of general data do exist?
