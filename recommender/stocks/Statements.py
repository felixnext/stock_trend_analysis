'''Provides the base class to access financial statements (cashflow and balance-sheets) from various APIs.

Use-Cases:
- Retrieve Balance Statements from companies
- Retrieve Cash Flow Statements and Meta Information
'''


from abc import ABC, abstractmethod
import pandas as pd


class Statements():
  '''Base Class for retrieving statements about a public traded company.'''

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
