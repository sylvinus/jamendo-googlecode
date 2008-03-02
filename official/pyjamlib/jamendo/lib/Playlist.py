import JamendoMusicApi
from LowFi import LowFi
import threading,os
from Storage import Storage
from LocalDatabase import LocalTrack, LocalAlbum, LocalArtist


class Playlist(threading.Thread):
    
    def __init__(self,feedback,db,audio_backend,lowfi="ogg2",p2p="ogg3"):
        
        threading.Thread.__init__(self)
        self.feedback=feedback
        self.db=db
        
        #currently playing index
        self.currentTrackIndex=0
        self.trackids=[]
        self.status="ready"
        
        self.storage=Storage(self.feedback,lowfi,p2p)
        self.storage.createUserDir()
        self.storage.createMusicDir()
        
        self.downloads={"lowfi":{},"hifi":{}}
        
        from jamendo.audio.common import AudioBackend
        
        self.audio=AudioBackend(self.feedback).factory(audio_backend)
        
        if not self.audio:
            return False
        
        self.audio.registerFinishedCallback(self.playerFinished)
        
        
        self.manager = PlaylistManager({},self.startDownload)
        
    def setManageOptions(self,options):
        if self.manager:
            self.manager.setOptions(options)
        
    """
    callbacks
    """

    def startDownload(self,type,trackid):
        if type=="lowfi":
            edone = threading.Event()
            efailure = threading.Event()
            eabort = threading.Event()
            
            self.downloads[type][str(trackid)] = {
                  "downloader":LowFi(self.feedback,trackid,self.storage.getEncoding('lowfi'),self.storage.getTemporaryFileFromId(trackid,'lowfi'),abortevent = eabort, doneevent = edone, failureevent = efailure),
                  "doneevent":edone,
                  "failureevent":efailure,
                  "abortevent":eabort
                  
            }
            
            self.downloads[type][str(trackid)]["downloader"].start()
            
        elif type=="hifi":
            pass
        
    def playerFinished(self):
        self.feedback.put(["debug","playlist","playlist finished, loop"])
        self.next()
        
        
        
        
        
    def run(self):

        self.feedback.put(["debug","playlist","starting playlist"])
        while True:
            self.loop()
    
    def loop(self):
        self.manager.manage()
        self.audio.checkStatus()
 
        
    def loadFromTrackIds(self,idlist):
        self.trackids=idlist
        self.manager.setTrackList(idlist)
    
    def getStatus(self):
        
        self.audio.checkStatus()
        return self.status
    
    
    def load(self,params1,params2):
        
        self.loadFromTrackIds(JamendoMusicApi.JamendoMusicApiQuery(params1,params2,feedback=self.feedback).get())
    
    def play(self):
        #"play" always plays track from the begining
        #if you want to resume after "pause", select "pause" again
        
        trackid = self.getCurrentTrackId()
        
        track=LocalTrack(self.db,trackid)
        track.getData()
        if track.data["ondisk"]==0:
            if self.status=="play": 
                self.next()
        else:
            self.status="play"
            file=self.storage.findFileFromInfo(self.findInfoFromId(trackid))
            if file != None:
                self.audio.playFile(file)
                self.feedback.put(["debug","playlist","play file: "+str(file)])
    
        
    def pause(self):
        self.audio.pause()    
        self.feedback.put(["debug","playlist","pause"])
    def next(self):
        self.setCurrentTrackIndex(self.currentTrackIndex+1)
        
        if self.status=="play":
            self.play()
        self.feedback.put(["debug","playlist","go to next track"])
            
    def prev(self):
        self.setCurrentTrackIndex(self.currentTrackIndex-1)
        
        if self.status=="play":
            self.play()
        self.feedback.put(["debug","playlist","go to previous track"])
 
    def getCurrentTrackId(self):
        return self.trackids[self.currentTrackIndex]
    
    def setCurrentTrackIndex(self,trackindex):
        i = (trackindex) % len(self.trackids)
        self.currentTrackIndex = i
        self.manager.setCurrentTrackNo(i)
    
    #
    # This function makes sure we download in advance
    #
    #
    
    def findInfoFromId(self,trackid):
        #return a list where it can be found in this order:
        #artist, album, track
        
        
        
        info=[]
        track=LocalTrack(self.db,trackid).getData()
        #insert the track name
        info.insert(0,track["filename"])
        #find the album_id
        album=LocalAlbum(self.db,track["album_id"]).getData()
        #insert album name
        info.insert(0,album["name"])
        #find the artist id
        artist=LocalArtist(self.db,album["artist_id"]).getData()
        #insert artist name
        info.insert(0,artist["dispname"])
        return info
    
    def loop(self):
       
        for type in ["lowfi","hifi"]: 
            for tid in self.downloads[type].keys():
                if self.downloads[type][str(tid)]["doneevent"].isSet():
                    
                    self.storage.registerTrackFromTemporaryFile(trackid,self.findInfoFromId(trackid),'lowfi')
                    
                    """ todo port this into storage
                    lt=LocalTrack(self.db,trackid)
                    lt.setData({"ondisk":1})
                    lt.save()
                    """
                    
                    self.manager.setFinishedDownload(type,tid,self.downloads[type][tid]["failureevent"].isSet())
                    self.downloads[type].remove(str(tid))
                    
        self.manager.manage()
        
        

        
