'''Provides the base class to access financial statements (cashflow and balance-sheets) from various APIs.

Use-Cases:
- Retrieve Balance Statements from companies
- Retrieve Cash Flow Statements and Meta Information
'''


from abc import ABC, abstractmethod
import pandas as pd


def Statements():
  '''Base Class for retrieving statements about a public traded company.'''

  @abstractmethod
  def balance_sheet(self, symbol, before=None, after=None):
    '''Retrieves the balance sheet for the given year.

    Args:
      symbol (str): Symbol of the company to retrieve data for.
      before (datetime): Only include statements before the given time
      after (datetime): Only include statements after the given time

    Returns:
      DataFrame that contains the list of balance sheets. Different positions are listed as columns and different dates as index
    '''
    pass

  @abstractmethod
  def cash_flow(self, symbol, before=None, after=None):
    '''Retrieves the cash flow statements of a company for the time.

    Args:
      symbol (str): Symbol of the company to retrieve data for.
      before (datetime): Only include statements before the given time
      after (datetime): Only include statements after the given time

    Returns:
      DataFrame that contains the cash-flow information. Different positions are listed in columns and different dates as index.
    '''
    pass
