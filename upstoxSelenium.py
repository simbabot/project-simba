from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from upstox_api.api import *
import time



class UpstoxSelenium:
    def __init__(self, driverpath, loginurl, apikey, apisecret):
        self.driver = driverpath
        self.loginurl = loginurl
        self.apikey = apikey
        self.apisecret = apisecret
        self.token = ""
        # self.fulltime = []
        # self.fullprice = []
        self.startScrape()

    def startScrape(self):
        options = Options()
        options.add_argument('--headless')
        #options.add_argument('--no-sandbox')
        #options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1680x1050")

        driver = webdriver.Chrome(self.driver, chrome_options=options)

        # driver = webdriver.Chrome(self.driver, chrome_options=options)

        driver.get(self.loginurl)
        driver.maximize_window()

        usrInput=driver.find_element_by_id("name")
        pwdInput=driver.find_element_by_id("password")
        yearOfBirth= driver.find_element_by_id("password2fa")

        usrInput.send_keys("152566")
        time.sleep(1)
        pwdInput.send_keys("Simba123#")
        time.sleep(1)
        yearOfBirth.send_keys("1994")
        driver.find_element_by_tag_name("button").click()
        delay = 5 #seconds
        try:
            myElem = WebDriverWait(driver, delay).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'div'),'Request Access'))
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")

        time.sleep(1)
        driver.find_element_by_id("allow").click()

        try:
            myElem = WebDriverWait(driver, delay).until(EC.url_contains('127'))
            requestToken = str(driver.current_url).split('code=')[1]
            print (requestToken)
            dt = datetime.fromtimestamp(int(time.time())).strftime('%Y_%m_%d')
            with open(dt+"_code.txt","w") as f:
                f.write(requestToken)
            return requestToken
        except TimeoutException:
            print ("Loading took too much time!!")

    def upstoxConnectionsetup(self, requestToken):
        # proxy = {
        #     'host': 'fr0-proxylan-vip.eu.airbus.corpfr0-proxylan-vip.eu.airbus.corp',
        #     'port': 3000,
        #     'auth': ('username', 'password')
        # }
        s = Session(self.apikey)
        s.set_redirect_uri('http://127.0.0.1')
        s.set_api_secret(self.apisecret)
        s.set_code(requestToken)
        access_token = s.retrieve_access_token()
        print ('Received access_token: %s' % access_token)
        return access_token


    def upstoxEstablishConnection(self,access_token):
        u = Upstox(self.apikey, access_token)
        u.get_master_contract('nse_eq')
        u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', 'RELIANCE'), OHLCInterval.Minute_5,
                   datetime.datetime.strptime('%d/%m/%Y').date(),
                   datetime.datetime.strptime('%d/%m/%Y').date())


if __name__ == '__main__':
    loginurl = "https://api.upstox.com/index/dialog/authorize?apiKey=mOq86xk9sq7urT6eb21PX54hDoUbW1OM9Xch0x2h&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1"
    filename = r"C:\Users\NG6EADA\Downloads\chromedriver_win32\chromedriver.exe"
    kite_api_key = "mOq86xk9sq7urT6eb21PX54hDoUbW1OM9Xch0x2h"
    kite_api_secret = "xhjidqia8h"
    k = UpstoxSelenium(filename, loginurl,kite_api_key,kite_api_secret)
    print k
