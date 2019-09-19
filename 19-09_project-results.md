# Stock Trend Recommender System

**Keywords**: Recommender-System, Regression, Stock-Prediction

## Motivation

This project contains a stock-recommender system that uses quarterly reports, news information pieces and stock prices to recommend relevant stocks for further (manual) analysis based on user interest (e.g. resources or tech-companies). The system is designed for relevance, novelty and serendipity (with configurable parameters) to allow exploration of potential n-bagger stocks.

The goal of this project was to create a hybrid approach between machine learning and human interaction.
While the system will provide recommendations for stocks to the user, the user still has to make a final decision and analyze the stocks in detail.
This approach is not suited for short term (technical) trading. However, it allows more informed decisions for longer term investments.

Due to timely constraints for this project the overall goal is narrowed down to:

* Retrieve and clean stock data (i.e. stock prices, company statements) from various sources
* Use this stock data to predict the profitability of a stock on multiple time-scales
* Combine both features to compute a similarity between stocks and provide recommendations to the user based on input keywords and stock ranking

## Related Work & Libraries

There are several other projects and libraries that are working on similar goals. Most tasks are focused on stock price prediction.
Those include:

* TODO

## Data Analysis

For the current state of the project, we are using a combination of income, balance-sheet and cash-flow statements for intermediary company information.
As well as actual stock prices and trading volume on a daily opening and closing date resolution. Both data is used to make predictions, while the statements and meta-information about the company (e.g. sector) is used for similarity matching.

This leaves us with the following data sources:

* TODO

### Feature Engineering

In order to retrieve the correct features, we

**Stock Prediction**

* Forward Timestep
* Last n as Input Features
* Last n diffs as Input Features

## ML Pipeline Design

**Stock Prediction**

* Trained as classifier
* Trained as regression

**Recommender**

Since we have no ground-truth data for the similarity between stocks (e.g. a dataset with user-investments), the measuring of the absolute quality of the results is difficult.

## Results

> The results are currently available through a Streamlit Report (in the `notebooks` folder). The web-app is currently not functional, but I am planning on developing it in the near future.

## Future Work

* News Sentiment Mining
* More Complex RNN approaches
* Build an elaborate web-app
