'''Holds various normalization and pre-processing functions to generate appropriate training data.'''

import pandas as pd
import numpy as np
from datetime import datetime
# create alias
as_strided = np.lib.stride_tricks.as_strided


def normalize_stock_array(arr):
  '''Normalizes the given input array.'''
  norm = arr[-1]
  arr = np.divide(arr, norm) - 1
  return arr


def normalize_stock_window(arr, days_back, days_target, smooth_interval):
  '''Normalizes the stock data in the given window and returns the values and the target

  This function should be used on the data returned from a sliding window on the stock data of a single symbol

  Args:
    arr (np.Array): Numpy Array that contains only one values column
    days_back (int): How many days of history data should be included
    days_target (int): How many days shoudl the target value lie ahead
    smooth_interval (int): Interval in days around the target value that is used for smoothing (if None use just target day)

  Returns:
    Numpy array that has the normalized data of length `days_back` and an additional datapoint with the target value
  '''
  # retrieve the normalized data
  norm = arr[days_back - 1]
  arr = np.divide(arr, norm) - 1

  # retrieve the input stock values
  vals = arr[:days_back]
  # TODO: might call additional compaction (e.g. only weekly data)

  # calculate the target value
  target_loc = days_back + days_target - 1
  if smooth_interval is None:
    target = arr[target_loc]
  else:
    target = arr[(target_loc - smooth_interval):(target_loc + smooth_interval + 1)].mean()

  # return result vector
  return np.concatenate([vals, [norm, target]])

def create_stock_dataset(df, days_back, days_target, smooth_interval, value_col='close', jump_size=7):
    '''Creates a dataset from the given stock data.

    Args:
        df (DataFrame): DataFrame of stock prices. Each Row should contain these columns: `[symbol, date, values]`
        value_col (str): Name of the column that contains the relevant stock data
        days_back (int): How many days of history data should be included
        days_target (int): How many days shoudl the target value lie ahead
        smooth_interval (int): Interval in days around the target value that is used for smoothing
        jump_size (int): Number of days to jump between different data points

    Returns:
        DataFrame that should contain the relevant stock information. It contains the following columns: `[date, *data, norm_value, target, symbol]`.
        `date` is thereby the starting date before the prediction.
        `norm_value` is the dollar value of the stock used as normalization point (from date+days_back)
        `data` are a list of columns from newest to oldest (number is defined by `days_back`)
           |------------------|----------------------------|
         date    data    date+days_back                 target
    '''
    # safty checks
    if jump_size < 1:
      raise ValueError("Value `jump_size` may not be smaller than 1 (current value: {})".format(jump_size))
    if value_col not in df.columns:
      raise ValueError("The provided value column ({}) does not exist in the given dataframe".format(value_col))

    # iterate through all symbols in the df
    symbols = df['symbol'].unique()
    # make sure that date column is converted
    if df['date'].dtype == 'object':
        df['date'] = df['date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))

    # calculate window size and the column names
    win = days_back + days_target + (smooth_interval if smooth_interval is not None else 0)
    cols = ["day_{}".format(i+1) for i in range(days_back)] + ["norm_value", "target"]

    # order symbol-df for time and perform sliding window
    df_symbol = df['symbol'].str.lower()
    df_norm = []
    for symbol in symbols:
        # retrieve partial df
        df_sym = df[df_symbol == symbol.lower()].sort_values(by='date').set_index('date')[[value_col]]
        # note: use copy to ensure memory safty for as_strided function
        df_arr = np.copy(df_sym.to_numpy())

        # sliding window (Note: pandas does not write a new array to disk, but references the old one, as long as no values are modified)
        st = df_arr.strides   # number of bytes for as_stride to jump
        sz = np.ceil((len(df_arr) - (win-1)) / jump_size)
        # make sure that we have minimum requried data
        if sz <= 0: continue
        # note: as_strided works directly on memory blocks and might crash the program
        wnds = as_strided(df_arr, (int(sz), win), (st[0] * jump_size, st[1] * 1), writeable=False)

        # apply normalization
        df_res = np.apply_along_axis(lambda wnd: normalize_stock_window(wnd, days_back, days_target, smooth_interval), axis=1, arr=wnds)
        df_res = pd.DataFrame(df_res)

        # add columns and index
        df_res.columns = cols
        df_res.index = df_sym.index[:-(win-1)][0::jump_size]
        df_res['symbol'] = symbol

        # add to result
        df_norm.append(df_res)

    # add data to target
    df_norm = pd.concat(df_norm, axis=0)

    return df_norm

def categorize_stock_data(df, xlim, num_cats=6, debug=True):
    '''Performs categorization of the target values in the data.

    Args:
        df (DataFrame): DataFrame that contains the datapoints and a value of the target values
        xlim (tuple): tuple of limit values for the min and max values
        num_cats (int): Number of categories to apply (2 categories are outer)
        debug (bool): Prints the category borders

    Returns:
        DataFrame with update `target` column that contains int categorical value
    '''
    # define boundaries of categories
    d = (xlim[1] - xlim[0]) / (num_cats - 2)
    cats = np.array([xlim[0] + (d*i) for i in range(0, num_cats - 1)])
    if debug: print(cats)

    # update the target column
    df['target_cat'] = df['target'].clip(xlim[0], xlim[1]).apply(lambda x: num_cats - 1 if x == xlim[1] else np.where((cats >= x))[0][0])

    return df
