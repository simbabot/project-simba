import logging
import requests
from kiteconnect import KiteConnect
r_proxy = {'http': r'EU\NG6EADA:Password123%25@fr0-proxylan-vip.eu.airbus.corp:3128',
           'https': r'EU\NG6EADA:Password123%25@fr0-proxylan-vip.eu.airbus.corp:3128' }

kite_api_key = "yw8yelu5bpfel8ib"
kite_api_secret = "vaddqe1qb3lzorst3uolc1ptdo0l2cku"

logging.basicConfig(level=logging.DEBUG)

kite = KiteConnect(api_key="yw8yelu5bpfel8ib",proxies=r_proxy)
kite_api_key = "yw8yelu5bpfel8ib"
kite_api_secret = "vaddqe1qb3lzorst3uolc1ptdo0l2cku"

kite = KiteConnect(api_key="yw8yelu5bpfel8ib",proxies=r_proxy)


#rq = kite.generate_session("WfebfEp4bKQ5hG7a8mS0a7H0cs0Wvd9g","vaddqe1qb3lzorst3uolc1ptdo0l2cku")

actoken = "iyW5pKI0dZ4x5jErqt22yz5NGdiXaHt5"

kite.set_access_token(actoken)

def placeOrder(tr_type,symbol,qty,prc,trig):
    try:
        order_id = kite.place_order(variety="regular",
                                    tradingsymbol=symbol,
                                    quantity=qty,
                                    price=prc,
                                    transaction_type=tr_type,
                                    order_type="SL",
                                    trigger_price=trig,
                                    validity="DAY",
                                    exchange="NSE",
                                    product ="MIS")

        with open("orderLog.txt","a+") as f:
            print "orderplaced : {}".format(order_id)
            f.write(order_id+","+"TRUE")
    except Exception as e:

        with open("orderLog.txt","a+") as f:
            print "orderplaced : {}".format(order_id)
            f.write(order_id+","+"FALSE,"+e.message)

