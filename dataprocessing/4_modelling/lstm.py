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


#the start and end date
start_date = dt.datetime(2020,4,1)
end_date = dt.datetime(2023,4,1)

#loading from yahoo finance
data = yf.download("GOOGL",start_date, end_date)

pd.set_option('display.max_rows', 4)
pd.set_option('display.max_columns',5)
print(data)

# Setting 80 percent data for training
training_data_len = math.ceil(len(data) * .8)
training_data_len 

#Splitting the dataset
train_data = data[:training_data_len].iloc[:,:1] 
test_data = data[training_data_len:].iloc[:,:1]
print(train_data.shape, test_data.shape)

# Selecting Open Price values
df_train = train_data.Open.values 
# Reshaping 1D to 2D array
df_train = np.reshape(df_train, (-1,1)) 
df_train.shape



scaler = MinMaxScaler(feature_range=(0,1))
# scaling dataset
scaled_train = scaler.fit_transform(df_train)

print(scaled_train[:5])

# Selecting Open Price values
df_test = test_data.Open.values 
# Reshaping 1D to 2D array
df_test = np.reshape(df_test, (-1,1)) 
# Normalizing values between 0 and 1
scaled_test = scaler.fit_transform(df_test) 
print(*scaled_test[:5])


X_train = []
y_train = []
for i in range(50, len(scaled_train)):
	X_train.append(scaled_train[i-50:i, 0])
	y_train.append(scaled_train[i, 0])
	if i <= 51:
		print(X_train)
		print(y_train)
		print()

# The data is converted to Numpy array
X_train, y_train = np.array(X_train), np.array(y_train)

X_test = []
y_test = []
for i in range(50, len(scaled_test)):
	X_test.append(scaled_test[i-50:i, 0])
	y_test.append(scaled_test[i, 0])


#Reshaping
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1],1))
y_train = np.reshape(y_train, (y_train.shape[0],1))
print("X_train :",X_train.shape,"y_train :",y_train.shape)


# The data is converted to numpy array
X_test, y_test = np.array(X_test), np.array(y_test)

#Reshaping
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1],1))
y_test = np.reshape(y_test, (y_test.shape[0],1))
print("X_test :",X_test.shape,"y_test :",y_test.shape)





## fitting the model

#Initialising the model
regressorLSTM = Sequential()

#Adding LSTM layers
regressorLSTM.add(LSTM(50, 
					return_sequences = True, 
					input_shape = (X_train.shape[1],1)))
regressorLSTM.add(LSTM(50, 
					return_sequences = False))
regressorLSTM.add(Dense(25))

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
#y_RNN = regressor.predict(X_test)
y_LSTM = regressorLSTM.predict(X_test)
#y_GRU = regressorGRU.predict(X_test)


# scaling back from 0-1 to original
#y_RNN_O = scaler.inverse_transform(y_RNN) 
y_LSTM_O = scaler.inverse_transform(y_LSTM) 
#y_GRU_O = scaler.inverse_transform(y_GRU)

fig, axs = plt.subplots(3,figsize =(18,12),sharex=True, sharey=True)
fig.suptitle('Model Predictions')

#Plot for RNN predictions
"""axs[0].plot(train_data.index[150:], train_data.Open[150:], label = "train_data", color = "b")
axs[0].plot(test_data.index, test_data.Open, label = "test_data", color = "g")
axs[0].plot(test_data.index[50:], y_RNN_O, label = "y_RNN", color = "brown")
axs[0].legend()
axs[0].title.set_text("Basic RNN")"""

#Plot for LSTM predictions
axs[1].plot(train_data.index[150:], train_data.Open[150:], label = "train_data", color = "b")
axs[1].plot(test_data.index, test_data.Open, label = "test_data", color = "g")
axs[1].plot(test_data.index[50:], y_LSTM_O, label = "y_LSTM", color = "orange")
axs[1].legend()
axs[1].title.set_text("LSTM")

#Plot for GRU predictions
"""axs[2].plot(train_data.index[150:], train_data.Open[150:], label = "train_data", color = "b")
axs[2].plot(test_data.index, test_data.Open, label = "test_data", color = "g")
axs[2].plot(test_data.index[50:], y_GRU_O, label = "y_GRU", color = "red")
axs[2].legend()
axs[2].title.set_text("GRU")"""

plt.xlabel("Days")
plt.ylabel("Open price")

plt.show()

# Evaluate the model on the test set
evaluation_result = regressorLSTM.evaluate(X_test, y_test)
print("Test MSE:", evaluation_result[1])


################################################################## C19 Wastewater Data ##################################################################
#print(train_data.shape, test_data.shape) for example
#(605, 1) (151, 1) 
# org has seq len = 50, but has x 605 ~10% seq len here = 5

