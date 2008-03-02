import xmlrpclib
import urllib2



def getXmlrpcProxy(endpoint,authDetails=None,proxyDetails=None):
    
    mtransport = Urllib2Transport()
    
    if authDetails is not None:
        mtransport.jamSetAuth(authDetails)
        
    #todo test that
    if proxyDetails is not None:
        checkProxySettings()
        mtransport.jamSetProxy(proxyDetails)
        
    
    return xmlrpclib.ServerProxy(endpoint,transport=mtransport,encoding="UTF-8")


class Urllib2Transport(xmlrpclib.Transport):
    """Provides an XMl-RPC transport routing via a http proxy.
    
    This is done by using urllib2, which in turn uses the environment
    varable http_proxy and whatever else it is built to use (e.g. the
    windows    registry).
    
    NOTE: the environment variable http_proxy should be set correctly.
    See checkProxySetting() below.
    
    Written from scratch but inspired by xmlrpc_urllib_transport.py
    file from http://starship.python.net/crew/jjkunce/ by jjk.
    
    A. Ellerton 2006-07-06
    """
    
    def __init__(self):
        self.jamProxied = False
        self.jamAuth = False
        
        #needed for python 2.5 ??
        self._use_datetime=True

    def request(self, host, handler, request_body, verbose):
        
        self.verbose=verbose
        url='http://'+host+handler
        if self.verbose: "ProxyTransport URL: [%s]"%url

        request = urllib2.Request(url)
        request.add_data(request_body)
        # Note: 'Host' and 'Content-Length' are added automatically
        request.add_header("User-Agent", self.user_agent)
        request.add_header("Content-Type", "text/xml") # Important


        if self.jamProxied:
            proxy_handler=urllib2.ProxyHandler()
            opener=urllib2.build_opener(proxy_handler)
        elif self.jamAuth:
            if self.jamAuth["type"]=="httpdigest":
                pm = urllib2.HTTPPasswordMgrWithDefaultRealm()
                pm.add_password(None,host,self.jamAuth["user"],self.jamAuth["pass"])
                opener=urllib2.build_opener(urllib2.HTTPDigestAuthHandler(pm))

        else:
            opener=urllib2.build_opener()
            
        f=opener.open(request)
        return(self.parse_response(f))
    
    
    def jamSetAuth(self,details):
        self.jamAuth = details
        

    
    def jamSetProxy(self,details):
        self.jamProxied = True
        pass


def checkProxySetting():
    """If the variable 'http_proxy' is set, it will most likely be in one
    of these forms (not real host/ports):
    
          proxyhost:8080
          http://proxyhost:8080
    
    urlllib2 seems to require it to have 'http;//" at the start.
    This routine does that, and returns the transport for xmlrpc.
    """
    import os, re
    try:
        http_proxy=os.environ['http_proxy']
    except KeyError:
        return
    
    # ensure the proxy has the 'http://' at the start
    #
    match = re.match("(http://)?([-_\.A-Za-z]+):(\d+)", http_proxy)
    if not match: raise Exception("Proxy format not recognised: [%s]" % http_proxy)
    os.environ['http_proxy'] = "http://%s:%s" % (match.group(2), match.group(3))
    #print "Determined proxy: %s" % os.environ['http_proxy']
    return

