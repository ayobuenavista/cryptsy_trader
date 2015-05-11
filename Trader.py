#!/usr/bin/python

import subprocess
import sys
import time
import traceback
from operator import itemgetter
import Helper
from Cryptsy import Cryptsy

"""
This is the main entry of the script.
"""
if __name__ == '__main__':
    config = Helper.Config()
    #log = Helper.Log()
    #printing = Helper.Printing()
    cryptsy = Cryptsy(config.publickey, config.privatekey)
    markets = cryptsy.getMarkets()

    """
    list = []
    for i in markets['return']:
        element = []
        element.append(int(i['marketid']))
        element.append(str(i['label']))
        list.append(element)

    final = sorted(list, key=itemgetter(0))
    for i in final:
        #print "%s" % (i[1])
        #print "self.pairs['%s'] = self.parser.getboolean('Markets', '%s')" % (i[1], i[1])
        print "%i %s" % (i[0], i[1])
    """
    info = cryptsy.getInfo()

    print info['return']['serverdatetime']
    for i in info['return']['balances_available']:
        if (float(info['return']['balances_available'][i]) > 0.0):
            print "%s balance: %s" % (i, info['return']['balances_available'][i])

    # TODO bot trading logic #
