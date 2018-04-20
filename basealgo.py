import talib
import pandas as pd
import numpy as np
from collections import namedtuple
# from autostk import ZerodhaSelenium
# import matplotlib.pyplot as plt
#df1 = pd.DataFrame([[1,2],[3,4]],columns=['LTP','Time'])


class Simbha:
    def __init__(self, filename):
        self.filename = filename
        self.buy, self.sell = True, False               # buy is true because first buy and then sell
        self.shortbuy, self.shortsell = False, True     # shorting first sell and then buy
        self.stratliveTrade(self.filename)

    def round_nearest(self, x, a):
        return round(x / a) * a

    def ohlc(self, df):
        #df = pd.read_csv(filename)
        # df = pd.read_csv('intraday_1min_MSFT.csv')
        # df = df.iloc[::-1]
        #df.columns = ['price', 'time']
        df['timepass'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('timepass', inplace=True)
        dataOhlc = df['price'].resample('5Min').ohlc()
        # return df
        return dataOhlc

    def createOhlcFile(self, filename,timeframe):
        # stockdata = pd.read_csv(filename)
        # stocktimeprice = np.column_stack((stockdata['BHARTIARTL'].values, stockdata['TIME'].values))
        df = pd.read_csv(filename)
        # df = df.iloc[::-1]
        # columns = ['price', 'time']
        # df = pd.DataFrame(stocktimeprice, columns=columns)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # df.timestamp = df.timestamp.dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        # df.set_index('timepass', inplace=True)
        # dataOhlc = df['price'].resample(str(timeframe)+'Min').ohlc()
        # dataOhlc.to_csv(filename.split('.csv')[0] + "ohlc.csv")
        return df
        # return dataOhlc

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
        return df

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
        # df["Bullishwithoutwick"] = bullishCandleWithWick
        # df["Bullish"] = bullishCandle
        # df['BullishShit1'] = bullishCandle.shift(1)
        # df["bullishCandleWithWick"] = bullishCandleWithWick
        # df["Bearishwithoutwick"] = bearishCandleWithWick
        # df["bullishCandle"] = bullishHeikinCandle
        # df["Bearish"] = bearishCandle
        # buy logic
        bullishHeikinCandleShift2 = bullishHeikinCandle.shift(1)
        buysignal = bullishHeikinCandle & bullishHeikinCandleShift2
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

        # buy logic starts
        # check if already bought or not if not bought check the current signal if true buy and append it to buy list
        # once bought make self.buy false until you sell the stock
            if self.buy:
                if currentbuysignal:
                    buy.append(True)   # place the kite buy here
                    self.buy = False
                    self.sell = True
                else:
                    buy.append(False)
            else:
                # if not self.sell:
                buy.append(False)
                # if currentsellsignal:
                #     self.buy = True
            # sell logic
            # check the stock is sold first. If not sold append false to sell list.
            # if stock is sold then check for current sell signal.
            if self.sell:
                if currentsellsignal:
                    sell.append(True)
                    self.buy = True
                    self.sell = False
                else:
                    sell.append(False)
            else:
                sell.append(False)
                self.buy = True
            # shorting sell logic starts
            # check if already sell or not if not sell check the current signal.
            # if true sell and append it to shortsell list
            # once bought make self.buy false until you sell the stock

            if self.shortsell:
                if currentshortsellsignal:
                    shortsell.append(True)
                    self.shortsell = False
                    self.shortbuy = True
                else:
                    shortsell.append(False)
            else:
                shortsell.append(False)

            if self.shortbuy:
                if currentshortbuysignal:
                    shortbuy.append(True)
                    self.shortsell = True
                    self.shortbuy = False
                else:
                    shortbuy.append(False)
            else:
                shortbuy.append(False)
                self.shortsell = True

        df['buy'] = pd.Series(buy)
        df['sell'] = pd.Series(sell)
        df['ShortSell'] = pd.Series(shortsell)
        df['ShortBuy'] = pd.Series(shortbuy)
        pass

    def startTrade(self, df):
        hadf = self.HA(df)
        emadf = self.EMA(hadf)
        self.trades(emadf)

    def stratliveTrade(self, filename):
        ohlcdf = self.createOhlcFile(filename, 10)
        df1 = ohlcdf
        # for oneohlc in ohlcdf.iterrows():
        #     if 'close' in df1:
        #         self.previousindex = df1['close'].count()
        #     else:
        #         self.previousindex = 0
        #     TIME = oneohlc[1][0]
        #     openi = oneohlc[1][1]
        #     high = oneohlc[1][2]
        #     low = oneohlc[1][3]
        #     close = oneohlc[1][4]
        #     data = pd.Series([TIME, openi, high, low, close], index=['TIME', 'open', 'high', 'low', 'close'])
        #     df1 = df1.append(data, ignore_index=True)
        self.lastindex = df1['close'].count()
        self.startTrade(df1)
            # print (index)
        df1.timestamp = pd.to_datetime(df1.timestamp).dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        # df1.to_csv('dataforalo.csv', sep='\t', encoding='utf-8')
        print('working')


if __name__ == '__main__':
    filename = r'C:\Users\NG6E4BC\workspace\Simba_Bot\sitePackages\TECHM10min_April_1to19_2018Copy.csv'
    driver = "C:\Users\NG6E4BC\Documents\DoNotDelete\chromedriver_win32\chromedriver.exe"

    Simbha(filename)
