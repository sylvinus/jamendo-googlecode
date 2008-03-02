import unittest,Queue,sys,os,threading
from pysqlite2 import dbapi2 as sqlite

# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', '..'))

from jamendo.lib.LocalDatabase import LocalDatabase,LocalDatabaseSync,LocalTrack,LocalAlbum,LocalArtist


class DatabaseCheck(unittest.TestCase):

    def setUp(self):
        self.feedback=Queue.Queue(10000)
        if os.path.isfile("mydb-test"):
            os.unlink("mydb-test")
        self.db=LocalDatabase(self.feedback,datafile="mydb-test")
        self.db.start()

    def tearDown(self):
        
        queue=self.db.close(erase_datafile=True)
        
        #wait for the close
        queue.get()
        
        self.assertFalse(os.path.isfile("mydb-test"))

    def testCreate(self):
        """ tests CREATE TABLE """
        try:
            self.db.dropTables()
        except:
            pass
        
        self.db.createTables()
        
        q=self.db.fetchall("SELECT * FROM albums;").get()

        self.assertEqual(q[0],True)
        self.assertEqual(q[1],[])

    
    def testDrop(self):
        
        try:
            self.db.createTables()
        except:
            pass
        
        self.db.dropTables()
        
        q=self.db.fetchall("SELECT * FROM albums;").get()
        
        self.assertEqual(q[0],False)
        self.assertEqual(q[1],sqlite.OperationalError)
    
    
    def testLocalAlbum(self):
        
        self.db.createTables()
        
        #load an album
        item=LocalAlbum(self.db,42)        
        self.assertEqual(item.data["id"],42)
        
        #set its name
        item.setData({"name":"A Test album"})
        self.assertEqual(item.data["name"],"A Test album")
        self.assertTrue(item.save()[0])
        
        #get its name
        item=LocalAlbum(self.db,42)
        itemdata=item.getData()
        self.assertEqual(itemdata["name"],"A Test album")
        
        #update the name
        item.setData({"name":"A Test album - reloaded"})
        self.assertTrue(item.save()[0])
        self.assertEqual(item.data["name"],"A Test album - reloaded")
        
        #get its name
        item=LocalAlbum(self.db,42)
        itemdata=item.getData()
        self.assertEqual(itemdata["name"],"A Test album - reloaded")
        
        
        #test saving local data
        item=LocalTrack(self.db,209)
        item.setData({"lengths":47,"ondisk":2})
        self.assertTrue(item.save()[0])
        
        item=LocalTrack(self.db,209)
        itemdata=item.getData()
        self.assertEqual(itemdata["ondisk"],2)
        
        item.setData({"lengths":47,"ondisk":1})
        self.assertTrue(item.save()[0])

        item=LocalTrack(self.db,209)
        itemdata=item.getData()
        self.assertEqual(itemdata["ondisk"],1)
        
        
        
        self.db.dropTables()
    
    def testSync(self):
        
        #return True
        
        done=threading.Event()
        failure=threading.Event()
        self.db.createTables()
        sync = LocalDatabaseSync(self.feedback,self.db,done,failure)
        sync.start()
        done.wait()
        
        self.failIf(failure.isSet())
        
        
        #print self.db.fetchone("SELECT * FROM tracks WHERE id=213").get()
        
        artists=self.db.fetchone("SELECT count(*) FROM artists").get()
        
        self.assertTrue(artists[0])
        self.assertTrue(artists[1][0]>1000)
        
        albums=self.db.fetchone("SELECT count(*) FROM albums").get()
        
        self.assertTrue(albums[0])
        self.assertTrue(albums[1][0]>1500)
        
        tracks=self.db.fetchone("SELECT count(*) FROM tracks").get()
        
        self.assertTrue(tracks[0])
        self.assertTrue(tracks[1][0]>10000)
        
        names=self.db.fetchone("SELECT tracks.name as track_name,albums.name as album_name,artists.dispname as artist_dispname FROM tracks,albums,artists WHERE tracks.album_id=albums.id and albums.artist_id=artists.id LIMIT 0,1").get()

        self.assertTrue(names[0])
        self.assertTrue(len(names[1]["track_name"])>0)
        self.assertTrue(len(names[1]["album_name"])>0)
        self.assertTrue(len(names[1]["artist_dispname"])>0)
            
        self.db.dropTables()

    

if __name__ == "__main__":
    unittest.main()
    sys.exit(0)