################################################################## C19 Wastewater Data ##################################################################
#print(train_data.shape, test_data.shape) for example
#(605, 1) (151, 1) 
# org has seq len = 50, but has x 605 ~10% seq len here = 5

import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import math
from sklearn.preprocessing import MinMaxScaler
# importing libraries
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, SimpleRNN, Dropout, GRU, Bidirectional
from tensorflow.keras.optimizers import SGD
from sklearn import metrics
from sklearn.metrics import mean_squared_error
import plotly.graph_objects as go
import configparser

sequence_len = 5

# Maximum size for graphs
max_width = 1200
max_height = 800

# How many rows & cols for pandas to display
pd.set_option('display.max_rows', 15)
pd.set_option('display.max_columns',10)

# series names
train = 'train'
test = 'test'
predict = 'prediction'

# Read the Conf file
config_file = '/home/stratega/code/analytics/covid/conf.ini'
config = configparser.ConfigParser()
config.read(config_file)

# Data Params
staged_datapath = config.get('Paths', 'staged_datapath')
final_datapath = config.get('Paths', 'final_datapath')
save_trend_dir_gh = config.get('Paths', 'save_trend_dir_gh')
save_trend_filepath_gh = os.path.join(save_trend_dir_gh, 'forecasts.html')

save_trend_dir_bb = config.get('Paths', 'save_trend_dir_bb')
save_trend_filepath_bb = os.path.join(save_trend_dir_bb, 'forecasts.html')

d1 = pd.read_parquet(os.path.join(staged_datapath, 'france_wastewater.parquet'))
d2 = pd.read_parquet(os.path.join(staged_datapath, 'sweden_wastewater.parquet'))
d3 = pd.read_parquet(os.path.join(staged_datapath, 'netherlands_wastewater.parquet')) 
d4 = pd.read_parquet(os.path.join(staged_datapath, 'denmark_wastewater.parquet')) #fail 1 makes html huge. Due to geofile probably.
d5 = pd.read_parquet(os.path.join(staged_datapath, 'austria_wastewater.parquet'))
d6 = pd.read_parquet(os.path.join(staged_datapath, 'poland_wastewater.parquet')) # this is just Poznan County. Normaized Value must be
d7 = pd.read_parquet(os.path.join(staged_datapath, 'finland_wastewater.parquet'))
d8 = pd.read_parquet(os.path.join(staged_datapath, 'switzerland_wastewater.parquet'))
d9 = pd.read_parquet(os.path.join(staged_datapath, 'canada_wastewater.parquet'))
d10 =pd.read_parquet(os.path.join(staged_datapath, 'usa_wastewater.parquet'))
d11 =pd.read_parquet(os.path.join(staged_datapath, 'newzealand_wastewater.parquet'))
d12 =pd.read_parquet(os.path.join(staged_datapath, 'germany_wastewater.parquet'))

## Remove old html
files_to_remove = [save_trend_filepath_bb, save_trend_filepath_gh]
for file in files_to_remove:
    trend_html_filepath = file
    try:
        os.remove(trend_html_filepath)
        print(trend_html_filepath, 'removed')
    except FileNotFoundError:
        print(trend_html_filepath, 'does not exist')
    except Exception as e:
        print(f"An error occurred: {e}")

# Concatenate DataFrames
df = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12], ignore_index=True))
df.sort_values(by=['cntr_nm'], inplace=True)
#df = d7
#df = d10
df = df[['first_day', 'region', 'cntr_code', 'cntr_nm','value', 'normalized_value', 'metric_nm']]
df['val_type'] = train # default naming
df = df.groupby(by=['first_day','cntr_nm','val_type','metric_nm'])['value'].mean().reset_index()
df = df.dropna(how='any')

location_groups = df.cntr_nm.unique()

