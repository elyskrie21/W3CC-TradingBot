import ccxt

# Connects to any exchange
# Used by DataFetch and Exchange
# Can be used by any future classes that needed to connect to an exchange. 
class ExchangeConnector:
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        self.exchange = getattr(ccxt, exchange)({
            'apiKey': '',
            'secret': ''
        })
        self.exchange.loadMarkets()
        if (setSandbox):
            self.exchange.setSandboxMode()

    def has(self):
      print(self.exchange.has)