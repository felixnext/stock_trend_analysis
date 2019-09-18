'''Helper for cryptography and secret storing.'''

import pandas as pd
import os

def read_keys(file=None):
  '''Reads the key file and retrieves a .'''
  # check if file is none
  if file is None:
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../keys.csv')

  if not os.path.exists(file):
    raise IOError("File does not exist ({})!".format(file))

  # read the file
  df = pd.read_csv(file, sep=';', header=None)
  return dict(zip(df.iloc[:, 0].values, df.iloc[:, 1]))
