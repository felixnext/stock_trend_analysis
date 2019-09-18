
import pandas as pd
from . import utils


def get_profile(symbol):
  '''Retrieve the company profile for the given symbol.'''
  # retrieve the data
  url = utils.build_url('company/profile', symbol)
  data = utils.fetch(url)

  # parse the data
  return pd.DataFrame(data)

def list_symbols():
  '''List all available stock symbols.'''
  url = utils.build_url('company/stock', 'list')
  data = utils.fetch(url)

  return pd.DataFrame(data['symbolsList'])
