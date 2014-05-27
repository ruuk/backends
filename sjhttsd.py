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
	canStreamWav = False
	
	settings = {	'engine':	None,
					'voice':	None,
					'voice.Flite':	None,
					'voice.eSpeak':	None,
					'voice.SAPI':	None,
					'voice.Cepstral':	None,
					'speed':	0,
					'remote_volume': 0,
					'player_volume': 0,
					'host':		'127.0.0.1',
					'port':		8256,
					'player':	None,
					'perl_server': True,
					'speak_on_server': False
	}

	def __init__(self):
		player = audio.WavAudioPlayerHandler(preferred=self.setting('player'))
		base.SimpleTTSBackendBase.__init__(self,player,mode=self.getMode())
		self.baseUpdate()
		self.process = None
		self.failFlag = False

	def setHTTPURL(self):
		host = self.setting('host')
		port = self.setting('port')
		if host and port:
			self.httphost = 'http://{0}:{1}/'.format(host,port)
		else:
			self.httphost = 'http://127.0.0.1:8256/'
		
	def updatePostdata(self,postdata):
		if self.engine: postdata['engine'] = self.engine
		if self.voice: postdata['voice'] = self.voice
		if self.speed: postdata['rate'] = self.speed
		if self.remote_volume: postdata['volume'] = self.remote_volume
		
	def runCommand(self,text,outFile):
		postdata = {'text': text.encode('utf-8')} #TODO: This fixes encoding errors for non ascii characters, but I'm not sure if it will work properly for other languages
		if self.perlServer:
			postdata['voice'] = self.voice
			postdata['rate'] = self.speed
			req = urllib2.Request(self.httphost + 'speak.wav', urllib.urlencode(postdata))
		else:
			self.updatePostdata(postdata)
			req = urllib2.Request(self.httphost + 'wav', urllib.urlencode(postdata))
		with open(outFile, "w") as wav:
			try:
				res = urllib2.urlopen(req)
				if not res.info().get('Content-Type') == 'audio/x-wav': return False #If not a wav we will crash XBMC
				shutil.copyfileobj(res,wav)
				self.failFlag = False
			except:
				util.ERROR('SJHttsdTTSBackend: wav.write',hide_tb=True)
				if self.failFlag: self.dead = True #This is the second fail in a row, mark dead
				self.failFlag = True
				return False
		return True

	def runCommandAndSpeak(self,text):
		postdata = {'text': text.encode('utf-8')} #TODO: This fixes encoding errors for non ascii characters, but I'm not sure if it will work properly for other languages
		self.updatePostdata(postdata)
		req = urllib2.Request(self.httphost + 'say', urllib.urlencode(postdata))
		try:
			urllib2.urlopen(req)
			self.failFlag = False
		except:
			util.ERROR('SJHttsdTTSBackend: say',hide_tb=True)
			if self.failFlag: self.dead = True #This is the second fail in a row, mark dead
			self.failFlag = True
			return False
	
	def getMode(self):
		if self.setting('speak_on_server'):
			self.serverMode = True
			return base.SimpleTTSBackendBase.ENGINESPEAK
		else:
			self.serverMode = False
			return base.SimpleTTSBackendBase.WAVOUT
			
	def baseUpdate(self):
		self.setHTTPURL()
		self.perlServer = self.setting('perl_server') #Not really currently used
		version = self.getVersion()
		if version.startswith('speech.server'):
			if self.perlServer:
				util.LOG('Perl server not detected. Switch to speech.server mode.')
				self.perlServer = False
		else:
			if not self.perlServer:
				util.LOG('speech.server not detected. Switch to Perl server mode.')
				self.perlServer = True
				
		if self.perlServer:
			self.voice = self.setting('voice')
		else:
			self.engine = self.setting('engine')
			voice = self.setting('voice.{0}'.format(self.engine))
			if voice: voice = '{0}.{1}'.format(self.engine,voice)
			self.voice = voice
		self.speed = self.setting('speed')
		self.setSpeed(self.speed)
		self.remote_volume = self.setting('remote_volume')
		self.setVolume(self.setting('player_volume'))
		
	def getVersion(self):
		req = urllib2.Request(self.httphost + 'version')
		try:
			resp = urllib2.urlopen(req)
			return resp.read()
		except:
			return ''

	def update(self):
		self.baseUpdate()
		
		self.setPlayer(self.setting('player'))
		self.setMode(self.getMode())
		
	def serverStop(self):
		req = urllib2.Request(self.httphost + 'stop', '')
		try:
			urllib2.urlopen(req)
		except:
			util.ERROR('SJHttsdTTSBackend: stop',hide_tb=True)

	def stop(self):
		if self.serverMode: self.serverStop()
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	def voices(self,engine=''):
		if engine: engine = '?engine={0}'.format(engine)
		try:
			return urllib2.urlopen(self.httphost + 'voices{0}'.format(engine)).read().splitlines()
		except urllib2.HTTPError:
			return None
		except:
			util.ERROR('SJHttsdTTSBackend: voices',hide_tb=True)
			self.failFlag = True
			return None

	@classmethod
	def settingList(cls,setting,*args):
		self = cls()
		if setting == 'engine':
			try:
				engines = urllib2.urlopen(self.httphost + 'engines/wav',data='').read().splitlines()
			except urllib2.HTTPError:
				return None
			except:
				util.ERROR('SJHttsdTTSBackend: engines',hide_tb=True)
				self.failFlag = True
				return None
				
			ret = []
			for e in engines:
				ret.append(e.split('.',1))
			return ret
		elif setting.startswith('voice.'):
			ret = []
			voices = self.voices(args[0])
			if not voices: return None
			for v in voices:
				v = v.split('.')[-1]
				ret.append((v,v))
			return ret
		return None
	
	@staticmethod
	def available():
		return True

