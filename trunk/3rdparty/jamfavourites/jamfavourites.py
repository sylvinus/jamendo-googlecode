#!/usr/bin/env python

import os,platform,sys,md5,webbrowser,time,re,socket,md5,shutil,xmlrpclib,Queue
try:
    from wx import App,Icon,BITMAP_TYPE_ICO,EventLoop,Yield,EVT_BUTTON,EVT_CLOSE,ID_OK,DirDialog,InitAllImageHandlers
    from wx.xrc import XmlResource,XRCCTRL,XRCID
except Exception,e:
    print "You need wxPython to run jamfavourites (%s)" % (e,)
    sys.exit(1)
    

if (not os.path.isfile("gui.xrc")):
    os.chdir(os.path.dirname(__name__ == '__main__' and sys.argv[0] or __file__))

  
# add pyjamendolib to path (mostly for dev)
sys.path.insert(0, os.path.join('..', 'pyjamlib'))

try:
    import jamendo.behaviours.DownloadAlbumList  
    from jamendo.lib.Storage import Storage
    from jamendo.lib.JamendoMusicApi import JamendoMusicApiQuery
except Exception,e:
    print "You need pyjamlib to run jamfavourites! : "+str(e)
    sys.exit(1)

class JamFavourites(App):


    ####
    #
    # Main Init function
    #
    def OnInit(self):
   
        self.res = XmlResource("gui.xrc")
        self.frame = self.res.LoadFrame(None, "JAMFAVOURITES")

        InitAllImageHandlers()

        try:
            self.frame.SetIcon(Icon(os.path.join("resources","j.ico"), BITMAP_TYPE_ICO));
        except:
            pass
            
        self.InitEvents();
        self.InitBindings();


        self.keepGoing=True
        self.started=False
                
                
        self.commands=Queue.Queue(1000)
        self.feedback=Queue.Queue(1000)
        
        self.storage = Storage(self.feedback,application_name="jamFavourites")
        
        self.bd_favourites_folder.SetValue(self.storage.getMusicDir())
        
        



        self.frame.Show(1)
            
        return True


    def MainLoop(self):

        # Create an event loop and make it active.  If you are
        # only going to temporarily have a nested event loop then
        # you should get a reference to the old one and set it as
        # the active event loop when you are done with this one...
        evtloop = EventLoop()
        old = EventLoop.GetActive()
        EventLoop.SetActive(evtloop)

        # This outer loop determines when to exit the application,
        # for this example we let the main frame reset this flag
        # when it closes.
        while self.keepGoing:
            # At this point in the outer loop you could do
            # whatever you implemented your own MainLoop for.  It
            # should be quick and non-blocking, otherwise your GUI
            # will freeze.  

            self.ProcessNonBlocking()


            # This inner loop will process any GUI events
            # until there are no more waiting.
            while evtloop.Pending():
                evtloop.Dispatch()

            # Send idle events to idle handlers.  You may want to
            # throttle this back a bit somehow so there is not too
            # much CPU time spent in the idle handlers.  For this
            # example, I'll just snooze a little...
            time.sleep(0.10)
            self.ProcessIdle()

        EventLoop.SetActive(old)



    def ProcessNonBlocking(self):

        try:
            f = self.feedback.get_nowait()
  
            if f[0]=="btstats":
                
                """parse the bittorrent stats"""
                allpercent=0
                notfinished=0
                for torrent in f[1]["torrents"].values():
                    percent=int(torrent.get("percent",0))
                    allpercent+=percent
                    if percent<1000:
                        notfinished+=1
                
                allpercent=(float(allpercent)/len(f[1]["torrents"]))/10;
                
                if allpercent<100:
                    self.bd_favourites_status.SetLabel("Downloading %i albums at %sKB/s..." % (notfinished,f[1]["xfer"]["dls"]/1024))
                else:
                    self.bd_favourites_status.SetLabel("Download finished! Please leave me open to seed")
                    
                self.bd_favourites_gauge.SetValue(allpercent)
                
            else:
                self.bd_console.SetValue(str(f)+"\n"+self.bd_console.GetValue())
        except Exception,e:
            pass
        
        
        
    ####
    #
    # Inits the bindings between GUI and python
    #
    def InitBindings(self):
        self.bd_console=XRCCTRL(self.frame, "CONSOLE")

        self.bd_favourites_user=XRCCTRL(self.frame, "FAVOURITES_USER")
        self.bd_favourites_aenc=XRCCTRL(self.frame, "FAVOURITES_AENC")
        self.bd_favourites_status=XRCCTRL(self.frame, "FAVOURITES_STATUS")
        self.bd_favourites_gauge=XRCCTRL(self.frame, "FAVOURITES_GAUGE")
        
        self.bd_favourites_folder=XRCCTRL(self.frame, "FAVOURITES_FOLDER")
        
    ####
    #
    # Inits the events in the GUI
    #
    def InitEvents(self):
       EVT_BUTTON(self, XRCID("FAVOURITES_GO"), self.EventGo)
       EVT_BUTTON(self, XRCID("FAVOURITES_FOLDER_B"), self.EventFolder)
       
       EVT_CLOSE(self.frame, self.OnFrameClose)
        
    def OnFrameClose(self,a):
        self.keepGoing=False
        return True

    def EventFolder(self,a):
        

        dlg=DirDialog(self.frame,"Choose a directory for downloaded albums",self.bd_favourites_folder.GetValue());
        path=""
        if dlg.ShowModal() == ID_OK:
            path = dlg.GetPath()
            self.bd_favourites_folder.SetValue(path)
        dlg.Destroy()

    def EventGo(self,a):
        
        Yield()
        
        if not self.started:
           
            self.bd_favourites_status.SetLabel("Starting, please wait...")
            uid = JamendoMusicApiQuery("user/name/user/id//"+self.bd_favourites_user.GetValue(),{}).get()
            Yield()
            
            if len(uid)==0:
                self.bd_favourites_status.SetLabel("Invalid username!")
            else:
                albums = JamendoMusicApiQuery("album/list/album/id//",{"n":"all","uid":uid[0],"subset":"user_star"}).get()
                Yield()
                
                if len(albums)==0:
                    self.bd_favourites_status.SetLabel("No favourite albums for this user!")
                else:
                    
                    encodings=['mp32','ogg3']
                    
                    
                    
                    torrent_dir = os.path.join(self.storage.getUserDir(),"torrents")
                    
                    try:
                        shutil.rmtree(torrent_dir)
                    except:
                        pass
                    
                    """ todo move in musicdir once finished """
                    options={
                             "audio_encoding":encodings[self.bd_favourites_aenc.Selection],
                             "albumlist":albums,
                             "stats_interval":1,
                             "stats_individual":True,
                             "bt_client":'bittornadocvs',
                             "torrentpool_dir":torrent_dir,
                             "data_dir":self.bd_favourites_folder.GetValue()
                             
                    }
                
                    self.behaviour=jamendo.behaviours.DownloadAlbumList.JamendoBehaviourDownloadAlbumList(self.feedback,options)
                    self.behaviour.start()
                    self.started=True
               
                    
try:
    app = JamFavourites()
    app.MainLoop()
except Exception, e:    
    import traceback
    errorstring = str(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
    print errorstring
    time.sleep(1)
    Yield()
    time.sleep(1)
    Yield()
    time.sleep(1)
    Yield()
    time.sleep(1)
    Yield()
    time.sleep(1)
    Yield()
    time.sleep(1)
    Yield()
    time.sleep(1)