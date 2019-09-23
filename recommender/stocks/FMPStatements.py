'''Implements the Statements interface through the FinancialModelingPrep API.'''


import pandas as pd
import numpy as np
from datetime import date, datetime
from .Statements import Statements
from recommender.contrib import fmp_api


class FMPStatements(Statements):
  '''Retrieves Company Statements through the FMP Api.

  Args:
    granularity (str): Default granularity that is used for statements (options: 'annual', 'quarter')
  '''
  def __init__(self, granularity='quarter'):
    self.period = granularity

  def _filter(self, df, before, after):
    '''Filters the dataframe based on the given dates.'''
    # transform datetime
    df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())

    # convert data to common format
    df = df.set_index('date')

    # filter the relevant data
    if before is not None:
      df = df.loc[df.index < before]
    if after is not None:
      df = df.loc[df.index > after]

    return df

  def balance_sheet(self, symbol, before=None, after=None, period=None):
    period = self.period if period is None else period
    # retrieve the relevant data
    df = fmp_api.statements.balance_sheet(symbol, period=period)
    df = self._filter(df, before, after)

    # convert data
    name_map = {
      'Cash and cash equivalents': 'cash',
      'Short-term investments': 'marketable_securities',
      'Total debt': 'debt_total',
      'Short-term debt': 'debt_shortterm',
      'Long-term debt': 'debt_longterm',
      'Total assets': 'assets_total',
      'Total current assets': 'assets_total_current',
      'Total non-current assets': 'assets_total_noncurrent',
      'Tax assets': 'assets_tax',
      'Total liabilities': 'liability_total',
      'Tax Liabilities': 'liability_tax',
      'Deposit Liabilities': 'liability_deposit',
      'Deferred revenue': 'revenue_deffered',
      'Investments': 'investments',
      'Inventories': 'inventory',
      'Total shareholders equity': 'shareholder_equity'
    }
    type_map = {}
    df = df.rename(columns=name_map).loc[:, list(name_map.values())].astype('float32')

    return df

  def cash_flow(self, symbol, before=None, after=None, period=None):
    period = self.period if period is None else period
    # retrieve the relevant data
    df = fmp_api.statements.cash_flow(symbol, period=period)
    df = self._filter(df, before, after)

    # convert data in common format
    name_map = {
      'Capital Expenditure': 'capital_expenditure',
      'Stock-based compensation': 'compensation_stockbased',
      'Free Cash Flow': 'cashflow_free',
      'Investing Cash flow': 'cashflow_invest',
      'Financing Cash Flow': 'cashflow_finance',
      'Operating Cash Flow': 'cashflow_operate',
      'Net Cash/Marketcap': 'cash_marketcap_ratio',
      'Issuance (buybacks) of shares': 'buybacks',
      'Dividend payments': 'dividends'
    }
    df = df.rename(columns=name_map).loc[:, list(name_map.values())].astype('float32')

    return df

  def income(self, symbol, before=None, after=None, period=None):
    period = self.period if period is None else period
    # retrieve the relevant data
    df = fmp_api.statements.income(symbol, period=period)
    df = self._filter(df, before, after)

    # convert data in common format
    name_map = {
      'EBIT': 'ebit',
      'EBIT Margin': 'ebit_margin',
      'EPS': 'eps',
      'EPS Diluted': 'eps_diluted',
      'Consolidated Income': 'income_consolidated',
      'Cost of Revenue': 'revenue_costs',
      'Gross Profit': 'gross_profit',
      'Gross Margin': 'gross_margin',
      'R&D Expenses': 'expenses_research',
      'Operating Expenses': 'expenses_operating',
      'Net Income': 'income_net',
      'Operating Income': 'income_operating',
      'Dividend per Share': 'dividend_share',
      'Revenue': 'revenue',
      'Revenue Growth': 'revenue_growth',
    }
    df = df.rename(columns=name_map).loc[:, list(name_map.values())].astype('float32')

    return df

  def growth(self, symbol, before=None, after=None, period=None):
    period = self.period if period is None else period
    # retrieve the relevant data
    df = fmp_api.statements.growth(symbol, period=period)
    df = self._filter(df, before, after)

    # convert the relevant data
    name_map = {
      'Debt Growth': 'debt_growth',
      'R&D Expense Growth': 'research_growth',
      'Book Value per Share Growth': 'bookvalue_share_growth',
      'EPS Growth': 'eps_growth',
      'Dividends per Share Growth': 'dividend_share_growth'
    }
    if period == 'annual':
      name_map.update( {
        '10Y Dividend per Share Growth (per Share)': 'dividend_share_growth_10y',
        '5Y Dividend per Share Growth (per Share)': 'dividend_share_growth_5y',
        '3Y Dividend per Share Growth (per Share)': 'dividend_share_growth_3y',
        '10Y Revenue Growth (per Share)': 'revenue_share_growth_10y',
        '5Y Revenue Growth (per Share)': 'revenue_share_growth_5y',
        '3Y Revenue Growth (per Share)': 'revenue_share_growth_3y',
      } )
    df = df.rename(columns=name_map).loc[:, list(name_map.values())].astype('float32')

    return df
