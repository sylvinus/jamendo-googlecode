#!/usr/bin/env python

#
# jamcorder 0.4
#
# http://www.jamendo.com/?s=jamendotools_jamcorder
#
# Authors :
#  * Sylvain ZIMMER <sylvain _at_ sylvainzimmer.com>
#
# Licensed under the GNU GPLv2 (see LICENSE)
#






from wxPython.wx import *
from wxPython.xrc import *
from threading import *
import commands,os,time,string,platform
import id3
import wave
import ConfigParser
from optparse import OptionParser

if platform.system()=="Windows":
	import pymedia.audio.sound as sound
	

INVALID_CHARS = unicode ('*/\?<>:|"')

class jamcorder(wxApp):
	def OnInit(self):
		listCfgFiles = [os.path.expanduser('~/.jamcorder.cfg')];
		usage = "usage: %prog [options] arg"
		cmdLineOptions = OptionParser(usage);
		cmdLineOptions.add_option("-c", "--config-file",
				dest="configFilename", \
				help="Use the configuration defined in FILE", metavar="FILE");
		cmdLineOptions.add_option("-p", "--playlist",
				dest="playlistFilename", \
				help="Use the track names defined in FILE", metavar="FILE");
		(options, args) = cmdLineOptions.parse_args()
		print options.configFilename
		if options.configFilename<>None :
			listCfgFiles = listCfgFiles + [options.configFilename];

		self.trackList = []
		if options.playlistFilename<>None :
			f = open(options.playlistFilename)
			try :
				for line in f :
					self.trackList = self.trackList + [line.strip("\n")]
			finally :
				f.close
			
		self.res = wxXmlResource("wx.xrc")
		self.frame = self.res.LoadFrame(None, "MainFrame")
		self.jamcorder=self; #dummy test
		self.InitEvents();
		self.InitBindings();
		
		if len(self.trackList) > 0 :
			self.bd_live_trackname.SetValue(self.trackList[0])

        #default filename template
		self.bd_settings_fntemplate.SetValue(os.path.join("%f","%N - %t.%f"));

		#default incoming dir
		self.bd_settings_inc.SetValue("output");
       
		#configDefaults = \
		#{ \
				#"ArtistName" : self.bd_live_artistname.GetValue(), \
				#"AlbumName" : self.bd_live_albumname.GetValue(), \
				#"LicenceURL" : self.bd_live_licenseurl.GetValue(), \
				#"Comment" : self.bd_live_comment.GetValue() \
		#};
		#cf = ConfigParser.RawConfigParser(configDefaults);
		cf = ConfigParser.RawConfigParser();
		if len(listCfgFiles) > 1 :
			listFiles = cf.read(listCfgFiles);
		else :
			listFiles = cf.read(listCfgFiles[0]);

		if len(listFiles)>0 :
			print "Config file found";
			#entryList = cf.options("Live");
			#print entryList;
			# Live options
			if cf.has_option("Live", "ArtistName") :
				print "ArtistName = " + cf.get("Live", "ArtistName");
				self.bd_live_artistname.SetValue(cf.get("Live", "ArtistName"));
			if cf.has_option("Live", "AlbumName") :
				print "AlbumName = " + cf.get("Live", "AlbumName");
				self.bd_live_albumname.SetValue(cf.get("Live", "AlbumName"));
			if cf.has_option("Live", "LicenceURL") :
				print "LicenceURL = " + cf.get("Live", "LicenceURL");
				self.bd_live_licenseurl.SetValue(cf.get("Live", "LicenceURL"));
			# Settings options
			if cf.has_option("Settings", "OutputDir") :
				print "OutputDir = " + cf.get("Settings", "OutputDir");
				self.bd_settings_inc.SetValue(cf.get("Settings", "OutputDir"));
			if cf.has_option("Settings", "AudioInput") :
				audioInputOpt = cf.get("Settings", "AudioInput");
				print "AudioInput = " + audioInputOpt;
				if audioInputOpt == "pyMedia" :
					self.bd_settings_audioinput.SetSelection(0);
				elif audioInputOpt == "arecord" :
					self.bd_settings_audioinput.SetSelection(1);
				else :
					self.bd_settings_audioinput.SetSelection(0);
			if cf.has_option("Settings", "FileNameTemplate") :
				print "FileNameTemplate = " + cf.get("Settings", "FileNameTemplate");
				self.bd_settings_fntemplate.SetValue(cf.get("Settings", "FileNameTemplate")); 
			if cf.has_option("Settings", "MP3Encoding") :
				print "MP3Encoding = " + cf.get("Settings", "MP3Encoding");
				self.bd_settings_enc_mp3.SetValue(cf.getboolean("Settings", "MP3Encoding")); 
			if cf.has_option("Settings", "MP3CommandParameters") :
				print "MP3CommandParameters = " + cf.get("Settings", "MP3CommandParameters");
				self.bd_settings_enc_mp3_cmd.SetValue(cf.get("Settings", "MP3CommandParameters")); 
			if cf.has_option("Settings", "FlacEncoding") :
				print "FlacEncoding = " + cf.get("Settings", "FlacEncoding");
				self.bd_settings_enc_flac.SetValue(cf.getboolean("Settings", "FlacEncoding")); 
			if cf.has_option("Settings", "FlacCommandParameters") :
				print "FlacCommandParameters = " + cf.get("Settings", "FlacCommandParameters");
				self.bd_settings_enc_flac_cmd.SetValue(cf.get("Settings", "FlacCommandParameters")); 
			if cf.has_option("Settings", "OggEncoding") :
				print "OggEncoding = " + cf.get("Settings", "OggEncoding");
				self.bd_settings_enc_ogg.SetValue(cf.getboolean("Settings", "OggEncoding")); 
			if cf.has_option("Settings", "OggCommandParameters") :
				print "OggCommandParameters = " + cf.get("Settings", "OggCommandParameters");
				self.bd_settings_enc_ogg_cmd.SetValue(cf.get("Settings", "OggCommandParameters")); 
		
		wxInitAllImageHandlers()
		Img = wxBitmap(os.path.join("resources","upper.jpg"), wxBITMAP_TYPE_JPEG)
		self.bd_global_upperbitmap.SetBitmap(Img)

		self.frame.CreateStatusBar()

		self.time_totalTracks=0
		self.time_finishedTracks=0
		self.time_currentTrackStart=0
		self.time_currentTrack=0
		
		self.size_mp3=0
	
		self.taskcount=0
		self.exiting=false

		self.sv_live_trackno=0
		self.sv_settings_inc=self.bd_settings_inc
		
		self.frame.Show(1);
		self.addStatus("jamcorder started ! Have fun.");

		self.updateTime()
		
		self.wavinputstop=[]
		self.recordingthreads=[]
		for i in range(1000): #todo dummy
			self.wavinputstop+=[0]
			self.recordingthreads+=[0]

		return true;

	def InitBindings(self):            
		self.bd_live_trackno=XRCCTRL(self.frame, "LIVE_TRACKNO")
		self.bd_live_status=XRCCTRL(self.frame, "LIVE_STATUS")
		self.bd_live_artistname=XRCCTRL(self.frame, "LIVE_ARTISTNAME")
		self.bd_live_trackname=XRCCTRL(self.frame, "LIVE_TRACKNAME")
		self.bd_live_albumname=XRCCTRL(self.frame, "LIVE_ALBUMNAME")
		self.bd_live_licenseurl=XRCCTRL(self.frame, "LIVE_LICENSEURL")
		self.bd_live_comment=XRCCTRL(self.frame, "LIVE_COMMENT")
		self.bd_live_next=XRCCTRL(self.frame, "LIVE_NEXT")
		self.bd_live_start=XRCCTRL(self.frame, "LIVE_START")
		self.bd_live_stop=XRCCTRL(self.frame, "LIVE_STOP")
		
		
		self.bd_global_upperbitmap=XRCCTRL(self.frame, "GLOBAL_UPPERBITMAP")

		self.bd_settings_inc=XRCCTRL(self.frame, "SETTINGS_INC")
		self.bd_settings_audioinput=XRCCTRL(self.frame, "SETTINGS_AUDIOINPUT")
		self.bd_settings_fntemplate=XRCCTRL(self.frame, "SETTINGS_FNTEMPLATE")
		
		self.bd_settings_fntemplate=XRCCTRL(self.frame, "SETTINGS_FNTEMPLATE")
		#self.bd_settings_enc_wav=XRCCTRL(self.frame, "SETTINGS_ENC_WAV")
		self.bd_settings_enc_mp3=XRCCTRL(self.frame, "SETTINGS_ENC_MP3")
		self.bd_settings_enc_mp3_cmd=XRCCTRL(self.frame, "SETTINGS_ENC_MP3_CMD")
		self.bd_settings_enc_ogg=XRCCTRL(self.frame, "SETTINGS_ENC_OGG")
		self.bd_settings_enc_ogg_cmd=XRCCTRL(self.frame, "SETTINGS_ENC_OGG_CMD")
		self.bd_settings_enc_flac=XRCCTRL(self.frame, "SETTINGS_ENC_FLAC")
		self.bd_settings_enc_flac_cmd=XRCCTRL(self.frame, "SETTINGS_ENC_FLAC_CMD")

	def InitEvents(self):
		EVT_BUTTON(self, XRCID("LIVE_NEXT"), self.EventLiveNext)
		EVT_BUTTON(self, XRCID("LIVE_START"), self.EventLiveStart)
		EVT_BUTTON(self, XRCID("LIVE_STOP"), self.EventLiveStop)
		
		EVT_BUTTON(self, XRCID("SETTINGS_INCBROWSE"), self.EventSettingsIncBrowse)

		EVT_RESULT(self,self.catchResultEvent)


	def EventLiveStart(self,evt):
		self.StartRecording()
		
	
	def EventLiveStop(self,evt):
		self.StopRecording()

	def EventLiveNext(self,evt):
		self.addStatus("Next track...");
		self.StopRecording()
		self.bd_live_trackno.SetValue(self.bd_live_trackno.GetValue() + 1)
		trackName = ""
		if self.bd_live_trackno.GetValue() <= len(self.trackList) :
			trackName = self.trackList[self.bd_live_trackno.GetValue()-1]
		if trackName=="" :
			self.bd_live_trackname.SetValue("--enter the name of the next track !--")
		else :
			self.bd_live_trackname.SetValue(trackName)

		self.StartRecording()

		
	def EventSettingsIncBrowse(self,evt):
		dlg=wxDirDialog(self.frame,"Choose a directory for the audio files","",wxDD_NEW_DIR_BUTTON);
		path=""
		if dlg.ShowModal() == wxID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		self.bd_settings_inc.SetValue(path)
		

	def OnExit(self):


                #remove wav files ?
                if self.sv_live_trackno>0:
                    for i in (range(self.sv_live_trackno)):
    			os.unlink(os.path.join(self.sv_settings_inc,'wav',str(i+1)+".wav"))
		
                self.exiting=true
                
                #wait for the timers to end
                time.sleep(0.4)
                
                self.ExitMainLoop()


	def StartRecording(self):

                #remember values
                self.sv_settings_inc=self.bd_settings_inc.GetValue()
                self.sv_live_trackno=int(self.bd_live_trackno.GetValue())
                
		self.wavinputstop[self.bd_live_trackno.GetValue()]=0;
		self.bd_live_start.Disable()
		self.bd_live_stop.Enable(1)
		self.bd_live_next.Enable(1)
	
		#launch the recording thread
		self.recordingthreads[self.bd_live_trackno.GetValue()]=jamcorder_Recorder(self,self.bd_live_trackno.GetValue(),self.bd_live_trackname.GetValue(),self.bd_settings_inc.GetValue(),self.bd_settings_audioinput.GetSelection())
		
		self.time_currentTrackStart=time.time();


	def StopRecording(self):
		self.wavinputstop[self.bd_live_trackno.GetValue()]=1;
		self.bd_live_start.Enable(1)
		self.bd_live_stop.Disable()
		self.bd_live_next.Disable()

		#wait for the recording thread to finish
		self.recordingthreads[self.bd_live_trackno.GetValue()].abort()
		self.recordingthreads[self.bd_live_trackno.GetValue()].join(1)

		#add track time to finished tracks time
		self.time_finishedTracks+=self.time_currentTrack
		
		#end the timer
		self.time_currentTrackStart=0
		self.time_currentTrack=0

		
		#start encoding right after the recording is finished.
		#todo : overlapping encoders ?
		self.StartEncoding(self.bd_live_trackno.GetValue(),self.bd_live_trackname.GetValue())




	def StartEncoding(self,trackno,trackname):
	
		if self.bd_settings_enc_mp3.IsChecked():
			jamcorder_Encoder(self,trackno,trackname,"mp3",self.bd_settings_enc_mp3_cmd.GetValue())
		if self.bd_settings_enc_ogg.IsChecked():
			jamcorder_Encoder(self,trackno,trackname,"ogg",self.bd_settings_enc_ogg_cmd.GetValue())
		if self.bd_settings_enc_flac.IsChecked():
			jamcorder_Encoder(self,trackno,trackname,"flac",self.bd_settings_enc_flac_cmd.GetValue())
