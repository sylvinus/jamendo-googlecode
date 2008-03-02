from threading import Thread
import os,locale,time,math,md5,xmlrpclib

from jamendo.lib.XMLRPC import getXmlrpcProxy


numRetries = 1
packetNumRetries = 24

#last IP is upload2
fallbackServers = [{"host":"upload2.jamendo.com"},{"host":"upload3.jamendo.com"},{"host":"upload4.jamendo.com"},{"host":"91.121.79.165"}]

class ContentUploader:
    
    def __init__(self,queueOut):
        self.queueOut = queueOut
        self.isSending = False
        self.pieceSize = 50000
        
        self.sessionId = False
        
        self.setClientInfo({"type":"pyjamlib","version":"1","string":"PyJamLib"})

        self.jamendoXmlrpc = getXmlrpcProxy("http://www.jamendo.com/xmlrpc2/")

        
    def setCredentials(self,user,password,isTesting=False):
        #isTesting = True
        self.username = user
        self.password = password
        self.isTesting = isTesting
        
        if isTesting:
            self.jamendoXmlrpc = getXmlrpcProxy("http://local.jamendo.com/xmlrpc2/?auth=httpdigest",{"type":"httpdigest","user":user,"pass":password})
        else:
            self.jamendoXmlrpc = getXmlrpcProxy("http://www.jamendo.com/xmlrpc2/?auth=httpdigest",{"type":"httpdigest","user":user,"pass":password})


    def setClientInfo(self,info):
        self.clientInfo = info
    
    def getSessionId(self):
  
            try:
                sess = self.jamendoXmlrpc.jamloader_initsession(self.clientInfo)
            except Exception,e:
                raise Exception, [7,"Session initialization failed"]
            
            self.queueOut.put(["sessionid",sess["sessionId"]])
            self.setSessionId(sess["sessionId"])
            return sess["sessionId"]

    def setSessionId(self,sessid):
        self.sessionId = sessid
		  
		  
    def trackInit(self,wantedFileName):
        try :
            #myLocale = locale.getdefaultlocale()
            #if (myLocale[1] != "UTF8") and (myLocale[1] is not None) and (myLocale[1] !="utf-8"):
            #    wantedFileName = unicode( wantedFileName, myLocale[1] )
            #    #print localFileName.encode(myLocale[1])
            
            
            trackInfos = self.jamendoXmlrpc.jamloader_trackuploadinit(self.sessionId,wantedFileName)
        except Exception,e:
            raise Exception, [8,"Track upload initialization failed! " + wantedFileName + " " + str(e)]
            
            
        self.setTrackId(trackInfos["trackId"])
        
        
    def setTrackId(self,trackId):
        self.trackId = trackId

        self.queueOut.put(["trackid",self.trackId])
        
          
    def uploadNow(self):
        
        
        if not self.sessionId:
            self.sessionId = self.getSessionId()
                
        if len(self.sessionId)<20:
            self.queueOut.put(["Error","sessionId looks too small"])
            raise Exception, [1,"sessionId looks too small"]

        self.trackInit(self.wantedFileName)
        success = False
        #while not success:
        
        
        if not self.isTesting:
            servers = self.jamendoXmlrpc.jamloader_getservers() + fallbackServers
        else:
            servers = [{"host":"127.0.0.1:8081"},{"host":"127.0.0.1:8080"}] + fallbackServers
        

        for server in servers:
            #print server
            
            try:
                serverXmlrpc = getXmlrpcProxy("http://"+server["host"]+"/xmlrpc/")
                av = serverXmlrpc.isAvailable()
            except Exception, e:
                self.queueOut.put(["Warning", server["host"] + " : " + str(e)])
                continue
            
            
            #todo ban servers if upload always fails with them?
            if av:
                self.uploadTrackToXmlrpcServer(serverXmlrpc,self.localFileName)
                return True
        
        return False
            
    def uploadTrackToXmlrpcServer(self,serverXmlrpc,localFileName):
        try:
            localFileStat = os.stat(localFileName)
        except Exception,e:
            self.queueOut.put(["Error", "Can't stat() the file %s: %s" % ( localFileName, str(e) )])
            raise Exception, [2,"Can't stat() the file %s: %s " + ( localFileName, str(e) )]

        
        try:
            localFileSize = localFileStat.st_size
            assert localFileSize>1024
        except Exception,e:
            raise Exception, [3,"Flac file is too small or empty. " + str(e)]

        
        try:
            localFilePointer = file(localFileName,'rb')
            localFilePointer.seek(0)
        except Exception,e:
            raise Exception, [4,"Flac file is not readable! " + str(e)]

        return self.uploadTrackToXmlrpcServerWithPointer(serverXmlrpc,localFileName,localFilePointer,localFileSize)





    def uploadTrackToXmlrpcServerWithPointer(self,serverXmlrpc,localFileName,localFilePointer,localFileSize):

        self.isSending =True
        pieceNo = 0
        pieceCount = int(math.ceil(localFileSize*1.0/self.pieceSize))
        #print pieceCount
        try:
            while pieceNo < pieceCount+1:
                packetData = localFilePointer.read(self.pieceSize)
                i = 0
                while i < packetNumRetries+1 :
                    if i == (packetNumRetries):
                        raise Exception, ["max try reach (%s)" % packetNumRetries]
                    try:
                        ret = serverXmlrpc.trackUpload(self.sessionId,self.trackId,pieceNo,self.pieceSize,xmlrpclib.Binary(packetData))
                        self.queueOut.put_nowait(["status",["uploading",(pieceNo/float(pieceCount))*100 ]])
                        i = packetNumRetries+1
                    except xmlrpclib.Fault, fault:
                        self.queueOut.put_nowait(["debug",["xmlrpc fault sending piece %s on try %s (%s)" % (pieceNo, i, fault.faultString )]])
                        if str(fault.faultCode) == "22222":
                            pieceNo = -1
                            localFilePointer.seek(0)
                            i = packetNumRetries+1
                    except Exception, e:
                    	#print "error sending piece %s on try %s (%s)" % (pieceNo, i, e)
                        self.queueOut.put_nowait(["debug",["error sending piece %s on try %s (%s)" % (pieceNo, i, e )]])
                        time.sleep(5)
                    i+=1
                pieceNo += 1

                        
                                    

        except Exception,e:
            localFilePointer.close()
            self.queueOut.put(["Error", [5,"Upload failed : %s " % e] ]) 


        self.queueOut.put(["status",["hashing", localFileName]])
        
        localFilePointer.seek(0)
        localMD5 = md5.new(localFilePointer.read()).hexdigest()
        localFilePointer.close()

        self.queueOut.put(["status",["finalizing", localFileName]])
        self.isSending = False
        try:
            resp = serverXmlrpc.trackFinished(self.sessionId,self.trackId,localMD5)
        except Exception,e:
            if str(e)=="<Fault 8002: 'error'>": # md5 doesn't match
                raise Exception, [10,"Track finalization failed : MD5 do not match"]
            else :
                raise Exception, [9, "Track finalization failed : "+str(e)]
        
        if resp!=True:
            raise Exception, [6,"Track finalization failed : "+str(resp)]
                        

    def setUploadTrack(self,localFileName):
        self.localFileName = localFileName
        self.wantedFileName = localFileName
        
    def setUploadTrackWithName(self,localFileName, wantedFileName):
        self.localFileName = localFileName
        self.wantedFileName = wantedFileName


