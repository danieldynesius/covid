import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler



datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'



d1 = pd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))
d2 = pd.read_parquet(os.path.join(datapath, 'sweden_wastewater.parquet'))
d3 = pd.read_parquet(os.path.join(datapath, 'netherlands_wastewater.parquet')) 
d4 = pd.read_parquet(os.path.join(datapath, 'denmark_wastewater.parquet')) #fail 1 makes html huge
d5 = pd.read_parquet(os.path.join(datapath, 'austria_wastewater.parquet'))
d6 = pd.read_parquet(os.path.join(datapath, 'poland_wastewater.parquet')) # this is just Poznan County. Normaized Value must be
d7 = pd.read_parquet(os.path.join(datapath, 'finland_wastewater.parquet'))
d8 = pd.read_parquet(os.path.join(datapath, 'switzerland_wastewater.parquet'))
d9 = pd.read_parquet(os.path.join(datapath, 'canada_wastewater.parquet'))
d10 =pd.read_parquet(os.path.join(datapath, 'usa_wastewater.parquet'))

# Concatenate DataFrames
df = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10], ignore_index=True))
df = df[['first_day', 'region', 'cntr_code', 'cntr_nm','value', 'normalized_value', 'metric_nm']]
df['normalized_value'] = df['normalized_value'].fillna(df['normalized_value'].mean())

# Assuming df is your DataFrame with 'normalized_value', 'cntr_nm', and 'region' columns
# Adjust this based on your actual DataFrame structure

# Assuming df has a datetime column 'first_day' - replace it with your actual datetime column
df['first_day'] = pd.to_datetime(df['first_day'])

# Sort the DataFrame by date
df = df.sort_values(by='first_day')

# Extract unique countries and regions
unique_countries = df['cntr_nm'].unique()
unique_regions = df['region'].unique()

# Create dictionaries to map countries and regions to integers
country_to_int = {country: i for i, country in enumerate(unique_countries)}
region_to_int = {region: i for i, region in enumerate(unique_regions)}

# Map countries and regions to integers in the DataFrame
df['cntr_int'] = df['cntr_nm'].map(country_to_int)
df['region_int'] = df['region'].map(region_to_int)

# Select relevant columns
data = df[['first_day', 'normalized_value', 'cntr_int', 'region_int']]

# Example: Fill NaN values with the mean of the column
data['normalized_value'] = data['normalized_value'].fillna(data['normalized_value'].mean())


# Normalize the 'normalized_value' column
scaler = MinMaxScaler()
data['normalized_value'] = scaler.fit_transform(data[['normalized_value']])

# Define sequence length (number of time steps to consider)
sequence_length = 7

# Function to create sequences for training
def create_sequences(data, sequence_length):
    sequences = []
    targets = []
    
    for i in range(len(data) - sequence_length):
        seq = data.iloc[i:i+sequence_length]
        target = data.iloc[i+sequence_length]['normalized_value']
        sequences.append(seq[['cntr_int', 'region_int', 'normalized_value', 'year', 'month', 'week', 'day']].values)
        targets.append(target)
    
    return np.array(sequences), np.array(targets)

# Create sequences and targets
sequences, targets = create_sequences(data, sequence_length)

# Split the data into training and testing sets
split = int(0.8 * len(sequences))
train_sequences, test_sequences = sequences[:split], sequences[split:]
train_targets, test_targets = targets[:split], targets[split:]

# Build the LSTM model
model = tf.keras.Sequential([
    tf.keras.layers.LSTM(50, input_shape=(sequence_length, 3)),
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(train_sequences, train_targets, epochs=10, batch_size=32, validation_split=0.1)

# Evaluate the model on the test set
loss = model.evaluate(test_sequences, test_targets)
print(f'Test Loss: {loss}')

# Predictions on the test set
predictions = model.predict(test_sequences)

# Denormalize the predictions
denormalized_predictions = scaler.inverse_transform(predictions.reshape(-1, 1))


# Plotting predictions vs actual with offset
plt.plot(denormalized_predictions, label='Predictions', linestyle='--', alpha=0.7)  # Solid line with circle markers for predictions
plt.plot(test_targets, label='Actual (Offset)', linestyle='--', alpha=0.2)  # Solid line with 'x' markers for offset actual values
plt.legend()
plt.show()



from sklearn.metrics import mean_squared_error
import numpy as np

# Inverse transform to get original scale
predictions_original = denormalized_predictions
y_test_original = scaler.inverse_transform(test_targets.reshape(-1, 1))

# Reshape y_test_original to match the shape of predictions_original
y_test_original = np.repeat(y_test_original, predictions_original.shape[1], axis=-1)

# Compute RMSE
rmse = np.sqrt(mean_squared_error(y_test_original, predictions_original))
print(f'Root Mean Squared Error (RMSE): {rmse}')



## T2


import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers import Adam


# Assuming df is your DataFrame with 'normalized_value' column
# Replace this with your actual data loading and preprocessing steps
# Ensure df is sorted by date if it's a time series data
# ...


# Feature scaling
scaler = MinMaxScaler(feature_range=(0, 1))

df['normalized_value'] = scaler.fit_transform(df[['normalized_value']])

# Creating sequences for LSTM
def create_sequences(data, sequence_length):
    sequences, labels = [], []
    for i in range(len(data) - sequence_length):
        seq = data[i:i+sequence_length]
        label = data[i+sequence_length]
        sequences.append(seq)
        labels.append(label)
    return np.array(sequences), np.array(labels)

# Sequence length (you can adjust this)
sequence_length = 10

# Creating sequences and labels
X, y = create_sequences(df['normalized_value'].values, sequence_length)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

# Model architecture
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(units=50, return_sequences=True))
model.add(LSTM(units=50))
model.add(Dense(units=1))

# You can experiment with different values for the following hyperparameters
model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')


# Train the model for more epochs
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), shuffle=False)

