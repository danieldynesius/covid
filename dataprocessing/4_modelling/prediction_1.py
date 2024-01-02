import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as offline
import math
from plotly.subplots import make_subplots
import numpy as np
import os


datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'




df = pd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))
df = pd.read_parquet(os.path.join(datapath, 'sweden_wastewater.parquet'))
d3 = pd.read_parquet(os.path.join(datapath, 'netherlands_wastewater.parquet')) 
d4 = pd.read_parquet(os.path.join(datapath, 'denmark_wastewater.parquet')) #fail 1 makes html huge
d5 = pd.read_parquet(os.path.join(datapath, 'austria_wastewater.parquet'))
d6 = pd.read_parquet(os.path.join(datapath, 'poland_wastewater.parquet')) # this is just Poznan County. Normaized Value must be
d7 = pd.read_parquet(os.path.join(datapath, 'finland_wastewater.parquet'))
d8 = pd.read_parquet(os.path.join(datapath, 'switzerland_wastewater.parquet'))
d9 = pd.read_parquet(os.path.join(datapath, 'canada_wastewater.parquet'))
d10 =pd.read_parquet(os.path.join(datapath, 'usa_wastewater.parquet'))

# Concatenate DataFrames
#df = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10], ignore_index=True))
df = df[['first_day', 'region', 'cntr_code', 'cntr_nm','value', 'normalized_value', 'metric_nm']]

df.groupby('cntr_code')['region'].agg('nunique')




#import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
df = pd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))
# Load stock data
symbol = 'AAPL'
#data = yf.download(symbol, start=d_start, end=d_end, progress=False)

# Use closing prices for prediction
df = df[['value']]

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
rf_model.fit(X_train, y_train.ravel())

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
plt.title(f"{symbol} WW test Prediction")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.legend()
plt.show()


## t2


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
#data = yf.download(symbol, start=d_start, end=d_end, progress=False)
df = pd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))

# Use closing prices for prediction
df = df[['value']]

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
#### t3


from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
df = pd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))
# Assuming X_train and y_train are your training data
param_grid = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_model = RandomForestRegressor()

# Use RandomizedSearchCV for hyperparameter tuning
rf_random = RandomizedSearchCV(estimator=rf_model, param_distributions=param_grid, n_iter=100, cv=3, random_state=42, n_jobs=-1)
rf_random.fit(X_train, y_train)

# Best parameters
print("Best Parameters for RandomForestRegressor: ", rf_random.best_params_)


from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import RandomizedSearchCV

# Assuming X_train and y_train are your training data

# Function to create LSTM model
def create_lstm_model(units=50, dropout_rate=0.2, learning_rate=0.001):
    model = Sequential()
    model.add(LSTM(units=units, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

# Define parameters for hyperparameter tuning
param_dist = {
    'units': [50, 100, 150],
    'dropout_rate': [0.2, 0.3, 0.4],
    'learning_rate': [0.001, 0.01, 0.1]
}

lstm_model = KerasRegressor(build_fn=create_lstm_model, epochs=10, batch_size=32, verbose=0)

# Use RandomizedSearchCV for hyperparameter tuning
lstm_random = RandomizedSearchCV(estimator=lstm_model, param_distributions=param_dist, n_iter=10, cv=3, n_jobs=-1)
lstm_random.fit(X_train, y_train)

# Best parameters
print("Best Parameters for LSTM: ", lstm_random.best_params_)





# Assuming df has columns 'first_day' and 'value'
plt.figure(figsize=(10, 6))
plt.plot(df['first_day'], df['value'], label='Value', color='blue')
plt.title('Line Graph of Value Over Time')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.show()

































#### GPT TEST #########################################

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
