# Going to use CCXT for the initial implentation
# Main reason is that their is a better way to implment a general Exchange class that would be better
# If we want to be super perfomant, we would stick to ONE exchange and write custom requests for it. 
import ccxt

class Exchange:
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        self.exchange = getattr(ccxt, exchange)({
            'apiKey': '',
            'secret': ''
        })
        self.exchange.loadMarkets()
        if (setSandbox):
            self.exchange.setSandboxMode()

        print(self.exchange.has)

    @property 
    def free_balance(self):
        balance = self.exchange.fetch_free_balance()

        return {k: v for k, v in balance.items() if v > 0}
    
    def fetchOpenOrders(self, symbol: str = None):
        return self.exchange.fetchOpenOrders()
    
    def cancelOrder(self, orderId: int):
        try: 
            self.exchange.cancelOrder(orderId)
        except ccxt.OrderNotFound:
            pass
    
    def getAccountBalance(self, params: dict = {}):
        return self.exchange.fetchBalanc(params)
    
    def buy(self, symbol: str, type: str, amount: float, price: float, params: dict = {}):
        return self.exchange.createOrder(symbol, type, "buy", amount, price, params)

    def sell(self, symbol: str, type: str, amount: float, price: float, params: dict = {}):
        return self.exchange.createOrder(symbol, type, "sell", amount, price, params)
    

