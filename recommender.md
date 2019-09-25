# Recommender Library

The library is constructed to help with data gathering and pre-processing regarding the various sources of stock data. It has the general components:

* contrib - contains helper code, like API access functions
* learning - Preprocessing for models (later on also actual models)
* news - Functions to gather news information related to specific companies
* stocks - Various wrapper classes that allow to access different APIs for access to stock information (`Ticker`) and statement data (`Statements`)
* utils - Various helper functions used throughout the library

> Note: I have planned to extend the library with code for actual model training, but this is currently in future work

We will look at the most relevant parts of the library in detail. All functions also have doc-strings that should be self-explanatory.

## `stocks`

**Main Classes**

* `Statements` - Interface class to interact with API to retrieve company statements (e.g. balance-sheet)
* `Ticker` - Interface class to interact with API to retrieve current and historic stock data
* `Cache` - Helper class to buffer data from APIs (to reduce network load)

### Statements Classes

There are currently two API implementations:

* `FMPStatements` - Uses [Financial Modeling Prep API](https://financialmodelingprep.com/developer/docs/) to retrieve the information. The API is implemented in `contrib.financialmodelingprep`
* `IEXStatements` - Uses [IEX Cloud API](https://iexcloud.io/financial-data/) to retrieve the information - based on external API (found [here](https://github.com/addisonlynch/iexfinance))

> Note that there are some specifics in the init of the different APIs - Each class should have a self-explanatory doc-string

**Functions**

- `balance_sheet` - (abstract) Retrieves the balance statements for a given symbol (features in columns, different times in rows)
- `income` - (abstract) Retrieves the income statements for a given symbol
- `growth` - (abstract) Retrieves the growth statements for a given symbol
- `cash_flow` - (abstract) Retrieves the cash-flow statements for a given symbol
- `get_feature` - Returns a pivot table that contains the values of a single feature for all symbols over time
- `add_quarter` - Extracts the year and quarter from the date column of the statement dataframes
- `merge_records` - Retrieves records from various given stock symbols

**Example**

```python
from datetime import date
state = FMPStatements()
df_balance = state.balance_sheet('AAPL', before=date(2019, 1, 1))
```

### Ticker Class

There are currently two API implementations:

* `AlphaVantageTicker` - Uses [Alpha Vantage API](https://www.alphavantage.co/documentation/) to retrieve information - based on external API (found [here](https://github.com/portfoliome/alphavantage))
* `QuandlTicker` - Uses [Quandl API](https://www.quandl.com/tools/api) to retrieve information - based on external API (found [here](https://github.com/quandl/quandl-python))

> These APIs require accounts and API keys. They can be stored in the key.csv in the root dir (make sure not to commit them and keep them secret!)

**Functions**

- `historic` - (abstract) Retrieves historic prices for a symbol in the given timeframe and resolution (as far as from API supported)
- `price` - (abstract)
- `generator` -
- `price_simple` -

**Example**

```python
ticker = AlphaVantageTicker()
df_price = ticker.historic('AAPL', resolution='15min')
```

### Cache Class

The cache class provides a buffer to avoid unnecessary API load.

**Functions**

* `list_data` - Retrieves all elements in the cache for a given type (as dict with link to files)
* `get_data`
* `load_stock_data`
* `load_statement_data`
* `load_profile_data`

**Example**

```python
# define the cache folder
cache = Cache('./cache/')
# dict of all available stocks in the cache
dc_stocks = cache.list_data()
```

## `news`

**Main Classes**

* `NewsFeed` - Allows to retrieve news from undefined sources

### NewsFeed Class

Implementations:

* `FPNewsFeed` - Uses the [FeedParser](https://github.com/kurtmckee/feedparser) library to retrieve RSS feeds

**Functions**

* `news` - Retrieves the current news - Returns a metadata element and a dataframe with the actual news

**Example**

```python
feed = FPNewsFeed("http://...")
meta, news = feed.news()
```

## `learning`

The learning library is divided into two parts

> Note: only pre-processing is currently implemented

### Preprocessing

Contains a collection of function to use the data from `stocks` and `news` and convert them into a data that can be used by machine learning approaches.

**Stock Functions**

* `normalize_stock_array`
* `normalize_stock_window`
* `create_stock_dataset`
* `categorize_stock_data`

**Statement Functions**

* `normalize_statement_data`

**Merging Functions**

* `merge_stock_statement` - Links generated stock and statement data together (finds the last statements datapoint for each stock datapoint)
* `create_dataset`
* `create_input`

**Other Functions**

* `create_profile_dataset` - Retrieves company profile information using the FMP API directly.
* `extract_nouns` - NLP - Extracts Noun-Phrases from a given text (can be used to identify entities)
