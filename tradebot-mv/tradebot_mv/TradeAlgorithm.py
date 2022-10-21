from turtle import color, done
import ccxt
import numpy as np
import pandas as pd
from DataFetch import DataFetch
from Exchange import Exchange
from matplotlib import pyplot as plt
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
    limitPrice = 0; 

    def __init__(self):
        self.done=False
        self.side=None
        self.id=0
    
    def __str__(self) -> str:
        return "Done: " + self.done + ", Side: " + self.side + ", ID: " + self.id

class ElyseAlgo():

    order_list=[]
    balanceData = np.array([])
    tradeCount = 0; 
    tradeCountData = np.array([])
    orderProfitData = np.array([0])
    
    # changing default plot size
    plt.rcParams["figure.figsize"] = (10,7)


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
        try:
            f = open(self.logFile, "a")
            f.write(s + "\n")
            f.close()
        except:
            pass
    
    async def performanceGrapH(self, symbol: str):
        print(self.tradeCountData.size)
        print(self.balanceData.size)
        while True:
            # checking each loop
            print("Loop in :", datetime.datetime.now())

            # updating info for grid
            await self.updateGrid()

            bid_price, ask_price = await self.sendRequest("get_bid_ask_price")

            lineFit = np.poly1d(np.polyfit(self.tradeCountData, self.balanceData, 1))
        
            plt.clf()

            plt.subplot(2,2,1)
            plt.plot(self.tradeCountData, self.balanceData, color="k", label="USDT Balance")
            plt.plot(self.tradeCountData, lineFit(self.tradeCountData), color="b", label="Account Balance Fit")

            plt.title("Account Balance Across Filled Orders")
            plt.xlabel("Filled Orders")
            plt.ylabel("Acount Balance (" + symbol + ")")
            
            plt.subplot(2,2,2) # two rows, two columns, second cell
            plt.bar(x=self.tradeCountData, height=self.orderProfitData, color=[('green' if p > 0 else 'red') for p in self.orderProfitData])
            plt.title("Profit of Filled Orders")
            plt.xlabel("Filled Orders")
            plt.ylabel("Profit (" + symbol + ")")

            plt.subplot(2,2,(3,4)) # two rows, two colums, combined third and fourth cell
            orderGridX = np.arange(len(self.order_list))
            orderGridY = np.array([x.limitPrice for x in self.order_list])
            plt.title("Visual Order Grid")
            plt.xlabel("Grid Level")
            plt.ylabel("Grid Level Price")
            
            plt.axhline(y=self.upperPrice, color="b", linestyle="dotted")
            plt.axhline(y=self.lowerPrice, color="k", linestyle="dotted")
            plt.axhline(y=ask_price, color="m", linestyle="dotted")
            plt.scatter(orderGridX, orderGridY, color=[('green' if p.side == "sell" else 'red') for p in self.order_list])
        
            majorTicks = np.arange(self.lowerPrice, self.upperPrice + 1, self.intervalProfit * 5);
            minorTicks = np.arange(self.lowerPrice, self.upperPrice + 1, self.intervalProfit)
            plt.yticks(majorTicks)
            plt.yticks(minorTicks, minor=True)
            plt.grid(True)
        
            plt.subplots_adjust(bottom=0.1,  
                        top=0.9,  
                        wspace=0.5,  
                        hspace=0.5)        
            plt.draw()
            plt.pause(0.01)

            plt.gca().lines.clear()
            time.sleep(1)


    async def placeOrderInit(self): 
         #start cal level and place grid oreder
        for i in range(self.gridLevel + 1): #  n+1 lines make n grid
            price = self.lowerPrice + i * self.intervalProfit
            bid_price, ask_price = await self.sendRequest("get_bid_ask_price")
            order = Order_Info()
            order.limitPrice = price;

            if  price < ask_price : 
                order.id = await self.sendRequest("place_order","buy",price)
                order.side = "buy"
                self.myLogger("place buy order id = " + str(order.id) + " in "+ str(price))
            else:
                order.id = await self.sendRequest("place_order","sell",price)
                order.side = "sell"
                self.myLogger("place sell order id = " + str(order.id) + " in "+ str(price))
            
            self.order_list.append(order)
        
        await self.updateTradeCount()
        
    async def updateGrid(self):
        bid_price, ask_price = await self.sendRequest("get_bid_ask_price")
        enterMarket = False

        if (enterMarket):
            self.enterMarket()

        else:

            if (ask_price > (self.upperPrice + self.intervalProfit * 2)): 
                self.takeProfit()
                enterMarket = True

            elif (ask_price < (self.lowerPrice - self.intervalProfit * 2)):
                self.stopLoss()
                enterMarket = True

            else: 
                for order in self.order_list:
                    order_info = await self.sendRequest("get_order",order.id, self.symbol)
                    side = order_info["side"].lower()
                    status = order_info["status"].lower()
            
                    if  status == "filled":   
                        await self.updateTradeCount()             
                        new_order_price = 0.0
                        old_order_id = order_info["orderId"]
                        bid_price, ask_price = await self.sendRequest("get_bid_ask_price")

                        msg = side + " order id : " + str(old_order_id)+" : " + str(order_info["price"]) + " completed , put "
                    
                        if side == "buy" :
                            self.orderProfitData = np.append(self.orderProfitData, -self.intervalProfit)
                            
                            new_order_price = float(order_info["price"]) + self.intervalProfit 
                            order.limitPrice = new_order_price
                            order.id = await self.sendRequest("place_order","sell",new_order_price)
                            order.side = "sell"
                            msg = msg + "sell"

                        else:
                            self.orderProfitData = np.append(self.orderProfitData, self.intervalProfit)
                        
                            new_order_price = float(order_info["price"]) - self.intervalProfit
                            order.limitPrice = new_order_price
                            order.id = await self.sendRequest("place_order","buy",new_order_price)
                            order.side = "buy"
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
                    return (await self.fetcher.fetchOrder(input1, input2))["info"]

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
                    return (await self.exchange.getAccountBalance())["total"][input1]

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

    async def stopLoss(self):
        coinAccountBalance = await self.sendRequest("get_balance", self.symbol.split("/")[0])
        stopLossOrderID = self.sendRequest("place_order", "sell", coinAccountBalance); 

        status = ""

        while(status != "filled"):
            self.myLogger("Waiting for StopLossOrder: " + stopLossOrderID + ", to be completed")
            order_info = await self.sendRequest("get_order",stopLossOrderID.id, self.symbol)
            status = order_info["status"].lower()

            time.sleep(5)

        self.myLogger("StopLossorder: " + stopLossOrderID + ", has been completed")
        

    async def updateTradeCount(self):
        accountBalance = await self.sendRequest("get_balance", "USDT")
        self.balanceData = np.append(self.balanceData, accountBalance)            


        self.tradeCount += 1   
        self.tradeCountData = np.append(self.tradeCountData, self.tradeCount)

    async def takeProfit(self):
        print("Taking profit!")
        self.myLogger("taking profit!")

    async def enterMarket(self):
        pass 

# Example base class for other algorithms
class OtherAlgo() :
    def __init__(self) -> None:
        pass

    # ..... create other functions and such

