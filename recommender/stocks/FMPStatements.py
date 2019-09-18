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

    # TODO: convert data

    return df

  def cash_flow(self, symbol, before=None, after=None):
    period = self.period if period is None else period
    # retrieve the relevant data
    df = fmp_api.statements.cash_flow(symbol, period=period)
    df = self._filter(df, before, after)

    # TODO: convert data in common format

    return df

  def income(self, symbol, before=None, after=None, period=None):
    period = self.period if period is None else period
    # retrieve the relevant data
    df = fmp_api.statements.income(symbol, period=period)
    df = self._filter(df, before, after)

    return df
