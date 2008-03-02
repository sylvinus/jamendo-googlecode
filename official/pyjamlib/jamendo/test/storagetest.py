import os,time,sys,Queue,threading
import unittest

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.Playlist import Playlist
from jamendo.lib.storage import Storage
from jamendo.lib.LocalDatabase import LocalDatabase,LocalTrack,LocalDatabaseSync




class StorageCheck(unittest.TestCase):

    def setUp(self):
        self.feedback=Queue.Queue(10000)
        self.storage=Storage('mp31','ogg3',self.feedback)
        self.sync=False
        self.storage.createUserDir()
        self.storage.createMusicDir()
        dbname=self.storage.provideDBFile()
        if os.path.isfile(dbname):
            os.unlink(dbname)
        self.db=LocalDatabase(self.feedback,datafile=dbname)
        self.db.start()
        
        
        """
    def test1(self):
        
        if self.sync:
            self.db.dropTables()
            done=threading.Event()
            failure=threading.Event()
            self.db.createTables()
            sync = LocalDatabaseSync(self.feedback,self.db,done,failure)
            sync.start()
            done.wait()
        
        playlist=Playlist(self.feedback,self.db,'mp31','ogg3')
        playlist.setManageOptions({
            "lookahead_lowfi":[0,30],
            "lookahead_bittorrent":[0,0],
            "max_concurrent_lowfi":3,
            "max_concurrent_bittorrent":20
        })
        
        #lt=LocalTrack(self.db,213)
        #print lt.getData()
        #lt.setData({"name":"echo","lengths":120})
        #lt.save()
        playlist.loadFromTrackIds([213])
        
        i=0
        cont=True
        while cont:
            i+=1
            time.sleep(1)
            playlist.loop()
            
            #if i==2:
             #   self.assertTrue("213" in playlist.downloads_lowfi.keys())
            
            
            #download finished !
            if i>2 and len(playlist.downloads_lowfi.keys())==0:
                cont=False
                
            
            #timeout=60s
            if i>60:
                cont=False
                print "time out"
                
        time.sleep(1)        
        #file should be downloaded !
        playlist.play()
        time.sleep(10)
        playlist.next()
        time.sleep(10)
        
        """
    def test2(self):
        time.sleep(5)
        tids = [255,253,211]
        userdir=self.storage.getUserDir()
        musicdir=self.storage.getMusicDir()
        self.assertTrue(os.path.isdir(userdir))
        self.assertTrue(os.path.isdir(musicdir))
        self.assertTrue(os.path.isfile(str(self.storage.provideDBFile())))
        playlist=Playlist(self.feedback,self.db,'vlc','mp31','ogg3')
        playlist.setManageOptions({
            "lookahead_lowfi":[0,30],
            "lookahead_bittorrent":[0,0],
            "max_concurrent_lowfi":3,
            "max_concurrent_bittorrent":20
        })
        
        playlist.loadFromTrackIds(tids)
        
        i=0
        cont=True
        step2=False
        while cont:
            i+=1
            time.sleep(1)
            playlist.loop()
            
                        
            #download finished !
            if i>10 and len(playlist.downloads_lowfi.keys())==0:
                cont=False
                
            
            #timeout=120s
            if i>120:
                cont=False
        
        for id in tids:
            info=playlist.findInfoFromId(id)
            artist,album,name=info[0].encode("ascii","ignore"), info[1].encode("ascii","ignore"), info[2].encode("ascii","ignore")
            self.assertTrue(os.path.isdir(os.path.join(self.storage.getMusicDir(),artist)))
            self.assertTrue(os.path.isdir(os.path.join(self.storage.getMusicDir(),artist,album)))
            self.assertTrue(os.path.isfile(os.path.join(self.storage.getMusicDir(),artist,album,name+".mp3")))
        
        playlist.play()
        time.sleep(5)
        playlist.next()
        time.sleep(5)
        playlist.next()
        time.sleep(5)
        
        
        self.storage.resetMusic()
        self.storage.resetProfile()
        self.assertFalse(os.path.isdir(userdir))
        self.assertFalse(os.path.isdir(musicdir))
        
        
if __name__ == "__main__":
    unittest.main()