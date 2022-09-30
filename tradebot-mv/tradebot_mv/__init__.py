from Exchange import Exchange
from DataFetch import DataFetch
import asyncio

async def main():
    exchange = Exchange("binance"); 
    fetcher = DataFetch("binance");

    print(await fetcher.fetchOrderBook(symbol="BTCUSDT", limit=10))

if (__name__ == "__main__"):
   asyncio.run(main())
