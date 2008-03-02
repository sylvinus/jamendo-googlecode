try:
    from pysqlite2 import dbapi2 as sqlite
except:
    from sqlite3 import dbapi2 as sqlite
    
import time

if __name__ == "__main__":
    print sqlite.sqlite_version_info
    print sqlite.Row

from jamendo.lib.JamendoMusicApi import JamendoMusicApiQuery
import threading, Queue

import Storage


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class LocalDatabase(threading.Thread):
    
    def __init__(self,feedback,datafile):
        
        threading.Thread.__init__(self)
        self.feedback=feedback
        self.datafile=datafile
        self.setDaemon(True)
        self.commit=False
        self.queries=Queue.Queue(10000)
        self.do_run=True
        

    #this code runs on the caller!
    def fetchone(self,query,data=()):
        
        queue = Queue.Queue(1)
        self.queries.put(["fetchone",query,data,queue])
        return queue
    
    #this code runs on the caller!
    def fetchall(self,query,data=()):
        
        queue = Queue.Queue(1)
        self.queries.put(["fetchall",query,data,queue])
        return queue

    
    #this code runs on the caller!
    def execute(self,query,data=()):
        
        queue = Queue.Queue(1)
        self.queries.put(["execute",query,data,queue])
        return queue

    #this code runs on the caller!
    def fetchfirst(self,query,data=()):
        
        queue = Queue.Queue(1)
        self.queries.put(["fetchfirst",query,data,queue])
        return queue

    
    #this code runs on the caller!
    def executescript(self,query):
        
        queue = Queue.Queue(1)
        self.queries.put(["executescript",query,0,queue])
        return queue
    
     #this code runs on the caller!
    def executemany(self,query,data=()):
        
        queue = Queue.Queue(1)
        self.queries.put(["executemany",query,data,queue])
        return queue
    
    def close(self,erase_datafile=False):
        queue = Queue.Queue(1)
        self.queries.put(["close",erase_datafile,queue])
        return queue
    
    def dropTables(self):
        self.executescript("""
         DROP TABLE albums;
         DROP TABLE artists;
         DROP TABLE tracks;
         
        """)
    
    """
     todo how to manage changes to the structure ??
    """
    def createTables(self):
        
        self.executescript("""
   CREATE TABLE albums (
  id integer,
  artist_id integer,
  name text,
  release_date timestamp,
  archive_set integer,
  filename text
    );
   CREATE TABLE albumsl (
     id integer
   );
   
    CREATE TABLE artists (
  id integer,
  name text,
  dispname text,
  homepage text,
  pays text,
  image text
    );
    CREATE TABLE artistsl (
     id integer
   );
    
    CREATE TABLE tracks (
  id integer,
  album_id integer,
  name text,
  track_no integer,
  filename text,
  lengths integer,
  license text
  );
  CREATE TABLE tracksl (
     id integer,
     ondisk integer
   );
       
        
        """)
        
    
    def run(self):
        self.connect()
        self.time=time.time()
        while self.do_run:
            #print "boucle database\n"
            if self.commit and time.time()-self.time > 10:
                self.con.commit()
                self.time=time.time()
                self.commit=False
                self.feedback.put(["debug","commit","commit every 10 seconds"])

                
            q=self.queries.get()
            self.feedback.put(["debug","LocalDatabase query : "+str(q)])
            
            try:
                cur = self.con.cursor()
                #raise Exception,str(q[0])+str(q[1])+str(q[2])
                if (q[0]=="execute"):
                    q[3].put([True,cur.execute(q[1],q[2])])
                    self.commit=True
                if (q[0]=="executemany"):
                    q[3].put([True,cur.executemany(q[1],q[2])])
                    self.commit=True
                if (q[0]=="executescript"):
                    q[3].put([True,self.con.executescript(q[1])])
                    self.commit=True
                if (q[0]=="fetchall"):
                    cur.execute(q[1],q[2])
                    q[3].put([True,cur.fetchall()])
                if (q[0]=="fetchone"):
                    cur.execute(q[1],q[2])
                    q[3].put([True,cur.fetchone()])
                if (q[0]=="fetchfirst"):
                    cur.execute(q[1],q[2])
                    one=cur.fetchone()
                    if one==None:
                        q[3].put([True,None])
                    else:
                        q[3].put([True,one[0]])
                    
            except sqlite.OperationalError,e:
                q[3].put([False,sqlite.OperationalError,e])
            except Exception,e:
                q[3].put([False,Exception,e])
                
    
    def connect(self):
        self.con=sqlite.connect(self.datafile, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        #if you want persistent database : isolation_level=None
        self.con.row_factory = sqlite.Row
        #self.con.row_factory = dict_factory
        
        
        self.createTables()
        self.con.commit()




class LocalDatabaseSync(threading.Thread):
    
    def __init__(self,feedback,db,doneevent,failureevent):
        
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.feedback=feedback;
        self.db=db
        self.doneevent=doneevent
        self.failureevent=failureevent
    

    def run(self):

        self.feedback.put(["debug","sync started"])
        
        #http://initd.org/pub/software/pysqlite/doc/usage-guide.html#connecting-to-a-database
        artists=JamendoMusicApiQuery('artist/list/artist/data//',{'o':'id_asc','ari':'info_min'},feedback=self.feedback).get()
        artists_replace=[]
        artists_replacel=[]
        for row in artists:
            artists_replace.append((row["id"],row["name"],row["dispname"]))
            artists_replacel.append((row["id"],))
        
        #todo transaction
        self.db.executemany("REPLACE INTO artists(id,name,dispname) VALUES(?,?,?)",artists_replace)
        self.db.executemany("INSERT INTO artistsl(id) VALUES (?)",artists_replacel)
        
        del artists
        del artists_replace
        del artists_replacel
        




        albums=JamendoMusicApiQuery('album/list/album/data//',{'o':'id_asc','ali':'info_min'},feedback=self.feedback).get()
        albums_replace=[]
        albums_replacel=[]
        for row in albums:
            albums_replace.append((row["id"],row["name"],row["archive_set"],row["artist_id"]))
            albums_replacel.append((row["id"],))
        self.db.executemany("REPLACE INTO albums(id,name,archive_set,artist_id) VALUES(?,?,?,?)",albums_replace)
        self.db.executemany("INSERT INTO albumsl(id) VALUES (?)",albums_replacel)
        del albums
        del albums_replace
        del albums_replacel
        
        
        tracks=JamendoMusicApiQuery('track/list/track/data//',{'o':'id_asc','tri':'info_common'},blockunit=2000,feedback=self.feedback).get()

        tracks_replace=[]
        tracks_replacel=[]
        for row in tracks:
            tracks_replace.append((row["id"],row["name"],row["lengths"],row["track_no"],row["album_id"],row["filename"]))
            tracks_replacel.append((row["id"],))
        self.db.executemany("REPLACE INTO tracks(id,name,lengths,track_no,album_id,filename) VALUES(?,?,?,?,?,?)",tracks_replace)
        self.db.executemany("INSERT INTO tracksl(id) VALUES(?)",tracks_replacel)
        
        del tracks
        del tracks_replace
        del tracks_replacel

        self.feedback.put(["debug","sync finished"])

        self.doneevent.set()
        self.db.commit()
        


class LocalItem:
    def __init__(self,db,id):
        self.db=db
        self.data={"id":id}
        self.fields={}
        self.fields_local={}
        self.feedback=Queue.Queue(1000)
        self.init()
    
    
    def save(self):    
        return [self._save(self.table,self.fields)[0] and self._save(self.table+"l",self.fields_local)[0]]
        
    
    def _save(self,table,fields):
        q=self.db.fetchfirst("SELECT 1 FROM "+table+" WHERE id = ?",(self.data["id"],)).get()
        
        if not q[0]:
            raise Exception,str(q[1])+" "+str(q[2])
            return q

        if (q[1]):
            q="UPDATE "+table+" SET "
            args=[]
            updates=[]
            for k in self.data.keys():
                if k!="id" and (k in fields):
                    updates.append(k+"=?")
                    args.append(self.data[k])
            q+=(",".join(updates))+" WHERE id=?"
            args.append(self.data["id"])
            
            if len(args)>1:
                return self.db.execute(q,tuple(args)).get()
            else:
                return [True]
        else:
            q="INSERT INTO "+table+" ("
            values=[]
            args=[]
            insertfields=[]
            for k in self.data.keys():
                if (k=="id" or (k in fields)):
                    values.append("?")
                    args.append(self.data[k])
                    insertfields.append(k)
                    
            q+=(",".join(insertfields))+") VALUES ("+(",".join(values))+");"
            
            if len(args)>0:
                return self.db.execute(q,tuple(args)).get()
            else:
                return [True]
    
    
    def setData(self,data):
        self.data.update(data)
    
    #fetch_when : never, needed, always
    def getData(self,infos={},fetch_when="needed"):
        
        d=self.db.fetchone("SELECT * FROM "+self.table+" WHERE id=?",(self.data["id"],)).get()

        if (d[0] and d[1]):
            for f in self.fields.keys():
                if d[1][f]!=None:
                     self.data[f]=d[1][f]
        else:
            self.getDataFromMusicApi(self.data["id"])
            if self.table=="tracks":
                self.data["ondisk"]=0
            self.save()
             

        d=self.db.fetchone("SELECT * FROM "+self.table+"l WHERE id=?",(self.data["id"],)).get()

        if (d[0] and d[1]):
            for f in self.fields_local.keys():
                if d[1][f]!=None:
                     self.data[f]=d[1][f]
            
   
        return self.data
                    

    def getDataFromMusicApi(self,id):
        
        #print JamendoMusicApiQuery('track/id/track/data/json/'+str(id),{'o':'id_asc','tri':'info_common'},blockunit=2000,feedback=self.feedback).get()
        if self.table=="tracks":
            d=JamendoMusicApiQuery('track/id/track/data/json/'+str(id),{'o':'id_asc','tri':'info_common'},blockunit=2000,feedback=self.feedback).get()
        elif self.table=="albums":
            d=JamendoMusicApiQuery('album/id/album/data/json/'+str(id),{'o':'id_asc','ali':'info_min'},feedback=self.feedback).get()
        else:
            d=JamendoMusicApiQuery('artist/id/artist/data/json/'+str(id),{'o':'id_asc','ari':'info_min'},feedback=self.feedback).get()
            
        for f in self.fields.keys():
            if f in d[0]:
                 self.data[f]=d[0][f]
        for f in self.fields_local.keys():
            if f in d[0]:
                 self.data[f]=d[0][f]
        
class LocalAlbum(LocalItem):
    
    def init(self):
        self.table="albums"
        self.fields={
            "id":"integer",
            "artist_id":"integer",
            "name":"text",
            "release_date":"timestamp",
            "archive_set":"integer",
            "filename":"text"
            }
    

class LocalArtist(LocalItem):
    
    def init(self):
        self.table="artists"
        self.fields={
            "id":"integer",
            "name":"text",
            "dispname":"text",
            "homepage":"text",
            "pays":"text",
            "image":"text"
            }
    
class LocalTrack(LocalItem):
    
    def init(self):
        self.table="tracks"
        self.fields={
            "id":"integer",
            "album_id":"integer",
            "name":"text",
            "track_no":"integer",
            "filename":"text",
            "lengths":"integer",
            "license":"text"
        }
        self.fields_local={
            "ondisk":"integer"
            }
    
        
        
        
        
        
        