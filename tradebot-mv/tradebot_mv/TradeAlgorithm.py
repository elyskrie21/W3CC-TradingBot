import numpy as np
import pandas as pd
from SendRequest import SendRequest
from SendRequest import SendRequest
from Logger import myLogger
from matplotlib import pyplot as plt
import time
import datetime
import ccxt
from sklearn.linear_model import HuberRegressor
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
    orderProfitData = [0] * 2

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
        self.upperPrice = askPrice + (self.gridLevel / 2);
        self.lowerPrice = askPrice - (self.gridLevel / 2)
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
            plt.bar(x=["Sells", "Buys"], height=self.orderProfitData, color=["green", "red"])
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
        bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")
        myLogger("Starting account balance: " + str(ask_price), self.logFile); 

        await self.setBuyPrice()

        # Since when starting the bot there would be no coin balance 
        # We need to buy some in order to creqte the sell orders needed

        setUpId = await self.sendRequest.req("enter_market", (self.gridLevel / 2) + 1)
        order_info = await self.sendRequest.req("get_order",setUpId, self.symbol)
        status = order_info["status"].lower()
        tries = 0; 
        

        while(status != "filled"):
            myLogger("Waiting for enter_market order, to be completed", self.logFile)
            order_info = await self.sendRequest.req("get_order",setUpId, self.symbol)
            status = order_info["status"].lower()

            if (tries == 60):
                self.reenterMarket = True
                return

            tries += 1
            time.sleep(1)

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
            reEnter = await self.enterMarket()
            
            if (reEnter): 
                self.reenterMarket = False
                myLogger("Re-Enter Market Succeed", self.logFile)

                await self.placeOrderInit()
            else:
                myLogger("Re-Enter Market Failed", self.logFile)


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
                            self.orderProfitData[1] += 1
                            
                            new_order_price = float(order_info["price"]) + self.intervalProfit 
                            order.limitPrice = new_order_price
                            order.id = await self.sendRequest.req("place_order","sell",new_order_price)
                            order.side = "sell"
                            msg = msg + "sell"

                        else:
                            self.orderProfitData[0] += 1
                                                    
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
            #  We should cancel all open orders when 
            await self.cancelOrders()

            while(status != "filled"):
                myLogger("Waiting for " + sellType + ": " + stopLossOrderID + ", to be completed", self.logFile)
                order_info = await self.sendRequest.req("get_order",stopLossOrderID, self.symbol)
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
        data = []

        for i in range(1000):
            bid_price, ask_price = await self.sendRequest.req("get_bid_ask_price")
            data.append(ask_price); 
            time.sleep(1)

        y = np.array(data, dtype=float)
        x = np.array(list(range(0, y.size)))

        std = np.std(y); 

        A = np.vstack([x, np.ones(x.size)]).T
        epsilon = 1.75
        huber = HuberRegressor(alpha=0.0, epsilon=epsilon)
        huber.fit(A, y)
        huber.predict(A)

        myLogger("EnterMarket Data: (Coef: " + huber.coef_[0] + "), (STD: " + std + ")", self.logFile)
        if (huber.coef_[0] > 0 and std < 1):
            return True
        
        return False

        
    
    async def cancelOrders(self):
        for order in self.order_list:
            order_info = await self.sendRequest.req("cancel_order",order.id, self.symbol)
            if (type(order_info) is str):
                myLogger("Attempting to cancel order: " + order.id + ", has resulted in the status of: OrderNotFound", self.logFile)
            else:         
                status = order_info["status"].lower()
                myLogger("Attempting to cancel order: " + order.id + ", has resulted in the status of: " + status, self.logFile)

# Example base class for other algorithms
class OtherAlgo() :
    def __init__(self) -> None:
        pass

    # ..... create other functions and such

