from Exchange import Exchange
from DataFetch import DataFetch
import asyncio

# Main function where evertyhing comes together. 

# Here, create a seperate function that connects everything needed for your crypto trading bot
# We will then call all trading bots in the main() function for testing peformance. 
async def main():
    await ElyseBot()

async def ElyseBot():
    exchange = Exchange("binance"); 
    fetcher = DataFetch("binance");

    # print(fetcher.has())
    # print(await fetcher.fetchOrderBook(symbol="BTCUSDT", limit=10))
    print(await fetcher.fetchOHLCV("ETH/USDT", '1m'))


if (__name__ == "__main__"):
   asyncio.run(main())