#		if self.bd_settings_enc_wav.IsChecked():
#			ccLiveEncoder(self,trackno,trackname,"wav",false)


	#add text to the status textarea
	def addStatus(self,text):
		self.bd_live_status.SetValue(text + "\n" + self.bd_live_status.GetValue())
		self.frame.Refresh()
		self.frame.Update()
		print self.bd_settings_enc_flac.GetValue()


	def updateTime(self):

		#relaunch timer
                if not self.jamcorder.exiting:
        		t=Timer(0.2,self.jamcorder.updateTime)
        		t.start()

		#if we're recording
		if self.jamcorder.time_currentTrackStart>0:
			
			# duration of the current track
			self.jamcorder.time_currentTrack=int(time.time()-self.jamcorder.time_currentTrackStart)
			
			# total duration of the live
			self.jamcorder.time_totalTracks=self.jamcorder.time_finishedTracks+self.jamcorder.time_currentTrack

			
			
			
		# update the GUI
		wxPostEvent(self.jamcorder,ResultEvent("statusbar",""))


	
	def addNewFile(self,trackno,filesize):
		
		self.size_mp3+=filesize
		
		wxPostEvent(self.jamcorder,ResultEvent("statusbar",""))
		
		



	def updateStatusBar(self):
		
		self.frame.SetStatusText("Current track time : "+str(self.time_currentTrack)+"s        Total time : "+str(self.time_totalTracks)+"s         MP3 size : "+str(int(self.size_mp3/(1024*1024)))+" Mo          Active tasks : "+str(self.taskcount));
		
		self.frame.Refresh()
		self.frame.Update()
		
					 


	def catchResultEvent(self,evt):
		if evt.type=="status":
			self.addStatus(evt.data)
		elif evt.type=="statusbar":
			self.updateStatusBar()
		elif evt.type=="newfile":
			self.addNewFile(evt.data[0],evt.data[1])
		elif evt.type=="taskstart":
			self.taskcount+=1
		elif evt.type=="taskend":
			self.taskcount-=1
		



