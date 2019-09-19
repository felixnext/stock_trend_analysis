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
