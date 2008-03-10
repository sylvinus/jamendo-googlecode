
(function() {

/**
 * Init our Jamendo singleton
 **/
var JamendoClass = function() {}
JamendoClass.prototype = {

	apiDomain:"http://api.jamendo.com",

	onDomReadyCallbacks:[],
	
	get2:function(path,params,callback,options) {
	
	},
	
	set:function(method,arguments,callback) {
	
	},
	
	jsonRequest:function(url,callback,options) {
	
	
	
	},
	
	_jsonRequest:function(url,callback) {
	
	},
	
	onDomReady:function(callback) {
		this.onDomReadyCallbacks.push(callback);
	},
	_domIsReady:function() {
		for(var i=0,len=this.onDomReadyCallbacks.length;i<len; i++) {
			this.onDomReadyCallbacks[i]();
		}
	}

};


window.Jamendo = new JamendoClass();


})();