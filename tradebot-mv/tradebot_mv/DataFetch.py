import ccxt
from ExchangeConnector import ExchangeConnector
import asyncio

class DataFetch(ExchangeConnector):
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        super().__init__(exchange, setSandbox)

    
    async def fetchOrderBook(self, limit: int = 0, symbol: str = ''):
        return  self.exchange.fetchOrderBook(symbol, limit)
    
    
    