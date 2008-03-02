import threading,urllib2,time,os,md5


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
	

class HTTPDownloader:
	
	def __init__(self,feedback,remotefile,localfile,abortevent=False,doneevent=False,failureevent=False,checkmd5=False,retries=5):

		self.remote = remotefile
		self.local = localfile
		self.feedback = feedback
		
		self.checkmd5=checkmd5
		
		self.failureevent=failureevent
		self.doneevent=doneevent
		self.abortevent = abortevent
		
		self.retries=retries

	
	""" thread-safe """
	def abort(self):
		if self.abortevent:
			self.abortevent.set()
	
	def get(self):
		
		self.opener = urllib2.build_opener()
		self.opener.feedback=self.feedback
		
		req = urllib2.Request(self.remote);
		
		
		try:

			r = self.opener.open(req)

			l = open(self.local,"wb")
					
			eof=False
			while (not eof) and not (self.abortevent and self.abortevent.isSet()):
				data=r.read(8096)
				if len(data)==0:
					eof = True
				else:
					l.write(data)		
			
					
			r.close()
			l.close()
			
			return (not (self.abortevent and self.abortevent.isSet()) and self.md5check())
			
		except Exception,e:
			
			self.feedback.put(['error','While downloading '+str(self.remote)+' to '+str(self.local)+' : '+str(e)])
			#Try to close the local file
			try:
				l.close()
			except Exception,e2:
				pass
				
			return False
		
	
	# 5 retries ?
	def run(self):
		
		self.feedback.put(['debug','Starting download of '+str(self.remote)+' to '+str(self.local)])
		
		i=0;
		while i<(self.retries+1):
			
			if i>0:
				time.sleep(20)
				
			if self.get():
				self.feedback.put(['debug','Download of '+str(self.remote)+' completed.'])
				self.success()
				return True
			else:
				
				if self.abortevent and self.abortevent.isSet():
					return self.failure()
				
				self.feedback.put(['warning','Download of '+str(self.remote)+' failed. Retrying in 20 seconds...'])
			i+=1
			
		self.failure()

	def md5check(self):
		if self.checkmd5:
			try:
				assert self.checkmd5 == md5sum(self.local)
				return True
			except Exception,e:
				self.feedback.put(['warning','Download of '+str(self.remote)+' was corrupt.'])
				return False
		else:
			return True

	def success(self):
		if self.doneevent:
			self.doneevent.set()
		
	def failure(self):
		if self.doneevent:
			self.doneevent.set()
		if self.failureevent:
			self.failureevent.set()
		self.deleteLocalFile()
		
	def deleteLocalFile(self):

		try:
			os.unlink(self.local)
		except:
			pass
