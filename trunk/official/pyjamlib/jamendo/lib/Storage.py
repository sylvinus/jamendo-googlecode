import os,platform
from shutil import move,rmtree
import Queue
from LocalDatabase import LocalDatabase
import uuid
# formats jam
# mp31 : lowfi mp3
# mp32 : p2p mp3
# ogg1 : ogg q-1 lowfi
# ogg2 : ogg q3 lowfi
# ogg3 : ogg q7 p2p
#
#



class Storage:
    
    def __init__(self,feedback,application_name='jamendo',lowfi_encoding="ogg2",p2p_encoding="ogg3"):
        self.feedback=feedback
        self.appname = application_name
        self.musicdir=''
        self.userdir=''
        self.downloaddir=''
        self.encodinglist={'mp31':('.mp3','lowfi'),'mp32':('.mp3','p2p'),'ogg1':('.ogg','q-1 lowfi'),'ogg2':('.ogg','q3 lowfi'),'ogg3':('.ogg','q7 p2p')}
        self.encoding={}
        self.setEncoding("lowfi",lowfi_encoding)
        self.setEncoding("p2p",p2p_encoding)
        
        self.dbfilename="jamendodb.dat"
    
    
    def setEncoding(self,format,e):

        self.encoding[format]=e
        
    def getDownloadDir(self):
        self.createUserDir()
        return self.downloaddir
    
    def getUserDir(self):
        self.createUserDir()
        return self.userdir
    
    def getMusicDir(self):
        self.createMusicDir()
        return self.musicdir
    
    def getEncodingExt(self,format):
        #format is 'lowfi' or 'p2p'
        return self.encodinglist[self.encoding[format]][0]
        
    def getEncoding(self,format):
        #format is 'lowfi' or 'p2p'
        return self.encoding[format]
    
    def getTemporaryFileFromId(self,trackid,format):
        self.createUserDir()
        return os.path.join(self.downloaddir,str(trackid)+self.getEncodingExt(format))
 
 
 
    def getDBFilename(self):
        
        self.createUserDir()
        return os.path.join(self.userdir,self.dbfilename)
        
 
    def createUserDir(self):
        
        home=os.path.expanduser('~')
        if "windows" in platform.system().lower() or "cygwin" in platform.system().lower():
            path=os.path.join(home,self.appname)
                
        elif "darwin" in platform.system().lower():
                 path=os.path.join(home,'Library','Application Support',self.appname)
            
        else: #Linux
                 path=os.path.join(home,'.'+self.appname)
                    
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
                self.feedback.put(["debug","storage","make user directory succeed"])
            except Exception,e:
                self.feedback.put(["debug","storage","make user directory failed or it exist already"])
        
        download=os.path.join(path,'download')
        
        if not os.path.isdir(download):
            try:
                os.makedirs(download)
                self.feedback.put(["debug","storage","make download directory succeed"])
            except Exception,e:
                self.feedback.put(["debug","storage","make download directory failed or it exist already"])
                              
        self.userdir=path
        self.downloaddir=download
        if not os.path.isfile(str(os.path.join(self.userdir,"key"))):
            f=open(os.path.join(self.userdir,"key"), 'w')
            key=str(uuid.uuid3(uuid.NAMESPACE_DNS, self.appname+'.jamendo.com'))
            f.write(key)
            f.close()
            self.feedback.put(["debug","storage","user key created"])
            self.feedback.put(["internal","key_created",key])
        else:
            self.feedback.put(["debug","storage","user key already exist"])
    
    
    def createMusicDir(self):
        home=os.path.expanduser('~')
        if "windows" in platform.system().lower() or "cygwin" in platform.system().lower():
             #todo chercher system call
             path=os.path.join(home,'Ma Musique','Jamendo')
            
        elif "darwin" in platform.system().lower():
             path=os.path.join(home,'Music','Jamendo')
        
        else: #Linux
             path=os.path.join(home,'Jamendo')
                
        try:
             os.makedirs(path)
             self.feedback.put(["debug","storage","make music directory succeed"])
        except Exception,e:
            self.feedback.put(["debug","storage","make music directory failed or it exist already"])
        
        self.musicdir = path
        
    def resetUserDir(self):
        self.createUserDir()
        
        #todo more protection from bagoo's code !
        if self.userdir!="" and self.userdir!="/":
            rmtree(self.userdir)
            
        self.createUserDir()

    def resetMusicDir(self):
        self.createMusicDir()
        
        #todo more protection from bagoo's code !
        if self.musicdir!="" and self.musicdir!="/":
            rmtree(self.musicdir)
       
        self.createMusicDir()
    
    def findFileFromInfo(self,info):
        self.createMusicDir()
        
        #be sure that the file is on the disk
        artist,album,name=info[0].encode("ascii","ignore"), info[1].encode("ascii","ignore"), info[2].encode("ascii","ignore")
        file=os.path.join(self.musicdir,artist,album,name+self.getEncodingExt("lowfi"))
        if os.path.isfile(file):
            return file
        file=str(os.path.join(self.musicdir,artist,album,name+self.getEncodingExt("p2p")))
        if os.path.isfile(file):
            return file
        else:
            #the file is not on the disk
            self.feedback.put(["debug","storage","File "+str(os.path.join(artist,album,name))+" is not on the disk"])
    
    
    def registerTrackFromTemporaryFile(self,trackid,info,format):

        file=self.getTemporaryFileFromId(trackid,format)
        #say that the file is on the computer
        
        self.createMusicDir()
        
        artist,album,name=info[0].encode("ascii","ignore"), info[1].encode("ascii","ignore"), info[2].encode("ascii","ignore")
                    
        if not os.path.isdir(os.path.join(self.musicdir,artist)):
            os.makedirs(os.path.join(self.musicdir,artist))
        if not os.path.isdir(os.path.join(self.musicdir,artist,album)):
            os.makedirs(os.path.join(self.musicdir,artist,album))
        if not os.path.isfile(os.path.join(self.musicdir,artist,album,name+self.getEncodingExt(format))):
            move(file,os.path.join(self.musicdir,artist,album,name+self.getEncodingExt(format)))
        self.feedback.put(["debug","storage","track "+str(os.path.join(self.musicdir,artist,album,name+self.getEncodingExt(format)))+" successfully registered"])
            
        