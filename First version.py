print("Big Data Technologies Project 6")

import pandas as pd
import os
from kaggle.api.kaggle_api_extended import KaggleApi
import zipfile

# Ensure the .kaggle directory exists
kaggle_dir = os.path.join(os.path.expanduser('~'), '.kaggle')
os.makedirs(kaggle_dir, exist_ok=True)

# Ensure the kaggle.json file is in the correct location
kaggle_json = os.path.join(kaggle_dir, 'kaggle.json')
if not os.path.exists(kaggle_json):
    raise FileNotFoundError(f"'{kaggle_json}' not found. Place your kaggle.json file in {kaggle_dir}")

# Authenticate using the Kaggle API
api = KaggleApi()
api.authenticate()

# Define the dataset path
dataset_path = 'ieee-fraud-detection'

# Download the dataset files
api.competition_download_files('ieee-fraud-detection', path=dataset_path)

# Unzip the downloaded files
with zipfile.ZipFile(f'{dataset_path}/ieee-fraud-detection.zip', 'r') as zip_ref:
    zip_ref.extractall(dataset_path)

# Load the dataset using pandas

train_transaction = pd.read_csv(f'{dataset_path}/train_transaction.csv')
train_identity = pd.read_csv(f'{dataset_path}/train_identity.csv')
test_transaction = pd.read_csv(f'{dataset_path}/test_transaction.csv')
test_identity = pd.read_csv(f'{dataset_path}/test_identity.csv')

# Display the first few rows of the transaction data
print(train_transaction.head())
print(train_identity.head())