# inter-thread communication
# from http://wiki.wxpython.org/index.cgi/LongRunningTasks

EVT_RESULT_ID = wxNewId()

def EVT_RESULT(win, func):
	win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wxPyEvent):
	def __init__(self, type, data):
		wxPyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.type = type
		self.data = data	







#Thread that writes .wav files
class jamcorder_Recorder(Thread):
	def __init__(self,jamcorder,trackno,trackname,inc,audioinput):
		Thread.__init__(self)
		self.must_abort=0

		self.jamcorder=jamcorder
		self.trackno=trackno
		self.trackname=trackname
		self.inc=inc
		self.audioinput=audioinput
		
		self.start()	


	def run(self):

		wxPostEvent(self.jamcorder,ResultEvent("status","Input thread started"))	
		wxPostEvent(self.jamcorder,ResultEvent("taskstart",""))	
	
		#wav file to be written (CD quality)
		
                try:
		    os.makedirs(os.path.join(self.inc,'wav'), mode=0777);
		except OSError:
		    a=1 #do nothing ?
	
		wavfilepath=os.path.join(self.inc,'wav',str(self.trackno)+".wav");
		wavfile=wave.open(wavfilepath.encode("latin1"),"wb");
		wavfile.setparams( (2,2,44100,0,'NONE','') )

		#pymedia input
		if self.audioinput==0:
			
			#88khz fix for sylvinus' laptop ? how to automatically deal with it ?
			sndinput= sound.Input( 44100, 2, sound.AFMT_S16_LE )
			sndinput.start()
			 
			#recording loop
			while self.must_abort==0:
				buf=sndinput.getData()
				if buf and len(buf):
					wavfile.writeframes(buf)
				else:
					time.sleep(0.003)
				
			sndinput.stop()
			
		
		#arecord input
		elif self.audioinput==1:
			
			sndinput=os.popen("arecord -f cd","r");
			
			#recording loop
			while self.must_abort==0:
				buf=sndinput.read(1000)
				wavfile.writeframes(buf)
				
			sndinput.close();
			
			
		wavfile.close();
	
				
		wxPostEvent(self.jamcorder,ResultEvent("taskend",""))	
		wxPostEvent(self.jamcorder,ResultEvent("status","Input thread ended"))	

	def abort(self):
		self.must_abort=1






