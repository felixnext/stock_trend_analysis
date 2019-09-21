'''Just a test of the streamlit stuff out of curiosity.

Requires streamlit: pip install -U streamlit
'''

import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd

# define head
st.title("Feature Extraction")

@st.cache
def load_data():
  return pd.read_csv('../data/statements.csv')

data_load_state = st.text('Loading data...')
df = load_data()
data_load_state.text('Loading data... done!')

st.write("Just a simple output example")
st.line_chart(df[df['symbol'] == 'AMZN'].set_index('date')['ebit'].rename('AMZN'))
st.line_chart(df[df['symbol'] == 'AAPL'].set_index('date')['ebit'].rename('AAPL'))

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(df.head(40))

st.write('Extract features from the given data')

st.subheader("Testing Stock Normalization")

import sys
sys.path.insert(1, '..')
import recommender as rcmd

st.write('Load data')
cache = rcmd.stocks.Cache()
ls_stocks = cache.list_data()
sample = np.random.choice(list(ls_stocks.keys()), 30)
st.write("Relevant Stocks: {}".format(sample))

df_stocks = cache.load_stock_data(sample, ls_stocks)

st.write('Loaded Stock data')
st.write('Generate normalization')

df_data = rcmd.learning.preprocess.create_stock_dataset(df_stocks, 7, 30, 3)

st.write('Completed normalization')
