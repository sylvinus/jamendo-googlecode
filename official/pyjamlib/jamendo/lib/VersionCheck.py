import xmlrpclib, os, re, sys

from jamendo.lib import LocalPlatform
from threading import Thread


class VersionCheck:
    
    def __init__(self,name,version):
        self.setParams(name,version)
        
    def setParams(self,name,version):
        self.name=name
        self.version=version
        self.error=False
    
    def query(self):
        
        try:
            self.result = xmlrpclib.ServerProxy("http://www.jamendo.com/xmlrpc2/").software_versions(self.name,LocalPlatform.getOS(),self.version)
        except Exception,e:
            self.error = e
            self.result= {"upgrade":"unknown"}
        
        
        return self.result
    
    
    
class VersionCheckThread(VersionCheck,Thread):
    
    def __init__(self,queueOut,name,version):
        Thread.__init__(self)
        self.setParams(name,version)
        self.queueOut=queueOut
        self.setDaemon(True)
        
    def run(self):
        
        self.query()
        
        if self.error:
            self.queueOut.put(["error",self.error])
        else:
            self.queueOut.put(["result",self.result])