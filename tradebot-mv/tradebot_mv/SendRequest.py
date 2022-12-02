import time
import ccxt
from DataFetch import DataFetch
from Logger import myLogger
from Exchange import Exchange

class SendRequest: 
    def __init__(self, symbol, exchange, amount, logFile, setSandbox = False) -> None:
        self.symbol = symbol
        self.amount = amount
        self.logFile = logFile
        self.exchange = Exchange(exchange, setSandbox)
        self.fetcher = DataFetch(exchange, setSandbox)

        
    async def req(self, task, input1=None, input2=None):
        tries = 3

        for i in range(tries):
            try:
                if task == "get_bid_ask_price":
                    ticker = await self.fetcher.fetchTickers(self.symbol)
                    return ticker["bid"],  ticker["ask"]

                elif task == "get_order":
                    return (await self.fetcher.fetchOrder(input1, input2))["info"]
                
                elif task == "cancel_order":
                    data = (await self.exchange.cancelOrder(input1, input2))
                    if (type(data) is str):
                        return "OrderNotFound"
                    else:
                        return data["info"]

                elif task == "place_order":
                    #sendRequest(self,task,input1=side,input2=price)
                    side = input1
                    price = input2
                    orderid=0
                    if side =="buy":
                        orderid = (await self.exchange.buy(self.symbol, "limit", self.amount, price))["info"]["orderId"]
                    else:
                        orderid = (await self.exchange.sell(self.symbol, "limit", self.amount, price))["info"]["orderId"]
                    return orderid
                
                elif task == "get_balance":
                    return (await self.exchange.getAccountBalance())["free"][input1]
                
                elif task == "fetch_order_book":
                    return (await self.fetcher.fetchOrderBook(limit=input1, symbol=self.symbol))[input2]
                
                elif task == "exit_market":
                    coinAccountBalance = (await self.exchange.getAccountBalance())["free"][self.symbol.split("/")[0]]
                    ask_price = (await self.fetcher.fetchTickers(self.symbol))["ask"]

                    if coinAccountBalance <= 0:
                        return -1; 

                    orderid = (await self.exchange.sell(self.symbol, "limit", coinAccountBalance, ask_price))["info"]["orderId"]
                    
                    return orderid
                elif task == "enter_market":
                    ask_price = (await self.fetcher.fetchTickers(self.symbol))["ask"]
                    orderid = (await self.exchange.buy(self.symbol, "limit", self.amount * input1, ask_price))["info"]["orderId"]
                    
                    return orderid


                else:
                    return None
            except ccxt.NetworkError as e:
                if i < tries - 1: # i is zero indexed
                    
                    myLogger("NetworkError , try last "+str(i) +"chances" + str(e), self.logFile)
                    time.sleep(0.5)
                    continue
                else:
                    myLogger(str(e), self.logFile)
                    raise
            except ccxt.ExchangeError as e:
                if i < tries - 1: # i is zero indexed
                    myLogger(str(e), self.logFile)
                    time.sleep(0.5)
                    continue
                else:
                    myLogger(str(e), self.logFile)
                    raise