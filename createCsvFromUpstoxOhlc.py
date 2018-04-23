import time
import csv
import os


while True:
    time.sleep(5 * 60)
    textfile = r"C:\Users\NG6E4BC\Downloads\Techm.json"
    if os.path.exists(textfile):
        with open(textfile, 'r') as myfile:
            data = myfile.read().replace('\n', '')
        # filename = r'C:\Users\NG6E4BC\workspace\Simba_Bot\OHLCdata\TECHM10min_April_1to19_2018.json'
        # data = json.load(open(filename))
        # data = data[u'data']
        data = eval(data)
        ohlc = []
        for one in data['x']:
            ohlc.append([one[u'timestamp'], one[u'open'], one['high'], one['low'], one['close']])
        with open("TECHM5min.csv", 'wb') as resultFile:
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerow(['timestamp', 'open', 'high', 'low', 'close'])
            wr.writerows(ohlc)
        os.remove(textfile)