#Thread that encodes audio files.
class jamcorder_Encoder(Thread):
	
	def __init__(self,jamcorder,trackno,trackname,outformat,cmdargs):
		Thread.__init__(self)

		self.jamcorder=jamcorder
		self.trackno=trackno
		self.trackname=trackname
		self.outformat=outformat
		self.cmdargs=cmdargs

		self.start();
	
	def run(self):
		
		wxPostEvent(self.jamcorder,ResultEvent("taskstart",""))	
		
		#quite dirty (thread shouldn't access GUI), but it's readonly.
		filename=self.jamcorder.bd_settings_fntemplate.GetValue()
		incdir=self.jamcorder.bd_settings_inc.GetValue()
	
		artistname=self.jamcorder.bd_live_artistname.GetValue()
		albumname=self.jamcorder.bd_live_albumname.GetValue()
		licenseurl=self.jamcorder.bd_live_licenseurl.GetValue()
		comment=self.jamcorder.bd_live_comment.GetValue()

                #parse the file name template
		filename=filename.replace("%f",self.outformat)
		if (self.trackno<10):
			filename=filename.replace("%N",str(0)+str(self.trackno))
		else:
			filename=filename.replace("%N",str(self.trackno))
		filename=filename.replace("%p",createValidFilename(artistname))
		filename=filename.replace("%t",createValidFilename(self.trackname))
		filename=filename.replace("%a",createValidFilename(albumname))

                #warning ultra dummy
		#create the dir when filename template contains a dir
		print filename.rfind("/")
		if filename.rfind("/")>-1:
			dirname=filename[0:filename.rfind("/")]+"/"
		elif filename.rfind('\\')>-1: 
			dirname=filename[0:filename.rfind('\\')]+'\\'
		else:
			dirname=""
		
		try:
			os.makedirs(os.path.join(incdir,dirname))
		except OSError:
			a=1 #do nothing ?
	
		wxPostEvent(self.jamcorder,ResultEvent("status",filename+" being encoded."))	
	
				
		if platform.system()=="Windows":
             		FLAC_PATH=os.path.join('.', 'bin', 'flac')
             		LAME_PATH=os.path.join('.', 'bin', 'lame')
             		OGG_PATH=os.path.join('.', 'bin', 'oggenc')
                elif platform.system()=="Linux":
			FLAC_PATH=os.path.join('/','usr','bin','flac')
			LAME_PATH=os.path.join('/','usr','bin','lame')
             		OGG_PATH=os.path.join('/' ,'usr','bin','oggenc')
					     
                wavfile=os.path.join(incdir,'wav',str(self.trackno)+".wav");
                encfile=os.path.join(incdir,filename);
	
		if self.outformat=="mp3":
			
			os.system(LAME_PATH+" "+self.cmdargs+" \""+wavfile+"\" \""+encfile+"\"")

                        #tag the MP3
			id3v2=id3.ID3v2(encfile);
