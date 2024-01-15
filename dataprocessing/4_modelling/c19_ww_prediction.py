
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

sequence_len = 5
pd.set_option('display.max_rows', 15)
pd.set_option('display.max_columns',10)

train = 'train'
test = 'test'
predict = 'prediction'

staged_datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'


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

# Concatenate DataFrames
df = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12], ignore_index=True))
df = d2
df = df[['first_day', 'region', 'cntr_code', 'cntr_nm','value', 'normalized_value', 'metric_nm']]
df['val_type'] = train # default naming
df = df.groupby(by=['first_day','cntr_nm','val_type'])['value'].mean().reset_index()
df = df.dropna(how='any')

location_groups = df.cntr_nm.unique()

cntr_list = []
rmse_list = []
for location in location_groups:
    print(location)
    #df_location = df
    df_location = df[df.cntr_nm == location]
        
    print('df_location.head():', df_location.head(1))

    # Setting 80 percent data for training
    training_data_len = math.ceil(len(df_location) * .8)
    training_data_len 
    df_location.loc[training_data_len:, 'val_type'] = test

    #Splitting the dataset
    train_data = df_location[:training_data_len][['value']]
    test_data = df_location[training_data_len:][['value']]
    print(train_data.shape, test_data.shape)

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
    y_LSTM_reshaped = np.reshape(y_LSTM, (y_LSTM.shape[0], y_LSTM.shape[1]))



    # scaling back from 0-1 to original
    y_LSTM_O = scaler.inverse_transform(y_LSTM_reshaped)

    # Average the prediction
    y_LSTM_O_avg = np.mean(y_LSTM_O, axis=1)



    # Original data
    #fig.add_trace(go.Scatter(x=df.index, y=df['value'], mode='lines', name='original_data', line=dict(color='blue')))
    

    # Test data
    #fig.add_trace(go.Scatter(x=test_data.index, y=test_data['value'], mode='lines', name='test_data', line=dict(color='green')))
    # Join 'test_data' with 'df_location' on the index
    #test_data_with_first_day = test_data.join(df_location['first_day'], how='left')
    #test_data_with_first_day['val_type'] = 'test'
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


    # Plot the test_data with extended x-axis
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_orig['first_day'], y=df_orig['value'], mode='lines', name=train, line=dict(color='green')))
    fig.add_trace(go.Scatter(x=con_row1['first_day'], y=con_row1['value'], mode='lines', name=train, line=dict(color='green'),showlegend=False))
    fig.add_trace(go.Scatter(x=df_test['first_day'], y=df_test['value'], mode='lines', name=test, line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=con_row2['first_day'], y=con_row2['value'], mode='lines', name=test, line=dict(color='blue'),showlegend=False))
    fig.add_trace(go.Scatter(x=df_pred['first_day'], y=df_pred['value'], mode='lines', name=predict, line=dict(color='orange')))



    #test_data_with_first_day = test_data.join(df_location['first_day'], how='left')

    # Use 'first_day' as the x-axis for test_data
    #fig.add_trace(go.Scatter(x=test_data_with_first_day['first_day'], y=test_data_with_first_day['value'], mode='lines', name='test_data', line=dict(color='green')))
    

    # LSTM predictions
    #fig.add_trace(go.Scatter(x=test_data.index[sequence_len:], y=y_LSTM_O_avg, mode='lines', name='y_LSTM', line=dict(color='orange')))
    #fig.add_trace(go.Scatter(x=test_data_with_first_day, y=y_LSTM_O_avg, mode='lines', name='y_LSTM', line=dict(color='orange')))
    # Assuming 'first_day' is a datetime column, you should use it as x-axis for LSTM predictions
    #future_dates = pd.date_range(start=test_data_with_first_day['first_day'].iloc[-1], periods=len(y_LSTM_O_avg)+1, freq='D')[1:]
    #fig.add_trace(go.Scatter(x=future_dates, y=y_LSTM_O_avg, mode='lines', name='y_LSTM', line=dict(color='orange')))



    # Layout
    fig.update_layout(title=f"LSTM {location.title()}", xaxis_title='first_day (first day of week)', yaxis_title='Value', showlegend=True)

    # Show the plot
    fig.show()
    
    plt.show()

    # Evaluate the model on the test set
    evaluation_result = regressorLSTM.evaluate(X_test, y_test)
    #cntr_list = cntr_list.append(location)
    #rmse_list = rmse_list.append(evaluation_result[1])
    print("Test MSE:", evaluation_result[1])