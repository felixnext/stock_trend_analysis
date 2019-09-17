# Stock Trend Analysis

This project contains a stock-recommender system that uses quarterly reports, news information pieces and stock prices to recommend relevant stocks for further (manual) analysis based on user interest (e.g. resources or tech-companies). The system is designed for relevance, novelty and serendipity (with configurable parameters) to allow exploration of potential n-bagger stocks.

## Getting Started

The system deploys as a flask web services. The easiest way to run it is through docker (recommended [nvidia docker]() for TensorFlow components):

```bash
$ TODO
```

You might also run the system locally through the command line:

```bash
$ TODO
```

## Architecture

The goal of the system should be:

* TODO

### General Design

You can find the data analysis and test of single algorithms in the jupyter notebooks (`notebooks` folder). Based on the results, I have created the actual Machine Learning Pipeline as a separate package in the `recommender` folder. This in turn is used by the `frontend` to be integrated into a flask webapp.

**Recommender**

The recommender consists of the following parts: TODO

### Data Sources

**Stock Data**

* Alpha Vantage Data (through [alpha-vantage](https://github.com/RomelTorres/alpha_vantage)) - Allows to retrieve daily stock data
* Quandl Data (through [quandl](https://github.com/quandl/quandl-python))

**Quarterly Reports**

TODO

**News Ticker**

* Twitter Data
* RSS Feeds - This allows us to basically read in any news source (using [feedparser](https://github.com/kurtmckee/feedparser))

Sources of RSS Data:

* Google Alerts - Allow to create a RSS reader based on any topic (using [python library](https://github.com/9b/google-alerts))

### Data Insights

TODO

### ML Pipeline Design

TODO

## Dependencies

I am using the following packages for the system:

* Apache Spark
* [sklearn-recommender](https://github.com/felixnext/sklearn-recommender) (*note: written for this project, but decoupled into a separate repository*)
* DS Python Toolstack (Pandas, Numpy, Sklearn, etc.)
* TensorFlow

## Future Work

TODO

## License

The code is published under MIT License.
