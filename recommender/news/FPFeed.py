'''Implementation of the NewsFeed based on the Feedparser lib.'''


import feedparser as fp
import pandas as pd
from .Feed import NewsFeed


class FPNewsFeed(NewsFeed):
  '''FeedParser implementation of the newsfeed.'''

  def __init__(self, url, col_map=None, col_lambda=None, filter=False):
    super(FPNewsFeed, self).__init__(url, col_map, col_lambda, filter)

  def news(self):
    d = fp.parse(self.url)
    feed = pd.DataFrame(d['entries'])
    meta = d['feed']

    feed = self._transform(feed)

    return meta, feed
