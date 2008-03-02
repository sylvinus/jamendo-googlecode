import unittest,Queue,sys,os,threading

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.JamendoMusicApi import JamendoMusicApiQuery

class MusicApiCheck(unittest.TestCase):

	def testAllAlbums(self):
		self.assertEquals(500,len(JamendoMusicApiQuery("album/list/album/data/json",{"n":500}).get()))
    

if __name__ == "__main__":
    unittest.main()
    sys.exit(0)