'''Holds various normalization and pre-processing functions to generate appropriate training data.'''

import pandas as pd
import numpy as np
from datetime import datetime
# create alias
as_strided = np.lib.stride_tricks.as_strided
# natural language processing stuff
import sklearn_recommender as rec
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk import Tree
import nltk
# download relevant datasets
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('omw')

from recommender.stocks import AlphaVantageTicker, FMPStatements


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
    cols = ["day_{}".format(i+1) for i in range(days_back)] + ["norm_price", "target"]

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

def extract_nouns(text, singular=True):
  '''Retrieves the noun phrases from the given column.

  Args:
    text (str): Text to extract nouns from

  Returns:
    DataFrame only with the extracted column
  '''
  # safty: check correct type
  if not isinstance(text, str):
    #print('error ({}) - ({})'.format(type(text), text))
    return []

  # chunk the data
  chunked = ne_chunk(pos_tag(word_tokenize(text)))
  continuous_chunk = []
  current_chunk = []

  for subtree in chunked:
    if type(subtree) == Tree:
      current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
    elif current_chunk:
      named_entity = " ".join(current_chunk)
      if named_entity not in continuous_chunk or singular == False:
        continuous_chunk.append(named_entity)
        current_chunk = []
    else:
      continue

  return continuous_chunk

def create_profile_dataset(df, embedding='glove'):
  '''Creates a dataset used for similarity actions for company profiles.

  Args:
    df (DataFrame): List of profiles loaded from cache or API
    embedding (str): Defines the type of embedding (options: 'glove', 'nouns', 'tfidf')
  '''
  # safty: check if embeddings valid
  if embedding not in ['glove', 'nouns', 'tfidf']:
    raise ValueError('Unkown embedding type: ({})'.format(embedding))

  # calculate the dummies for all categorical values
  df_sector_dummy = pd.get_dummies(df['sector'], dummy_na=True, prefix='sector')
  df_industry_dummy = pd.get_dummies(df['industry'], dummy_na=True, prefix='industry')
  df_exchange_dummy = pd.get_dummies(df['exchange'], dummy_na=True, prefix='exchange')

  # create embeddings
  embs = None
  if embedding == 'glove':
    gt = rec.glove.GloVeTransformer('twitter', 25, 'sent', tokenizer=rec.nlp.tokenize_clean)
    embs = gt.transform(df['description'])
  elif embedding == 'nouns':
    cv = CountVectorizer(tokenizer=extract_nouns, binary=True, lowercase=False)
    embs = cv.fit_transform(df['description'].fillna("").values)
  elif embedding == 'tfidf':
    cv = CountVectorizer(tokenizer=rec.nlp.tokenize_clean, max_df=0.5)
    tf = TfidfTransformer()
    embs = cv.fit_transform(df['description'].fillna("").values)
    embs = tf.fit_transform(embs)

  # update column names
  embs.columns = ["emb_{}".format(i+1) for i in range(len(embs.columns))]

  # combine into final matrix
  df_final = pd.concat([df[['symbol']], df_sector_dummy, df_industry_dummy, df_exchange_dummy, embs], axis=1).set_index('symbol')

  return df_final

def normalize_statement_data(df, impute=False, impute_method='linear'):
  '''Normamlizes the given reports and extracts relevant statement data.

  Args:
    df (DataFrame): DataFrame with merged statement informations for each company
    impute (bool): Defines if missing values should be imputed to create a stable dataset
    impute_method (str): Defines the method for imputing (options: 'linear', 'pad')

  Returns:
    DataFrame with chained data
  '''
  # check if index is not date already
  if df.index.name == 'date':
    df = df.reset_index()
  if 'date' in df.columns:
    if str(df['date'].dtype) == 'object':
      df['date'] = df['date'].astype('str').apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
    df = df.set_index('date')

  # impute data (note: data should only be imputed per symbol and in a forward fashion)
  if impute == True:
    df = df.reset_index().groupby('symbol').apply(lambda x: x.interpolate(method=impute_method)).set_index('date')

  # calculate some additional statements
  df['cash_overall_position'] = df['cash'] + df['marketable_securities']
  df['cash_net'] = df['cash_overall_position'] - df['debt_longterm']
  df['expenses_research_netcash'] = np.divide(df['expenses_research'], df['cash_net'])

  # list of relevant positions
  name_map = [
    'cash_net',
    'eps_diluted',
    'dividend_share',
    'revenue_growth',
    'cash_marketcap_ratio',
    'expenses_research_netcash',
    'shareholder_equity',
    'debt_growth',
    'eps_growth',
    'research_growth',
    'bookvalue_share_growth',
    'dividend_share_growth',
    'dividend_share_growth_3y',
    'dividend_share_growth_5y',
    'dividend_share_growth_10y',
    'revenue_share_growth_3y',
    'revenue_share_growth_5y',
    'revenue_share_growth_10y'
  ]
  symbol = df['symbol']
  df = df.loc[:, name_map].astype('float32')
  df['symbol'] = symbol

  return df