sequence_len = 5

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


pd.set_option('display.max_rows', 4)
pd.set_option('display.max_columns',10)


datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'


df = pd.read_parquet(os.path.join(datapath, 'sweden_wastewater.parquet'))
df = df.dropna(how='any')

regions = df.region.unique()

for region in regions:
    print(region)
    df_region = df
    #df_region = df[df.region == region]
    
    print('df_region.head():', df_region.head(1))

    # Setting 80 percent data for training
    training_data_len = math.ceil(len(df_region) * .8)
    training_data_len 

    #Splitting the dataset
    train_data = df_region[:training_data_len][['value']]
    test_data = df_region[training_data_len:][['value']]
    print(train_data.shape, test_data.shape)

    # Selecting Open Price values
    df_train = train_data['value'].values

    # Reshaping 1D to 2D array
    df_train = np.reshape(df_train, (-1,1)) 
    df_train.shape



    scaler = MinMaxScaler(feature_range=(0,1))
    # scaling dataset
    scaled_train = scaler.fit_transform(df_train)

    print(scaled_train[:5])

    # Selecting Open Price values
    df_test = test_data['value'].values 
    # Reshaping 1D to 2D array
    df_test = np.reshape(df_test, (-1,1)) 
    # Normalizing values between 0 and 1
    scaled_test = scaler.fit_transform(df_test) # Needed when wanteding to do transorm
    # scaled_test = df_test #if no transform. but normalized_value was worse than norm norm transform
    print(*scaled_test[:5])


    """X_train = []
    y_train = []
    for i in range(sequence_len, len(scaled_train)):
        X_train.append(scaled_train[i-sequence_len:i, 0])
        y_train.append(scaled_train[i, 0])
        if i <= sequence_len+1:
            print(X_train)
            print(y_train)
            print()

    # The data is converted to Numpy array
    X_train, y_train = np.array(X_train), np.array(y_train)

    X_test = []
    y_test = []
    for i in range(sequence_len, len(scaled_test)):
        X_test.append(scaled_test[i-sequence_len:i, 0])
        y_test.append(scaled_test[i, 0])
        print('len X_test:',y_test)


    #Reshaping
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1],1))
    y_train = np.reshape(y_train, (y_train.shape[0],1))
    print("X_train :",X_train.shape,"y_train :",y_train.shape)


    # The data is converted to numpy array
    X_test, y_test = np.array(X_test), np.array(y_test)

    #Reshaping
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1],1))
    y_test = np.reshape(y_test, (y_test.shape[0],1))"""

    import numpy as np

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
    regressorLSTM.add(LSTM(5, 
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
    #y_RNN = regressor.predict(X_test)


    y_LSTM = regressorLSTM.predict(X_test)

    #y_GRU = regressorGRU.predict(X_test)

    y_LSTM_reshaped = np.reshape(y_LSTM, (y_LSTM.shape[0], y_LSTM.shape[1]))



    # scaling back from 0-1 to original
    #y_RNN_O = scaler.inverse_transform(y_RNN) 
    #y_LSTM_O = scaler.inverse_transform(y_LSTM) 
    # Use inverse_transform on the reshaped array
    y_LSTM_O = scaler.inverse_transform(y_LSTM_reshaped)
    #y_GRU_O = scaler.inverse_transform(y_GRU)

    fig, axs = plt.subplots(nrows=3,figsize =(18,12),sharex=True, sharey=True)
    fig.suptitle('Model Predictions')


    # Average the prediction
    y_LSTM_O_avg = np.mean(y_LSTM_O, axis=1)



    #Plot for LSTM predictions
    axs[1].plot(train_data.index, train_data.value, label="train_data", color="b")
    axs[1].plot(test_data.index, test_data.value, label="test_data", color="g")
    axs[1].plot(test_data.index[sequence_len:], y_LSTM_O_avg, label="y_LSTM", color="orange")
    axs[1].legend()
    axs[1].title.set_text("LSTM")

    # Assuming 'x' is the time variable in the original DataFrame
    """
    axs[1].plot(df.index, df['first_day'], label="original_data", color="blue")
    axs[1].plot(test_data.index, test_data['value'], label="test_data", color="green")
    axs[1].plot(test_data.index[sequence_len:], y_LSTM_O_avg, label="y_LSTM", color="orange")
    axs[1].legend()
    axs[1].set_title("LSTM")
    """
    plt.xlabel("Days")
    plt.ylabel("Transmission Level")

    plt.show()

    # Evaluate the model on the test set
    evaluation_result = regressorLSTM.evaluate(X_test, y_test)
    print("Test MSE:", evaluation_result[1])