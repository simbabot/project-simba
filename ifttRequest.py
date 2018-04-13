import requests

def send2ifttt(key,event,value1="_",value2="_",value3="_"):
    proxies = {
        'http': 
        'https':
    }

    headers = {
        'Content-Type': 'application/json',
    }

    data = "{\"value1\":\"%s\",\"value2\":\"%s\",\"value3\":\"%s\"}" %(value1,value2,value3)

    print data
    print 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(event,key)
    response = requests.post('http://maker.ifttt.com/trigger/{}/with/key/{}'.format(event,key), headers=headers, data=data,proxies=proxies)


def generateOrderValue(symbol,price,qty):
    return symbol+"_p"+str(price)+"_q"+str(qty)

if __name__=="__main__":
    key = "cFWCCEmJgrHvRaAr50_4os"
    event= "Stock"
    value1 = "SELL"
    value2 = generateOrderValue("INFY",100,200)

    send2ifttt(key,event,"SELL",value2)
