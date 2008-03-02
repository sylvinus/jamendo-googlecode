import os,time,sys,Queue
import unittest

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

import jamendo.lib.Playlist


class PlaylistManagerCheck(unittest.TestCase):

    def setUp(self):
        self.feedback=Queue.Queue(10000)
        self.downloads={"lowfi":[],"hifi":[]}
        self.finished={"lowfi":[],"hifi":[]}


    def testManage1(self):
        
        """ Basic behaviour, lowfi only : max concurrent, currentTrackNo, download callback, slicing """
        
        self.manager = jamendo.lib.Playlist.PlaylistManager({
            "lookahead_lowfi":[0,100],
            "lookahead_hifi":[10,300],
            "max_concurrent_lowfi":2,
            "max_concurrent_hifi":20
        },self.callback_Download)
        
        self.manager.setCurrentTrackNo(1)
        
        self.manager.setTrackList([1,2,3,4])
        self.manager.setTrackInfos({
           "1":{"lengths":"60.1"},                    
           "2":{"lengths":"60.1"},
           "3":{"lengths":"60.1"},
           "4":{"lengths":"60.1"},
       })
        
        self.manager.manage()
        
        self.assertEquals(self.downloads["lowfi"],[2,3])
        self.assertEquals(self.downloads["hifi"],[])
        
        self.simulate_FinishedDownload("lowfi",2)
        
        self.assertEquals(self.downloads["lowfi"],[3])
        self.assertEquals(self.downloads["hifi"],[])
        
        self.manager.manage()

        self.assertEquals(self.downloads["lowfi"],[3,4])
        self.assertEquals(self.downloads["hifi"],[])
        
        self.simulate_FinishedDownload("lowfi",4)
        
        self.assertEquals(self.downloads["lowfi"],[3])
        self.assertEquals(self.downloads["hifi"],[])
        
        self.manager.manage()
        
        self.assertEquals(self.downloads["lowfi"],[3,1])
        self.assertEquals(self.downloads["hifi"],[])


    def testManage2(self):
        
        """ lookaheads, lowfi+hifi, setcurrenttrack """
        
        self.manager = jamendo.lib.Playlist.PlaylistManager({
            "lookahead_lowfi":[0,4],
            "lookahead_hifi":[2,300],
            "max_concurrent_lowfi":20,
            "max_concurrent_hifi":20
        },self.callback_Download)
        
        self.manager.setCurrentTrackNo(1)
        
        self.manager.setTrackList([1,2,3,4,5,6,7])
        self.manager.setTrackInfos({
           "1":{"lengths":"60.1"},                    
           "2":{"lengths":"60.1"},
           "3":{"lengths":"60.1"},
           "4":{"lengths":"60.1"},
           "5":{"lengths":"60.1"},
           "6":{"lengths":"60.1"},
           "7":{"lengths":"600000"},
       })
        
        self.manager.manage()
        
        
        self.assertEquals(self.downloads["lowfi"],[2,3,4,5,6])
        self.assertEquals(self.downloads["hifi"],[5,6,7])
        
        self.simulate_FinishedDownload("lowfi",2)
        self.simulate_FinishedDownload("lowfi",4)
        self.simulate_FinishedDownload("hifi",5)
        self.simulate_FinishedDownload("hifi",7)
        
        self.manager.manage()
        
        """ nothing new should have been downloaded """                    
        self.assertEquals(self.downloads["lowfi"],[3,5,6])
        self.assertEquals(self.downloads["hifi"],[6])
        
        self.manager.setCurrentTrackNo(2)
        
        self.manager.manage()
        
        self.assertEquals(self.downloads["lowfi"],[3,5,6,7])
        self.assertEquals(self.downloads["hifi"],[6])
        
               
      
    def simulate_FinishedDownload(self,type,trackid):
        self.finished[type].append(trackid)
        self.downloads[type].remove(trackid)
        self.manager.setFinishedDownload(type,trackid)
        
           
    def callback_Download(self,type,trackid):
        self.downloads[type].append(trackid)
        
        if trackid in self.finished[type]:
            self.simulate_FinishedDownload(type,trackid)
            
if __name__ == "__main__":
    unittest.main()
