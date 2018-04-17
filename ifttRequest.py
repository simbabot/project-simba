import requests
import socket


class IftttMessage:
    def __init__(self, stockname="_", price="_", quantity="_"):
        self.keykir = "cFWCCEmJgrHvRaAr50_4os"
        self.keysujit = "ebtClwlcqkeBf0YC1D8UUq8jpB1FxYUnCLmflmhxbT9"
        self.event = "Stock"
        # value2 = self.generateOrderValue("INFY", 100, 200)
        self.send2ifttt(self.keysujit, self.event, stockname, price, quantity)
        self.send2ifttt(self.keykir, self.event, stockname, price, quantity)

    def send2ifttt(self, key, event, value1="_", value2="_", value3="_"):
        if 'BNDA' == socket.gethostname()[:4]:
            proxies = {
                'http': 'EU\NG6E4BC:samePassword123%23@fr0-proxylan-vip.eu.airbus.corp:3128',
                'https': 'EU\NG6E4BC:samePassword123%23@fr0-proxylan-vip.eu.airbus.corp:3128',
            }
        else:
            proxies = {

            }

        headers = {
            'Content-Type': 'application/json',
        }

        data = "{\"value1 \":\"%s\",\"value2\":\"%s\",\"value3\":\"%s\"}" % (value1, value2, value3)
        # data = {"STOCK_NAME": value1,
        #         "PRICE": value2,
        #         "QUANTITY": value3}

        # print data
        # print 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(event, key)
        response = requests.post('http://maker.ifttt.com/trigger/{}/with/key/{}'
                                 .format(event, key), headers=headers, data=data, proxies=proxies)

    def generateOrderValue(self, symbol, price, qty):
        return symbol + "_p" + str(price) + "_q" + str(qty)


if __name__ == "__main__":
    # key = "cFWCCEmJgrHvRaAr50_4os"
    # event = "Stock"
    # value1 = "SELL"
    # send2ifttt(key,event,"SELL",value2)

    IftttMessage("airtel", 2.34, 34)