cntr_list = []
rmse_list = []
error_countries = []
for location in location_groups:
    try:
        print(location.upper())
        
        #df_location = df
        df_location = df[df.cntr_nm == location]
        df_location.reset_index(inplace=True)
        metric_nm = df_location.metric_nm.iloc[0] # Just get the metric name
        print('df_location.head():', df_location.head(1))

        # Setting 80 percent data for training
        training_data_len = math.ceil(len(df_location) * .8)
        training_data_len 
        df_location.loc[training_data_len:, 'val_type'] = test

        #Splitting the dataset
        train_data = df_location[:training_data_len][['value']]
        test_data = df_location[training_data_len:][['value']]
        print(train_data.shape, test_data.shape)

        #sequence_len = math.ceil(len(train_data) * 0.1)  # Adjust the multiplier as needed TEST

        # Selecting Open Price values
        df_train = train_data['value'].values

        # Reshaping 1D to 2D array
        df_train = np.reshape(df_train, (-1,1)) 
        df_train.shape


        scaler = MinMaxScaler(feature_range=(0,1))
        # scaling dataset
        scaled_train = scaler.fit_transform(df_train)

        #print(scaled_train[:5])

        # Selecting Open Price values
        df_test = test_data['value'].values 
        # Reshaping 1D to 2D array
        df_test = np.reshape(df_test, (-1,1)) 
        # Normalizing values between 0 and 1
        scaled_test = scaler.fit_transform(df_test) # Needed when wanteding to do transorm
        # scaled_test = df_test #if no transform. but normalized_value was worse than norm norm transform
        #print(*scaled_test[:5])


        # Assuming you have already defined 'scaled_train' and 'scaled_test'

        # Training data
        X_train = []
        y_train = []

        for i in range(sequence_len, len(scaled_train)):
            X_train.append(scaled_train[i - sequence_len:i, 0])
            y_train.append(scaled_train[i, 0])

        # Convert to Numpy array
        X_train, y_train = np.array(X_train), np.array(y_train)

        # Reshape for LSTM input (samples, timesteps, features)
        X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
        y_train = np.reshape(y_train, (y_train.shape[0], 1))

        print("X_train shape:", X_train.shape, "y_train shape:", y_train.shape)

        # Testing data
        X_test = []
        y_test = []

        # PROB ERROR HERE
        # fi = 4 when -1
        for i in range(sequence_len, len(scaled_test)): 
            X_test.append(scaled_test[i - sequence_len:i, 0])
            y_test.append(scaled_test[i, 0])

        # Convert to Numpy array
        X_test, y_test = np.array(X_test), np.array(y_test)

        # Reshape for LSTM input (samples, timesteps, features)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
        y_test = np.reshape(y_test, (y_test.shape[0], 1))

        #X_test = np.reshape(X_test, (1, 5, 1))
        print("X_test shape:", X_test.shape, "y_test shape:", y_test.shape)


        ##fitting the model

        #Initialising the model
        regressorLSTM = Sequential()

        #Adding LSTM layers
        regressorLSTM.add(LSTM(sequence_len, 
                            return_sequences = True, 
                            input_shape = (X_train.shape[1],1)))
        """
        regressorLSTM.add(LSTM(5, 
                            return_sequences = False))
        regressorLSTM.add(Dense(2))
        """
        #Adding the output layer
        regressorLSTM.add(Dense(1))

        #Compiling the model
        regressorLSTM.compile(optimizer = 'adam',
                            loss = 'mean_squared_error',
                            metrics = ["accuracy"])

        #Fitting the model
        regressorLSTM.fit(X_train, 
                        y_train, 
                        batch_size = 1, 
                        epochs = 12)
        regressorLSTM.summary()


        # predictions with X_test data
        y_LSTM = regressorLSTM.predict(X_test)
        evaluation_result = regressorLSTM.evaluate(X_test, y_test)

        print('y_LSTM.shape:',y_LSTM)
        y_LSTM_reshaped = np.reshape(y_LSTM, (y_LSTM.shape[0], y_LSTM.shape[1]))


        # scaling back from 0-1 to original
        y_LSTM_O = scaler.inverse_transform(y_LSTM_reshaped)

        # Average the prediction
        y_LSTM_O_avg = np.mean(y_LSTM_O, axis=1)

        max_index = df_location.index.max()
        max_date = df_location.first_day.max()
        max_date_timestamp = pd.to_datetime(max_date)

        # Specify the number of weeks to jump forward
        weeks_to_jump = sequence_len
        date_range = [max_date_timestamp + pd.DateOffset(weeks=i) for i in range(1, weeks_to_jump + 1)]

        # Optionally, you can convert the result to date strings if needed
        date_strings = [date.strftime('%Y-%m-%d') for date in date_range]

        count_array = np.arange(max_index + 1, max_index + sequence_len + 1, 1)
        
        df_future = pd.DataFrame(index=count_array)
        df_future['first_day'] = date_strings
        df_future['value'] = y_LSTM_O_avg
        df_future['val_type'] = predict

        # Concatenate 'test_data_with_first_day' and 'future_data'
        df_loc_pred = pd.concat([df_location, df_future])
        df_loc_pred['val_type'] = df_loc_pred['val_type'].astype('category')


        fig = go.Figure()
        

        df_orig=df_loc_pred[df_loc_pred.val_type==train]
        df_test=df_loc_pred[df_loc_pred.val_type==test]
        df_pred=df_loc_pred[df_loc_pred.val_type==predict]

        # These 2 are just to connect the lines..adds visual trend clarity
        con_row1 = pd.concat([ df_orig.iloc[[-1]], df_test.iloc[[0]] ])
        con_row2 = pd.concat([ df_test.iloc[[-1]], df_pred.iloc[[0]] ])

        mean_value = df_loc_pred['value'].mean()

        # Plot The Data
        current_fig = go.Figure()

        current_fig.add_trace(go.Scatter(x=df_orig['first_day'], y=df_orig['value'], mode='lines', name=train, line=dict(color='green')))
        current_fig.add_trace(go.Scatter(x=con_row1['first_day'], y=con_row1['value'], mode='lines', name=train, line=dict(color='green'),showlegend=False))
        current_fig.add_trace(go.Scatter(x=df_test['first_day'], y=df_test['value'], mode='lines', name=test, line=dict(color='blue')))
        current_fig.add_trace(go.Scatter(x=con_row2['first_day'], y=con_row2['value'], mode='lines', name=test, line=dict(color='blue'),showlegend=False))
        current_fig.add_trace(go.Scatter(x=df_pred['first_day'], y=df_pred['value'], mode='lines', name=predict, line=dict(color='orange')))

        # Add the red mean line
        current_fig.add_trace(go.Scatter(
            x=[df_loc_pred['first_day'].min(), df_loc_pred['first_day'].max()],
            y=[mean_value, mean_value],
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name='mean'
        ))

        # Layout
        current_fig.update_layout(title=f"<b>{location.title()}</b><br>LSTM Neural Net <br>Mean Squared Error: {round(evaluation_result[1],2)}"
        ,xaxis_title='first_day (first day of week)'
        ,yaxis_title=metric_nm
        ,showlegend=True
        #,width=max_width
        #,height=max_height
        )

        # Show the plot
        current_fig.show()
        

        # Evaluate the model on the test set        
        #cntr_list = cntr_list.append(location)
        #rmse_list = rmse_list.append(evaluation_result[1])
        print("Test MSE:", evaluation_result[1])
            
        ### put figs into 1 graph
        with open(trend_html_filepath, 'a') as f:
            f.write(current_fig.to_html(full_html=False, include_plotlyjs='cdn'))

        with open(save_trend_filepath_bb, 'a') as f:
            f.write(current_fig.to_html(full_html=False, include_plotlyjs='cdn'))        


        
    except:
        print('FAILED:', location.upper())
        error_countries.append(location.upper())

print('All Failed Predictions:',error_countries)