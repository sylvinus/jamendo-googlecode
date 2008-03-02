import zipfile,os,threading
import jamendo.lib.HTTP
import jamendo.lib.JamendoMusicApi
import md5,os,re



def sumfile(fobj):
	'''Returns an md5 hash for an object with read() method.'''
	m = md5.new()
	while True:
		d = fobj.read(8096)
		if not d:
			break
		m.update(d)
	return m.hexdigest()
 
def md5sum(fname):
 	'''Returns an md5 hash for file fname'''
	try:
		f = open(fname, 'rb')
	except:
		return False
	ret = sumfile(f)
	f.close()
	return ret
	

class ArchiveRestricted(jamendo.lib.HTTP.HTTPDownloader, threading.Thread):
	def __init__(self,feedback,albumid,encoding,localdir,doneevent,failureevent,dounzip=True):
		
		threading.Thread.__init__(self)
				
		self.albumid=albumid
		self.encoding=encoding
		self.localdir=localdir
		self.setDaemon(True)
		self.setName('ArchiveRestrictedDownloader')
		self.dounzip=dounzip
		
		remotefile='http://www.jamendo.com/get/album/id/album/archiverestricted/redirect/'+str(self.albumid)+'/?p2pnet=bittorrent&are='+str(self.encoding)
		
		localfile=os.path.join(self.localdir,'archiverestricted-'+str(self.albumid)+'-'+str(self.encoding)+'.tmp')
		
		jamendo.lib.HTTP.HTTPDownloader.__init__(self,feedback,remotefile,localfile,doneevent=doneevent,failureevent=failureevent,retries=1)
		
		
	def unzip(self,filename,destdir):
		f=zipfile.ZipFile(filename,"r")
		files=f.namelist()	   

		if not os.path.isdir(destdir):
			os.makedirs(destdir)
		
		for fn in files:
			self.feedback.put(['debug','unzipping '+str(fn)+' to '+str(destdir)])
			fw=open(os.path.join(destdir,fn),"wb")
			fw.write(f.read(fn))
			fw.close()
		f.close()
   
		
	def success(self):
		
		try:
			archivedata=jamendo.lib.JamendoMusicApi.JamendoMusicApiQuery('album/id/album/data/xmlrpc/'+str(self.albumid)+'/',{'ali':'archives'},method="xmlrpc").get()
			self.feedback.put(['debug','MusicApi returned : '+str(archivedata)])
			
			archivedata=archivedata[0]['archives'][self.encoding]
			
			assert len(archivedata['hash_md5'])==32
		except Exception,e:
			self.feedback.put(['error','MusicApi error : '+str(e)])
			return self.failure()
			
		try:
			assert archivedata['hash_md5']==md5sum(self.local)
		except Exception,e:
			self.feedback.put(['error','Archive '+str(self.albumid)+' was corrupted ('+str(archivedata['hash_md5'])+' vs '+str(md5sum(self.local))+')'])
			return self.failure()
		
		
		archivename=re.sub('\.zip$','',str(archivedata['filename']))
		
		if self.dounzip:	
			self.unzip(self.local,os.path.join(self.localdir,archivename))
	
			self.deleteLocalFile()
		
		jamendo.lib.HTTP.HTTPDownloader.success(self)
		