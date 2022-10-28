import time
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
    
    await bot.placeOrderInit()

    await bot.performanceGrapH("USDT")


async def testing():
    fetch = DataFetch("binance", setSandbox=True)
    orders = np.array([])

    for i in range(100):
        data = await fetch.fetchOrderBook(symbol="ETH/USDT", limit=500)
        orders = np.concatenate((orders, [x[0] for x in data['asks']]))
        time.sleep(5)

    y = np.array(np.unique(orders), dtype=float)
    x = np.array(list(range(0, y.size)))
    

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
    # asyncio.run(main())

    asyncio.run(testing())
