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
Examples include:

* [Towards Data Science](https://towardsdatascience.com/stock-prediction-in-python-b66555171a2)
* [Predition using ML](https://medium.com/@randerson112358/predict-stock-prices-using-python-machine-learning-53aa024da20a)
* [LSTM Predictions](https://www.datacamp.com/community/tutorials/lstm-python-stock-market)

For the implementation of this project I have used various libraries, which are listed in the `readme.md`.

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

Due to time constraints the current state of the project is not the full scope, and there remains a lot left to do.
As mentioned in the motivation, news data could be used to provide a broader context of the company position.
This could be done on a variety of sources (e.g. RSS Feeds, twitter data, news corpora in general (Note: there appears to be a [corpus from HuffPost](https://www.kaggle.com/rmisra/news-category-dataset) with news from 2012 to 2018)).
This would require broader pre-processing pipeline (including NER and mapping news to relevant stock symbols, document embedding) to create a clean training dataset.
Such a dataset could be useful to extract further higher order features (e.g. sentiments) to identify psychological trends in the market.

Another way to improve the system would be the usage of more complex prediction methods (e.g. more advanced RNN approaches) or the use of online learning (e.g. through reinforcement learning) to adjust the trading strategy to the user needs.

From the engineering site, the web-app needs to be updated and the spark process could be streamlined.


## Conclusion

In this project, we have created a basic trading advisor for stock trading. It comprises a two step ML pipeline (prediction, recommendation) to advise potentially relevant stocks to the user.
The results show that the system can perform TODO.
