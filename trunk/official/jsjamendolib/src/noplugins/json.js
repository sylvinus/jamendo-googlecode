(function() {
	
	var insertScript = function(url) {
		var script = document.createElement('script');
		script.type = 'text/javascript';
		script.charset="utf-8";
		script.defer=true;
		script.src=url;
	
		document.getElementsByTagName('head').item(0).appendChild(script);
	};
	
	

})();