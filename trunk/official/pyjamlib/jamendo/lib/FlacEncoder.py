
from threading import Thread
import Queue, time
import os, sys, re, shutil
import LocalPlatform
from subprocess import Popen,PIPE,STDOUT

from jamendo.bin import getBinaryPath
from jamendo.lib.ContentUploadCheck import ContentUploadCheck




class FlacEncoder(Thread): 

    def __init__(self,queueIn, queueOut):
        Thread.__init__(self)
        self.queueIn=queueIn
        self.queueOut = queueOut
        self.forceQuit = False
        self.started = False
        
        self.setDaemon(True)
        

    def run(self):
        
        self.binFlac = getBinaryPath("flac")

        
        
        while True:# not self.forceQuit :
            #if not self.queueIn.empty() :
            msg = self.queueIn.get()

            if msg[0] == "toFlac" :

                self.toFlac( msg[1], msg[2])

            #elif msg[0] == "exit" :
            #    self.forceQuit = True


            time.sleep(0.1) # in seconds
            
            
    def toFlac(self,file,destProposition):

        check = ContentUploadCheck(file)

        #already a flac file!
        if (check[0]=="flac"):
            destProposition=file

            
        else:
            #encode the file
            command = self.binFlac + " -f " + "\"" + file.replace("\"", chr(92)+chr(34))  + "\"" + " -o " + "\"" + destProposition.replace("\"", chr(92)+chr(34)) + "\""
            #flacPipe = Popen(command, bufsize=1, shell=False, stdout=PIPE, stderr=STDOUT).stdout
            #flacPipe = Popen(command , shell=False, stdout=PIPE, stderr=STDOUT).communicate()
            (stdIn, stdOut_stdErr) = os.popen4(command, "b")
            
            notClosed = True
            while notClosed :
                try :
                    line = stdOut_stdErr.readline()
                    m = re.search("\: (ERROR|EOF)(.*)",line)
                    if m:
                        self.queueOut.put(["flac_error",m.group(2)])
                        return
                
                    m = re.search("\: ([0-9.])%",line)
                    if m:
                        self.queueOut.put(["flac_progress",m.group(1)])
                    
                    m = re.search("\: wrote ([0-9]+)",line)
                    if m:
                        break
                except :
                    notClosed = False
                    
            stdIn.close()
            stdOut_stdErr.close()
                    
            check = ContentUploadCheck(destProposition)

        if check[1]<0:
            self.queueOut.put(["flac_error",check[2]])
            return
        
        #perform an additional testing on the file
        test_command = self.binFlac + " -t " + "\"" + destProposition.replace("\"", chr(92)+chr(34)) + "\""
        #flacTestPipe = Popen(test_command, bufsize=1, shell=False, stdout=PIPE, stderr=STDOUT).stdout
        #flacTestPipe = Popen(command , shell=False, stdout=PIPE, stderr=STDOUT).communicate()
        (test_stdIn, test_stdOut_stdErr) = os.popen4(test_command, "b")
        testNotClosed = True
        while testNotClosed:
            try :
                line = test_stdOut_stdErr.readline()
                m = re.search("\: (ERROR|EOF)(.*)",line)
                if m:
                    self.queueOut.put(["flac_error",m.group(2)])
                    return    
                
                m = re.search("\: ok",line)
                if m:
                    break
            except : 
                testNotClosed = False      
     
        test_stdIn.close()
        test_stdOut_stdErr.close()
            
        self.queueOut.put(["flac_progress",100])
        self.queueOut.put(["flac_done",destProposition])