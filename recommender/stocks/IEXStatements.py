'''Uses the Iex Cloud Service to implement the Statements interface.'''


import pandas as pd
import numpy as np
import iexfinance as iex
from .Statements import Statements


class IEXStatements(Statements):
  '''Retrieves statements of a company through the IEX Cloud API.'''
  pass
