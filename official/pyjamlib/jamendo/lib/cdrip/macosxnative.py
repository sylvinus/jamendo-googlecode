import os, sys,re 
import  time
from threading import Thread
from Queue import Queue
from subprocess import Popen,PIPE,STDOUT

from jamendo.bin import getBinaryPath


class MacOsXCdNotification(Thread):
    
    def __init__(self,queueOut):
        Thread.__init__(self)
        self.queueOut = queueOut
        self.setDaemon(True)
        
        self.binPath = getBinaryPath("cd_detect_macosx")
        
    #we need to create a link to the newly found CD audio because it can be renamed
    def createLink(self,directory):
        Popen(["ln","-sf",directory+"/","/tmp/pyjamlib_link_to_cdaudio"], shell=False, stdout=PIPE, stderr=STDOUT).stdout.read()
        
        
    def oneshot(self):
        
        
        
        results = Popen([self.binPath,"--oneshot"], shell=False, bufsize=1, stdout=PIPE, stderr=STDOUT).stdout.read()

        
        m=re.search("mounted\:(.*)",results)
        if m:
            dir = "/Volumes/"+m.group(1)
            self.createLink(dir)
            self.queueOut.put(["cd_detect_mount",dir])
        
    
    def run(self):

        self.pipe = Popen([self.binPath,"--daemon"], shell=False, bufsize=1, stdout=PIPE, stderr=STDOUT).stdout
        
        line=True
        while line:
            line = self.pipe.readline()

            m = re.search("([a-z]+)\:(.*)",line)
            if m:
                command=m.group(1)
                arg=m.group(2)

                if command=="start":
                    self.queueOut.put(["cd_detect_start"])
                elif command=="mounted":
                    dir = "/Volumes/"+arg
                    self.createLink(dir)
                    self.queueOut.put(["cd_detect_mount",dir])
                elif command=="unmounted":
                    self.queueOut.put(["cd_detect_unmount"])
        

        self.queueOut.put(["cd_detect_stop"])  
                


class CdRipBackend:
    
    def __init__(self,CdRipper):
        self.CdRipper=CdRipper
        
        
    def startDetection(self):
        self._not = MacOsXCdNotification(self.CdRipper.queueOut)
        self._not.start()
        
    def stopDetection(self):
        pass  
    
    def manualDetection(self):
        self._not = MacOsXCdNotification(self.CdRipper.queueOut)
        self._not.oneshot()
    

    def getAudioTracks(self, device, useQueue=True):
        try:
            
            tracks=[]
            
            if os.path.isdir("/tmp/pyjamlib_link_to_cdaudio"):
                for fileName in os.listdir("/tmp/pyjamlib_link_to_cdaudio"):
                    if re.search("\.aif(f?)$",fileName):
                        tracks.append(fileName)
                        
            tracks.sort()
            
            self.tracks = tracks
            
            if useQueue:
                self.CdRipper.queueOut.put(["cd_tracks",self.tracks])

        except Exception,e:
            if useQueue:
                self.CdRipper.queueOut.put(["error","In getAudioTracks : %s" % e])

    
    """
    MacOsX supports direct extraction through the filesystem. (thanks, Apple!)
    """
    def extractTrackToFile(self,device,track_no, wavefile):
        
        #refresh the filenames
        self.getAudioTracks(device,False)
        
        buffer_size=131072
        
        filepath = "/tmp/pyjamlib_link_to_cdaudio/"+self.tracks[track_no]
        
        outf = open(wavefile,"wb")
        
        self.CdRipper.queueOut.put(["cd_extract_start",self.tracks[track_no]])
        
        
        
        if os.path.isfile(filepath):
            size = os.stat(filepath).st_size
            inf = open(filepath,"rb",buffer_size)
            read=0
            buf="dummy"
            while len(buf)>0:
                buf=inf.read(buffer_size)
                read+=len(buf)
                outf.write(buf)
                self.CdRipper.queueOut.put(["cd_extract_progress",read*100.0/size])
               
            inf.close()
            outf.close()
            
        self.CdRipper.queueOut.put(["cd_extract_stop",self.tracks[track_no]])


          
if __name__ == "__main__":
    
    
    print "test started"
    q = Queue(10000)    

    c = MacOsXCdNotification(q)
    c.start() #.run()
    
    while True:
        print q.get()