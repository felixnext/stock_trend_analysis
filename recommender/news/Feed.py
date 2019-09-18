'''Base Class for any news feed.'''


from abc import ABC, abstractmethod


class NewsFeed(object):
  '''Abstract Class for any news feed.

  Note that `col_lambda` supports various string function names of lambda functions.
  Supported string functions are: TODO

  Args:
    url (str): URL that is used for the feed
    col_map (dict): Optional mapping of columns - Keys should be old column name - value should be new column name
    col_lambda (dict): Optional parsing of columns - Keys should be new column name - Value should be a lambda function that can be used for pandas apply function.
    filter (bool): Defines if the data should be filtered to columns specified in `col_map`
  '''

  def __init__(self, url, col_map=None, col_lambda=None, filter=False):
    self.url = url
    self.col_map = col_map
    self.col_lambda = col_lambda
    self.filter = filter

  # contains the string defined functions
  _STR_FCT = {
    # tokenize the given string col
    'tokenize': lambda x: x,
    # convert the col into a datetime
    'datetime': lambda x: x
  }

  def _transform(self, df):
    '''Transforms a dataframe to apply the given col_map and col_lambda values.

    Args:
      df (DataFrame): Dataframe to transform

    Returns:
      Transformed DataFrame
    '''
    # rename relevant cols
    if self.col_map is not None:
      df = df.rename(columns=self.col_map)
    # iterate through all transformations
    if self.col_lambda is not None:
      for key in col_lambda:
        fct = col_lambda[key]
        # check if string function
        if isinstance(fct, str):
          fct = NewsFeed._STR_FCT[fct]
        df[key] = df[key].apply(fct)

    # check for column filter
    if self.filter and self.col_map is not None:
      df = df[list(self.col_map.values())]

    return df

  @abstractmethod
  def news(self):
    '''Retrieves the latest news from the given feed.

    Returns:
      meta (dict): Metainformation about the Feed
      feed (DataFrame): Actual feed data
    '''
    pass
