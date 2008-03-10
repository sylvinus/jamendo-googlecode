
(function() {

/**
 * Init our Jamendo singleton
 **/
var JamendoClass = function() {}
JamendoClass.prototype = {

	onDomReadyCallbacks:[],
	
	get2:function(path,params,callback,options) {
	
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