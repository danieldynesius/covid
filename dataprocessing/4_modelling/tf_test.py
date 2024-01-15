import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot as plt


use_prenormalized = False # works better on True currently

datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'

#pd.read_csv('/home/stratega/code/analytics/covid/data/metadata/country_stats.csv', encoding='utf-8', on_bad_lines='skip')


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

# NEED TO CREATE A CONTINENT VARIABLE SOMEWHERE
# Iterate over unique countries
for country in df['cntr_nm'].unique():
    # Filter data for the current country
    country_data = df[df['cntr_nm'] == country]
    
    # Iterate over unique regions within the current country
    for region in country_data['region'].unique():
        region_data = country_data[country_data['region'] == region]
        plt.plot(region_data['first_day'], region_data['normalized_value'], label=region)

    # Set labels and title
    plt.xlabel('Date')
    plt.ylabel('Normalized Value')
    plt.title(f'Normalized Values by Region in {country}')
    plt.legend()
    plt.show()


#df['normalized_value'] = df['normalized_value'].fillna(df['normalized_value'].mean())

# USE NORMALIZED VALUE
if use_prenormalized==True:
    print('Using Pre-Normalized')
    df['normalized_value'] = df['normalized_value'].fillna(df.groupby(['cntr_nm', 'region'])['normalized_value'].transform('mean'))

else:
    print('Creating Normalized')
    # Fill NaN values in the 'value' column with the mean of each group
    df['value'] = df['value'].fillna(df.groupby(['cntr_nm', 'region'])['value'].transform('mean'))

    # Normalize the 'value' column based on groups
    scaler_value = MinMaxScaler()
    df['normalized_value'] = df.groupby(['cntr_nm', 'region'])['value'].transform(lambda x: scaler_value.fit_transform(x.values.reshape(-1, 1)).flatten())

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
#data = df[['first_day', 'normalized_value', 'cntr_int', 'region_int']]



# Define sequence length (number of time steps to consider)
sequence_length = 4 # nr of steps for firt_day (weekly values)
my_predictor_list = ['cntr_int', 'region_int','week','day', 'normalized_value']
my_predictor_len = len(my_predictor_list)

# Function to create sequences for training
def create_sequences(data, sequence_length):
    sequences = []
    targets = []
    
    for i in range(len(data) - sequence_length):
        seq = data.iloc[i:i+sequence_length]
        target = data.iloc[i+sequence_length]['normalized_value']
        # Only include relevant features for training
        sequences.append(seq[my_predictor_list].values)
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
    tf.keras.layers.LSTM(50, input_shape=(sequence_length, my_predictor_len)),
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

# Fit the scaler on the training data
scaler.fit(train_targets.reshape(-1, 1))

# Denormalize the predictions
denormalized_predictions = scaler.inverse_transform(predictions.reshape(-1, 1))

# Plotting predictions vs actual with offset
plt.plot(denormalized_predictions, label='Predictions', linestyle='--', alpha=0.7)
plt.plot(test_targets, label='Actual (Offset)', linestyle='--', alpha=0.2)
plt.legend()
plt.show()


# Denormalize the predictions
denormalized_predictions = scaler.inverse_transform(predictions.reshape(-1, 1))

# Invert normalization on test_targets
denormalized_actuals = scaler.inverse_transform(test_targets.reshape(-1, 1))

# Create a DataFrame with denormalized predictions, country, region, and first_day
predictions_df = pd.DataFrame({
    'Denormalized_Predictions': denormalized_predictions.flatten(),
    'Denormalized_Actuals': denormalized_actuals.flatten(),
    'Country': df.iloc[split+sequence_length:]['cntr_nm'].values,
    'Region': df.iloc[split+sequence_length:]['region'].values,
    'First_Day': df.iloc[split+sequence_length:]['first_day'].values
})

# Merge the predictions DataFrame with the original DataFrame
merged_df = pd.merge(df, predictions_df, left_on=['cntr_nm', 'region', 'first_day'], right_on=['Country', 'Region', 'First_Day'], how='left')

# Print or use merged_df as needed
merged_df



# CHECK RMSE
# Predictions on the test set
predictions = model.predict(test_sequences)

# Calculate RMSE on the normalized predictions and normalized actuals
rmse = np.sqrt(mean_squared_error(test_targets, predictions))

print(f'RMSE on Normalized Predictions vs Normalized Actuals: {rmse}')
