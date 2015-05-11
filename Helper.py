#!/opt/python/bin/python
import logging
import time
from ConfigParser import SafeConfigParser
from Cryptsy import Cryptsy

# Setup logging levels and format
class Log(object):
    def __init__(self, file='cryptsy.log'):
        FORMAT = '%(asctime)s %(levelname)s %(message)s'
        logging.basicConfig(filename=file,
                            level=logging.DEBUG,
                            format=FORMAT)
        
    def info(self, string):
        logging.info(string)

    def warning(self, string):
        logging.warning(string)

    def error(self, string):
        logging.error(string)

    def critical(self, string):
        logging.critical(string)

    def exception(self, string):
        FORMAT = '%(asctime)s %(levelname)s %(message)s %(funcName)s exc_info'
        logging.basicConfig(filename=file,
                            level=logging.DEBUG,
                            format=FORMAT)
        logging.exception(string)
        

# Read settings.ini configuration file and store values on instance variables
class Config(object):
    def __init__(self, file='settings.ini'):
        self.file = file
        self.parser = SafeConfigParser()
        self.configAll()

    # Method: configAll
    # Description: Configure and store all user settings based on settings.ini values
    def configAll(self):
        self.parser.read(self.file)

        # API keys
        self.publickey = self.parser.get('API', 'public')
        self.privatekey = self.parser.get('API', 'private')

        # Check if keys are valid        
        self.cryptsy = Cryptsy(self.publickey, self.privatekey)

        if self.cryptsy.getInfo()['success'] != '1':
            raise Exception('Cryptsy key pairs are invalid.')

        # Settings
        self.configSettings()

        # Trading
        self.configTrading()

        # Signals
        self.configSignals()
        
        # Markets
        self.configMarkets()

    # Method: configSettings
    # Description: Configure and store settings only based on settings.ini values
    def configSettings(self):
        self.parser.read(self.file)
        self.showTicker = self.parser.getboolean('Settings', 'showTicker')
        self.verbose = self.parser.getboolean('Settings', 'verbose')
        self.loopSleep = self.parser.getint('Settings', 'loopSleep')
        self.saveGraph = self.parser.getboolean('Settings', 'saveGraph')
        self.graphDPI = self.parser.getint('Settings', 'graphDPI')

    # Method: configTrading
    # Description: Configure and store trading only based on settings.ini values
    def configTrading(self):
        self.parser.read(self.file)
        self.simMode = self.parser.getboolean('Trading','simMode')
        self.min_volatility = self.parser.getfloat('Trading', 'min_volatility')
        self.volatility_sleep = self.parser.getint('Trading', 'volatility_sleep')
        self.longOn = self.parser.get('Trading','longOn')
        self.orderType = self.parser.get('Trading','orderType')
        self.fokTimeout = self.parser.getint('Trading', 'fokTimeout')
        self.fee = self.parser.getfloat('Trading', 'fee')

    # Method: configSignals
    # Description: Configure and store signals only based on settings.ini values
    def configSignals(self):
        self.parser.read(self.file)
        self.signalType = self.parser.get('Signals','signalType')
        if self.signalType == 'single':
            self.single = self.parser.get('Signals','single')
        elif self.signalType == 'dual':
            self.fast = self.parser.getint('Signals','fast')
            self.slow = self.parser.getint('Signals','slow')
        elif self.signalType == 'ribbon':
            self.ribbonStart = self.parser.get('Signals','ribbonStart')
            self.numRibbon = self.parser.get('Signals','numRibbon')
            self.ribbonSpacing = self.parser.get('Signals','ribbonSpacing')
        self.priceBand= self.parser.getboolean('Signals','priceBand')

    # Method: configMarkets
    # Description: Configure and store markets based on settings.ini values
    def configMarkets(self):
        self.parser.read(self.file)
        self.request= self.cryptsy.getMarkets()
        self.markets= {}

        # Check to see if there are new or removed markets.
        # If not, configure settings.
        self.marketsCryptsy = []
        for label in self.request['return']:
            self.marketsCryptsy.append(str(label['label']).upper())
        self.marketsSettings = [x[0].upper() for x in self.parser.items('Markets')]
        self.marketDiffC = list(set(self.marketsCryptsy) - set(self.marketsSettings))
        self.marketDiffS = list(set(self.marketsSettings) - set(self.marketsCryptsy))
        if (len(self.marketDiffC + self.marketDiffS) == 0):
            for market in self.marketsCryptsy:
                self.markets[market] = self.parser.getboolean('Markets', market)
        else:
            if (len(self.marketDiffC) > 0):
                print "ERROR: New Cryptsy market(s) found. Add %s to settings.ini." % self.marketDiffC
            if (len(self.marketDiffS) > 0):
                print "ERROR: Cryptsy market(s) removed. Remove %s from settings.ini." % self.marketDiffS
            raise Exception("Cryptsy markets sync with settings.ini markets mismatch.")

class Printing(object):
    def __init__(self,log,config,trader):
        # Access to instantiated classes
        self.log = log
        self.config = config
        self.trader = trader

    def separator(self,num=1):
        '''print a 79 char line separator, dashes'''
        for i in range(num):
            print('-')*79
    
    def displayBalance(self):
        '''Print significant balances, open orders'''
        orders = self.trader.tradeData.get('openOrders', 'Failed to read orderCount')
        if type(orders) == int and orders > 0: 
            print"Open Orders:",orders
            self.processOrders(printOutput=True)
            self.separator()
        print'Available Balances:'
        funds = self.trader.tradeData['funds']
        for bal in funds.keys():
            if funds[bal] >= 0.01:
                print bal.upper()+':',funds[bal]
        self.separator()

    def processOrders(self, printOutput = False):
        '''Duild dict of open orders, by native ID. Update global orderData'''
        orderData = self.trader.tradeData.get('orders',None)
        if orderData.get('success') == 0:
            orderData = self.trader.tapi.getOrders()
        if printOutput:
            try:
                for key in orderData.keys():
                    order = orderData[key]
                    print('ID: %s %s %s %s at %s' %(key,
                                                    order['market'],
                                                    order['type'],
                                                    order['amount'],
                                                    order['rate']))
            except TypeError as e:
                print'TypeError in processOrders:'
                print e
                logging.error('Type error in helper.processOrders: %s' % e)
                logging.info('orderData: %s' % orderData)
            except KeyError as e:
                print'KeyError in processOrders'
                print e
                logging.error('Key error in helper.processOrders: %s' % e)
                logging.info('orderData: %s' % orderData)
        return orderData

    def displayTicker(self):
        '''Display ticker for any configured markets'''
        for market in self.config.markets:
            if self.config.markets[market]:
                self.printTicker(market, self.trader.tickerData)

    def printTicker(self, market, tickerData):
        '''Modular print, prints all ticker values of one market'''
        data = self.trader.tickerData[market]
        first = market[:3].upper()
        second = market[4:].upper()
        print str(first)+'/'+str(second)+' Volume'
        print str(first),':',data['volCur'],second,':',data['vol']
        print'Last:',data['last'],'Avg:',data['avg']
        print'High:',data['high'],'Low:',data['low']
        print'Bid :',data['sell'],'Ask:',data['buy']
        self.separator()
        
