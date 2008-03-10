/**
 * Use mootools handlers
 **/

Jamendo._jsonRequest = function(url,callback,options) {

	//does mootools allow cross domain json?
	var jsonRequest = new Json.Remote(url, {
		onComplete: callback
	}).send(options["post"] || {});
	
	return {
		"cancel":jsonRequest.cancel
	}
};

Jamendo.onDomReady = function(callback) {
	window.addEvent('domready',callback);
};