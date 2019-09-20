
import pandas as pd
from . import utils


def get_profile(symbol):
  '''Retrieve the company profile for the given symbol.'''
  # retrieve the data
  url = utils.build_url('company/profile', symbol)
  data = utils.fetch(url)

  # parse the data
  return pd.DataFrame(data)

def list_profiles(symbols=None):
  '''Generates a list of all available company profiles.

  Args:
    stocks (list): List of string values to search profiles for (if None use `list_symbols`)

  Returns:
    Company profiles as dataframe
  '''
  if symbols is None:
    symbols = list_symbols()['symbol'].values
  # iterate through all symbols
  ls = []
  for symbol in symbols:
    try:
      profile = get_profile(symbol)
    except:
      continue

    # check for empty dataframe
    if profile.empty == True or 'profile' not in profile.columns:
      continue

    # process the profile
    ls.append(profile[['profile']].transpose().assign(symbol=symbol).set_index('symbol'))

  # generate final dataframe
  return pd.concat(ls, axis=0)

def list_symbols():
  '''List all available stock symbols.'''
  url = utils.build_url('company/stock', 'list')
  data = utils.fetch(url)

  return pd.DataFrame(data['symbolsList'])

def find_symbol(name, stocks=None):
  '''Searches the data list based on the given description and returns the symbol.

  Args:
    name (str): Pattern to use searching
    stocks (DataFrame): List of stocks to search in (if None call `list_symbols`)

  Returns:
    List of all the matches found as tuples (name, symbol)
  '''
  if stocks is None:
    stocks = list_symbols()
  # retrieve all relevant patterns
  df = stocks[stocks['name'].str.contains(name, case=False)]
  if len(df) > 0:
    return list(zip(df['name'].values, df['symbol'].values))
  return []
