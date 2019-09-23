'''Provides the base class to access financial statements (cashflow and balance-sheets) from various APIs.

Use-Cases:
- Retrieve Balance Statements from companies
- Retrieve Cash Flow Statements and Meta Information
'''


from abc import ABC, abstractmethod
import pandas as pd
import functools
import warnings


class Statements():
  '''Base Class for retrieving statements about a public traded company.'''

  def merge_records(self, stocks, before=None, after=None, annual_growth=True):
    '''Merges different statements into one dataframe.

    Args:
      stocks (list): List of stock symbols to load
      before (date): Date before which the statements should be issued
      after (date): Date after which the statements should be issued
      annual_growth (bool): Defines if growth statements should always be captured annually

    Returns:
      Merged DataFrame of all records
    '''
    # iterate through all data
    dfs = []
    for stock in stocks:
      # retrieve data
      df_state = []
      try:
        df_state.append(self.balance_sheet(stock, before, after))
      except: pass
      try:
        df_state.append(self.income(stock, before, after))
      except: pass
      try:
        df_state.append(self.cash_flow(stock, before, after))
      except: pass
      try:
        if annual_growth:
          try:
            df_state.append(self.growth(stock, before, after, period='annual'))
          except:
            df_state.append(self.growth(stock, before, after))
        else:
          df_state.append(self.growth(stock, before, after))
      except: pass

      # check if valid
      if len(df_state) == 0: continue

      # merge data
      df = functools.reduce(lambda acc, val: acc.join(val), df_state).reset_index()
      df['symbol'] = stock

      # add data
      dfs.append(df)

    # combine all
    if len(dfs) == 0:
      warnings.warn("No statements found for given symbols")
      return pd.DataFrame()
    return pd.concat(dfs, axis=0, sort=True)

  def add_quarter(self, df, date_col='date', change_date=True):
    '''Updates the given dataframe to include quarter and year columns based on the 'date' column.

    Args:
      df (DataFrame): DataFrame to update (has to contain a date column)
      date_col (str): Optional name of the column that contains the date (default: `date`)
      change_date (bool): Defines if the date col in the dataframe should be changed if it is not a datetime dtype

    Returns:
      DataFrame with additional `year` and `quarter` columns
    '''
    # retrieve the column
    date = df[date_col]
    # check type
    if date.dtype == 'object':
      date = date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
      if change_date: df[date_col] = date

    # retrieve data
    df['year'] = date.dt.year
    df['quarter'] = date.dt.quarter

    return df

  def get_features(self, df, symbols, feat):
    '''Retrieves features from the statement dataframe.

    Args:
      symbols (list): list of symbols to use
      feat (str): Feature to extract

    Returns:
      DataFrame using
    '''
    # check if date is there
    if 'year' not in df.columns or 'quarter' not in df.columns:
      df = self.add_quarter(df)

    # convert and return
    return df[df['symbol'].isin(symbols)].pivot_table(index=['year', 'quarter'], columns='symbol', values=feat).sort_index(ascending=True)

  @abstractmethod
  def balance_sheet(self, symbol, before=None, after=None):
    '''Retrieves the balance sheet for the given year.

    The resulting DataFrame should contain at least the following columns (in brackets = optional):
      debt_total, debt_longterm, debt_shortterm
      liability_total, liability_tax, liability_deposit
      inventory, investments
      assets_tax, assets_total, (assets_total_current), (assets_total_noncurrent)

    Args:
      symbol (str): Symbol of the company to retrieve data for.
      before (date): Only include statements before the given time
      after (date): Only include statements after the given time

    Returns:
      DataFrame that contains the list of balance sheets. Different positions are listed as columns and different dates as index
    '''
    pass

  @abstractmethod
  def cash_flow(self, symbol, before=None, after=None):
    '''Retrieves the cash flow statements of a company for the time.

    The resulting DataFrame should contain at least the following columns:
      capital_expenditure, compensation_stockbased, dividends
      cashflow_free, cashflow_invest, cashflow_finance, cashflow_operate
      cash_marketcap_ratio, buybacks

    Args:
      symbol (str): Symbol of the company to retrieve data for.
      before (date): Only include statements before the given time
      after (date): Only include statements after the given time

    Returns:
      DataFrame that contains the cash-flow information. Different positions are listed in columns and different dates as index.
    '''
    pass

  @abstractmethod
  def income(self, symbol, before=None, after=None):
    '''Retrieves the income statements of a company for a time.

    The resulting DataFrame should contain at least the following columns:
      income_consolidated, dividend_share
      revenue, revenue_growth, revenue_costs,
      expenses_research, expenses_operating
      ebit, ebit_margin, income_net, income_operating
      gross_profit, gross_margin

    Args:
      symbol (str): Symbol of the company to retrieve data for.
      before (date): Only include statements before the given time
      after (date): Only include statements after the given time

    Returns:
      DataFrame that contains the cash-flow information. Different positions are listed in columns and different dates as index.
    '''
    pass

  @abstractmethod
  def growth(self, symbol, before=None, after=None):
    '''Retrieves the multi-year growth statements for a company.

    The resulting DataFrame should contain at least the following columns:

    Args:
      symbol (str): Symbol of the company to retrieve data for.
      before (date): Only include statements before the given time
      after (date): Only include statements after the given time

    Returns:
      DataFrame that contains the growth statements.
    '''
    pass
