
import time
import simplejson,urllib2,urllib
import xmlrpclib



class JamendoMusicApiQuery:
    
    
    
    def __init__(self,params1,params2,feedback=False,method="json",blockunit=500,use_beta=False):
        
        self.params1=params1
        self.params2=params2
        self.feedback=feedback
        self.method=method
        if ("n" not in params2) or (params2["n"]>blockunit) or params2["n"]=="all":
            self.blockunit=blockunit
        else:
            self.blockunit=False
        self.pn=0
        
        if use_beta:
            self.domain="http://beta.www.jamendo.com/"
        else:
            self.domain="http://www.jamendo.com/"
        
        
        if self.method=="json":
            
            self.setFormat("json")
            
        elif self.method=="xmlrpc":
            
            self.setFormat("xmlrpc")
            self.proxy = xmlrpclib.ServerProxy(self.domain+"xmlrpc/")
            
    
    def setFormat(self,format):
        p1=self.params1.split("/")
        p1[4]=format
        self.params1="/".join(p1)

    def get(self):
        
        eof=False
        all_data=[]
        
        while (not eof):
            (data,eof) = self.getNextBlock()
            if data != None:
                all_data+=data
            else: 
                return (False,True)
                
        return all_data
        
        
    def getNextBlock(self):
        
        if self.blockunit>0:
            self.pn+=1
            self.params2["pn"]=self.pn
            self.params2["n"]=self.blockunit
        

        retries=20
        i=0
        while i<retries:
            i+=1
            
            try:
                data=self.performQuery()
                    
                return (data, self.blockunit==0 or len(data)<self.params2["n"] )
            
            except Exception,e:
                if self.feedback:
                    self.feedback.put(["debug","MusicApi error : "+str(e)])
                time.sleep(2)
        
        return (None, False)
                           
        
        
    def performQuery(self):
        
        if self.feedback:
            self.feedback.put(["debug","MusicApi query : "+str(self.params1)+str(self.params2)])
                    
        if self.method=="xmlrpc":
            return self.proxy.jamendo.get(self.params1,self.params2)
        
        elif self.method=="json":
            
            self.req = urllib2.Request(self.domain+"get/"+self.params1+"?"+urllib.urlencode(self.params2));
            self.opener = urllib2.build_opener()
            f = self.opener.open(self.req)
            data = f.read()
            f.close()
            
            return simplejson.loads(data)