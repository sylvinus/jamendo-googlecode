import os, unittest, sys
from time import sleep
import Queue

sys.path.insert(0, os.path.join('..', '..'))

class test_audiobackend(unittest.TestCase):
    
    
    
    def setUp(self):
        self.callbackDone=False
        
    def callbackx(self):
        print 'callback'
        self.callbackDone=True
        
    def test_DefaultAudioBackend(self):
        from jamendo.audio.common import AudioBackend

        self.vlc=AudioBackend(Queue.Queue(1000)).factory("default")
        
        self.genericbehaviour()
 
    def genericbehaviour(self):
        

        self.vlc.setVolume(256)
        self.assertFalse(self.callbackDone)
        
        self.assertTrue(self.vlc.playFile('poisson.mp3'))
        
        self.vlc.registerFinishedCallback(self.callbackx)
        sleep(3)
        self.vlc.checkStatus()
        
        self.assertTrue(self.vlc.getHasPlayed())
        self.assertEqual(self.vlc.getStatus(),"play")
        
        self.vlc.setPosition(50)
        sleep(5)
        self.vlc.pause()
        
        self.assertEqual(self.vlc.getStatus(),'pause')
        
        sleep(3)
        self.vlc.pause()
        self.assertEqual(self.vlc.getStatus(),'play')
        sleep(3)
        self.vlc.stop()
        self.assertEqual(self.vlc.getStatus(),'stop')
        
        self.vlc.playFile('poisson.mp3')
        sleep(3)
        self.vlc.setPosition(95)
        sleep(10)
        
        print self.vlc.getStreamInfo()
        
        self.vlc.checkStatus()
        self.assertFalse(self.vlc.getHasPlayed())
        self.assertEqual(self.vlc.getStatus(),'stop')
        self.assertTrue(self.callbackDone)
        
        
        
        
        

if __name__ == "__main__":
    unittest.main()
    sys.exit(0)
        
        
        
    