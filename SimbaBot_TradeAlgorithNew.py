import talib
import time
import pandas as pd
import numpy as np
from collections import namedtuple
from SimbaBot_Ifttt import IftttMessage


class SimbhaBrain:
    def __init__(self, filename, ohlc, kiteapi, stockinstrument, stockmargin, bidbuysell, cash, stockbuycheck):
        self.ohlc = ohlc                                # OHLC data of stock
        self.filename = filename
        self.kiteapi = kiteapi                          # kite api
        self.stockinstrument = "TECHM"          # stock symbol or number
        self.stockmargin = stockmargin                  # stock margin
        self.bidbuysell = bidbuysell[unicode(stockinstrument)]  # buy/sell bid data of stock
        self.cash = cash                                # Cash to available to buy the stock
        self.stockbuycheck = stockbuycheck[stockinstrument]   # index to keep track of stock buy. to avoid repetation
        self.buy, self.sell = True, False               # buy is true because first buy and then sell
        self.shortbuy, self.shortsell = False, True     # shorting first sell and then buy
        self.buynowindex, self.sellnowindex = 0, 0      # index to keep track of OHLC and TIME
        self.shortsellnowindex, self.shortbuynowindex = 0, 0    # # index to keep track of OHLC and TIME
        self.stratliveTrade(self.filename)

    def createOhlcFile(self, filename):
        df = pd.read_csv(filename)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def HA(self, df):
        df['HA_Close'] = (df['open'] + df['high'] + df['low']+df['close'])/4
        hkOpen, hkclose = [], []
        nt = namedtuple('nt', ['open', 'close'])
        previous_row = nt(df.ix[0, 'open'], df.ix[0, 'close'])
        i = 0
        for row in df.itertuples():
            ha_open = (previous_row.open + previous_row.close) / 2
            hkOpen.append(previous_row[0])
            hkclose.append(previous_row[1])
            df.ix[i, 'HA_Open'] = ha_open
            previous_row = nt(ha_open, row.close)
            i += 1

        df['HA_High'] = df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
        df['HA_Low'] = df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
        df['HA_OldOPEN'] = pd.Series(np.array(hkOpen), index=df.index)
        df['HA_OldCLOSE'] = pd.Series(np.array(hkclose), index=df.index)
        return df.round(2)

    def EMA(self, df):
        df['EMA7'] = talib.EMA(df.close.values, timeperiod=5)
        df['EMA14'] = talib.EMA(df.close.values, timeperiod=10)
        return df

    def trades(self, df):
        # Heikin-Ashi bullish candle. with down wick == 0
        bullishHeikinCandle = (df['HA_Close'] > df['HA_Open']) & (df['HA_Low'] == df['HA_Open'])
        # Heikin-Ashi bearish candle. with up wick == 0
        bearishHeikinCandle = (df['HA_Close'] < df['HA_Open']) & (df['HA_High'] == df['HA_Open'])
        # Heikin-Ashi bullish candle
        bullishCandleWithWick = df['HA_Close'] > df['HA_Open']
        # Heikin-Ashi bearish candle
        bearishCandleWithWick = df['HA_Close'] < df['HA_Open']
        # buy logic
        bullishHeikinCandleShift2 = bullishHeikinCandle.shift(1)
        buysignal = bullishHeikinCandle & bullishHeikinCandleShift2
        df.timestamp = pd.to_datetime(df.timestamp).dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        df1 = pd.DataFrame()
        df1['BuySignal'] = buysignal
        df1['SellSignal'] = bearishCandleWithWick
        df1['bullishHeikinCandle'] = bullishHeikinCandle
        bearishHeikinCandleShift2 = bearishHeikinCandle.shift(1)
        shortsellsignal = bearishHeikinCandle & bearishHeikinCandleShift2
        df1['ShortsellSignal'] = shortsellsignal
        df1['ShortbuySignal'] = bullishCandleWithWick
        buy, sell = [], []
        shortsell, shortbuy = [], []
        for onerow in df1.iterrows():
            currentbuysignal = onerow[1]['BuySignal']
            currentsellsignal = onerow[1]['SellSignal']
            currentshortsellsignal = onerow[1]['ShortsellSignal']
            currentshortbuysignal = onerow[1]['ShortbuySignal']
            currentIndex = onerow[0]  # current index to buy the stock
            # buy logic
            self.buyStock(df, currentbuysignal, buy, currentIndex)
            # sell logic
            self.sellStock(df, currentsellsignal, sell, currentIndex)
            # short sell logic
            self.shortsellStock(df, currentshortsellsignal, shortsell, currentIndex)
            # short buy logic
            self.shortbuyStock(df, currentshortbuysignal, shortbuy, currentIndex)

        df['buy'] = pd.Series(buy)
        df['sell'] = pd.Series(sell)
        df['ShortSell'] = pd.Series(shortsell)
        df['ShortBuy'] = pd.Series(shortbuy)
        return df

    def buyStock(self, df, currentbuysignal, buy, currentIndex):
        # buy logic starts
        # check if already bought or not if not bought check the current signal if true buy and append it to buy list
        # once bought make self.buy false until you sell the stock
        if self.buy:
            if currentbuysignal:
                buy.append(True)  # place the kite buy here
                self.buy = False
                self.sell = True
                print('buy')
                self.buynowindex = currentIndex
                if self.buynowindex not in self.stockbuycheck:  # to stop repetation on buying the same stock
                    self.placeOrder("BUY", self.stockinstrument, df['open'][self.buynowindex],
                                    self.buynowindex, 'BUY')  # placeorder
                    IftttMessage(self.stockinstrument, df['open'][self.buynowindex], 'BUY')
                    self.stockbuycheck.append(self.buynowindex)
                    print('buy price ', df['open'][self.buynowindex], 'buy index ', self.buynowindex)
            else:
                buy.append(False)
        else:
            buy.append(False)

    def sellStock(self, df, currentsellsignal, sell, currentIndex):
        # sell logic
        # check the stock is sold first. If not sold append false to sell list.
        # if stock is sold then check for current sell signal.
        if self.sell:
            if currentsellsignal:
                sell.append(True)
                self.buy = True
                self.sell = False
                print('sell')
                self.sellnowindex = currentIndex
                if self.sellnowindex not in self.stockbuycheck:
                    self.placeOrder("SELL", self.stockinstrument, df['open'][self.sellnowindex],
                                    self.sellnowindex, 'SELL')  # placeorder
                    IftttMessage(self.stockinstrument, df['open'][self.sellnowindex], 'SELL')
                    self.stockbuycheck.append(self.sellnowindex)
                    print('sell price ', df['open'][self.sellnowindex], 'sell index ', self.sellnowindex)
            else:
                sell.append(False)
        else:
            sell.append(False)
            self.buy = True

    def shortsellStock(self, df, currentshortsellsignal, shortsell, currentIndex):
        # check if already sell or not if not sell check the current signal.
        # if true sell and append it to shortsell list
        # once bought make self.buy false until you sell the stock
        if self.shortsell:
            if currentshortsellsignal:
                shortsell.append(True)
                self.shortsell = False
                self.shortbuy = True
                print('shorsell')
                self.shortsellnowindex = currentIndex
                if self.shortsellnowindex not in self.stockbuycheck:
                    self.placeOrder("SELL", self.stockinstrument, df['open'][self.shortsellnowindex],
                                    self.shortsellnowindex, 'ShortSell')  # placeorder
                    IftttMessage(self.stockinstrument, df['open'][self.shortsellnowindex], 'ShortSell')
                    self.stockbuycheck.append(self.shortsellnowindex)
                    print('short sell price ', df['open'][self.shortsellnowindex],
                          'ShortSell index ', self.shortsellnowindex)
            else:
                shortsell.append(False)
        else:
            shortsell.append(False)

    def shortbuyStock(self, df, currentshortbuysignal, shortbuy, currentIndex):
        if self.shortbuy:
            if currentshortbuysignal:
                shortbuy.append(True)
                self.shortsell = True
                self.shortbuy = False
                print('shorbuy')
                self.shortbuynowindex = currentIndex
                if self.shortbuynowindex not in self.stockbuycheck:
                    self.placeOrder("BUY", self.stockinstrument, df['close'][self.shortbuynowindex],
                                    self.shortbuynowindex, 'ShortBuy')  # placeorder
                    IftttMessage(self.stockinstrument, df['close'][self.shortbuynowindex], 'ShortBuy')
                    self.stockbuycheck.append(self.shortbuynowindex)
                    print ('short Buy', df['close'][self.shortbuynowindex], 'ShortBuy Index ', self.shortbuynowindex)
            else:
                shortbuy.append(False)
        else:
            shortbuy.append(False)
            self.shortsell = True

    def placeOrder(self, tr_type, symbol, buyprice, buyindex, transctiontype):
        # if self.stockinstrument in self.stockmargin:
        #     actualcash = self.cash * self.stockmargin[self.stockinstrument]
        # else:
        #     actualcash = self.cash
        # prc = self.bidbuysell[u'last_price']
        # if tr_type == 'BUY':
        #     buyprice, buyquantity, sellprice, sellquantiy = self.getbidpriceandquantity()
        #     # buyprice = buybid[u'price']
        #     quantity = buyquantity
        #     if buyprice < prc:
        #         prc = buyprice
        #
        # else:
        #     buyprice, buyquantity, sellprice, sellquantiy = self.getbidpriceandquantity()
        #     # sellprice = sellbid[u'price']
        #     quantity = sellquantiy
        #     if sellprice > prc:
        #         prc = sellprice
        # if prc == 0:
        #     prc = 10
        # qty = actualcash / float(prc)
        # if qty > quantity:
        #     qty = quantity
        try:
            prc = buyprice
            self.kiteapi.place_order(variety="regular",
                                    tradingsymbol=symbol,
                                    quantity=1,
                                    price=prc,
                                    transaction_type=tr_type,
                                    order_type="SL",
                                    trigger_price=prc,
                                    validity="DAY",
                                    exchange="NSE",
                                    product ="MIS")

            x = "Order placed. " + str(transctiontype) + " at " + str(prc) + " and qunatity " + str(1) + "time " \
                + str(time.time()) + '\n'
            with open("buyrecord.txt", "a") as myfile:
                myfile.write(str(x))
        except Exception as e:
            x = "Order exception " + str(e) + '\n'
            with open("buyrecordexception.txt", "a") as myfile:
                myfile.write(str(x))

    def getbidpriceandquantity(self):
        buybid = self.bidbuysell[u'depth'][u'buy'][:2]
        sellbid = self.bidbuysell[u'depth'][u'sell'][:2]
        buyprice, buyquantity, sellprice, sellquantiy = 0, 0, 0, 0
        for bu in buybid:
            buyprice = buyprice + bu[u'price']
            buyquantity = buyquantity + bu[u'quantity']

        for sl in sellbid:
            sellprice = sellprice + sl[u'price']
            sellquantiy = sellquantiy + sl[u'quantity']

        buyprice, buyquantity, sellprice, sellquantiy = buyprice/2, buyquantity/2, sellprice/2, sellquantiy/2
        return buyprice, buyquantity, sellprice, sellquantiy

    def startTrade(self, df):
        hadf = self.HA(df)
        # emadf = self.EMA(hadf)
        df = self.trades(hadf)
        return df

    def stratliveTrade(self, filename):
        ohlcdf = self.createOhlcFile(filename)
        df1 = self.startTrade(ohlcdf)
        # df1.timestamp = pd.to_datetime(df1.timestamp).dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        # df1.to_csv('dataforalo.csv', sep='\t', encoding='utf-8')
        print('working')


if __name__ == '__main__':
    filename = r'C:\Users\NG6E4BC\workspace\Simba_Bot\sitePackages\TECHM10min_April_1to19_2018.csv'
    driver = "C:\Users\NG6E4BC\Documents\DoNotDelete\chromedriver_win32\chromedriver.exe"

    SimbhaBrain(filename)

