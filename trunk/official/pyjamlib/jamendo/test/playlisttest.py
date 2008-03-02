import os,time,sys,Queue
import unittest

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.Playlist import Playlist
from jamendo.lib.LocalDatabase import LocalDatabase,LocalTrack



class PlaylistCheck(unittest.TestCase):

    def setUp(self):
        self.feedback=Queue.Queue(10000)
        if os.path.isfile("mydb"):
            os.unlink("mydb")
            
        self.db=LocalDatabase(self.feedback,datafile="mydb")
        self.db.start()
        
        

    def testNavigation(self):
        
        playlist=Playlist(self.feedback,self.db,'mp31','ogg3')
        
        playlist.loadFromTrackIds([2,3,4,5,6,7,8,9,4,5,6])
        self.assertTrue(playlist.getStatus()!="play")
        self.assertEqual(playlist.getCurrentTrackId(),2)
        
        playlist.next()
        self.assertTrue(playlist.getStatus()!="play")
        self.assertEqual(playlist.getCurrentTrackId(),3)

        playlist.prev()
        self.assertTrue(playlist.getStatus()!="play")
        self.assertEqual(playlist.getCurrentTrackId(),2)
        
        time.sleep(1)

        playlist.prev()
        playlist.prev()
        self.assertTrue(playlist.getStatus()!="play")
        self.assertEqual(playlist.getCurrentTrackId(),5)
        
        playlist.next()
        playlist.next()
        self.assertTrue(playlist.getStatus()!="play")
        self.assertEqual(playlist.getCurrentTrackId(),2)
        
        playlist.setCurrentTrackIndex(6)
        self.assertTrue(playlist.getStatus()!="play")
        self.assertEqual(playlist.getCurrentTrackId(),8)
        self.assertEqual(playlist.getTrackCountdown(8),0)
        self.assertEqual(playlist.getTrackCountdown(9),1)
        self.assertEqual(playlist.getTrackCountdown(4),2)
        self.assertEqual(playlist.getTrackCountdown(2),5)
        
        
        self.assertEqual(playlist.getSlicedTrackIds(2),[4,5,6,7,8,9,4,5,6,2,3])
        
    def testManage1(self):
        """ Tests lowfi with only one track"""
        
        self.db.dropTables()
        self.db.createTables()
        
        playlist=Playlist(self.feedback,self.db,'mp31','ogg3')
        playlist.setManageOptions({
            "lookahead_lowfi":[0,30],
            "lookahead_bittorrent":[0,0],
            "max_concurrent_lowfi":3,
            "max_concurrent_bittorrent":20
        })
        
        if os.path.isfile("data/213.mp3"):
            os.unlink("data/213.mp3")
        
        lt=LocalTrack(self.db,213)
        lt.setData({"name":"echo","lengths":120})
        lt.save()
        
        playlist.loadFromTrackIds([213])
        
        i=0
        cont=True
        while cont:
            i+=1
            time.sleep(1)
            playlist.loop()
            
            if i==2:
                self.assertTrue("213" in playlist.downloads_lowfi.keys())
            
            
            #download finished !
            if i>2 and len(playlist.downloads_lowfi.keys())==0:
                cont=False
                
            
            #timeout=60s
            if i>60:
                cont=False
                
                
        #file should be downloaded !
        self.assertFalse("213" in playlist.downloads_lowfi.keys())
        
        self.assertTrue(os.path.isfile("data/213.mp3"))
        
        if os.path.isfile("data/213.mp3"):
            os.unlink("data/213.mp3")
        

    def testManage2(self):
        """ Tests lookahead_lowfi """

        self.db.dropTables()
        self.db.createTables()

        
        playlist=Playlist(self.feedback,self.db,'mp31','ogg3')
        playlist.setManageOptions({
            "lookahead_lowfi":[0,3],
            "lookahead_bittorrent":[0,0],
            "max_concurrent_lowfi":3,
            "max_concurrent_bittorrent":20
        })
        
        
        if os.path.isfile("data/213.mp3"):
            os.unlink("data/213.mp3")
        if os.path.isfile("data/210.mp3"):
            os.unlink("data/210.mp3")
        if os.path.isfile("data/211.mp3"):
            os.unlink("data/211.mp3")
        if os.path.isfile("data/212.mp3"):
            os.unlink("data/212.mp3")
        
            
        
        tids = [210,211,212,213]
        
        for id in tids:
            lt=LocalTrack(self.db,id)
            lt.setData({"name":"echo","lengths":120})
            lt.save()
        
        playlist.loadFromTrackIds(tids)
        
        i=0
        cont=True
        step2=False
        while cont:
            i+=1
            time.sleep(1)
            playlist.loop()
            
            if i==2:
                self.assertTrue("210" in playlist.downloads_lowfi.keys())
                self.assertTrue("211" in playlist.downloads_lowfi.keys())
                self.assertFalse("212" in playlist.downloads_lowfi.keys())
                self.assertFalse("213" in playlist.downloads_lowfi.keys())
            
            
            #210 finished, go next, 212 should begin downloading.
            if (not step2) and i>2 and (not "210" in playlist.downloads_lowfi.keys()):
                playlist.next()
                step2=True
                        
            #download finished !
            if i>10 and len(playlist.downloads_lowfi.keys())==0:
                cont=False
                
            
            #timeout=120s
            if i>120:
                cont=False
                
                
        #file should be downloaded !
        self.assertEquals(len(playlist.downloads_lowfi.keys()),0)
        
        self.assertTrue(os.path.isfile("data/210.mp3"))
        self.assertTrue(os.path.isfile("data/211.mp3"))
        self.assertTrue(os.path.isfile("data/212.mp3"))
        self.assertFalse(os.path.isfile("data/213.mp3"))
        
        if os.path.isfile("data/213.mp3"):
            os.unlink("data/213.mp3")
        if os.path.isfile("data/210.mp3"):
            os.unlink("data/210.mp3")
        if os.path.isfile("data/211.mp3"):
            os.unlink("data/211.mp3")
        if os.path.isfile("data/212.mp3"):
            os.unlink("data/212.mp3")
        

    def testManage3(self):
        """ Tests max_concurrent_lowfi """

        self.db.dropTables()
        self.db.createTables()

        
        playlist=Playlist(self.feedback,self.db,'mp31','ogg3')
        playlist.setManageOptions({
            "lookahead_lowfi":[0,30],
            "lookahead_bittorrent":[0,0],
            "max_concurrent_lowfi":2,
            "max_concurrent_bittorrent":20
        })
        
        
        if os.path.isfile("data/213.mp3"):
            os.unlink("data/213.mp3")
        if os.path.isfile("data/210.mp3"):
            os.unlink("data/210.mp3")
        if os.path.isfile("data/211.mp3"):
            os.unlink("data/211.mp3")
        if os.path.isfile("data/212.mp3"):
            os.unlink("data/212.mp3")
        
            
        
        tids = [210,211,212,213]
        
        for id in tids:
            lt=LocalTrack(self.db,id)
            lt.setData({"name":"echo","lengths":120})
            lt.save()
        
        playlist.loadFromTrackIds(tids)
        
        i=0
        cont=True
        step2=False
        while cont:
            i+=1
            time.sleep(1)
            playlist.loop()
            
            if i==2:
                self.assertTrue("210" in playlist.downloads_lowfi.keys())
                self.assertTrue("211" in playlist.downloads_lowfi.keys())
                self.assertFalse("212" in playlist.downloads_lowfi.keys())
                self.assertFalse("213" in playlist.downloads_lowfi.keys())
                playlist.next()
            
            #210 should have been cancelled !
            if i==4:
                self.assertFalse("210" in playlist.downloads_lowfi.keys())
                self.assertTrue("211" in playlist.downloads_lowfi.keys())
                self.assertTrue("212" in playlist.downloads_lowfi.keys())
                self.assertFalse("213" in playlist.downloads_lowfi.keys())
           
            self.assertTrue(len(playlist.downloads_lowfi.keys())<=2)     

            #downloads finished !
            if i>10 and len(playlist.downloads_lowfi.keys())==0:
                cont=False
                
            
            #timeout=120s
            if i>120:
                cont=False
                
                
        #file should be downloaded !
        self.assertEquals(len(playlist.downloads_lowfi.keys()),0)
        
        self.assertTrue(os.path.isfile("data/210.mp3"))
        self.assertTrue(os.path.isfile("data/211.mp3"))
        self.assertTrue(os.path.isfile("data/212.mp3"))
        self.assertTrue(os.path.isfile("data/213.mp3"))
        
        if os.path.isfile("data/213.mp3"):
            os.unlink("data/213.mp3")
        if os.path.isfile("data/210.mp3"):
            os.unlink("data/210.mp3")
        if os.path.isfile("data/211.mp3"):
            os.unlink("data/211.mp3")
        if os.path.isfile("data/212.mp3"):
            os.unlink("data/212.mp3")
        
                              
        
        
        
if __name__ == "__main__":
    unittest.main()
