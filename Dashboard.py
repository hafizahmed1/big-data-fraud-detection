import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.figure_factory as ff

# Example Data
np.random.seed(42)
data = {
    'TransactionID': range(1, 101),
    'TransactionDT': np.random.randint(1, 1000, size=100),
    'TransactionAmt': np.random.lognormal(mean=3, sigma=1, size=100),
    'ProductCD': np.random.choice(['A', 'B', 'C', 'D'], size=100),
    'card1': np.random.randint(1000, 2000, size=100),
    'card2': np.random.randint(2000, 3000, size=100),
    'card3': np.random.randint(100, 200, size=100),
    'card4': np.random.choice(['visa', 'mastercard', 'amex'], size=100),
    'card5': np.random.randint(300, 400, size=100),
    'card6': np.random.choice(['debit', 'credit'], size=100),
    'dist1': np.random.randint(1, 100, size=100),
    'dist2': np.random.randint(50, 150, size=100),
    'isFraud': np.random.choice([0, 1], size=100, p=[0.95, 0.05])
}
df = pd.DataFrame(data)

# Aggregated Data for Statistics
total_transactions = len(df)
total_fraud = df['isFraud'].sum()
total_non_fraud = total_transactions - total_fraud
fraud_percentage = (total_fraud / total_transactions) * 100

# Initialize the Dash App
app = dash.Dash(__name__)

# Dashboard Layout
app.layout = html.Div([
    html.H1('Fraud Detection Dashboard'),

    # Total Statistics
    html.Div([
        html.Div([
            html.H3('Total Transactions'),
            html.P(f'{total_transactions}')
        ], style={'width': '24%', 'display': 'inline-block'}),

        html.Div([
            html.H3('Total Fraud Transactions'),
            html.P(f'{total_fraud}')
        ], style={'width': '24%', 'display': 'inline-block'}),

        html.Div([
            html.H3('Total Non-Fraud Transactions'),
            html.P(f'{total_non_fraud}')
        ], style={'width': '24%', 'display': 'inline-block'}),

        html.Div([
            html.H3('Fraud Percentage'),
            html.P(f'{fraud_percentage:.2f}%')
        ], style={'width': '24%', 'display': 'inline-block'})
    ]),

    # Transaction Amounts Graph
    dcc.Graph(
        id='transaction-amounts',
        figure=px.histogram(df, x='TransactionAmt', color='isFraud', barmode='overlay',
                            title='Transaction Amounts Distribution',
                            labels={'TransactionAmt': 'Transaction Amount', 'isFraud': 'Fraud'},
                            nbins=50)
    ),

    # Dropdown Menu to Filter Transactions by Fraud/Non-Fraud
    html.Label('Filter by Fraud Status'),
    dcc.Dropdown(
        id='fraud-filter',
        options=[
            {'label': 'All Transactions', 'value': 'all'},
            {'label': 'Fraud Transactions', 'value': 'fraud'},
            {'label': 'Non-Fraud Transactions', 'value': 'non-fraud'}
        ],
        value='all',
        clearable=False
    ),

    # Transaction Table
    html.Div(id='transaction-table'),

    # Correlation Matrix
    dcc.Graph(
        id='correlation-matrix',
        config={'displayModeBar': False}
    )
])

# Callback to update table based on dropdown
@app.callback(
    Output('transaction-table', 'children'),
    [Input('fraud-filter', 'value')]
)
def update_table(filter_value):
    if filter_value == 'fraud':
        filtered_df = df[df['isFraud'] == 1]
    elif filter_value == 'non-fraud':
        filtered_df = df[df['isFraud'] == 0]
    else:
        filtered_df = df

    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in filtered_df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns
            ]) for i in range(len(filtered_df))
        ])
    ])

# Callback to update correlation matrix
@app.callback(
    Output('correlation-matrix', 'figure'),
    [Input('fraud-filter', 'value')]
)
def update_correlation_matrix(filter_value):
    if filter_value == 'fraud':
        filtered_df = df[df['isFraud'] == 1]
    elif filter_value == 'non-fraud':
        filtered_df = df[df['isFraud'] == 0]
    else:
        filtered_df = df

    numeric_cols = filtered_df.select_dtypes(include=np.number).columns
    correlation_matrix = filtered_df[numeric_cols].corr()

    fig = ff.create_annotated_heatmap(
        z=correlation_matrix.values,
        x=list(correlation_matrix.columns),
        y=list(correlation_matrix.index),
        colorscale='Viridis'
    )

    fig.update_layout(
        title='Correlation Matrix of Numerical Features',
        xaxis_title='Features',
        yaxis_title='Features'
    )

    return fig

# Starts Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
