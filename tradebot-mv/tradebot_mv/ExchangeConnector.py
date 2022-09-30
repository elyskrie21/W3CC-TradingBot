import ccxt

class ExchangeConnector:
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        self.exchange = getattr(ccxt, exchange)({
            'apiKey': '',
            'secret': ''
        })
        self.exchange.loadMarkets()
        if (setSandbox):
            self.exchange.setSandboxMode()

        print(self.exchange.has)