import xmlrpclib

from jamendo.lib import uuid
from jamendo.lib.XMLRPC import getXmlrpcProxy
import LocalPlatform
from threading import Thread
from Queue import Queue
import time


class DebugReport:
    
    def __init__(self,appname,appversion,appstring,remote=True,stdout=True):

        #generate an unique hash per-launch.
        self.hash = str(uuid.uuid4())
        
        self.appname = appname
        self.appversion = appversion
        self.appstring = appstring
        
        self.remote = remote
        self.stdout = stdout
        
        self.inited=False
     
       
    #threaded methods
    def init(self):

        try:
            
            if self.stdout:
                print "[debug] %s %s started on %s with python %s" % (self.appname,self.appversion,LocalPlatform.getOS(),LocalPlatform.getPythonVersion())
         
            if self.remote:
                self.xmlrpc = getXmlrpcProxy("http://www.jamendo.com/?m=xmlrpc2")
                
                self.xmlrpc.debugreport_init(self.hash,self.appname,self.appversion,self.appstring,LocalPlatform.getPythonVersion(),LocalPlatform.getOS(),LocalPlatform.getOSString())
            
            self.inited=True
            
        except:
            pass

    def debug(self,message):

        try:
    
            if not self.inited:
                DebugReport.init(self)

            if self.stdout:
                print "[debug] %s" % message
            
    
            if self.remote and self.inited:
                self.xmlrpc.debugreport_debug(self.hash,message)
        except:
            pass
            
    def error(self,code,message):

        try:
    
            if not self.inited:
                DebugReport.init(self)

            if self.stdout:
                print "[error] %s: %s" % (code,message)

                  
            if self.remote and self.inited:
                self.xmlrpc.debugreport_error(self.hash,code,message)

        except:
            pass


class DebugReportThread(DebugReport,Thread):
    
    def __init__(self,queueIn,queueOut,*args, **kwargs):
        Thread.__init__(self)
        
        if queueIn:
            self.queueIn=queueIn
        else:
            self.queueIn=Queue(10000)
        
        if queueOut:
            self.queueOut=queueOut
        else:
            self.queueOut=Queue(10000)
            
        self.setDaemon(True)
        DebugReport.__init__(self,*args,**kwargs)
        
    def run(self):

        while True:

            try:
                if not self.queueIn.empty():
                    while not self.queueIn.empty():
                        msg = self.queueIn.get()
                        
                        if msg[0]=="init":
                            DebugReport.init(self)
                        elif msg[0]=="debug":
                            DebugReport.debug(self,msg[1])
                        elif msg[0]=="error":
                            DebugReport.error(self,msg[1],msg[2])  
                else :    
                    time.sleep(0.5)
            except Exception,e:
                print "[DebugReport error] %s" % e
                
                
    def error(self,code,message):
        self.queueIn.put(["error",code,message])
        
    def debug(self,message):
        self.queueIn.put(["debug",message])
        
    def init(self):
        self.queueIn.put(["init"])