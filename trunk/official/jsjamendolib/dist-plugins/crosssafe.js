/**
CrossSafe - Secure cross domain JSON requests with the JSONRequest API. 
Copyright (C) 2007 Xucia Incorporation
Author - Kris Zyp - kriszyp@xucia.com
The contents of this file are subject to the Mozilla Public License Version
1.1 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
for the specific language governing rights and limitations under the
License.
**/
if (!window.JSONRequest) 
	(function() {
		CrossSafe = { // all the options you can change with CrossSafe:
						directory:'/CrossSafe/', 
						visibleFrames:false,
						callbackParameter:'callback',
						strictlyObjects:true,
						allowUnsecure:false,
						redirectToHost:'www',
						secureChannels:[],
						timeout:30000,
						webServiceHostName:'webservice',
						onReady:{}//this isn't an option, but used internally
						};
		
		function createIframe(parent,url) {
		    var iFrame = parent.appendChild(document.createElement("iframe"));
			if (!CrossSafe.visibleFrames) iFrame.style.display="none";
			iFrame.src=url;
			return iFrame.contentWindow;
		
		}
		var getXMLHttpRequest = function () {
			if (parent.XMLHttpRequest)
		        return new parent.XMLHttpRequest();
			else if (window.ActiveXObject)
		        return new ActiveXObject("Microsoft.XMLHTTP");
		}
		var hostErrorMsg = "The host name must have a domain name and a suffix, set CrossSafe.allowUnsecure to true if you want to allow CrossSafe to run without secured communication";
		try {
			var rootDomain = document.location.host.match(/\.([a-zA-Z]\w*\.[^\.]+$)?/)[1];
			if (!rootDomain) {
				if (CrossSafe.redirectToHost) { // TODO: A little cleverness could drastically decrease the size of this block
					var parts = document.location.href.match(/([^\/]+?\/\/)(.*)/);
					document.location = parts[1] + CrossSafe.redirectToHost + '.' + parts[2];
				}
				else if (!CrossSafe.allowUnsecure)
					throw new Error(hostErrorMsg); 
			}
		} catch(e){
			if (!CrossSafe.allowUnsecure)
				throw new Error(hostErrorMsg); 
		}
		var channels={};	
		var polling;
		var thisDomain = document.location.href.match(/\w+:\/\/[^\/]+/)[0];
		var singleMediator;
		var channelNum = 0;
		var requestId = 0;
		var statuses=[];
		var securing;
		mediatorWaitingRequests = [];
		function doError(callback,id, msg) {
			setTimeout(function() {
				callback(id,undefined,{name: "JSONRequestError", message: msg});
			},0);
		}
		JSONRequestError = function(msg){this.message = msg};
		JSONRequestError.prototype = Error.prototype;
		JSONRequest={
			get : function(url,done) {
				var thisId = requestId++;
				statuses[thisId] = done;
				var channel;
				if (typeof done != 'function') 
					throw new JSONRequestError('The done parameter is not a function');
					
				var crossDomain = url.match(/\w+:\/\/[^\/]+/)[0];
				var cbParam = CrossSafe.callbackParameter; // save it at the beginning
				setTimeout(function() {
					var cb = statuses[thisId]; 
					if (cb) {
						statuses[thisId]=0;
						doError(cb,thisId,"no response");
					}
				},CrossSafe.timeout);
				function checkValue(value) {
					if (statuses[thisId]) { // if it has not been responded too...
						statuses[thisId] = 0;
						if (CrossSafe.strictlyObjects || value === undefined) {
							if (typeof value != 'object') //JSONRequest spec says the top level value must be an object
								return doError(done,thisId,"bad data");
							function stripFuncs(obj) { // pure JSON must not have any functions
								for (var i in obj) {
									if (typeof obj[i] == 'function')
										delete obj[i];
									else if (typeof obj[i] == 'object')
										stripFuncs(obj[i]);
								}
							}
							stripFuncs(value);
						}
						setTimeout(function() {done(thisId,value)},0); // This is so the callback always happens after the get, and the error handling is correct 
					}
				}
				
				if (thisDomain == crossDomain) { // use XHR for local calls
				 	var xhr = getXMLHttpRequest();
				    xhr.open("GET",url, true); 
					xhr.onreadystatechange = function () {
						if (xhr.readyState == 4) {
					        // only if "OK"
					        try {
					        	var status = xhr.status;
					        	var loaded = status == 200 && xhr.responseText.length > 0;//firefox can throw an exception right here
					        } catch(e) {}
					        if (loaded) {
					        	var str = xhr.responseText; 
					        	statuses[thisId] = 0;
			                    if (!CrossSafe.strictlyObjects || /^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]*$/.test(str. // from json.js from json.org
					                    replace(/\\./g, '@').
					                    replace(/"[^"\\\n\r]*"/g, ''))) 
					                checkValue(eval('(' + str + ')'));
					            else {
					            	doError(done,thisId,"bad response");
					            }
				        	}
							else
								doError(done,thisId,"not ok");
				        	xhr = null; // This is to correct for IE memory leak
						}
					};
				    xhr.send(null);
				}
				else if (rootDomain) { // host-domain is properly setup
					var channel = (channels[crossDomain] = channels[crossDomain] || {num:channelNum++});
					channels[channel.num] = channel;
					function createMediator() {
						return createIframe(document.body,"mediator.html?"+channel.num);
					}	
					function createUntrusted(webservice) {
						return createIframe(document.body,webservice + "uwa.html?"+channel.num);			
					}
					function nextRequest() {				
						var testing = window.document.body;// cause Opera to throw an error if dynamic authorization is working
						if (channel.executors && channel.executors.length)
							channel.executors.shift()();
						else
							delete channel.executors;
					}
					function doRequest() {
							url += (url.match(/\?/) ? '&' : '?') + cbParam + "=done" + thisId;
							if (polling) {
								channel.urls[url]=thisId;
								var monitor = setInterval(function() {
									var response = channel.responses[url];
									if (response || !statuses[thisId]) { // false status means it was cancelled or there was a timeout, might want to use hasOwnProperty here
										clearInterval(monitor);
										delete channel.response;
										checkValue(response);
									}
								},10);
								nextRequest();
							}
							else {
								channel.request(url,function(value) {
									checkValue(value);
								},thisId);
								nextRequest();
							}
						}
	
					if (channel.executors || !channel.ready) {
						(channel.executors = channel.executors || []).push(doRequest);
						}
					else
						doRequest();
					
					if (!channel.ready) {
						var webservice = 'http://' + CrossSafe.webServiceHostName + (channel.num || "") + '.' + rootDomain + CrossSafe.directory;
						channel.ready=nextRequest;
						function makeChannel() {
							if (polling) { 
								var monitor = setInterval(function() {
									if (channel.ready === 1) {
										clearInterval(monitor);
										channel.urls={};
										channel.responses={};
										nextRequest();
									}
								},30);
							}
						}
						CrossSafe.onReady[channel.num] = function () {
							mediator.channel =channel;
							//polling = true;
							setTimeout(function() {
								if (polling)
									makeChannel();
							},100);
							try {
								mediator.sealer(webservice); 
								var testing = document.body; // cause Opera to throw an error if dynamic authorization is working
								polling = false;
							}
							catch (e){
								
								polling = true;
							}
							
						}
						// Secured Multichannel setup goes here ...
						// Create the mediator
						var mediator = createMediator();
					}					
				}
				else {
					if (!CrossSafe.allowUnsecure) 
						throw new Error(hostErrorMsg);
				    var scriptTag = document.createElement("script"); // must use the document that supports events, not his one
				    scriptTag.setAttribute("src", url + (url.match(/\?/) ? '&' : '?') + cbParam+ "=CrossSafe.done" + thisId);
				    scriptTag.onload=scriptTag.onreadystatechange=function() {
				    	setTimeout(checkValue,1); // trigger a bad data error if nothing has been loaded yet
					}
				    document.body.appendChild(scriptTag); // This is supposed to be asynchronous, but sometimes it will get its request before continuing
				    CrossSafe['done' + thisId] = function(value) {
				    	checkValue(value);
				    }
				}
				return thisId;
			},
			cancel : function(id) { 
				// Should this be wrapped in a setTimeout so that errors don't propagate to the caller 
				// of this function? The spec does not make it clear. 
				var cb = statuses[id];
				if (cb) {
					statuses[id]=0;
					doError(cb,id,"cancelled");
				}
			}
		};
	})();
