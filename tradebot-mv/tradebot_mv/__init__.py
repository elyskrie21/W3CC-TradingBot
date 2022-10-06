import time
import datetime
from TradeAlgorithm import ElyseAlgo
from Exchange import Exchange
from DataFetch import DataFetch
import asyncio
import simplejson as json

# Main function where evertyhing comes together.

# Here, create a seperate function that connects everything needed for your crypto trading bot
# We will then call all trading bots in the main() function for testing peformance.


async def main():
    await ElyseBot()


async def ElyseBot():
    config = None
    with open("config.json") as configFile:
        config = json.load(configFile)

    bot = ElyseAlgo("binance", config["symbol"], config["LOGFILE"], config["grid_level"],
                    config["lower_price"], config["upper_price"], config["amount"], True)
    await bot.placeOrderInit();

    while True:
        print("Loop in :", datetime.datetime.now())
        await bot.loopJob()
        time.sleep(1)


if (__name__ == "__main__"):
    asyncio.run(main())
