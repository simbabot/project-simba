from upstox_api.api import *

apikey ="mOq86xk9sq7urT6eb21PX54hDoUbW1OM9Xch0x2h"
apisecret = "xhjidqia8h"

s = Session (apikey)
s.set_redirect_uri ("http://127.0.0.1")
s.set_api_secret (apisecret)

print (s.get_login_url())
##############################################################
s.set_code ('b34657cdc58c502c9b7a465b734f9f7c1c3e3a95')

access_token = s.retrieve_access_token()#a0897f05351de49a927e757ccaaf0f19fdf56cb1
print ('Received access_token: %s' % access_token)
u = Upstox (apikey,access_token)
u.get_master_contract('nse_eq') # get contracts for NSE EQ
ohlc = u.get_ohlc(u.get_instrument_by_symbol('NSE_EQ', 'TECHM'), OHLCInterval.Minute_10, datetime.strptime('1/04/2018', '%d/%m/%Y').date(), datetime.strptime('19/04/2018', '%d/%m/%Y').date())
