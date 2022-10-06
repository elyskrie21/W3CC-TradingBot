from turtle import done
import ccxt
import numpy as np
import pandas as pd
from DataFetch import DataFetch
from Exchange import Exchange
import time
import datetime

# In this class we can all creat our own trading algoritms which will be tested later on
# These classes don't fetch their own data, but rather each algo while use the DataFetch and Exchange classes

# Testing the grid trading algo to start since its easy to understand and implements
# Will create a more complex/custom solution later. 
COLOR_RESET = "\033[0;0m"
COLOR_GREEN = "\033[0;32m"
COLOR_RED = "\033[1;31m"
COLOR_BLUE = "\033[1;34m"
COLOR_WHITE = "\033[1;37m"

class Order_Info:
    def __init__(self):
        self.done=False
        self.side=None
        self.id=0
    
    def __str__(self) -> str:
        return "Done: " + self.done + ", Side: " + self.side + ", ID: " + self.id

class ElyseAlgo():

    order_list=[]

    def __init__(self, exchange, symbol, logFile, gridLevel = 0.0, lowerPrice= 0.0, upperPrice= 0.0, amount=0, setSandbox = False) -> None:
        self.symbol = symbol;
        self.exchange = Exchange(exchange, setSandbox)
        self.fetcher = DataFetch(exchange, setSandbox)
        self.gridLevel = gridLevel
        self.upperPrice = upperPrice
        self.lowerPrice = lowerPrice
        self.amount = amount
        self.intervalProfit = (self.upperPrice - self.lowerPrice) / self.gridLevel
        self.logFile = logFile

    def myLogger(self, msg):
        timestamp = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S ")
        s = "[%s] %s:%s %s" % (timestamp, COLOR_WHITE, COLOR_RESET, msg)
        print(s)
        try:
            f = open(self.logFile, "a")
            f.write(s + "\n")
            f.close()
        except:
            pass
    
    async def placeOrderInit(self):
        #start cal level and place grid oreder
        for i in range(self.gridLevel + 1): #  n+1 lines make n grid
            price = self.lowerPrice + i * self.intervalProfit
            bid_price, ask_price = await self.sendRequest("get_bid_ask_price")
            order = Order_Info()
            if  price < ask_price : 
                order.id = await self.sendRequest("place_order","buy",price)
                self.myLogger("place buy order id = " + str(order.id) + " in "+ str(price))
            else:
                order.id = await self.sendRequest("place_order","sell",price)
                self.myLogger("place sell order id = " + str(order.id) + " in "+ str(price))
            self.order_list.append(order)
    
    async def loopJob(self):
        for order in self.order_list:
            order_info = await self.sendRequest("get_order",order.id)
            side = order_info["side"]
            if order_info["status"] == "closed":
                new_order_price = 0.0
                old_order_id = order_info["id"]
                bid_price, ask_price = await self.sendRequest("get_bid_ask_price")
                msg = side + " order id : " + str(old_order_id)+" : " + str(order_info["price"]) + " completed , put "
                if side == "buy" :
                    new_order_price = float(order_info["price"]) + self.intervalProfit 
                    order.id = await self.sendRequest("place_order","sell",new_order_price)
                    msg = msg + "sell"
                    self.myLogger(msg)
                else:
                    new_order_price = float(order_info["price"]) - self.intervalProfit
                    order.id = await self.sendRequest("place_order","buy",new_order_price)
                    msg = msg + "buy"
                msg = msg + " order id : " + str(order.id) + " : " + str(new_order_price)
                self.myLogger(msg)

    async def sendRequest(self, task, input1=None, input2=None):
        tries = 3

        for i in range(tries):
            try:
                if task == "get_bid_ask_price":
                    ticker = await self.fetcher.fetchTickers(self.symbol)
                    return ticker["bid"],  ticker["ask"]

                elif task == "get_order":
                    return (await self.fetcher.fetchOrder(input1))["info"]

                elif task == "place_order":
                    #sendRequest(self,task,input1=side,input2=price)
                    side = input1
                    price = input2
                    orderid=0
                    if side =="buy":
                        orderid = self.exchange.buy(self.symbol, "limit", self.amount, price)["info"]["orderId"]
                    else:
                        orderid = self.exchange.sell(self.symbol, "limit", self.amount, price)["info"]["orderId"]
                    return orderid

                else:
                    return None
            except ccxt.NetworkError as e:
                if i < tries - 1: # i is zero indexed
                    
                    self.myLogger("NetworkError , try last "+str(i) +"chances" + str(e))
                    time.sleep(0.5)
                    continue
                else:
                    self.myLogger(str(e))
                    raise
            except ccxt.ExchangeError as e:
                if i < tries - 1: # i is zero indexed
                    self.myLogger(str(e))
                    time.sleep(0.5)
                    continue
                else:
                    self.myLogger(str(e))
                    raise


# Example base class for other algorithms
class OtherAlgo() :
    def __init__(self) -> None:
        pass

    # ..... create other functions and such