def merge_stock_statement(df_stocks, df_stmnts, col_price='price', clean_na=True, drop_last_day=True):
  '''Merges the given stock and statement data

  Args:
    df_stocks (DataFrame):
    df_stmnts (DataFrame):
    col_price (str): Name of the column in `df_stocks` that holds the price
    clean_na (bool): Defines if columns with any NaN values should be cleared
    drop_last_day (bool): Defines if the column with the last day information should be dropped (as it is 0)

  Returns:
    Merged dataframe that has 4 special columns at then end (norm_price, target, target_cat, symbol) and date as index. Remaining cols are features.
  '''
  # find the historic length of data
  days_back = df_stocks.columns.str.contains('day_').sum()

  # make sure symbols are upper case
  df_stocks['symbol'] = df_stocks['symbol'].str.upper()
  df_stmnts['symbol'] = df_stmnts['symbol'].str.upper()

  # merge data (note: use values at the end - as pandas matches index otherwise...)
  df_stocks['date_cor'] = (df_stocks.reset_index()['date'] + pd.DateOffset(days_back)).values
  df = pd.merge_asof(
      df_stocks.reset_index().sort_values(by=['date_cor', 'symbol']),
      df_stmnts.reset_index().sort_values(by=['date', 'symbol']),
      left_on='date_cor', right_on='date', by='symbol',
      tolerance=pd.Timedelta('365 day'), direction='backward'
  )

  # calculate the pe_ratio
  df['pe_ratio'] = np.divide(df[col_price], df['eps_diluted'])
  df['cash_share'] = np.divide(df['cash_net'], np.divide(df['shareholder_equity'], df[col_price]))

  # reorder the dataframe
  #df = df.drop(['date_cor'], axis=1)
  special_cols = ['norm_price', 'target', 'target_cat', 'symbol']
  if 'date' in df.columns:
    special_cols.append('date')
  else:
    special_cols.append('date_x')
  cols = df.columns[(df.columns.isin(special_cols) == False) & (df.columns.str.contains("date") == False)].tolist()
  df = df[cols + special_cols].rename(columns={'date_x': 'date'}).set_index('date')

  # drop temporary cols
  df = df.drop(['shareholder_equity', 'cash_net'], axis=1)
  if drop_last_day:
    df = df.drop(['day_{}'.format(int(days_back))], axis=1)

  # clear data
  if clean_na == True:
    df = df.replace([np.inf, -np.inf], np.nan).dropna(how='any', axis=0)

  return df

def create_dataset(symbols, stocks, cache, back, ahead, xlim, num_cats=6, jump_size=21, smooth=5, sm=None, ti=None):
  '''Creates a complete dataset.

  Args:
    symbols (list): List of symbol names to include in the dataset
    stocks (dict): Dict with additional stock file mapping
    cache (Cache): Instance of the cache to load the data
    back (int): Number of days of historic stock data in the dataset
    ahead (int): Number of days the target value lies in the future
    xlim (tuple): Float Tuple of values to limit percentage (keep in mind, that a stock cannot fall below -1)
    num_cats (int): Number of categories to generate
    jump_size (int): Size of the jump in days between datapoints
    smooth (int): Interval of smoothing days around the target value
    sm (Statement): Instance of Statement to load data not in cache (if None use FMPStatements)
    ti (Ticker): Instance of Ticker to load data not in cahce (if None use AlphaVantageTicker)

  Returns:
    Merged final dataset with training data points
  '''
  # load relevant statements
  if sm is None: sm = FMPStatements()
  df_state = cache.load_statement_data(symbols, sm, limit=True)

  # load relevant stocks
  if ti is None: ti = AlphaVantageTicker()
  df_stocks = cache.load_stock_data(symbols, stocks, ti)

  # preprocess the data
  df_norm = create_stock_dataset(df_stocks, back, ahead, smooth, jump_size=jump_size)
  df_stocks_cat = categorize_stock_data(df_norm, xlim=xlim, num_cats=num_cats)
  df_state_norm = normalize_statement_data(df_state, impute=True)
  return merge_stock_statement(df_stocks_cat, df_state_norm, col_price='norm_price')
