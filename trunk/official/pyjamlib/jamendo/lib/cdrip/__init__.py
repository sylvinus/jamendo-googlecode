__all__ = [
    'CdRipper'
]

__version__ = '1.0'
from threading import Thread
import Queue, time
from jamendo.lib import LocalPlatform

class CdRipper(Thread):
    
    def __init__(self,queueIn, queueOut):
        Thread.__init__(self)
        self.queueIn=queueIn
        self.queueOut = queueOut

        self.backend=False
        self.backend_name=False
        self.triedBackends=[]
        
        self.setDaemon(True)
        
    def run(self):
        
        self.autoSelectBackend()
        
        
        
        while True:
            if True: #not self.queueIn.empty() :
                msg = self.queueIn.get()
                #print msg
                if msg[0] == "manualDetection":
                    self.backend.manualDetection()
                elif msg[0] == "startDetection":
                    self.backend.startDetection()
                elif msg[0] == "stopDetection":
                    self.backend.stopDetection()
                elif msg[0] == "getAudioTracks":
                    self.backend.getAudioTracks(msg[1])
                elif msg[0] == "extractTrackToFile":
                    self.backend.extractTrackToFile( msg[1], msg[2], msg[3] )
                    
                elif msg[0] == "exit":
                    return False

           
            time.sleep(0.01) # in seconds
            
            
         
        
    def autoSelectBackend(self):
        
        #no more backends
        backend = -1
        
        try:
            if LocalPlatform.getOS() == "windows" and not ("cdripexe" in self.triedBackends):
                
                self.backend_name="cdripexe"
                import cdripexe
                backend = cdripexe.CdRipBackend(self)
            
            elif LocalPlatform.getOS() == "windows" and not ("pymedia" in self.triedBackends):
                
                self.backend_name="pymedia"
                import pymedia
                backend = pymedia.CdRipBackend(self)
                
            elif LocalPlatform.getOS() == "unix" and not ("cdparanoia_unix" in self.triedBackends):
            
                self.backend_name="cdparanoia_unix"
                import cdparanoia_unix
                backend = cdparanoia_unix.CdRipBackend(self)
                
            elif LocalPlatform.getOS() == "macosx":
                
                self.backend_name="macosxnative"
                import macosxnative
                backend = macosxnative.CdRipBackend(self)
                
        except Exception,backend_error:
            backend = -2
            
            
        # Nothing more to try!
        if backend==-1:
            self.queueOut.put(["error",1,"No backends found"])
            return False
        
        
        # Backend had an error, try another one!
        if backend==-2:
            self.triedBackends.append(self.backend_name)
            return self.autoSelectBackend()
        
        
        # Found a backend!
        if backend:
            self.backend = backend
            self.queueOut.put(["backend",self.backend_name])
            
            return self.backend
