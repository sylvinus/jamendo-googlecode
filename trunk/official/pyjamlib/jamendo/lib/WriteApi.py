import urllib2
import urllib

import simplejson
import time


def setSynchronous(method,parameters=[]):
    finalp={}
    i=0
    for p in parameters:
        finalp["p"+str(i)]=p 
        i+=1
        
    for retry in range(0,20):
        try:
            return simplejson.loads(urllib2.urlopen("http://www.jamendo.com/set/"+method+"/post/json",urllib.urlencode(finalp)).read())
        except:
            print "writeapi call %s failed, retrying in 5s..." % method
            time.sleep(5)

try:
    
    from twisted.internet import defer,reactor
    from twisted.web import client
    
    twisted=True
except:
    twisted=False


if twisted:
    
    
    def httpClient(url,downloadTo=None,twoPass=None,post=None):
        
        url=str(url)
        
        d = defer.Deferred()
        
        def httptry(retriesleft):
            
            retriesleft-=1
            
            print "getting %s ... " % url
            
            if post:
                headers  = {"Content-type":"application/x-www-form-urlencoded"}
                postData = urllib.urlencode(post)
                method="POST"
            else:
                method="GET"
                postData = None
                headers=None
                
            scheme, host, port, path = client._parse(url)
            
            if downloadTo and (not twoPass):
                factory = client.HTTPDownloader(url, downloadTo)
                #timeout? factory.timeout=20
            else:
                factory = client.HTTPClientFactory(url,method=method,postdata=postData,headers=headers,timeout=60)
            
            factory.deferred.addCallback(success,retriesleft)
            factory.deferred.addErrback(failure,retriesleft)
            
            reactor.connectTCP(host, port, factory)
            
            
            
                
        def success(ret,retriesleft):
            
            if twoPass:
                d3 = self.httpClient(ret,downloadTo=downloadTo)
                d3.addCallbacks(d.callback,d.errback)
            else:
                d.callback(ret)
        
        def failure(f,retriesleft):
            if retriesleft>0:
                print "get %s failed (%s), retrying in 10s (%s retries left)" % (url,f,retriesleft)
                reactor.callLater(10,httptry,retriesleft)
            else:
                d.errback(url)

        httptry(60)

        return d
    
    
    def setTwisted(method,parameters=[]):
        
        #main deferred
        d = defer.Deferred()
        
        def err(err):
            d.errback(err)
            
        try:
        
            finalp={}
            i=0
            for p in parameters:
                finalp["p"+str(i)]=simplejson.dumps(p) 
                i+=1
            
            #try to download the album from other SJS
            d_servs = httpClient("http://www.jamendo.com/set/%s/postjson/json/" % method,post=finalp)
            
            
            
            def gotresult(json):
                try:
                    obj = simplejson.loads(json)
                    d.callback(obj)
                    
                except Exception,e:
                    err("Got nonjson return :%s "%e)
            
            d_servs.addCallbacks(gotresult,err)
        
        except Exception,e:
            err("E: %s" %e)
        
        return d
    