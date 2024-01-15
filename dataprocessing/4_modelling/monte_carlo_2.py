import yfinance as yf 
import numpy as np
import matplotlib.pyplot as plt

# https://www.youtube.com/watch?v=LWc-9v8RVwM

n_steps_prediction = 252 # 252 trading days
n_simulations = 1000

df = yf.download('TSLA')
df.columns = df.columns.str.lower()

returns = np.log(1 + df['adj close'].pct_change())

mu, sigma = returns.mean(), returns.std()
sim_rets = np.random.normal(mu, sigma, n_steps_prediction)

initial = df['adj close'].iloc[-1] # Intitial value is the most recent record
sim_prices = initial * (sim_rets + 1).cumprod()

plt.plot(sim_prices) # Random walk for the next timesteps

# Make this into array operation
"""
for i in range(n_simulations):
    sim_rets = np.random.normal(mu,sigma,n_steps_prediction)
    sim_prices = initial * (sim_rets + 1).cumprod()
    plt.axhline(initial,c='k')
    plt.plot(sim_prices)
"""

# Simulate returns for all steps and all simulations at once
sim_rets = np.random.normal(mu, sigma, size=(n_simulations, n_steps_prediction))

# Calculate simulated prices using cumulative product along the specified axis
sim_prices = initial * np.cumprod(1 + sim_rets, axis=1)

# Plot the simulations
plt.axhline(initial, c='k')
plt.plot(sim_prices.T)  # Transpose the array for correct plotting
plt.show()



### Test with brownian motion
import yfinance as yf 
import numpy as np
import matplotlib.pyplot as plt

# Download TSLA data
df = yf.download('TSLA')
df.columns = df.columns.str.lower()

# Calculate daily log returns
returns = np.log(1 + df['adj close'].pct_change())

# Calculate drift and volatility
mu = returns.mean()
sigma = returns.std()

# Set simulation parameters
n_steps_prediction = 252  # 252 trading days
n_simulations = 1000

# Initial value is the most recent record
initial = df['adj close'].iloc[-1]

# Simulate Brownian motion
sim_rets = np.random.normal(mu, sigma, size=(n_simulations, n_steps_prediction))
sim_prices = initial * np.exp(np.cumsum((mu - 0.5 * sigma**2) + sigma * sim_rets, axis=1))

# Plot the simulations
plt.plot(sim_prices.T, color='blue', alpha=0.1)  # Transpose the array for correct plotting
plt.axhline(initial, c='k')
plt.show()