class ContentUploaderThread(Thread):
    
    def __init__(self,queueIn, queueOut):
        Thread.__init__(self)
        self.queueIn = queueIn
        self.queueOut = queueOut
        self.isSending = False
        self.forceQuit = False
        self.contentUploader = ContentUploader(queueOut)
        self.setDaemon(True)
        
        
    def setCredentials(self,user,password,isTesting=False):
        self.contentUploader.setCredentials(user,password, False)
        
    def getSessionId(self):
        try:
            rep = self.contentUploader.getSessionId()
        except Exception,e:
            raise Exception, [7,"Session initialization failed"]
        
        return rep
        
    def run(self):
        
        while True: #not self.forceQuit:
            
            #if not self.queueIn.empty() and not self.contentUploader.isSending:
            msg = self.queueIn.get()
            #print msg
            #if msg[0] == "exit":
            #    self.forceQuit = True
            if msg[0] == "addTrack" :
                if len(msg)==3:
                    self.contentUploader.setUploadTrackWithName(msg[1], msg[2])
                    #print "addTrack : %s -- %s" % ( msg[1], msg[2] )
                else :
                    self.contentUploader.setUploadTrack(msg[1])
                    #print "addTrack : %s" % msg[1]
                for i in range(numRetries):
                    try :
                        self.contentUploader.uploadNow()
                    except Exception ,e:
                        #print e
                        self.queueOut.put(["Error",e])
                        
            time.sleep(0.01)  # in seconds
