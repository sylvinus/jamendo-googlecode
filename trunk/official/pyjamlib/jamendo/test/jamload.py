import os, unittest, sys
from time import sleep
import Queue

sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.ContentUploader import ContentUploader

class test_jamload(unittest.TestCase):
    
    
    def test_upload(self):
        
        q = Queue.Queue(10000)
        uploader = ContentUploader(q)
        
        uploader.setCredentials("testusera","a",True)
        
        uploader.setUploadTrack("test1.wav")
        
        
        #uploader.start()
        #uploader.join()
        uploader.uploadNow()
        
        #print "test thread joined"
        
        while True:
            try:
                msg = q.get_nowait()
            except:
                return
            print msg
            
            if msg[0]=="error":
                return self.fail(msg[1])
            elif msg[0]=="success":
                print "got success"
                return
        

if __name__ == "__main__":
    unittest.main()
    sys.exit(0)