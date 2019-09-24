'''Report for the entire Project.

Run this report with: `streamlit run 09-1_project-report.py`

This should provide an interactive mechanism to query the recommender system.
'''

import streamlit as st
import pandas as pd
import numpy as np
import sys
sys.path.insert(1, '..')
import recommender as rcmd
from recommender.contrib import fmp_api as fmp
import sklearn_recommender as skr
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity

# -- Setup --

st.title("Stock Recommender System")

@st.cache
def load_data():
  '''Load all data and setup the system.'''
  # retrieve all relevant symbols
  stocks = fmp.profile.list_symbols()
  cache = rcmd.stocks.Cache()

  # load the relevant profile informations
  df_profile = cache.load_profile_data()

  # generate glove embeddings
  skr.glove.download('twitter')
  gt = skr.glove.GloVeTransformer('twitter', 25, 'sent', tokenizer=skr.nlp.tokenize_clean)
  embs = gt.transform(df_profile['description'].fillna(""))
  df_embs = pd.concat([df_profile[['symbol']], pd.DataFrame(embs)], axis=1).set_index('symbol')

  # create dummy for categorical values
  df_sector_dummy = pd.get_dummies(df_profile['sector'], dummy_na=True, prefix='sector')
  df_industry_dummy = pd.get_dummies(df_profile['industry'], dummy_na=True, prefix='industry')
  df_exchange_dummy = pd.get_dummies(df_profile['exchange'], dummy_na=True, prefix='exchange')
  df_cats = pd.concat([df_profile[['symbol']], df_sector_dummy, df_industry_dummy, df_exchange_dummy], axis=1)

  tf = skr.transformer.SimilarityTransformer(cols=(1, None), index_col='symbol', normalize=True)
  df_sim = tf.transform(df_cats)

  # load the pre-trained model
  model = tf.keras.models.load_model('../data/keras-model.h5')

  # create api access for live data loading
  ticker = rcmd.stocks.AlphaVantageTicker()
  statement = rcmd.stocks.FMPStatements()

  return {'model': model, 'ticker': ticker, 'statement': statement, 'profiles': df_profile, 'embs': df_embs, 'cats': df_cats, 'similarity': df_sim, 'glove': gt}

# actually load the data
data = load_data()

# some settings
cosine_threshold = .92
sim_threshold = .65
max_stocks = 50

# -- General Information --

st.subheader("General Information:")

st.write("The system contains a total of {} stock informations.".format(len(df_cats)))
st.write('Distribution of sectors:')
dist = data['profiles'].groupby('sector').count()['price']
st.bar_chart(dist)

if st.checkbox('show relevant news'):
  st.write("Current stock market news:")
  feed = rcmd.news.FPNewsFeed('https://www.ft.com/business-education?format=rss', col_map={'link': 'article_link', 'summary': 'summary', 'title': 'headline', 'published': 'date'}, filter=True)
  news = feed.news()[1]
  st.text(news)

# -- Stock Selection --

st.subheader("Query System:")

# input a query
st.write("Input a query for the area of stocks you want to search for (e.g. 'Stocks in the Healthcare sector').")
query = st.text_input('Query:')

# -- Run Recommender --

# check if input is present
if len(query) < 3:
  st.write('Please write a query...')
else:
  st.write('Results for "{}":'.format(query))

# first step: filter relevant data
query_emb = data['glove'].transform([query])
# rank each stock according to cosine similarity
rank = cosine_similarity(data['embs'], query_emb)

# filter data according to threshold
df_res = pd.concat([df_profile['symbol'], pd.DataFrame(rank, columns=['cosine'])], axis=1)
df_res = df_res.sort_values(by='cosine', ascending=False)
df_res = df_res[df_res['cosine'] > cosine_threshold].dropna()

# find related items
symbols = df_res['symbol'].values
res_symbols = list(np.copy(symbols))
res_rankings = list(np.copy(df_res['cosine'].values))
for symbol in symbols:
    df_row = data['sim'].loc[symbol].sort_values(ascending=False)
    df_row = df_row[df_row > sim_threshold]
    for col in df_row.index:
        if isinstance(col, float): continue
        if len(res_symbols) > max_stocks: break
        res_symbols.append(col)
        res_rankings.append(cosine_threshold - 0.05)
    if len(res_symbols) > max_stocks: break

# combine with relevant profile data
df_res = pd.DataFrame({'symbol': res_symbols, 'ranking': res_rankings})
df_res = pd.merge(df_res, data['profiles'], on='symbol').sort_values(by='ranking', ascending=False)

st.write("Found {} very relevant and {} relevant stocks for you!".format(len(symbols), len(df_res) - len(symbols)))
load_text = st.write("Loading current stock data 🌍...")

# TODO: retrieve current data for most relevant stock
load_text.write("Prediction future prices 🌎...")

# TODO: load data for all stocks and predict ranking
load_text.write("Completing the ranking 🌏...")

# TODO: show the results
load_text.write("Results:")
