'''Defines a cache function that loads data from disk.'''

import os
import glob
import pandas as pd

class Cache():
  '''Cache Function that stores stock and statement data on disk and loads it if required.

  Args:
    cache_folder (str): Folder to store the cache data into
  '''
  def __init__(self, cache_folder='../data'):
    self.path = cache_folder

  def list_data(self, type='stock'):
    '''Generates a list of available symbols for the given data type in cache.

    Args:
      type (str): type of data to retrieve (options: 'stock', 'etf', 'statement')
    '''
    # safty check
    if type not in ['stock', 'etf', 'statement']:
      raise ValueError("Given type is not recognized ({})".format(type))

    # set folder
    fldr = 'Stocks' if type == 'stock' else 'ETFs'
    path = os.path.join(self.path, fldr, '*.txt')
    # list all fiels in direcotry
    files = glob.glob(path)
    names = pd.Series(files).apply(lambda f: os.path.basename(f).split('.')[0])

    # create dict for search
    return dict(zip(names, files))

  def load_data(self, symbols, type='stock'):
    '''Loads the historic data for the list of given symbols.

    Args:
      symbols (list): List of symbols that
      type (str): Type of data to load (options: 'stock', 'etf', 'statement')

    Returns:
      DataFrame with the loaded data for the given times
    '''
    stocks = self.list_stocks(type)
    for symbol in symbols:
      # check if data is not given
      if symbol not in stocks:
        pass

  def get_data(self, symbols, ticker=None, statement=None):
    '''Loads the relevant company data either from the Cache using the APIs.

    Args:
      symbols (list): List of symbols to load
      ticker (Ticker): Instance of a ticker to load data through (if None create AlphaVantage)
      statement (Statement): Instance of the statement to load data through (if None create FMP)

    Returns:
      DataFrame with the combined data for all given stocks.
    '''
    pass
