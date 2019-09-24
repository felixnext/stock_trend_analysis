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

  simtf = skr.transformer.SimilarityTransformer(cols=(1, None), index_col='symbol', normalize=True)
  df_sim = simtf.transform(df_cats)

  #return {'model': model, 'ticker': ticker, 'statement': statement, 'profiles': df_profile, 'embs': df_embs, 'cats': df_cats, 'similarity': df_sim, 'glove': gt}
  return df_profile, df_embs, df_cats, df_sim, gt

load_mods = st.text("Loading models...")
# actually load the data
model = tf.keras.models.load_model('../data/keras-model.h5')
# create api access for live data loading
ticker = rcmd.stocks.AlphaVantageTicker()
statement = rcmd.stocks.FMPStatements()
# load hashed data
df_profile, df_embs, df_cats, df_sim, gt = load_data()
load_mods.text("Loaded models.")

# some settings
cosine_threshold = .92
sim_threshold = .65
max_stocks = 50
max_enlarged = 10
# model params
model_back = 14

# -- General Information --

st.subheader("General Information:")

st.write("The system contains a total of {} stock informations.".format(len(df_cats)))
st.write('Distribution of sectors:')
dist = df_profile.groupby('sector').count()['price']
st.bar_chart(dist)

if st.checkbox('show relevant news'):
  st.write("Current stock market news:")
  feed = rcmd.news.FPNewsFeed('https://www.ft.com/business-education?format=rss', col_map={'link': 'link', 'summary': 'summary', 'title': 'headline', 'published': 'date'}, filter=True)
  news = feed.news()[1]
  st.dataframe(news[['headline', 'date', 'summary', 'link']].set_index('date'))

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
  query_emb = gt.transform([query])
  # rank each stock according to cosine similarity
  rank = cosine_similarity(df_embs, query_emb)

  # filter data according to threshold
  df_res = pd.concat([df_profile['symbol'], pd.DataFrame(rank, columns=['cosine'])], axis=1)
  df_res = df_res.sort_values(by='cosine', ascending=False)
  df_res = df_res[df_res['cosine'] > cosine_threshold].dropna()

  # limit data
  if df_res.shape[0] > max_stocks:
    df_res = df_res.iloc[:max_stocks, :]

  # find related items
  symbols = df_res['symbol'].values
  res_symbols = list(np.copy(symbols))
  res_rankings = list(np.copy(df_res['cosine'].values))
  for symbol in symbols:
      if len(res_symbols) >= max_stocks: break
      df_row = df_sim.loc[symbol].sort_values(ascending=False)
      df_row = df_row[df_row > sim_threshold]
      for col in df_row.index:
          if isinstance(col, float): continue
          if len(res_symbols) >= max_stocks: break
          res_symbols.append(col)
          res_rankings.append(cosine_threshold - 0.05)

  # combine with relevant profile data
  df_res = pd.DataFrame({'symbol': res_symbols, 'ranking': res_rankings})

  #df_res = pd.merge(df_res, data['profiles'], on='symbol').sort_values(by='ranking', ascending=False)

  st.write("Found {} very relevant and {} relevant stocks for you!".format(len(symbols), len(df_res) - len(symbols)))

  # load relevant stocks
  load_text = st.text("Loading current stock data ...")
  cache = rcmd.stocks.Cache()
  df_stocks = cache.load_stock_data(res_symbols, ticker=ticker, cache=False, load_data=False)
  df_state = cache.load_statement_data(res_symbols, statement, limit=True, cache=False, load_data=False)

  # preprocess input data
  load_text.text("Pre-Processing the data ...")
  df_input = rcmd.learning.preprocess.create_input(df_stocks, df_state, model_back)

  # use model to predict future prices (note: have to ensure the correct order of the input variables)
  load_text.text("Predicting future prices ...")
  df_input_adj = df_input.drop(['symbol', 'norm_price'], axis=1)
  df_pred = model.predict(df_input_adj.to_numpy())
  df_pred = pd.DataFrame(df_pred.argmax(axis=1), columns=['pred'])
  # merge relevant data
  results = pd.concat([df_input.reset_index()['symbol'], df_pred.reset_index()], axis=1)
  results = pd.merge(df_res, results, on='symbol').sort_values(by="ranking", ascending=False)

  # combine all results
  load_text.text("Results:")

  # iterate through enlarged stocks
  for symbol in results.iloc[:max_enlarged]['symbol'].values:
    st.write("**Stock - {}:**".format(symbol))
    res = results[results['symbol'] == symbol]
    st.write('  Score: {} - Prediction: {}'.format(res['ranking'].iloc[0], res['pred'].iloc[0]))
    stock = df_stocks[df_stocks['symbol'] == symbol].reset_index().set_index('date').sort_index(ascending=True)
    st.line_chart(stock['close'])
    # TODO: might show statement data

  # display remaining as dataframe
  if results.shape[0] > max_enlarged:
    st.write("Remaining:")
    st.text(results.iloc[max_enlarged:, :])
