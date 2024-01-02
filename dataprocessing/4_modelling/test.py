from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

import seaborn as sns

# Add all datapaths to an env-file?
datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'

df = pd.read_parquet(os.path.join(datapath, 'sweden_wastewater.parquet'))



df.value

df




# Get unique regions in the DataFrame
unique_regions = df['region'].unique()

# Create a separate histogram for each region
for region in unique_regions:
    plt.hist(df[df['region'] == region]['value'], bins='auto', alpha=0.7, label=region)

plt.title('Histogram of Time Series Data by Region')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.legend()
plt.show()




# Assuming df is your DataFrame with columns 'region' and 'value'

# KDE Plot
sns.kdeplot(data=df, x='value', hue='region', common_norm=False)
plt.title('Kernel Density Estimation (KDE) Plot by Region')
plt.xlabel('Value')
plt.ylabel('Density')

plt.show()

# Boxplot
sns.boxplot(data=df, x='region', y='value')
plt.title('Boxplot by Region')
plt.xlabel('Region')
plt.ylabel('Value')
plt.xticks(rotation=90)
plt.show()




df

# PREDICTION TEST W PROPHET
import pandas as pd
from fbprophet import Prophet
import matplotlib.pyplot as plt

# Assuming df is your DataFrame with columns 'ds' (date), 'normalized_value', and possibly other columns
# Ensure the 'ds' column is in datetime format

# Select relevant columns
df = df[['first_day', 'normalized_value']]

# Rename columns as required by Prophet
df.columns = ['ds', 'y']

# Create a Prophet model
model = Prophet()

# Fit the model
model.fit(df)

# Create a dataframe with future dates for prediction
future = model.make_future_dataframe(periods=365)  # Adjust the number of periods as needed

# Make predictions
forecast = model.predict(future)

# Plot the forecast
fig = model.plot(forecast)
plt.title('Time Series Forecast for Normalized Values in Sweden')
plt.xlabel('Date')
plt.ylabel('Normalized Value')
plt.show()


#### GPT TEST #########################################
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

# Assuming df is your DataFrame with 'first_day', 'cntr_nm', 'region', 'value', 'normalized_value'
# Make sure 'first_day' is in datetime format

df.first_day = pd.to_datetime(df.first_day)


# Feature Engineering (you can customize this based on your dataset)
df['year'] = df['first_day'].dt.year
df['month'] = df['first_day'].dt.month
df['weekofyear'] = df['first_day'].dt.isocalendar().week

# CatBoost doesnt handle NaN in Y-var
df.isnull().sum()
df[df.normalized_value.isnull()]
df.normalized_value = df.normalized_value.fillna(0)


# Split the data into training and testing sets
train_size = int(len(df) * 0.8)
train, test = df[0:train_size], df[train_size:]

# Define features and target
features = ['year', 'month', 'weekofyear', 'value']
target = 'normalized_value'

# Split into X and y
X_train, y_train = train[features], train[target]
X_test, y_test = test[features], test[target]

# XGBoost
xgb_model = xgb.XGBRegressor()
xgb_model.fit(X_train, y_train)
xgb_pred = xgb_model.predict(X_test)

# LightGBM
lgb_model = lgb.LGBMRegressor()
lgb_model.fit(X_train, y_train)
lgb_pred = lgb_model.predict(X_test)

# CatBoost
cb_model = cb.CatBoostRegressor()
cb_model.fit(X_train, y_train)
cb_pred = cb_model.predict(X_test)

# Evaluate models
print(f"XGBoost RMSE: {mean_squared_error(y_test, xgb_pred, squared=False)}")
print(f"LightGBM RMSE: {mean_squared_error(y_test, lgb_pred, squared=False)}")
print(f"CatBoost RMSE: {mean_squared_error(y_test, cb_pred, squared=False)}")


# Plotting the actual vs predicted values
plt.scatter(y_test, xgb_pred, alpha=0.5)
plt.title('Actual vs Predicted Values (LightGBM)')
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.show()




min_value = df['original_value'].min()  # Replace 'original_value' with the actual column name
max_value = df['original_value'].max()  # Replace 'original_value' with the actual column name

unnormalized_pred = inverse_min_max_scaling(normalized_pred, min_value, max_value)


### DEEEEEEEEEETAILLSS ###############

# load the dataset and print the first 5 rows
series = read_csv('temperatures.csv', header=0, index_col=0)
print(series.head())
# prepare data for normalization
values = series.values
values = values.reshape((len(values), 1))
# train the normalization
scaler = MinMaxScaler(feature_range=(0, 1))
scaler = scaler.fit(values)
print('Min: %f, Max: %f' % (scaler.data_min_, scaler.data_max_))
# normalize the dataset and print the first 5 rows
normalized = scaler.transform(values)
for i in range(5):
 print(normalized[i])
# inverse transform and print the first 5 rows
inversed = scaler.inverse_transform(normalized)
for i in range(5):
 print(inversed[i])



from matplotlib import pyplot
series = read_csv('temperatures.csv', header=0, index_col=0)
series.hist()
pyplot.show()


y = (x - mean) / standard_deviation
y = (20.7 - 10) / 5
y = (10.7) / 5



from pandas import read_csv
from sklearn.preprocessing import StandardScaler
from math import sqrt
# load the dataset and print the first 5 rows
series = read_csv('temperatures.csv', header=0, index_col=0)
print(series.head())
# prepare data for standardization
values = series.values
values = values.reshape((len(values), 1))
# train the standardization
scaler = StandardScaler()
scaler = scaler.fit(values)
print('Mean: %f, StandardDeviation: %f' % (scaler.mean_, sqrt(scaler.var_)))
# standardization the dataset and print the first 5 rows
normalized = scaler.transform(values)
for i in range(5):
 print(normalized[i])
# inverse transform and print the first 5 rows
inversed = scaler.inverse_transform(normalized)
for i in range(5):
 print(inversed[i])