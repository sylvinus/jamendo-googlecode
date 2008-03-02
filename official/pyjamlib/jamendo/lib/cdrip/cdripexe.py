import os, sys
import threading, time

from jamendo.bin import getBinaryPath

class CdRipBackend:
    
    def __init__(self,CdRipper):
        self.CdRipper=CdRipper
        self.cdDetected = False
        
    
    def checkStatus(self):
        self.cdrippath = getBinaryPath("cdio_paranoia")
        
        if self.cdrippath is None:
            return False
        else:
            return True

    def startDetection(self):
        try :
            if self.checkStatus() :
                self.firstDetectionTry = True
                while self.cdDetected == False :
                    if self.firstDetectionTry :
                        #only send message on first try
                        self.CdRipper.queueOut.put(["cd_detect_start"])
                    command=self.cdrippath+" --embedded --test-presence"
                    (child_stdin, child_stdout_and_stderr) = os.popen4(command)
                    ret=child_stdout_and_stderr.read()
                    if ret=="1" :
                        self.CdRipper.queueOut.put(["cd_detect_mount", "autodetected"])
                        self.cdDetected = True
                    else :
                        if self.firstDetectionTry :
                            self.CdRipper.queueOut.put(["error", "no cd found"])
                            self.firstDetectionTry = False
                        
                    # sleep before retry to detect
                    time.sleep(1)
        except Exeption, e:
            return [["error", "unknown : " + str(e)]]

    def getAudioTracks(self, device):
        try:
            command=self.cdrippath+" --embedded --count-tracks"
            (child_stdin, child_stdout_and_stderr) = os.popen4(command, "b")
            ret=child_stdout_and_stderr.read()
            if int(ret) > 0 and int(ret) < 100:
                ###
                #
                # We return a table of 'virtuals' identifiers 
                #
                self.CdRipper.queueOut.put(["cd_tracks", range( int(ret) )])
            else:
                self.CdRipper.queueOut.put(["error", "strange track list returned : " + str( ret )])
        
        except Exception,e:
            self.CdRipper.queueOut.put(["error", "strange track list returned : " + str(e) ])

            
    def extractTrackToFile(self,device,track_no, wavfile):
        
        
        try:
            command=self.cdrippath+ " --embedded --extract-track " +str( int(track_no) + 1)+ " \"" +str(wavfile)+ "\""
            (child_stdin, self.child_stdout_and_stderr) = os.popen4(command, "b")
            
            self.max_percent_reach = 0
            self.CdRipper.queueOut.put(["cd_extract_start" , track_no])
            
            getProgressReturn=True
            while getProgressReturn:
                getProgressReturn = self.getProgress()
                
        except Exception,e:
            self.CdRipper.queueOut.put(["error" , "unknow during extracting : " + str(e)])
        
    def getProgress(self):
        try:
            
            ret = self.child_stdout_and_stderr.readline()
            
            try :
                if int(ret) < 100 and int(ret) > -1 :
                    if int(ret) > int(self.max_percent_reach) :
                        self.max_percent_reach = int(ret)
                        self.CdRipper.queueOut.put(["cd_extract_progress" , self.max_percent_reach]) 
                        return True
                if int(ret) == 100:
                    self.CdRipper.queueOut.put(["cd_extract_progress" , 100]) 
                    self.CdRipper.queueOut.put(["cd_extract_stop"])
                    self.child_stdout_and_stderr.close()
                    return False
                
            except Exception, e:
                self.CdRipper.queueOut.put(["cd_extract_progress" , 0])
                return True
            
            return True

        except Exception, e: 
            self.CdRipper.queueOut.put(["error" , "cdripper binary pipe closed with error:" + str(e) ])