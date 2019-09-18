#!/bin/bash

# NOTE: ensure that you have kaggle installed and key set
kaggle datasets download borismarjanovic/price-volume-data-for-all-us-stocks-etfs -f Data.zip -p ./ --unzip
unzip '*.zip'
