'''Report for the entire Project.

Run this report with: `streamlit run 09-1_project-report.py`

This should provide an interactive mechanism to query the recommender system.
'''

import streamlit as st
import pandas as pd
import numpy as np

# -- Setup --

st.title("Stock Recommender System")

@st.cache
def load_data():
  '''Load all data and setup the system.'''
  pass

data = load_data()

# -- General Information --

st.subheader("General Information:")

st.write("The system contains a total of {} stock informations.")
# TODO

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

# TODO
