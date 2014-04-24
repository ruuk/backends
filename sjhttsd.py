# -*- coding: utf-8 -*-
import audio
import base
import urllib, urllib2
from lib import util
import shutil

class SJHttsdTTSBackend(base.SimpleTTSBackendBase):
	provider = 'ttsd'
	displayName = 'HTTP TTS Server (Requires Running Server)'
	interval = 100
	settings = {	'engine':	None,
					'voice':	None,
					'speed':	0,
					'host':		'127.0.0.1',
					'port':		8256,
					'player':	None
	}

	def __init__(self):
		preferred = self.setting('player') or None
		player = audio.WavPlayer(audio.UnixExternalPlayerHandler,preferred=preferred)
		base.SimpleTTSBackendBase.__init__(self,player)
		self.engine = self.setting('engine')
		self.voice = self.setting('voice')
		self.speed = self.setting('speed')
		self.setHTTPURL()
		self.process = None
		self.failFlag = False

	def setHTTPURL(self):
		host = self.setting('host')
		port = self.setting('port')
		if host and port:
			self.httphost = 'http://{0}:{1}/'.format(host,port)
		else:
			self.httphost = 'http://127.0.0.1:8256/'
		
	def runCommand(self,text,outFile):
		postdata = {'text': text.encode('utf-8')} #TODO: This fixes encoding errors for non ascii characters, but I'm not sure if it will work properly for other languages
		if self.engine: postdata['engine'] = self.engine
		if self.voice: postdata['voice'] = self.voice
		if self.speed: postdata['rate'] = self.speed
		req = urllib2.Request(self.httphost + 'speak.wav', urllib.urlencode(postdata))
		with open(outFile, "w") as wav:
			try:
				shutil.copyfileobj(urllib2.urlopen(req),wav)
				self.failFlag = False
			except:
				util.ERROR('SJHttsdTTSBackend: wav.write',hide_tb=True)
				if self.failFlag: self.dead = True #This is the second fail in a row, mark dead
				self.failFlag = True
				return False
		return True

	def update(self):
		self.engine = self.setting('engine')
		self.voice = self.setting('voice')
		self.speed = self.setting('speed')
		self.setPlayer(self.setting('player'))
		self.setHTTPURL()

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	def voices(self):
		return urllib2.urlopen(self.httphost + 'voices',data='').read().splitlines()
		
	def settingList(self,setting):
		if setting == 'engine':
			return urllib2.urlopen(self.httphost + 'engines/wav',data='').read().splitlines()
	
	@staticmethod
	def available():
		return True

