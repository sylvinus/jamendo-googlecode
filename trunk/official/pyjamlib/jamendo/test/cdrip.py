import unittest,Queue,sys,os,threading,time


# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))


from jamendo.lib import LocalPlatform
from jamendo.lib.cdrip import CdRipper


class CdRipCheck(unittest.TestCase):

    def setUp(self):
       pass
   

    def testProcedure(self):
              
        queueIn=Queue.Queue(1000)
        queueOut=Queue.Queue(1000)

        
        cdrip = CdRipper(queueIn,queueOut)
        cdrip.start()

        time.sleep(2)
        
        msg = queueOut.get_nowait()
        self.assertEquals("backend",msg[0])
        
        queueIn.put(["startDetection"])
        
        print "Please insert a CD within the 10 next seconds..."
        time.sleep(5)
        
        #detection should have started
        msg = queueOut.get_nowait()
        self.assertEquals("cd_detect_start",msg[0])
        
        print "5 seconds...."
        time.sleep(5)
        print "Now, I'm testing CD detection."
        
        msg = queueOut.get(True,20)
        self.assertEquals("cd_detect_mount",msg[0])
        print "Found CD at %s" % (msg[1],)
        cd_device = msg[1]
        
        
        queueIn.put(["getAudioTracks",cd_device])
        msg = queueOut.get(True,20)
        self.assertEquals("cd_tracks",msg[0])
        print msg[1]
        self.assertTrue(len(msg[1])>0)
        
        if os.path.isfile("extracted.wav"):
            os.unlink("extracted.wav")

            
        queueIn.put(["extractTrackToFile",cd_device,0,"extracted.wav"])
        
        
        msg=queueOut.get(True,15)
        self.assertEquals("cd_extract_start",msg[0])
        
        while msg[0]!="cd_extract_stop":
            msg=queueOut.get(True,15)
            if msg[0]=="cd_extract_progress":
                print "CD ripping %s%%" % msg[1]
        
        self.assertTrue(os.path.isfile("extracted.wav"))
        
        print "ripping done!"
        
        print "Now, you have 10 more seconds to eject the CD, please"
        time.sleep(5)
        print "5 seconds...."
        time.sleep(5)
        msg = queueOut.get(True,10)
        self.assertEquals("cd_detect_unmount",msg[0])
        print "CD was ejected ok."
        
        
if __name__ == "__main__":
    unittest.main()
    sys.exit(0)