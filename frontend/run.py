import json
import plotly
import pandas as pd

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar, Scatter
from sklearn.externals import joblib
from sqlalchemy import create_engine

# Load custom functions from the model folder
import sys
sys.path.insert(1, '../models')
import glove
import ml_helper as utils


app = Flask(__name__)

# load data
#engine = create_engine('sqlite:///../data/disaster_data.db')
#df = pd.read_sql_table('texts', engine)
# TODO: use recommender lib to load relevant stock data

# TODO: integrate user accounts?

# load model
#model = joblib.load("../models/pipeline.pkl")
# TODO: load spark pipeline

# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():

    # extract data needed for visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    categories = df.iloc[:, 4:].sum(axis=0)
    category_counts = categories.values
    category_names = categories.index.tolist()
    message_length = df['message'].apply(lambda x: len(x)).values
    message_cats = df.iloc[:, 4:].sum(axis=1).values

    # create visuals
    graphs = [
        {
            'data': [
                Bar(
                    x=genre_names,
                    y=genre_counts,
                )
            ],

            'layout': {
                'title': 'Distribution of Message Genres',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Genre"
                }
            }
        },
        {
            'data': [
                Bar(
                    x=category_names,
                    y=category_counts
                )
            ],

            'layout': {
                'title': 'Distribution of Message Categories',
                'yaxis': {
                    'title': "Count"
                },
                'xaxis': {
                    'title': "Category"
                }
            }
        },
        {
            'data': [{
              'type': 'scatter',
              'x': message_length,
              'y': message_cats,
              'mode': 'markers'
            }],

            'layout': {
                'title': 'Message Length vs Number of Categories',
                'yaxis': {
                    'title': "# Categories"
                },
                'xaxis': {
                    'title': "Message Length (in chars) [log-scale]",
                    'type': 'log'
                }
            }
        }
    ]

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# web page that handles user query and displays model results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '')

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html Please see that file.
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()
