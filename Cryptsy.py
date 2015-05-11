#!/opt/python/bin/python
import urllib
import urllib2
import json
import time
import hmac,hashlib

#Genererate time stamp for passed date string.
def TimeStamp(DateString, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(DateString, format))

class Cryptsy(object):
    def __init__(self, PublicKey, PrivateKey):
        self.PublicKey = PublicKey
        self.PrivateKey = PrivateKey

    # Method: Query
    # Description: Query method issues any supported request to CryptsyAPI.
    # {marketv2, orderdata, singlemarketdata, singleorderdata} are public methods and do not require an API key.
    # Inputs:
    #   method          Public method string name
    #   req             Dictionary with method parameters
    # Outputs:
    #   JSONResponse    Returns structered data response in JSON
    def Query(self, method, req={}):
        try:
            if (method == "marketdatav2" or method == "orderdata"):
                response = urllib2.urlopen(urllib2.Request('http://pubapi.cryptsy.com/api.php?method=' + method))
                JSONResponse = json.loads(response.read())
            elif (method == "singlemarketdata" or method == "singleorderdata"):
                response = urllib2.urlopen(urllib2.Request('http://pubapi.cryptsy.com/api.php?method=' + method + '&marketid=' + str(req['marketid'])))
                JSONResponse = json.loads(response.read())
            else:
                # Generate POST data string
                req['method'] = method
                req['nonce'] = int(time.time())
                post_data = urllib.urlencode(req)

                # Sign POST data string
                sign = hmac.new(self.PrivateKey, post_data, hashlib.sha512).hexdigest()

                # Extra headers for request
                headers = {
                    'Sign': sign,
                    'Key': self.PublicKey
                }

                response = urllib2.urlopen(urllib2.Request('https://api.cryptsy.com/api',post_data, headers))
                JSONResponse = json.loads(response.read())
   
                """
                # Add timestamps if there isnt one but is a datetime
                if('return' in JSONResponse):
                    if(isinstance(JSONResponse['return'], list)):
                        for x in xrange(0, len(JSONResponse['return'])):
                            if(isinstance(JSONResponse['return'][x], dict)):
                                if('datetime' in JSONResponse['return'][x] and 'timestamp' not in JSONResponse['return'][x]):
                                    JSONResponse['return'][x]['timestamp'] = float(TimeStamp(JSONResponse['return'][x]['datetime']))
                """
        except:
            raise Exception("Invalid response from Cryptsy.")
        return JSONResponse


    ### PUBLIC METHODS ###

    # Method: getGeneralMarketData
    # Description: Method that returns general market data.
    # Inputs:
    # Outputs:
    def getGeneralMarketData(self):
        return self.Query("marketdatav2")
    
    # Method: getSingleMarketData
    # Description: Method that returns market data of marketid.
    # Inputs:
    #   marketid        Market ID for which you are querying
    # Outputs:
    #   JSONResponse    Single market data JSON response
    def getSingleMarketData(self, marketid):
        return self.Query("singlemarketdata", {'marketid': marketid})

    # Method: getOrderbookData
    # Description: Method that returns general order data or single order data based on marketid.
    # Inputs:
    #   marketid        Market ID for which you are querying
    # Outputs:
    #   JSONREsponse    Orderbook data JSON response
    def getOrderbookData(self, marketid=None):
        if(marketid == None):
            return self.Query("orderdata")
        return self.Query("singleorderdata", {'marketid': marketid})
    
    ### END OF PUBLIC METHODS ###


    ### AUTHENTICATED METHODS ###

    # Method: getInfo
    # Description: Fetches general Cryptsy account information
    # Inputs: n/a
    # Outputs: 
    #   balances_available      Array of currencies and the balances availalbe for each
    #   balances_hold           Array of currencies and the amounts currently on hold for open orders
    #   servertimestamp         Current server timestamp
    #   servertimezone          Current timezone for the server
    #   serverdatetime          Current date/time on the server
    #   openordercount          Count of open orders on your account
    def getInfo(self):
        return self.Query('getinfo')


    # Method: getMarkets
    # Description: Fetches an array of active markets
    # Inputs: n/a
    # Outputs: 
    #   marketid                Integer value representing a market
    #   label                   Name for this market, for example: AMC/BTC
    #   primary_currency_code   Primary currency code, for example: AMC
    #   primary_currency_name   Primary currency name, for example: AmericanCoin
    #   secondary_currency_code Secondary currency code, for example: BTC
    #   secondary_currency_name Secondary currency name, for example: BitCoin
    #   current_volume          24 hour trading volume in this market
    #   last_trade              Last trade price for this market
    #   high_trade              24 hour highest trade price in this market
    #   low_trade               24 hour lowest trade price in this market
    #   created                 Datetime (EST) the market was created
    def getMarkets(self):
        return self.Query('getmarkets')


    # Method: myTransactions
    # Description: Fetches an array of Deposits and Withdrawals on your account 
    # Inputs: n/a
    # Outputs:
    #   currency                Name of currency account
    #   timestamp               The timestamp the activity posted
    #   datetime                The datetime the activity posted
    #   timezone                Server timezone
    #   type                    Type of activity. (Deposit / Withdrawal)
    #   address                 Address to which the deposit posted or Withdrawal was sent
    #   amount                  Amount of transaction (Not including any fees
    #   free                    Fee (if any) Charged for this Transaction (Generally only on Withdrawals)
    #   trxid                   Network Transaction ID (if available)
    def myTransactions(self):
        return self.Query('mytransactions')


    # Method: marketTrades
    # Description: Fetches an array of last 1000 Trades for this Market, in Date Decending Order 
    # Inputs:
    #   marketid                Market ID for which you are querying
    # Outputs:
    #   tradeid                 A unique ID for the trade
    #   datetime                Server datetime trade occurred
    #   tradeprice              The price the trade occurred at
    #   quantity                Quantity traded
    #   total                   Total value of trade (tradeprice * quantity)
    #   initiate_ordertype      The type of order which initiated this trade
    def marketTrades(self, marketid):
        return self.Query('markettrades', {'marketid': marketid})


    # Method: marketOrders
    # Description:  Fetches 2 Arrays. First array is sellorders listing current open sell orders
    #               ordered price ascending. Second array is buyorders listing current open buy
    #               orders ordered price descending. 
    # Inputs:
    #   marketid                Market ID for which you are querying
    # Outputs:
    #   sellprice               If a sell order, price which order is selling at
    #   buyprice                If a buy order, price the order is buying at
    #   quantity                Quantity on order
    #   total                   Total value of order (price * quantity)
    def marketOrders(self, marketid):
        return self.Query('marketorders', {'marketid': marketid})


    # Method: myTrades
    # Description: Fetches an array of your Trades for this Market, in Date Decending Order
    # Inputs:
    #   marketid                Market ID for which you are querying
    #   limit                   (optional) Limit the number of results. Default: 200
    # Outputs:  
    #   tradeid                 An integer identifier for this trade
    #   tradetype               Type of trade (Buy/Sell)
    #   datetime                Server datetime trade occurred
    #   tradeprice              The price the trade occurred at
    #   quantity                Quantity traded
    #   total                   Total value of trade (tradeprice * quantity)
    #   fee                     Fee Charged for this Trade
    #   initiate_ordertype      The type of order which initiated this trade
    #   order_id                Original order ID this trade was executed against
    def myTrades(self, marketid, limit=200):
        return self.Query('mytrades', {'marketid': marketid, 'limit': limit})

    # Method: allMyTrades
    # Description: Fetches an array your Trades for all Markets, in Date Decending Order
    # Inputs: n/a
    # Outputs: 
    #   tradeid                 An integer identifier for this trade
    #   tradetype               Type of trade (Buy/Sell)
    #   datetime                Server datetime trade occurred
    #   marketid                The market in which the trade occurred
    #   tradeprice              The price the trade occurred at
    #   quantity                Quantity traded
    #   total                   Total value of trade (tradeprice * quantity)
    #   fee                     Fee Charged for this Trade
    #   initiated_ordertype     The type of order which initiated this trade
    #   order_id                Original order ID this trade was executed
    #   against
    def allMyTrades(self):
        return self.Query('allmytrades')


    # Method: myOrders
    # Description: Fetches an array of your orders for this market listing your current open sell and buy orders.
    # Inputs:
    #   marketid                Market ID for which you are querying
    # Outputs:
    #   orderid                 Order ID for this order
    #   created                 Datetime the order was created
    #   ordertype               Type of order (Buy/Sell)
    #   price                   The price per unit for this order
    #   quantity                Quantity for this order
    #   total                   Total value of order (price * quantity)
    #   orig_quantity           Original Total Order Quantity
    def myOrders(self, marketid):
        return self.Query('myorders', {'marketid': marketid})


    # Method: depth
    # Description: Fetch an array of buy and sell orders on the market representing market depth.
    # Inputs:
    #   marketid                Market ID for which you are querying
    # Outputs:
    #   Format is:
    #       array(
    #           'sell'=>array(
    #               array(price,quantity), 
    #               array(price,quantity),
    #               ....
    #           ), 
    #           'buy'=>array(
    #               array(price,quantity), 
    #               array(price,quantity),
    #               ....
    #           )
    #       )
    def depth(self, marketid):
        return self.Query('depth', {'marketid': marketid})


    # Method: allMyOrders
    # Description: Fetches an array of all open orders for your account.
    # Inputs: n/a
    # Outputs: 
    #   orderid             Order ID for this order
    #   marketid            The Market ID this order was created for
    #   created             Datetime the order was created
    #   ordertype           Type of order (Buy/Sell)
    #   price               The price per unit for this order
    #   quantity            Quantity for this order
    #   total               Total value of order (price * quantity)
    #   orig_quantity       Original Total Order Quantity
    def allMyOrders(self):
        return self.Query('allmyorders')


    # Method: createOrder
    # Description: Sends a request to create an order on marketid
    # Inputs:
    #   marketid            Market ID for which you are creating an order for
    #   ordertype           Order type you are creating (Buy/Sell)
    #   quantity            Amount of units you are buying/selling in this order
    #   price               Price per unit you are buying/selling at
    # Outputs: 
    #   orderid             If successful, the Order ID for the order which was created
    def createOrder(self, marketid, ordertype, quantity, price):
        return self.Query('createorder', {'marketid': marketid, 'ordertype': ordertype, 'quantity': quantity, 'price': price})
    
    
    # Method: cancelOrder
    # Description: Sends a request to cancel an order on orderid
    # Inputs:
    #   orderid             Order ID for which you would like to cancel
    # Outputs: n/a
    #          If successful, it will return a success code. 
    def cancelOrder(self, orderid):
        return self.Query('cancelorder', {'orderid': orderid})

    
    # Method: cancelMarketOrders
    # Description: Sends a request to cancel all open orders on marketid
    # Inputs:
    #   marketid            Market ID for which you would like to cancel all open orders
    # Outputs: 
    #   return              Array for return information on each order cancelled
    def cancelMarketOrders(self, marketid):
        return self.Query('cancelmarketorders', {'marketid': marketid})


    # Method: cancelAllOrders
    # Description: Sends a request to cancel all open orders on all markets
    # Inputs: n/a
    # Outputs: 
    #   return              Array for return information on each order cancelled
    def cancelAllOrders(self):
        return self.Query('cancelallorders')

    # Method: calculateFees
    # Description: Sends a request to calculate fees and net profits
    # Inputs:
    #   ordertype           Order type you are calculating for (Buy/Sell)
    #   quantity            Amount of units you are buying/selling
    #   price               Price per unit you are buying/selling at
    # Outputs: 
    #   fee                 The that would be charged for provided inputs
    #   net                 The net total with fees
    def calculateFees(self, ordertype, quantity, price):
        return self.Query('calculatefees', {'ordertype': ordertype, 'quantity': quantity, 'price': price})


    # Method: generateNewAddress
    # Description: Generate new hash address for currencyid or currencycode
    # Inputs: (either currencyid OR currencycode required - you do not have to supply both)
    #   currencyid          Currency ID for the coin you want to generate a new address for (ie. 3 = BitCoin)
    #   currencycode        Currency Code for the coin you want to generate a new address for (ie. BTC = BitCoin)
    # Outputs: 
    #   address             The new generated address
    def generateNewAddress(self, currencyid=None, currencycode=None):
        if(currencyid != None):
            req = {'currencyid': currencyid}
        elif(currencycode != None):
            req = {'currencycode': currencycode}
        else:
            return None

        return self.Query('generatenewaddress', req)

    ### END OF AUTHENTICATED METHODS ####
