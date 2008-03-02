import os,re, time, sys

from jamendo.bin import getBinaryPath

class CdRipBackend:
    
    def __init__(self,CdRipper):
        self.CdRipper=CdRipper
        self.cdDetected = False


    def checkStatus(self):
        self.cdparanoiapath = getBinaryPath("cdparanoia")
        
        if self.cdparanoiapath is None:
            return False
        else:
            return True
        
    def startDetection(self):
        try:
            if self.checkStatus() :
                self.firstDetectionTry = True
                while self.cdDetected == False :
                    if self.firstDetectionTry :
                        #only send message on first try
                        self.CdRipper.queueOut.put(["cd_detect_start"])
                    command=self.cdparanoiapath+" -Q"
                    (child_stdin, child_stdout_and_stderr) = os.popen4(command, "b")
                    self.ret=child_stdout_and_stderr.read()
                    child_stdin.close()
                    child_stdout_and_stderr.close()
                    m=re.compile("audio tracks only")
                    if m.search(self.ret):
                        self.CdRipper.queueOut.put(["cd_detect_mount", "autodetected"])
                        self.cdDetected = True
                    else:
                        if self.firstDetectionTry :
                            self.CdRipper.queueOut.put(["error", "no cd found"])
                            self.firstDetectionTry = False
                    # sleep before retry to detect
                    time.sleep(1)
                
            else :
                self.CdRipper.queueOut.put(["error", "cdparanoia binary not found"])
            
        except Exception,e:
            return [["error", "unknown : " + str(e)]]
                
              
        
    def getAudioTracks(self, device):
        try:
            m=re.compile("audio tracks only")
            if m.search(self.ret):
                tracks=re.findall("(?m)^\s*([0-9]+)\.\s+([0-9]+)",self.ret)
                ###
                #
                # cdparanoia count tracks from 1 to x and we want them from 0 to x-1
                #
                for i in range( len(tracks) ):
                    tracks[i] = [ str( int (tracks[i][0]) - 1 ), tracks[i][1] ]
                    
                self.CdRipper.queueOut.put(["cd_tracks", tracks])
            else:
                self.CdRipper.queueOut.put(["error", "strange track list returned : " + tracks])
            
        except Exception,e:
            self.CdRipper.queueOut.put(["error", "strange track list returned : " + str( e ) ])
        
    def extractTrackToFile(self,device,track_no, wavfile):
        try:
            command=self.cdparanoiapath+" -e -w "+str( int(track_no) + 1 )+" "+str(wavfile)
            (child_stdin, self.child_stdout_and_stderr) = os.popen4(command, "b")
            
            self.max_percent_reach = 0
            self.cur_track_start = 0
            self.cur_track_end = 0
            self.cur_track_length = 0

            self.CdRipper.queueOut.put(["cd_extract_start" , track_no])
            getProgressReturn=True
            while getProgressReturn:
                getProgressReturn = self.getProgress()
                #time.sleep(0.01)
            
        except Exception,e:
            self.CdRipper.queueOut.put(["error" , "unknow during extracting : " + str(e)])
            
    
    def getProgress(self):
        try:
            '''
            ratio de 1200
            '''
            f=re.compile("from sector")
            t=re.compile("to sector")
            r=re.compile("read")
            d=re.compile("Done.")
            
            ret = self.child_stdout_and_stderr.readline()
            ret_t = ret
            ret_f = ret
            ret_r = ret
            ret_d = ret
            if f.search(ret_f) :
                ret_f = re.search("sector\s+([0-9]+)\s+",ret_f)
                ret_f = ret_f.group(1)
                self.cur_track_start = int(ret_f)
            if t.search(ret_t) :
                ret_t = re.search("sector\s+([0-9]+)\s+",ret_t)
                ret_t = ret_t.group(1)
                self.cur_track_end = int(ret_t)
                self.cur_track_length = self.cur_track_end - self.cur_track_start
                
            if r.search(ret_r) :
                ret_r = ret_r.lstrip("##: 0 [read] @ ")
                ret_r = int(ret_r) / 1180
                pos = ret_r - self.cur_track_start
                if pos < 0 :
                    self.CdRipper.queueOut.put(["cd_extract_progress" , 0])
                    return True
                elif pos > self.cur_track_length :
                    self.CdRipper.queueOut.put(["cd_extract_progress" , 99])
                    return True
                else :
                    percent = ( float(pos) / float(self.cur_track_length) ) *100
                    if int(percent) > self.max_percent_reach :
                        self.max_percent_reach = int(percent)
                        self.CdRipper.queueOut.put(["cd_extract_progress" , self.max_percent_reach])
                        return True
            if d.search(ret_d) :
                self.max_percent_reach = 100
                self.CdRipper.queueOut.put(["cd_extract_progress" , self.max_percent_reach])
                self.CdRipper.queueOut.put(["cd_extract_stop"])
                self.child_stdout_and_stderr.close()
                return False
                 
            return True

        except : 
            self.CdRipper.queueOut.put(["error" , "cdparanoia binary pipe closed"])