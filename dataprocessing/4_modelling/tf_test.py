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

# Extract additional temporal features from 'first_day'
df['year'] = df['first_day'].dt.year
df['month'] = df['first_day'].dt.month
df['week'] = df['first_day'].dt.isocalendar().week
df['day'] = df['first_day'].dt.day

# Normalize the new temporal features
scaler_temporal = MinMaxScaler()
df[['year', 'month', 'week', 'day']] = scaler_temporal.fit_transform(df[['year', 'month', 'week', 'day']])

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
        # Only include relevant features for training
        sequences.append(seq[['cntr_int', 'region_int', 'normalized_value']].values)
        targets.append(target)
    
    return np.array(sequences), np.array(targets)

# Create sequences and targets
sequences, targets = create_sequences(df, sequence_length)



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

