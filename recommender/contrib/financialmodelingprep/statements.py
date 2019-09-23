
import numpy as np
import pandas as pd
from . import utils


def income(symbol, period='annual'):
  '''Retrieves the income statements from the given symbol.

  Args:
    symbol (str): Symbol to retrieve the income statements for
    period (str): Interval for the statements (options: 'annual' or 'quarter')

  Returns:
    Pandas DataFrame with the relevant statements
  '''
  meta = {}
  if period == 'quarter':
    meta['period'] = period
  url = utils.build_url('financials/income-statement', symbol, meta=meta)
  data = utils.fetch(url)

  # convert to datafraem
  df = pd.DataFrame(data['financials']).replace(r'^\s*$', np.nan, regex=True)
  return utils.convert_dtype(df, 'float32', ['date'])

def balance_sheet(symbol, period='annual'):
  '''Retrieves the relevant balance sheet statements for the given symbol

  Args:
    symbol (str): Symbol to retrieve the income statements for
    period (str): Interval for the statements (options: 'annual' or 'quarter')

  Returns:
    Pandas DataFrame with the relevant statements
  '''
  meta = {}
  if period == 'quarter':
    meta['period'] = period
  url = utils.build_url('financials/balance-sheet-statement', symbol, meta=meta)
  data = utils.fetch(url)

  df = pd.DataFrame(data['financials']).replace(r'^\s*$', np.nan, regex=True)
  return utils.convert_dtype(df, 'float32', ['date'])

def cash_flow(symbol, period='annual'):
  '''Retrieves the relevant cash-flow statements for the given symbol.

  Args:
    symbol (str): Symbol to retrieve the income statements for
    period (str): Interval for the statements (options: 'annual' or 'quarter')

  Returns:
    Pandas DataFrame with the relevant statements
  '''
  meta = {}
  if period == 'quarter':
    meta['period'] = period
  url = utils.build_url('financials/cash-flow-statement', symbol, meta=meta)
  data = utils.fetch(url)

  df = pd.DataFrame(data['financials']).replace(r'^\s*$', np.nan, regex=True)
  return utils.convert_dtype(df, 'float32', ['date'])

def growth(symbol, period='annual'):
  '''Retrieves the growth statements for the given symbol.

  Args:
    symbol (str): Symbol to retrieve the income statements for
    period (str): Interval for the statements (options: 'annual' or 'quarter')

  Returns:
    Pandas DataFrame with the relevant statements
  '''
  meta = {}
  if period == 'quarter':
    meta['period'] = period
  url = utils.build_url('financial-statement-growth', symbol, meta=meta)
  data = utils.fetch(url)

  # convert all items
  ratios = data['growth']
  items = {}
  dates = []
  for rat in ratios:
      dates.append(rat.pop('date'))
      for key in rat:
          if key in items:
              items[key].append(rat[key])
          else:
              items[key] = [rat[key]]

  df = pd.DataFrame(items).assign(date=dates).replace(r'^\s*$', np.nan, regex=True)
  return utils.convert_dtype(df, 'float32', ['date'])
