import threading
import jamendo.lib.HTTP

class LowFi(jamendo.lib.HTTP.HTTPDownloader, threading.Thread):
    def __init__(self,feedback,trackid,encoding,localfile,abortevent,doneevent,failureevent):
        
        threading.Thread.__init__(self)
                
        self.trackid=trackid
        self.encoding=encoding

        self.setDaemon(True)
        self.setName('LowFiDownloader')
        
        remotefile='http://www.jamendo.com/get/track/id/track/audio/redirect/'+str(self.trackid)+'/?aue='+str(self.encoding)
        
        jamendo.lib.HTTP.HTTPDownloader.__init__(self,feedback,remotefile,localfile,abortevent=abortevent,doneevent=doneevent,failureevent=failureevent)
