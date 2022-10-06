from json import load
import ccxt
import os
from dotenv import load_dotenv

# Connects to any exchange
# Used by DataFetch and Exchange
# Can be used by any future classes that needed to connect to an exchange. 
class ExchangeConnector:
    def __init__(self, exchange: ccxt.Exchange, setSandbox: bool = False) -> None:
        load_dotenv() 
       
        self.exchange = getattr(ccxt, exchange)({
            'apiKey': os.environ.get('APIKEY'),
            'secret': os.environ.get('SECRET'),
            'enableRateLimit': True,
        })

        self.exchange.setSandboxMode(setSandbox)        
        self.markets = self.exchange.loadMarkets()
        


    def has(self):
      print(self.exchange.has)