#			id3v2.version=(2,4,0,)
			
                        id3_tpe1=id3v2.new_frame("TPE1");
                        id3_tpe1.set_value(artistname);
                        
                        id3_talb=id3v2.new_frame("TALB");
                        id3_talb.set_value(albumname);
                        
                        id3_trck=id3v2.new_frame("TRCK");
                        id3_trck.set_value(str(self.trackno));
                        
                        id3_tit2=id3v2.new_frame("TIT2");
                        id3_tit2.set_value(self.trackname);
                        
                        id3_tcop=id3v2.new_frame("TCOP");
                        id3_tcop.set_value("2005 "+artistname+". Licensed to the public under "+licenseurl); #todo verify at + year
                        
                        id3_tenc=id3v2.new_frame("TENC");
                        id3_tenc.set_value("jamcorder");
                        
                        id3v2.save()	

		elif self.outformat=="ogg":
			os.system(OGG_PATH+" "+self.cmdargs+" \""+wavfile+"\" -o \""+encfile+"\"")
			
		elif self.outformat=="flac":
			os.system(FLAC_PATH+" "+self.cmdargs+" -o \""+encfile+"\" \""+wavfile+"\"")
		
#		elif self.outformat=="wav":
#			os.rename(encfile,wavfile)
		

	
		wxPostEvent(self.jamcorder,ResultEvent("status",filename+" encoded."))
			
		
		#get size of the file if MP3.
		if self.outformat=="mp3":
			encodedfile=os.stat(encfile);
			wxPostEvent(self.jamcorder,ResultEvent("newfile",[self.trackno, encodedfile.st_size]))	
	
	
		wxPostEvent(self.jamcorder,ResultEvent("taskend",""))	
	
