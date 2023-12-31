import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

d_start = "2020-01-01"
d_end = "2022-12-31"

# Download historical stock data
ticker_symbol = "AAPL"  # Change this to the stock symbol you're interested in
stock_data = yf.download(ticker_symbol, start=d_start, end=d_end)

# Feature engineering
stock_data['Year'] = stock_data.index.year
stock_data['Month'] = stock_data.index.month
stock_data['Day'] = stock_data.index.day

# Define features and target variable
features = ['Year', 'Month', 'Day']
target = 'Close'

# Split the data into training and testing sets
train_size = int(len(stock_data) * 0.8)
train, test = stock_data.iloc[:train_size], stock_data.iloc[train_size:]

X_train, X_test = train[features], test[features]
y_train, y_test = train[target], test[target]

# Initialize the XGBoost model
xgb_model = XGBRegressor()

# Fit the model
xgb_model.fit(X_train, y_train)

# Make predictions on the test set
xgb_pred = xgb_model.predict(X_test)

# Calculate Mean Squared Error
mse = mean_squared_error(y_test, xgb_pred)
print(f"Mean Squared Error: {mse}")

# Visualize the predictions
plt.figure(figsize=(12, 6))
plt.plot(test.index, y_test, label='Actual', linewidth=2)
plt.plot(test.index, xgb_pred, label='Predicted', linestyle='dashed', linewidth=2)
plt.title(f'Stock Price Prediction for {ticker_symbol} with XGBoost')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()




############################################# TF ############################################################
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Load stock data
symbol = 'AAPL'
data = yf.download(symbol, start=d_start, end=d_end, progress=False)

# Use closing prices for prediction
df = data[['Close']]

# Normalize data
scaler = MinMaxScaler(feature_range=(0, 1))
df_scaled = scaler.fit_transform(df)

# Create sequences for LSTM
def create_sequences(data, sequence_length):
    X, y = [], []
    for i in range(len(data) - sequence_length):
        seq = data[i:i+sequence_length]
        label = data[i+sequence_length]
        X.append(seq)
        y.append(label)
    return np.array(X), np.array(y)

sequence_length = 10
X, y = create_sequences(df_scaled, sequence_length)

# Split data into training and testing sets
split = int(0.8 * len(X))
X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]

# Build LSTM model
model = Sequential()
model.add(LSTM(units=50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dense(units=1))
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=2)

# Make predictions
y_pred = model.predict(X_test)

# Inverse transform predictions to original scale
y_pred_original = scaler.inverse_transform(np.reshape(y_pred, (-1, 1)))
y_test_original = scaler.inverse_transform(np.reshape(y_test, (-1, 1)))

# Calculate MSE
mse = mean_squared_error(y_test_original, y_pred_original)
print(f"Mean Squared Error: {mse}")

# Visualize predictions vs actual
plt.figure(figsize=(15, 6))
plt.plot(df.index[-len(y_test_original):], y_test_original, label='Actual')
plt.plot(df.index[-len(y_pred_original):], y_pred_original, label='Predicted')
plt.title(f"{symbol} Stock Price Prediction")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.legend()
plt.show()




#### TF 2

import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# Load stock data
symbol = 'AAPL'
data = yf.download(symbol, start=d_start, end=d_end, progress=False)

# Use closing prices for prediction
df = data[['Close']]

# Normalize data
scaler = MinMaxScaler(feature_range=(0, 1))
df_scaled = scaler.fit_transform(df)

# Create features and target variable
X = df_scaled[:-1]  # Use all but the last data point as features
y = df_scaled[1:]   # Shifted by one day to predict the next day

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Build RandomForestRegressor model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)

# Inverse transform predictions to original scale
y_pred_original = scaler.inverse_transform(np.reshape(y_pred, (-1, 1)))
y_test_original = scaler.inverse_transform(np.reshape(y_test, (-1, 1)))

# Calculate MSE
mse = mean_squared_error(y_test_original, y_pred_original)
print(f"Mean Squared Error: {mse}")

# Visualize predictions vs actual
plt.figure(figsize=(15, 6))
plt.plot(df.index[-len(y_test_original):], y_test_original, label='Actual')
plt.plot(df.index[-len(y_pred_original):], y_pred_original, label='Predicted')
plt.title(f"{symbol} Stock Price Prediction")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.legend()
plt.show()



from pytrends.request import TrendReq
import pandas as pd
import time
from datetime import date, timedelta

# Set up the pytrends object
pytrends = TrendReq(hl='en-US', tz=10)

# Define the search term and the time range
search_term = 'covid'
time_range = 'today 12-m'  # Last 365 days
end_date = date.today()
start_date = end_date - timedelta(days=7)
time_range = f'{start_date} {end_date}'

# Get the list of countries you are interested in
countries = ['US', 'Canada']  # Add more countries as needed

# Create an empty DataFrame to store the results
df = pd.DataFrame()

# Loop through each country
for country in countries:
    # Build the payload for the request
    pytrends.build_payload(kw_list=[search_term], cat=0, timeframe=time_range, geo=country)

    # Get interest over time data
    try:
        interest_over_time_df = pytrends.interest_over_time()

        # Add the data to the main DataFrame
        if not interest_over_time_df.empty:
            df = pd.concat([df, interest_over_time_df[search_term]], axis=1)

        # Sleep to avoid rate limiting (required by Google Trends)
        time.sleep(1)

    except Exception as e:
        print(f"Error for {country}: {e}")

# Rename columns to include country names
df.columns = countries

# Print the resulting DataFrame
print(df)


##########


import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
import time

# Set up pytrends object
pytrends = TrendReq(hl='en-US', tz=360)
#pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80',], retries=2, backoff_factor=0.1, requests_args={'verify':False})
# Build payload
kw_list = ["covid"]
#pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='SE')  # 'SE' is the ISO 3166-1 alpha-2 country code for Sweden
pytrends.build_payload(kw_list, cat=0, timeframe='today 1-y', geo='FI')

# 1. Interest over Time
data = pytrends.interest_over_time()
data = data.reset_index()

# Display the chart using Plotly Express
fig = px.line(data, x="date", y=['covid'], title='Keyword Web Search Interest Over Time - Sweden')
fig.show()

# Sleep to avoid rate limiting (required by Google Trends)
time.sleep(1)





import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
import time

# Function to get data with retries and delay
def get_trends_data_with_retry(pytrends, retries=3, delay_seconds=2):
    for _ in range(retries):
        try:
            data = pytrends.interest_over_time()
            return data.reset_index()
        except Exception as e:
            print(f"Error: {e}")
            print("Retrying after a delay...")
            time.sleep(delay_seconds)
    raise Exception("Failed after retries")

# Set up pytrends object
pytrends = TrendReq(hl='en-US', tz=360)

# Build payload
kw_list = ["covid"]
pytrends.build_payload(kw_list, cat=0, timeframe='today 1-y', geo='SE')  # 'SE' is the ISO 3166-1 alpha-2 country code for Sweden

# 1. Interest over Time
data = get_trends_data_with_retry(pytrends)

# Display the chart using Plotly Express
fig = px.line(data, x="date", y=['covid'], title='Keyword Web Search Interest Over Time - Sweden')
fig.show()
