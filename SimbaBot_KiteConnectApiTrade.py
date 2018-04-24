import os
import time
import datetime
import socket
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
from SimbaBot_ZerodhaSelenium import ZerodhaSelenium
# from SimbaBot_MongoDbObject import MongoDbSetup
from SimbaBot_ZerodhaMargin import ZerodhaMargin
from SimbaBot_TradeAlgorithNew import SimbhaBrain
# from SimbaBot_DbObject import DbObject


class KiteConnectApiTrade:
    def __init__(self):
        self.apikey = "yw8yelu5bpfel8ib"
        self.user = "YK8879"
        self.apisecret = "vaddqe1qb3lzorst3uolc1ptdo0l2cku"
        self.loginurl = "https://kite.trade/connect/login?api_key=yw8yelu5bpfel8ib&v=3"
        dirpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        dt = datetime.datetime.fromtimestamp(int(time.time())).strftime('_%Y_%m_%d')
        self.fullstockdata = os.path.join(dirpath, 'csvData', "21STocks_" + dt+".csv")
        self.stocktouse = os.path.join(dirpath, 'csvData', "StocksNamewithInstrument.csv")
        if os.name == 'nt':
            self.filename = os.path.join(dirpath, 'driver', 'chromedriver.exe')
        else:
            self.filename = os.path.join(dirpath, 'driver', 'chromedriver')
        if 'BNDA' == socket.gethostname()[:4]:
            r_proxy = {
                'http': 'EU\NG6E4BC:samePassword123%23@fr0-proxylan-vip.eu.airbus.corp:3128',
                'https': 'EU\NG6E4BC:samePassword123%23@fr0-proxylan-vip.eu.airbus.corp:3128',
            }
        else:
            r_proxy = {

            }
        self.stockbuyindex = {}  # to keep track of index at which it was bought
        self.publictoken = ''  # this public token not the access token
        self.starttime = time.time()
        self.marginurl = "https://api.kite.trade/margins/equity"
        self.stock = pd.read_csv(self.stocktouse)
        self.stock = self.stock.values
        # self.stockname = self.mog.get500stockName(self.db)
        self.stockmargin = {}
        self.starttime = time.time()
        self.kite = KiteConnect(api_key=self.apikey, proxies=r_proxy)
        self.kiteConnection()

    def margin(self, url):
        mar = ZerodhaMargin(url)
        mardata = mar.getReguest()
        for one in mardata:
            if str(one[u'tradingsymbol']) in self.stock[:, 1]:
                stockind = np.where(self.stock[:, 1] == str(one[u'tradingsymbol']))[0]
                self.stockmargin[int(self.stock[stockind, 0])] = one[u'mis_multiplier']
        print('margin working')

    def kiteConnection(self):
        sel = ZerodhaSelenium(self.filename, self.loginurl, self.apikey, self.apisecret)
        self.kite.set_access_token(sel.token["access_token"])
        while True:
            now = datetime.datetime.now()
            today9_15am = now.replace(hour=9, minute=15, second=0)
            if now >= today9_15am:
                currtime = time.time()
                timedifff = (5*60) + 5
                # time.sleep(timedifff)
                # sel = ZerodhaSelenium(self.filename, self.loginurl, self.apikey, self.apisecret)
                # self.kite.set_access_token(sel.token["access_token"])
                # ltp = self.kite.ltp(self.stock)
                self.margin(self.marginurl)
                # stockdata = pd.read_csv(self.fullstockdata)
                # stockdata = stockdata.drop(stockdata.index[len(stockdata)-1])
                stockdata = pd.read_csv(r'C:\Users\NG6E4BC\workspace\Simba_Bot\sitePackages\TECHM5min.csv')
                fileis = r'C:\Users\NG6E4BC\workspace\Simba_Bot\sitePackages\TECHM5min.csv'
                # stocktimeprice = np.column_stack((stockdata['TECHM'].values, stockdata['TIME'].values))
                stocktimeprice = stockdata
                try:
                    cash = self.kite.margins('equity')[u'available'][u'cash']
                except Exception as e:
                    cash = 1500
                # for stock in self.stock:
                stock = "3465729"
                bidbuysell = self.kite.quote("NSE", stock)
                if stock not in self.stockbuyindex:
                    self.stockbuyindex[stock] = []
                SimbhaBrain(fileis, stocktimeprice, self.kite, stock, self.stockmargin, bidbuysell, cash, self.stockbuyindex)
                self.starttime = time.time()
                x = "trade finish " + str(self.starttime - currtime) + '\n'
                with open("traderecord.txt", "a") as myfile:
                    myfile.write(str(x))
                # print(self.starttime - currtime)


if __name__ == '__main__':
    kt = KiteConnectApiTrade()
