import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
#pio.renderers.default='browser'
from scipy import stats
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import yfinance as yf
from pytz import timezone

simulations = 500
steps_forward = 50
symbol = "AAPL"
period = "30d"  # 30 dias
interval = "5m"  # 5 minutos

# Crie um objeto Ticker para o símbolo
ewz_ticker = yf.Ticker(symbol)

intraday_data = ewz_ticker.history(period=period, interval=interval)
intraday_data.reset_index(inplace=True)

# Troca as linhas da cabeça pelo tail e vice-versa
intraday_data = intraday_data.iloc[::-1].reset_index(drop=True)
dataset = intraday_data.copy()
dataset.set_index('Datetime', inplace = True)
dataset.head(5)

Y = dataset.head(steps_forward)
X = dataset.tail(dataset.shape[0] - steps_forward)

fig = px.line(title = f'Training sample {symbol}')
fig.add_scatter(x = X.index, y = X['Open'], name = 'Training')
fig.show()


fig = px.line(title = f'Saida real {symbol}')
fig.add_scatter(x = Y.index, y = Y['Open'], name = 'Training')
fig.show()

dataset_opening = pd.DataFrame(X['Open'])

dataset_normalized = dataset_opening.copy()
for i in dataset_opening:
  dataset_normalized[i] = dataset_opening[i] / dataset_opening[i][0]
  #dataset_normalized.iloc[i] = dataset_opening.iloc[i] / dataset_opening.iloc[i][0]

dataset_return_rate = np.log(1 + dataset_normalized.pct_change())
dataset_return_rate.fillna(0, inplace=True)

mean = dataset_return_rate.mean()

variance = dataset_return_rate.var()

drift = mean - (0.5 * variance)

standard_deviation = dataset_return_rate.std()

Z = stats.norm.ppf(np.random.rand(steps_forward, simulations))
daily_returns = np.exp(drift.values + standard_deviation.values * Z)


predicted = np.zeros_like(daily_returns)

predicted[0] = dataset_opening.iloc[0]

for step in range(1, steps_forward):
  predicted[step] = predicted[step - 1] * daily_returns[step]

list_name = []
for i in range(0,simulations):
    list_name.append('simulation' + str(i + 1))

df_predicted = pd.DataFrame(predicted, columns=list_name)
mean = df_predicted.iloc[:, 0:simulations+1].mean(axis=1)

df_predicted['Open'] = mean
df_predicted['data'] = Y.index


df_predicted.set_index('data', inplace = True)

fig = px.line(title = f'Forward {steps_forward} predictions for {symbol} ')
fig.add_scatter(x = df_predicted.index, y = df_predicted['Open'], name = 'Test Period Prediction')
fig.add_scatter(x = Y.index, y = Y['Open'], name = 'Actual')
fig.show()

mae = mean_absolute_error(Y['Open'], df_predicted['Open'])
mape = mean_absolute_percentage_error(Y['Open'], df_predicted['Open'])
print('MAE: ', mae)
print('MAPE: ', mape)