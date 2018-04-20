var Upstox = require("upstox");
api =  "mOq86xk9sq7urT6eb21PX54hDoUbW1OM9Xch0x2h"
secret = "xhjidqia8h"
var upstox = new Upstox(api);

var accesstoken1 = "15713b9b8242b8529e75131f4270bbf7e46d232f";
upstox.setToken(accesstoken1);	 

function getohlc(){
upstox.getOHLC({
  "exchange": "nse_eq",
  "symbol": "TECHM",
  "start_date": "20-04-2018",
  "end_date": "20-04-2018",
  "format" : "csv",
  "interval" : "5minute"
})
.then(function (response) {
    //alert(JSON.stringify({ x: response.data}));
    //alert(response.data)
    var FileSaver = require('file-saver');
    var blob = new Blob([response.data], {type: "text/plain;charset=utf-8"});
    FileSaver.saveAs(blob, "Techm.csv");
})
.catch(function(error){
	alert(error);
    done(error);
	
});
}
setInterval(getohlc, 5*60*1000);
