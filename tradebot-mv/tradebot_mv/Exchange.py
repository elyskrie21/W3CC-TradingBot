# Going to use CCXT for the initial implentation
# Main reason is that their is a better way to implment a general Exchange class that would be better
# If we want to be super perfomant, we would stick to ONE exchange and write custom requests for it. 
import ccxt
from ExchangeConnector import ExchangeConnector
import asyncio

# This classes is all about the private side of each exchange
# Here is where account information will be fetch 
# Also any buy/sell calls will be controlled by this class

# Feel free to add any other functions that is needed to handle account data or private api calls. 
class Exchange(ExchangeConnector):
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        super().__init__(exchange, setSandbox)

    @property 
    async def free_balance(self):
        balance = self.exchange.fetch_free_balance()

        return {k: v for k, v in balance.items() if v > 0}
    
    async def fetchOpenOrders(self, symbol: str = None):
        return self.exchange.fetchOpenOrders()
    
    async def cancelOrder(self, orderId: int, symbol: str):
        try: 
            self.exchange.cancelOrder(orderId, symbol)
        except ccxt.OrderNotFound:
            pass
    
    async def getAccountBalance(self, params: dict = {}):
        return self.exchange.fetchBalance(params)
    
    async def buy(self, symbol: str, type: str, amount: float, price: float, params: dict = {}):
        return self.exchange.createOrder(symbol, type, "buy", amount, price, params)

    async def sell(self, symbol: str, type: str, amount: float, price: float, params: dict = {}):
        return self.exchange.createOrder(symbol, type, "sell", amount, price, params)
    

