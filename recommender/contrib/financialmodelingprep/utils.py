'''Defines the basic util functions for the API.'''


import pandas as pd
import numpy as np
import requests
import json


def build_url(category, symbol, meta={}, version=3):
  '''Creates the url based on the given information.

  Args:
    category (str): The category of the information (e.g. 'company/profile' or 'financials/income-statement')
    symbol (str): The symbol for the current category to fetch information for (e.g. 'AAPL')
    meta (dict): Dictionary of metadata to append to the url
    version (int): Optional version of the API (default is 3)

  Returns:
    Created url string
  '''
  # create the basic string
  base = "https://financialmodelingprep.com/api/v{}".format(version)
  # build the metadata
  metadata = '&'.join(["{}={}".format(key, meta[key]) for key in meta])
  # build the final data
  return "{}/{}/{}{}".format(base, category, symbol, "?{}".format(metadata) if len(metadata) > 0 else "")

def fetch(url, type='get', body=None):
  '''Fetches information from the API.

  Args:
    url (str): The url of data to retrieve
    type (str): The type of the request (options: ['get', 'post', 'options'])
  '''
  # select correct type
  type = type.lower()
  if type == 'get':
    res = requests.get(url)
  elif type == 'post':
    res = requests.post(url, data=json.dump(body))
  elif type == 'options':
    res = requests.options(url)

  # execute command
  return res.json()
