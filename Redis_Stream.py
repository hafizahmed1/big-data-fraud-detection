import pandas as pd
from zipfile import ZipFile
from io import BytesIO
from redis import Redis
import json
from sklearn.ensemble import RandomForestClassifier
from dask_ml.preprocessing import DummyEncoder, StandardScaler
from dask_ml.impute import SimpleImputer
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import joblib

# Define selected columns and their data types
selected_columns = ['TransactionID', 'TransactionDT', 'TransactionAmt', 'ProductCD', 'card1', 'card2',
                    'card3', 'card4', 'card5', 'card6', 'dist1', 'dist2']

# Redis connection
redis_conn = Redis(host='localhost', port=6379, db=0)

# Function to preprocess data
def preprocess_data(df):
    # Handle missing values for numeric columns
    numeric_columns = ['TransactionDT', 'TransactionAmt', 'card1', 'card2', 'card3', 'card5', 'dist1', 'dist2']
    imputer_numeric = SimpleImputer(strategy='mean')
    df[numeric_columns] = imputer_numeric.fit_transform(df[numeric_columns])

    # Handle missing values for categorical columns
    categorical_columns = ['ProductCD', 'card4', 'card6']
    imputer_categorical = SimpleImputer(strategy='most_frequent')
    df[categorical_columns] = imputer_categorical.fit_transform(df[categorical_columns])

    # Convert categorical columns to categorical dtype
    df[categorical_columns] = df[categorical_columns].astype('category')

    # Encode categorical variables
    encoder = DummyEncoder()
    df = encoder.fit_transform(df)

    # Scale numeric features
    scaler = StandardScaler()
    df[numeric_columns] = scaler.fit_transform(df[numeric_columns])

    return df

# Function to process messages from Redis stream
def process_message(message, model):
    try:
        data = json.loads(message['data'])
    except KeyError:
        print(f"Error: 'data' field not found in message: {message}")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON data: {message['data']}")
        return

    # Convert data to DataFrame
    df = pd.DataFrame([data], columns=selected_columns)

    # Preprocess data
    df = preprocess_data(df)

    # Ensure the columns match the model's expected input features
    model_features = ['TransactionDT', 'TransactionAmt', 'card1', 'card2', 'card3', 'card5', 'dist1', 'dist2',
                      'ProductCD_C', 'ProductCD_H', 'ProductCD_R', 'ProductCD_S',
                      'card4_american express', 'card4_discover', 'card4_mastercard',
                      'card6_charge card', 'card6_credit', 'card6_debit or credit']

    # Filter DataFrame columns to match model features
    X = df[model_features]

    try:
        y_pred = model.predict(X)
        print(f"Prediction for message: {y_pred}")
        redis_conn.xadd('predictions', {'isFraud': str(y_pred)})
    except Exception as e:
        print(f"Error predicting: {e}")

# Function to load the model
def load_model(model_path):
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Function to read and stream data from CSV to Redis
def stream_data_to_redis(csv_file_path, model):
    try:
        with ZipFile(csv_file_path, 'r') as zip_file:
            csv_file = zip_file.namelist()[0]
            with zip_file.open(csv_file) as f:
                test_df = pd.read_csv(f, usecols=selected_columns)
                for _, row in test_df.iterrows():
                    json_data = row.to_dict()
                    redis_conn.xadd('test_data', {'data': json.dumps(json_data)})
                    process_message({'data': json.dumps(json_data)}, model)  # Simulate processing each message
    except Exception as e:
        print(f"Error streaming data: {e}")

# Function to create and run the Dashboard
def create_dashboard():
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1("Fraud Detection Dashboard"),
        html.Div(id='live-update-text'),
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Update every 5 seconds
            n_intervals=0
        )
    ])

    @app.callback(
        Output('live-update-text', 'children'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_dashboard(n):
        latest_predictions = redis_conn.xrange('predictions', count=10)  # Get latest predictions from Redis stream
        if not latest_predictions:
            return "No predictions yet..."

        return html.Div([
            html.H2("Latest Predictions"),
            html.Ul([html.Li(f"Prediction: {prediction}") for _, prediction in latest_predictions])
        ])

    app.run_server(debug=True)

if __name__ == "__main__":
    # Paths
    test_dataset_path = r'C:\Big Data Datasets\test_transaction.csv.zip'
    model_path = r'C:\Big Data Datasets\Big Data Project model.pkl'

    # Load model
    model = load_model(model_path)

    # Stream data from CSV to Redis
    stream_data_to_redis(test_dataset_path, model)

    # Create and run Dashboard
    create_dashboard()