"""
 I manage a playlist
 I make sure we always have something to play next
"""
class PlaylistManager:
    
    def __init__(self,options,callbackDownload):
        
        """ Some default options """
        self.options = {
            "lookahead_lowfi":[0,30],
            "lookahead_hifi":[10,300],
            "max_concurrent_lowfi":3,
            "max_concurrent_hifi":20
        }
        self.trackids = []
        self.trackinfos = {}
        self.trackno=0
        self.setOptions(options)
        
        self.hasChanges=True
        
        self.callbackDownload = callbackDownload
        
        self.downloads={"lowfi":[],"hifi":[]}
        
        self.finishedDownloadsInTheLookahead={"lowfi":[],"hifi":[]}
    
    def setTrackList(self,trackids):
        self.trackids=trackids
        self.hasChanges=True
    
    def setTrackInfos(self,trackinfos):
        self.trackinfos=trackinfos
        self.hasChanges=True
        
    def setOptions(self,options):
        self.options.update(options)
        self.options["lookahead_max"]=max(self.options["lookahead_lowfi"][1],self.options["lookahead_hifi"][1])
        self.hasChanges=True
        
    def setFinishedDownload(self,type,trackid,failure=False):
        self.downloads[type].remove(trackid)
        self.finishedDownloadsInTheLookahead[type].append(trackid)
        self.hasChanges=True
    
    def startDownload(self,type,trackid):
        if not (trackid in self.downloads[type]) and not (trackid in self.finishedDownloadsInTheLookahead[type]):
            self.downloads[type].append(trackid)
            self.callbackDownload(type,trackid)
    
    def setCurrentTrackNo(self,trackno):
        
        """ Reinit the finished downloads list each time. Todo optimize that """
        self.finishedDownloadsInTheLookahead={"lowfi":[],"hifi":[]}
        
        self.trackno = trackno
        self.hasChanges=True
    
    """ Called each time we need to refresh the manage info """
    def manage(self):
        
        """ nothing has changed, there's no need to recompute anything """
        if not self.hasChanges:
            return
        
        nextTracks = self.getSlicedTrackIds(self.trackno)
        

        lookahead = 0    
        lookahead_no = 0
        
        while lookahead <= self.options["lookahead_max"] and lookahead_no<len(nextTracks):

            """ lookahead starts at the beginning of the next track """
            lookahead_afterfirst = lookahead - float(self.trackinfos[str(nextTracks[0])]["lengths"])/60
            
            trackid = nextTracks[lookahead_no]
            
            types = ["lowfi","hifi"]
            
            for type in types:
           
               
                if (max(0,lookahead_afterfirst)>=self.options["lookahead_"+type][0] and lookahead_afterfirst<=self.options["lookahead_"+type][1]):
                    
                    if len(self.downloads[type])<self.options["max_concurrent_"+type]:
                        self.startDownload(type,trackid)
                
                
            lookahead_no += 1
            lookahead += float(self.trackinfos[str(trackid)]["lengths"])/60

            """
                    
                    #do we have to remove a download to make space?
                    if len(self.downloads_lowfi.keys())>=self.manage_options["max_concurrent_lowfi"]:
                        
                        prioritizedList = self.downloads_lowfi.keys()
                        prioritizedList.sort(self.cmpTrackCountdown,reverse=True)
                        currentCountdown = self.getTrackCountdown(t)
                        self.feedback.put(["debug","playlist","too much lowfi "+str(prioritizedList)])
                        
                        #if the lowest priority is lower than current track, replace it
                        if self.getTrackCountdown(prioritizedList[0])>currentCountdown:
                            self.feedback.put(["debug","playlist","delete lowfi "+str(prioritizedList[0])])
                            self.downloads_lowfi[str(prioritizedList[0])].stop()
                            del self.downloads_lowfi[str(prioritizedList[0])]
                        else:
                            downloadme=False
                
      """  
       
       
       
   
    
    def getSlicedTrackIds(self,from_index):
        return self.trackids[from_index:]+self.trackids[0:from_index]
    
    #
    # In how many tracks will trackid be played ?
    # we must loop through the entire array, as the
    # track may be more than once in the playlist
    #
    def getTrackCountdown(self,trackid):
    
        trackid=int(trackid)
        
        i=0
        tids=self.getSlicedTrackIds(self.currentTrackIndex)
        for t in tids:
            if t==trackid:
                return i
            i+=1
        
        return 999999


    def cmpTrackCountdown(self,x,y):
        return cmp(self.getTrackCountdown(x), self.getTrackCountdown(y))
            