var Upstox = require("upstox");
api =  "mOq86xk9sq7urT6eb21PX54hDoUbW1OM9Xch0x2h"
secret = "xhjidqia8h"
var upstox = new Upstox(api);
//https://api.upstox.com/index/dialog/authorize?apiKey=mOq86xk9sq7urT6eb21PX54hDoUbW1OM9Xch0x2h&response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1

code = "7fc285161f500bf626e8eb808d664d5eb790a05f" //replace this code  

 var params= {
         "apiSecret" : secret,
         "code" : code,
         "redirect_uri" : "http://127.0.0.1"
     };

 var accessToken;

 upstox.getAccessToken(params)
     .then(function(response) {
       accessToken = response.access_token;
	   alert(accessToken)
     })
     .catch(function(err) {
         // handle error
		alert("error")
     });
