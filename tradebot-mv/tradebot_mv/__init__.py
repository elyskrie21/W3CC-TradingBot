import time
from Exchange import Exchange
from TradeAlgorithm import ElyseAlgo
from DataFetch import DataFetch
import asyncio
import simplejson as json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import HuberRegressor, Ridge

# Main function where evertyhing comes together.

# Here, create a seperate function that connects everything needed for your crypto trading bot
# We will then call all trading bots in the main() function for testing peformance.


async def main():
    await ElyseBot()


async def ElyseBot():
    config = None
    with open("config.json") as configFile:
        config = json.load(configFile)


    bot = ElyseAlgo("binance", config["symbol"], config["LOGFILE"], config["grid_level"], config["amount"], True)

    exchange = Exchange("binance", True)


    # await exchange.sell("BTC/USDT", "market", 0.05, 15000)


    # await bot.exitMarket("Test")
    print(await exchange.getAccountBalance())

    # await bot.placeOrderInit()

    # await bot.performanceGrapH("USDT")


async def testing():
    fetch = DataFetch("binance", setSandbox=True)
    data = []

    for i in range(500):
        data.append((await fetch.fetchTickers(symbol="ETH/USDT"))['ask'])
        time.sleep(0)

    y = np.array(data, dtype=float)
    x = np.array(list(range(0, y.size)))

    std = np.std(y); 
    print("StD: ", std)
    

    A = np.vstack([x, np.ones(x.size)]).T
   
    plt.plot(x, y, "b.")
    
    colors = ["r-", "b-", "y-", "m-"]
    epsilon_values = [1, 1.5, 1.75, 1.9]
    for k, epsilon in enumerate(epsilon_values):
        huber = HuberRegressor(alpha=0.0, epsilon=epsilon)
        huber.fit(A, y)
        plt.plot(x, huber.predict(A), colors[k], label="huber loss, %s" % epsilon)

    ridge = Ridge(alpha=0.0, random_state=0)
    ridge.fit(A, y)
    plt.plot(x, ridge.predict(A), "g-", label="ridge regression")

    plt.title("Comparison of HuberRegressor vs Ridge")
    plt.xlabel("X")
    plt.ylabel("y")
    plt.legend(loc=0)
    plt.show()



if (__name__ == "__main__"):
    asyncio.run(main())

    # asyncio.run(testing())
