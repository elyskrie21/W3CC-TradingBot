import numpy as np
import pandas as pd
from SendRequest import SendRequest
from SendRequest import SendRequest
from Logger import myLogger
from matplotlib import pyplot as plt
import time
import datetime
import ccxt

# In this class we can all creat our own trading algoritms which will be tested later on
# These classes don't fetch their own data, but rather each algo while use the DataFetch and Exchange classes

# Testing the grid trading algo to start since its easy to understand and implements
# Will create a more complex/custom solution later. 

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

    # buy prices
    upperPrice = 0
    lowerPrice = 0
    intervalProfit = 0
    reenterMarket = False
    
    # changing default plot size
    plt.rcParams["figure.figsize"] = (10,7)


    def __init__(self, exchange, symbol, logFile, gridLevel = 0.0, amount=0, setSandbox = False) -> None:
        self.symbol = symbol;
        self.gridLevel = gridLevel
        self.logFile = logFile
        self.sendRequest = SendRequest(symbol, exchange, amount, logFile, setSandbox)
    
    async def setBuyPrice(self):
        bidPrice, askPrice = await self.sendRequest.req("get_bid_ask_price");
        self.upperPrice = askPrice + 25
        self.lowerPrice = askPrice - 25
        self.intervalProfit = (self.upperPrice - self.lowerPrice) / self.gridLevel
    
    async def performanceGrapH(self, symbol: str):
        while True:
            # checking each loop
            print("Loop in :", datetime.datetime.now())

            # updating info for grid
            await self.updateGrid()

            bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")

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
        await self.setBuyPrice()

         #start cal level and place grid oreder
        for i in range(self.gridLevel + 1): #  n+1 lines make n grid
            price = self.lowerPrice + i * self.intervalProfit
            bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")
            order = Order_Info()
            order.limitPrice = price;

            if  price < ask_price : 
                order.id = await self.sendRequest.req("place_order","buy",price)
                order.side = "buy"
                myLogger("place buy order id = " + str(order.id) + " in "+ str(price), self.logFile)
            else:
                order.id = await self.sendRequest.req("place_order","sell",price)
                order.side = "sell"
                myLogger("place sell order id = " + str(order.id) + " in "+ str(price), self.logFile)
            
            self.order_list.append(order)
        
        await self.updateTradeCount()
        
    async def updateGrid(self):
        bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")

        if (self.reenterMarket):
            await self.enterMarket()

        else:

            if (ask_price > self.upperPrice): 
                await self.exitMarket("takeProfitOrder")
                self.reenterMarket = True

            elif (ask_price < self.lowerPrice):
                await self.exitMarket("stopLossOrder")
                self.reenterMarket = True

            else: 
                for order in self.order_list:
                    order_info = await self.sendRequest.req("get_order",order.id, self.symbol)
                    side = order_info["side"].lower()
                    status = order_info["status"].lower()
            
                    if  status == "filled":   
                        await self.updateTradeCount()             
                        new_order_price = 0.0
                        old_order_id = order_info["orderId"]
                        bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")

                        msg = side + " order id : " + str(old_order_id)+" : " + str(order_info["price"]) + " completed , put "
                    
                        if side == "buy" :
                            self.orderProfitData = np.append(self.orderProfitData, -self.intervalProfit)
                            
                            new_order_price = float(order_info["price"]) + self.intervalProfit 
                            order.limitPrice = new_order_price
                            order.id = await self.sendRequest.req("place_order","sell",new_order_price)
                            order.side = "sell"
                            msg = msg + "sell"

                        else:
                            self.orderProfitData = np.append(self.orderProfitData, self.intervalProfit)
                        
                            new_order_price = float(order_info["price"]) - self.intervalProfit
                            order.limitPrice = new_order_price
                            order.id = await self.sendRequest.req("place_order","buy",new_order_price)
                            order.side = "buy"
                            msg = msg + "buy"

                        msg = msg + " order id : " + str(order.id) + " : " + str(new_order_price)
                        myLogger(msg, self.logFile)


    async def exitMarket(self, sellType):
        bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")
        stopLossOrderID = 0   
        status = ""

        myLogger("Starting: " + sellType, self.logFile)
        
        while (stopLossOrderID == 0 or (ask_price < self.upperPrice and ask_price > self.lowerPrice)):
            try:
                stopLossOrderID = await self.sendRequest.req("exit_market")
            
            except ccxt.NetworkError as e:
                myLogger("NetworkError , " + str(e), self.logFile)
                time.sleep(3)
            except ccxt.ExchangeError as e:
                myLogger(str(e), self.logFile)
                time.sleep(3)

        if (stopLossOrderID != 0):
            while(status != "filled"):
                myLogger("Waiting for " + sellType + ": " + stopLossOrderID + ", to be completed", self.logFile)
                order_info = await self.sendRequest.req("get_order",stopLossOrderID.id, self.symbol)
                status = order_info["status"].lower()

                time.sleep(5)
            
            myLogger(sellType + ": " + stopLossOrderID + ", has been completed", self.logFile)
            
        else:
            myLogger(sellType + " was not completed: price re-entered grid", self.logFile)    

    async def updateTradeCount(self):
        accountBalance = await self.sendRequest.req("get_balance", "USDT")
        self.balanceData = np.append(self.balanceData, accountBalance)            


        self.tradeCount += 1   
        self.tradeCountData = np.append(self.tradeCountData, self.tradeCount)

    async def enterMarket(self):
        print("Entering market")
        myLogger("Entering market", self.logFile) 

# Example base class for other algorithms
class OtherAlgo() :
    def __init__(self) -> None:
        pass

    # ..... create other functions and such

