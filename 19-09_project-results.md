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

My desired outcome for the project is to have starting point for future experiments that provides data pre-processing and a set of baseline models that can be extended and enriched with additional data sources.

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

* FinancialModelingPrep - Used for Statement data, company information as well as a general overview of available stocks
* Kaggle Dataset - Provides cached stock data, which reduces our load on the APIs
* Alpha-Vantage - Historic and current stock price information

In order to retrieve the correct features, we perform a general analysis of the stock data.

**Stock Prediction**

The goal of the stock prediction system is to use current information:

* Last Statements from a given company
* Recent stock history

To predict the outcome of the stock data (i.e. would an invest in the stock be profitable over time horizon X). This leaves us with the following parameters for the data training:

1. Time Horizon of prediction (How long do we want to look in the future?)
2. Amount of Recent Data (Do we just give the current state of a windows of data from the past X days/month?)
3. Cliping of target values (in which interval is a stock profitable, neutral or unprofitable?)
3. Normalization of the Data (Do we use absolute values of differences?)
4. Smoothing of the Data (Do we take the stock closing price on a single day or of a week?)

The last two questions are probably easiest to answer. Since all stocks have different values (i.e. different start prices of the stock and current statement values) and these values do not have an impact on our prediction (if a \\$10 stock rises to \\$200 this is a much better investment than a \\$1000 stocks rise to \\$1500). We will therefore adopt a normalization that takes the current stock price as a starting point and computes percental difference from there. This will provide a normalized scale across all stocks.

For the smoothing we might use a time windows that is dependent on the length of the prediction (e.g. +/- 3 days for a quarter prediction and +/- 1 Week for a year prediction).

The normalized stock data was computed based on 22 day sliding window applied to the historic stock prices of each available symbol.
To analyze the target distributions, two parameters were modified (distance of days of the target value from the start price and size of the smoothing window).
The distributions can be seen below. The graphs are fixed to a range of 5 to -5 and the bar-charts use a total of 100 bins. As stock data is only recorded for work-days, the length of the window are in work days (with 22 days resulting in a month and 66 days in a quarter).

![Target distribution for 22 days ahead and 3 day smoothing window](./imgs/target-dist_22-3.png)
![Target distribution for 66 days ahead and 3 day smoothing window](./imgs/target-dist_66-3.png)
![Target distribution for 66 days ahead and 5 day smoothing window](./imgs/target-dist_66-5.png)
![Target distribution for 132 days ahead and 5 day smoothing window](./imgs/target-dist_132-5.png)
![Target distribution for 268 days ahead and 10 day smoothing window](./imgs/target-dist_268-10.png)
![Target distribution for 528 days ahead and 10 day smoothing window](./imgs/target-dist_528-10.png)

As one can see, the target values follow a normal distribution with growing variance over the look ahead length (as expected). Smoothing on the other hand appears to have negligible impact on the distributions.

Based on these data, clipping areas for the training data of models prediction for different time horizons can be chosen.
The normal distribution of the data also means an unequal balance of the training data for a classification approach (indicating that we might perform well using gaussian mixture models).

To better understand the prediction power of historic data on future values, the category data was divided into 6 categories (based on the percentage of change from the current day value). Then the correlation of the historic data w.r.t. the categories was calculated.

> The correlation for each day was calculated and averaged. In order to account for non-linear factors we use Spearman correlation.

The following data is an excerpt from the correlations calculated on different datasets (more can be found in the `./imgs/` folder)

![Correlation between Target-Categories with 66 days ahead and 7 days historic data](./imgs/target-dist_corr-7-66.png)
![Correlation between Target-Categories with 132 days ahead and 7 days historic data](./imgs/target-dist_corr-7-132.png)
![Correlation between Target-Categories with 132 days ahead and 14 days historic data](./imgs/target-dist_corr-14-132.png)
![Correlation between Target-Categories with 264 days ahead and 14 days historic data](./imgs/target-dist_corr-14-264.png)
![Correlation between Target-Categories with 528 days ahead and 14 days historic data](./imgs/target-dist_corr-14-528.png)
![Correlation between Target-Categories with 528 days ahead and 21 days historic data](./imgs/target-dist_corr-21-528.png)

> Note that the lower limit is capped before -1 as no stock descents to 0 (except in a bankruptcy, in which case the stock is not traded any more, so there are no datapoints for that case)

> There is also a special case for diagonal values in which case we use the `corr` function to calculate a self-correlation as compared to the `corrwith` function used by remaining items. Both elements will use `spearman-correlation`

The correlation matrixes show multiple things:

* Longer time horizons of historic data slightly improve correlations between similar classes
* Positive stocks seem to be more correlated in historic data
* There is no clear diagonal structure (esp. stocks moving in negative direction have a low self-correlation)

This could be an indicator that stock behavior (esp. over a longer time horizon) randomizes (or at least is not strongly dependent on previous performance). (A common piece of knowledge already advocated by many trading books).

In order to improve the prediction power of the data w.r.t. the target categories, statement information was added to get a better understanding of the underlying fundamentals of a company.
One would expect that this increases the correlation, as it provides information commonly used by big wall street traders (e.g. Benjamin Graham, Warren Buffet or Peter Lynch).
Specifically, the following indicators are used:

