import unittest,Queue,sys,os,threading
from pysqlite2 import dbapi2 as sqlite

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.LocalDatabase import LocalDatabase,LocalDatabaseSync,LocalTrack,LocalAlbum,LocalArtist


class DatabaseCheck(unittest.TestCase):

    def setUp(self):
       pass
   

    def testFirstLaunch(self):
              
        commands=Queue.Queue(1000)
        feedback=Queue.Queue(1000)
        
        storage=Storage('mp31','ogg3',feedback)
        storage.resetProfile()
        storage.resetMusic()
        
        db=jamendo.lib.LocalDatabase.LocalDatabase(feedback)
        db.start()
        B=jamendo.behaviours.PlayAutomatedRadio.JamendoBehaviourPlayAutomatedRadio(feedback,{"audio_backend":"default","force_sync":True,"commands":commands,"db":db})
        B.start()
