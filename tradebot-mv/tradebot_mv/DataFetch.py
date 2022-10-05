from cmath import sin
import ccxt
from ExchangeConnector import ExchangeConnector
import asyncio


# This class will fetch all the data from an exchange
# This data will be used by the TradeAlgorithm class

# Create any functions needed to fetch the data that is required for your algorithm 
class DataFetch(ExchangeConnector):
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        super().__init__(exchange, setSandbox)

    
    async def fetchOrderBook(self, limit: int = 0, symbol: str = ''):
        return self.exchange.fetchOrderBook(symbol, limit)

    async def fetchOHLCV(self, symbol: str, timeFrame = str, since = None, limit = None):
        return self.exchange.fetchOHLCV(symbol, timeFrame, limit=limit, since=since)
    
    
    