* Revenue per Share Growth (for 3, 5 and 10 years)
* Dividend per Share Growth (for 3, 5 and 10 years)
* Research Expenses compared to net-cash position
* Earnings per Share (EPS)
* Dividend per Share
* Price / Earnings Ratio (based on the current stock price)
* Book-Value per Share (even though this can be misleading)
* Research Growth
* Debt Growth
* Net-Cash per outstanding share

All these indicators are relative (except maybe dividends and earnings, which are divided per share). This makes them easier to use in model training (absolute values would have a high variance).

Looking at the correlations (this time the diagonal elements are not calculated in a separate way), we can generally see a lower correlation further away from the diagonal. This might indicate that these features are better suited to predict future stock prices than historic changes alone.

![Correlation between Target-Categories with 132 days ahead and 14 days historic data based on debt growth](./imgs/target-dist_debt-growth-corr-14-132.png)
![Correlation between Target-Categories with 264 days ahead and 7 days historic data based on dividend growth](./imgs/target-dist_dividends-corr-7-264.png)
![Correlation between Target-Categories with 66 days ahead and 7 days historic data based on revenue growth](./imgs/target-dist_revenue-corr-7-66.png)
![Correlation between Target-Categories with 132 days ahead and 7 days historic data based on revenue growth](./imgs/target-dist_revenue-corr-7-132.png)

Since the statement features are (at least partially) independent, the correlations look at them individually and not as an average (as is the case for the historic stock data). We can see that certain features (like revenue, debt and dividends) appear to show better correlations with the data, so they will hopefully improve prediction results.
As before, the data for diagonal items are divided into two distinct sets to calculate the correlation. The 0 values on the diagonal are curious, especially since the variance of the distinct sets is not 0.

**Recommender System**

For the recommender system, we will use data from company profiles to identify the similarity between stocks.
There are a total of 15525 company profiles in the dataset collected for this task. The actual industries and sectors are distributed as follows:

![Distribution of sectors](./imgs/comp-dist_sector.png)
![Distribution of industry](./imgs/comp-dist_industry.png)
![Distribution of exchange](./imgs/comp-dist_exchange.png)

As the distributions show, there is a certain imbalance in the datasets. `Financial Services`, `Healthcare` and `Technology` (among a few others) are clearly over-represented in the data. Those trends re-appear in the industry section in finer granularity, with `Asset Management` by far the largest (followed by `banks` and `biotechnology`).
This might cause a certain bias in the training of the recommender systems.

To get a better understanding of the cross-dependencies between these categorical variables, I performed a correlation test (based on pearson method, as we only have binary data per category):

![Correlation between categories in sector and industry](./imgs/comp-conf_sector-industry.png)
![Correlation between categories in exchange and sector](./imgs/comp-conf_sector-exchange.png)

These correlation show us a certain overlap in some categories between sector and industry (e.g. Communication Services) and also some closely related field (e.g. Biotechnology and Healthcare). This basically explains the mapping between the distributions of sector and industry.
We might want to try to only use one of these categorical variables as input for the system to avoid redundancy (and bias). Another option would be to weight the input features to avoid a double counting in the input features.

The correlation between exchange and sector on the other hand only shows light preferences (e.g. Technology companies correlate weakly with Nasdaq). But overall the categories appear more distinct.


Each company profile also has a description that can be used to detect similarities. To identify relevant clusters, I have extracted the Noun-Phrases from each description and transformed them into a vector set (i.e. Existence Vectorizer). I then performed t-SNE as dimensionality reduction to visualize the data in 2D. The points are colored according to their sector.

Noun Phrase Clustering:

![Clustering on Noun Phrase Vectors with PCA](./imgs/comp-desc_pca-sector.png)
![Clustering on Noun Phrase Vectors with T-SNE](./imgs/comp-desc_tsne-sector.png)

These clusters are pretty much meaningless, especially since we work with binary vectors, which have a statistical tendency to cluster into 4 directions (see PCA image).
To get a better understanding of the semantic information embedded in the descriptions, I used GloVe embeddings and performed the same dimensionality reductions:


![Clustering on Noun Phrase Vectors with PCA](./imgs/comp-desc_pca-glove-sector.png)
![Clustering on Noun Phrase Vectors with T-SNE](./imgs/comp-desc_tsne-glove-sector.png)

The embeddings (esp. the PCA) of the glove vectors show us certain clusters, which seem to correlate with sector information (even though the clusters have a high variance). This leads to the assumption, that these embeddings might provide additional useful information to identify relationships between stocks.

## ML Pipeline Design

### Stock Prediction

In order to know if a stock is relevant for investment we do not want to predict the exact prices, but rather identify if the stock is moving in a certain direction.
Therefore I have split the stocks into categories of movement dependent on the current price (see `Data Analysis` section). Using this data, we can either use a classification approach (i.e. classify each of the movement categories) or use regression.
Since the categories have a semantic distance to each other, we can simply use normalize the target value and perform a regression approach.

**Classification**

