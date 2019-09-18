# Stock Trend Analysis

This project contains a stock-recommender system that uses quarterly reports, news information pieces and stock prices to recommend relevant stocks for further (manual) analysis based on user interest (e.g. resources or tech-companies). The system is designed for relevance, novelty and serendipity (with configurable parameters) to allow exploration of potential n-bagger stocks.

## Getting Started

**1. Data Access:**


First you will need to create a `keys.csv` file in the root directory that contains the API keys for the various serivces used. You can find the available keys in the `keys.tmp.csv` template.


**2. Training:**


Next we need to train the machine learning models. TODO


**3. Deploy:**


The system deploys as a flask web services. The easiest way to run it is through docker (recommended [nvidia docker](https://github.com/NVIDIA/nvidia-docker) for TensorFlow components):

```bash
$ docker build -t felixnext/stocks .
$ docker run -d -p 8000:3001 --name stocks -v <PATH>:/storage felixnext/stocks
```

The service should now be available under `http://localhost:8000/`

You might also run the system locally through the command line:

```bash
$ cd frontend
$ python run.py
```

The service should now be available under `http://localhost:3001/`

## Architecture

The goal of the system should be to provide recommendations of stocks for a specific user. Therefore the system should leverage the following information:

* User Interest - Which economic field the user wants to invest in (KB Filtering)
* Specific Stocks - Which stocks liked the user
* Stock Forecast - Using various sources of information (including news, balance sheet statements and historic stock prices among others) to create a ranking for stocks to suggest potentially profitable stocks to the user

### General Design

You can find the data analysis and test of single algorithms in the jupyter notebooks (`notebooks` folder).
Based on the results, I have created the actual Machine Learning Pipeline as a separate package in the `recommender` folder.
This in turn is used by the `frontend` to be integrated into a flask webapp.

**Recommender**

The recommender consists of the following parts:

1. ETL Pipeline - This pipeline uses various APIs (e.g. RSS Feeds, Stock APIs) to gather relevant information and create a list of available stocks with categories to recommend
2. Higher Order Features - Machine learning pipeline that uses various approaches to generate higher-order features based on the data coming from ETL (e.g. a rating for stock profitability)
3. User Recommendation - A recommendation system that compares user interest to relevant stocks and computes the higher-order features for these stocks to generate a basic understanding of the data

All pipelines are implemented into a Spark Process, allowing them to easily scale out.

**Frontend**

The frontend consists of a simple flask web-app that has access to the spark pipeline. From there it can retrieve information and render general stock information to the user.

### Data Sources

The system uses various sources of data. However, as financial apis appear incomplete and volatile, the system pacakges each of these API behind an abstraction interface, that will make it easier to change or add new APIs down the road.

**Stock Data**

* Alpha Vantage Data (through [alpha-vantage](https://github.com/RomelTorres/alpha_vantage)) - Allows to retrieve daily stock data (including long range historic data). It also allows to retrieve intra-day data (in 15min intervals)
* Quandl Data (through [quandl](https://github.com/quandl/quandl-python)) - Allows to retrieve intraday trading data (however does not have long term historic data in free plans)

*Training Data*

* For training an additional [stock market dataset](https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs) is used to account for historic data

> Note: There is a download script to retrieve the data in `data` folder. Before you run it, make sure you have the [kaggle-cli](https://github.com/Kaggle/kaggle-api) installed and setup


**Quarterly Reports**

* IEX Cloud (using [iexfinance](https://github.com/addisonlynch/iexfinance))
* Financial Modeling Prep (using the [API](https://financialmodelingprep.com/developer/docs/) directly)

**News Ticker**

* Twitter Data - (using [tweepy](https://github.com/tweepy/tweepy))
* RSS Feeds - This allows us to basically read in any news source (using [feedparser](https://github.com/kurtmckee/feedparser))

*Sources of RSS Data:*

* Google Alerts - Allow to create a RSS reader based on any topic (using [python library](https://github.com/9b/google-alerts))
* Financial Times [RSS Feed](https://www.ft.com/business-education?format=rss)
* CNN Money [RSS Feed](http://rss.cnn.com/rss/money_latest.rss)

**Economic Data**

* World Bank - (using [wbdata](https://github.com/oliversherouse/wbdata))

### Data Insights

TODO

### ML Pipeline Design

TODO

## Dependencies

I am using the following packages for the system:

* Apache Spark
* [sklearn-recommender](https://github.com/felixnext/sklearn-recommender) (*note: written for this project, but decoupled into a separate repository*)
* DS Python Toolstack (Pandas, Numpy, Sklearn, Plotly, Seaborn, sqlalchemy, etc.)
* TensorFlow

## Future Work

* Create Recommenders for different time frames
* Integrate multiple higher order features
* Create additional higher order features (e.g. RNN predictions)
* Integrate Rule Based approaches (e.g. implement Ben Graham Strategies)
* Implement better error handling for `financialmodelingprep`

## License

The code is published under MIT License.