# from http://svn.weird-birds.org/wbc/mac2winvalidutf8/mac2winvalidutf8.py
# used to clean filenames

def createValidFilename (brokenFilename, fixedFilename = ""):
	"""
	replaces invalid characters for windows with '_'
	strips whitespace from beg./end of names
	strips dots from beg./end of names
	runs at least twice per name to check if output of 'createValidFilename' is really a valid name
	it recursively continues until filename has a length of 0 or stays the same after validation.
	example filename why recursion is necessary: '...  file.extension  ...'
	    when the dots are stripped invalid spaces are left
	"""
	brokenFilename = string.strip (brokenFilename) # remove whitespace from start and end of filename
	brokenFilename = brokenFilename.replace(u"\xe9","e")
	brokenFilename = brokenFilename.replace(u"\xe8","e")
	brokenFilename = brokenFilename.replace(u"\xe0","a")
	brokenFilename = brokenFilename.replace(u"\xf9","u")
	brokenFilename = brokenFilename.replace(u"\xe2","a")
	brokenFilename = brokenFilename.replace(u"\xea","e") #todo add more..
	brokenFilename = brokenFilename.encode("ascii","replace")
	

	retval = unicode("")
	for character in brokenFilename[:]:
		if character in INVALID_CHARS:
			retval += unicode ("_")
		else:
			retval += character
	retval = stripChar (unicode('.'), retval)
	if len(retval) == 0:
		return unicode("")
	if retval == fixedFilename:
		return retval
	else:
		return createValidFilename (retval, retval) # run recursively because invalid filenames like ' ... ... ... .... ..' result in yet again invalid names, and again, and again....

def stripChar (c, s):
	while len(s) > 0 and s[0] == c:
		s = s[1:]
	while len(s) > 0 and s[-1] == c:
		s = s[:-1]
	return s









		
def main():
	app = jamcorder()
	app.MainLoop()

main()
