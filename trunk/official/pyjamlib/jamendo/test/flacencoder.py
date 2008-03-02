#!/usr/bin/python
# -*- coding: UTF_8 -*-
          
import unittest,Queue,sys,os,threading,time


# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))


from jamendo.lib.ContentUploadCheck import ContentUploadCheck
from jamendo.lib.FlacEncoder import FlacEncoder



class FlacEncoderCheck(unittest.TestCase):

    def setUp(self):
       pass
   

    def testContentUploadCheck(self):

        check = ContentUploadCheck("flac_test_corpus/audio_11025hz8bit.wav")
        self.assertEquals("wav",check[0])
        self.assertEquals(-1,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_44100hz.aiff")
        self.assertEquals("aiff",check[0])
        self.assertEquals(0,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_44100hz16bit.flac")
        self.assertEquals("flac",check[0])
        self.assertEquals(1,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_44100hz16bit.wav")
        self.assertEquals("wav",check[0])
        self.assertEquals(1,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_44100hz24bit.flac")
        self.assertEquals("flac",check[0])
        self.assertEquals(-2,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_44100hz24bit.wav")
        self.assertEquals("wav",check[0])
        self.assertEquals(-2,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_48000hz16bit.wav")
        self.assertEquals("wav",check[0])
        self.assertEquals(1,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_cut_44100hz16bit.wav")
        self.assertEquals("wav",check[0])
        self.assertEquals(1,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_nok_44100hz16bit.flac")
        self.assertEquals("flac",check[0])
        self.assertEquals(1,check[1])
        
        check = ContentUploadCheck("flac_test_corpus/audio_nonpcm_44100hz.wav")
        self.assertEquals("wav",check[0])
        self.assertTrue(check[1]<0)
        
        check = ContentUploadCheck("flacencoder.py")
        self.assertEquals(None,check[0])
        self.assertEquals(0,check[1])
        
        
    def testFlacing(self):
        
        queueIn = Queue.Queue(1000)
        queueOut = Queue.Queue(1000)
        
        
        flacer = FlacEncoder(queueIn,queueOut)
        flacer.start()
        
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_11025hz8bit.wav",False)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_44100hz.aiff",True)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_44100hz16bit.flac",True)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_44100hz16bit.wav",True)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_44100hz24bit.flac",False)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_48000hz16bit.wav",True)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_cut_44100hz16bit.wav",False)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_nok_44100hz16bit.flac",False)
        self._oneFlacTest(queueIn,queueOut,"flac_test_corpus/audio_nonpcm_44100hz.wav",False)
        
        
        
    def _oneFlacTest(self,queueIn,queueOut,file,shouldsucceed):
        
        
        queueIn.put(["toFlac",file,"encoded with Iñtërnâtiônàlizætiøn.flac"])
        
        continueGetting = True
        while continueGetting:
            msg=queueOut.get(True,5)
            
            if msg[0]=="flac_done":
                self.assertTrue(shouldsucceed)
                continueGetting = False
            
            elif msg[0]=="flac_error":
                self.assertFalse(shouldsucceed)
                continueGetting = False
            
            elif msg[0]=="flac_progress":
                print "progress at %s%%" % msg[1]
        
if __name__ == "__main__":
    unittest.main()
    sys.exit(0)