Our baseline for the classification approach will be a multi-output logistic regression. The table below shows the remaining models used.
I assume that most of the models require no further explanation for a technical audience (otherwise, please see regarding articles in the [sklearn documentation](https://scikit-learn.org/stable/documentation.html)).
One exception is the neural network architecture used, which is build as a custom network based on keras (i.e. TensorFlow). I trained two types of networks.
A simple network using only four densely connected layers (128, 256, 128, 5) to capture the output as a softmax. And a more complex architecture that uses a stem block (64, 64, 128) as well as Batch-Normalization and Dropouts (to increase generalization). I also used a longer training for this network (200 eps compared to 100). Both networks use the adam optimizer.

> It is also worth noting that the problem is apparently quite non-linear, leading to non-convergence warnings in the Logistic Regression approach.


| **Model** | F1 Score | Precision | Recall |
| --------- | -------- | --------- | ------ |
| Logistic Regression (Baseline) | .27 | .5 | .18 |
| Support Vector Machines | .41 | .54 | .33 |
| Neural Network (Simple) | .48 | .48 | .48 |
| Neural Network (Complex) | .49 | .49 | .49 |

> Note: During experiments I found that standard scaled data also provides benefits for neural network architectures.


Please note that I did not perform GridSearch for any of the models, though that might be part of future work (together with the analysis of additional input features, such as news-sentiments).
Overall we can see that the approaches perform better than random (given 6 classes), with a biases towards class representations in the training data (see regarding notebook output for details).
Nevertheless, the results show a decent prediction power (after all I did not do much optimization here) for the neural network approaches. This is inline with my expectations, as I would assume the data to have non-linear dependencies.

**Regression**

As an added bonus I wanted to test the performance of regression models on the same task, as the output values are categories on a scale, they can also be interpreted as a single regression target. In order to measure the regression performance I used MSE (however, I only tested a linear baseline against a simple neural network).
I only used the data from the last 7 days (without statement data) for the linear regression.

| **Model** | MSE |
| --------- | -------- |
| Logistic Regression (Baseline) | .039 |
| Neural Network | 1.58 |

Interestingly the neural network has a higher regression score. Further analysis is needed to narrow down the reasons and improve this approach.

### Recommender

Since we have no ground-truth data for the similarity between stocks (e.g. a dataset with user-investments), the measuring of the absolute quality of the results is difficult.

The current recommender process uses glove embeddings based on the descriptions in the company profiles to find relevant items and filters them based on a threshold. The found symbols are then used to find similar stocks based on similarity across three categorical features (exchange, sector and industry).

## Results

**Stock Prediction**

From the results of the experiments and subjective test sampling, I decided to use X models (specifically the X model) for the final system, as it provided the best results.

Surprising to me was the poor performance of the complex NN model compared to the simple model. Nevertheless, there is much room for improvement (e.g. LSTMs, Residual Networks) to improve the results further.

The regression approaches showed some promise in that regard

**Recommender**

From subjective testing, we can see that the results from the recommender are roughly aligned with the user-queries in most cases (there are edge cases, where no words in the GloVe dictionary are found and random vectors are used). Up-filling of the results with similarity matches also shows decent results, given that the categorical variables do not necessarily carry much semantics w.r.t. the users information need.

> The results are currently available through a Streamlit Report (in the `notebooks` folder). The web-app is currently not functional, but I am planning on developing it in the near future.

## Future Work

Due to time constraints the current state of the project is not the full scope, and there remains a lot left to do.
As mentioned in the motivation, news data could be used to provide a broader context of the company position.
This could be done on a variety of sources (e.g. RSS Feeds, twitter data, news corpora in general (Note: there appears to be a [corpus from HuffPost](https://www.kaggle.com/rmisra/news-category-dataset) with news from 2012 to 2018)).
This would require broader pre-processing pipeline (including NER and mapping news to relevant stock symbols, document embedding) to create a clean training dataset.
Such a dataset could be useful to extract further higher order features (e.g. sentiments) to identify psychological trends in the market.

Another way to improve the system would be the usage of more complex prediction methods (e.g. more advanced RNN approaches) or the use of online learning (e.g. through reinforcement learning) to adjust the trading strategy to the user needs.
Apart from more complex models, there are also biases in the data that should be addressed (e.g. high number of stocks in middle categories).

The recommender system can also be improved in many ways. Including abstraction on the description to find new categorical information (e.g. NER) to perform a better similarity matching, more elaborate pre-processing of the user-queries to better capture their information need and filtering underperform stocks from the beginning, among many others.

From the engineering site, the web-app needs to be updated and the spark process could be streamlined.


## Conclusion

In this project, we have created a basic trading advisor for stock trading. It comprises a two step ML pipeline (prediction, recommendation) to advise potentially relevant stocks to the user.

As with most machine learning pipelines, a large chunk of the work for this project was distributed to pre-processing of the data. Resulting in a large library of functions that provide a solid entry point for further experiments with stock related information system.

The system presented in this project shows promising results as a first vertical prototype. Especially the data pre-processing lies the foundation for other experiments in the area of stock market exploration for me (and hopefully for others as well).
