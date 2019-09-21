
import numpy as np
import pandas as pd
import sys
sys.path.insert(1, '..')
import recommender as rcmd

cache = rcmd.stocks.Cache()
ls_stocks = cache.list_data()
sample = np.random.choice(list(ls_stocks.keys()), 30)

df_stocks = cache.load_stock_data(sample, ls_stocks)


print("norm now")

df_data = rcmd.learning.preprocess.create_stock_dataset(df_stocks, 7, 30, 3)

print('done')
print(df_data)