# Training the model
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test), shuffle=False)


# Predictions
predictions = model.predict(X_test)

# Inverse transform to get original scale
predictions_original = scaler.inverse_transform(predictions)
y_test_original = scaler.inverse_transform(y_test.reshape(-1, 1))




# Plotting predictions vs actual with offset
plt.plot(predictions_original, label='Predictions', linestyle='--', alpha=0.8)  # Solid line with circle markers for predictions
plt.plot(y_test_shifted, label='Actual (Offset)', linestyle='--', alpha=0.2)  # Solid line with 'x' markers for offset actual values
plt.legend()
plt.show()


## DD TEST
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go
def make_region_subplots(df, value):
    unique_areas = list(df.region.unique())

    plot_titles = list((df.cntr_code.str.upper() +' - '+ df.region.str.title()).unique())


    n_unique_areas = len(unique_areas)
    n_cols_for_output = 4 # user specified
    n_rows_for_output = math.ceil(n_unique_areas/n_cols_for_output) # needed based on n areas in data

    df = df[['first_day', 'region', 'cntr_code', 'value', 'normalized_value']]

    fig = make_subplots(
        rows=n_rows_for_output, cols=n_cols_for_output,
        y_title='Covid Transmission Value',
        subplot_titles=plot_titles
    )

    for i, area in enumerate(unique_areas, start=1):
        print(i,'....' ,area)
        area_lowercase = area.lower()

        row_num = (i - 1) // n_cols_for_output + 1
        col_num = (i - 1) % n_cols_for_output + 1
        print('Current area:', area, 'RC:',row_num, col_num)
        area_x_series = df[df['region'].str.lower() == area_lowercase].first_day
        area_y_series = df[df['region'].str.lower() == area_lowercase].normalized_value

        area_x_series_last365 = df[(df['region'].str.lower() == area_lowercase) ].first_day
        area_y_series_last365 = df[(df['region'].str.lower() == area_lowercase) ].normalized_value

        fig.add_trace(
            go.Scatter(
                x=area_x_series
                ,y=area_y_series
                #,y=test_list
                ,mode='lines+markers'
                ,connectgaps=True
                ,showlegend=False
            ),
            row=row_num, col=col_num
        )

    fig.update_layout(
        height=300 + (50*n_unique_areas), width=300*n_cols_for_output,  # Adjust width to accommodate all subplots
        title_text="Covid-19 Wastewater Measurements"
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='black', size=14))

    return fig


make_region_subplots(df=df, value=df.normalized_value)


## T3
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers import Adam

# Assuming df is your DataFrame with 'normalized_value', 'cntr_nm', and other columns
# Replace this with your actual data loading and preprocessing steps
# Ensure df is sorted by date if it's a time series data
# ...

# Feature scaling for normalized_value
scaler = MinMaxScaler(feature_range=(0, 1))
df['normalized_value'] = scaler.fit_transform(df[['normalized_value']])

# One-hot encoding for cntr_nm
encoder = OneHotEncoder(sparse=False)
df_encoded = pd.get_dummies(df, columns=['cntr_nm'], prefix='country')

# Creating sequences for LSTM
def create_sequences(data, sequence_length):
    sequences, labels = [], []
    for i in range(len(data) - sequence_length):
        seq = data[i:i+sequence_length]
        label = data[i+sequence_length]
        sequences.append(seq)
        labels.append(label)
    return np.array(sequences), np.array(labels)

# Sequence length (you can adjust this)
sequence_length = 10

# One-hot encoding for country_nm
encoder = OneHotEncoder(sparse=False)
df_encoded = pd.get_dummies(df, columns=['cntr_nm'], prefix='country')

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)


# Model architecture
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(units=50, return_sequences=True))
model.add(LSTM(units=50))


# You can experiment with different values for the following hyperparameters
model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

# Train the model for more epochs
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), shuffle=False)

# Predictions
predictions = model.predict(X_test)

# Inverse transform to get original scale
predictions_original = scaler.inverse_transform(predictions)
y_test_original = scaler.inverse_transform(y_test.reshape(-1, 1))

# Plotting predictions vs actual
plt.plot(predictions_original, label='Predictions')
plt.plot(y_test_original, label='Actual')
plt.legend()
plt.show()


# Plotting predictions vs actual with offset
plt.plot(predictions_original, label='Predictions', linestyle='--', alpha=0.8)  # Solid line with circle markers for predictions
plt.plot(y_test_original, label='Actual (Offset)', linestyle='--', alpha=0.2)  # Solid line with 'x' markers for offset actual values
plt.legend()
plt.show()

from sklearn.metrics import mean_squared_error
import numpy as np

# Inverse transform to get original scale
predictions_original = scaler.inverse_transform(predictions)
y_test_original = scaler.inverse_transform(y_test.reshape(-1, 1))

# Reshape y_test_original to match the shape of predictions_original
y_test_original = np.repeat(y_test_original, predictions_original.shape[1], axis=-1)

# Compute RMSE
rmse = np.sqrt(mean_squared_error(y_test_original, predictions_original))
print(f'Root Mean Squared Error (RMSE): {rmse}')

