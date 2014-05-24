# -*- coding: utf-8 -*-
from base import ThreadedTTSBackend
import locale, os
import speechd
from lib import util

def getSpeechDSpeaker(test=False):
	try:
		return speechd.Speaker('XBMC', 'XBMC')
	except:
		try:
			socket_path = os.path.expanduser('~/.speech-dispatcher/speechd.sock')
			so = speechd.Speaker('XBMC', 'XBMC',socket_path=socket_path)
			try:
				so.set_language(locale.getdefaultlocale()[0][:2])
			except (KeyError,IndexError):
				pass
			return so
		except:
			if not test: util.ERROR('Speech-Dispatcher: failed to create Speaker',hide_tb=True)
	return None
	
class SpeechDispatcherTTSBackend(ThreadedTTSBackend):
	"""Supports The speech-dispatcher on linux"""

	provider = 'Speech-Dispatcher'
	displayName = 'Speech Dispatcher'
	interval = 100
	settings = {	'module':None,
					'voice':None,
					'speed':0,
					'pitch':0,
					'volume':100
	}

	def __init__(self):
		self.connect()
		self.threadedInit()

	def connect(self):
		self.speechdObject = getSpeechDSpeaker()
		if not self.speechdObject: return
		self.update()

	def threadedSay(self,text,interrupt=False):
		if not self.speechdObject:
			return
		try:
			self.speechdObject.speak(text)
		except speechd.SSIPCommunicationError:
			self.reconnect()
		except AttributeError: #Happens on shutdown
			pass

	def stop(self):
		try:
			self.speechdObject.cancel()
		except speechd.SSIPCommunicationError:
			self.reconnect()
		except AttributeError: #Happens on shutdown
			pass

	def reconnect(self):
		self.close()
		if self.active:
			util.LOG('Speech-Dispatcher reconnecting...')
			self.connect()
			
	def update(self):
		module = self.setting('module')
		if module: self.speechdObject.set_output_module(module)
		voice = self.setting('voice')
		if voice: self.speechdObject.set_synthesis_voice(voice)
		print self.setting('speed')
		print self.setting('pitch')
		self.speechdObject.set_rate(self.setting('speed'))
		self.speechdObject.set_pitch(self.setting('pitch'))
		self.speechdObject.set_volume( (self.setting('volume') * 2) - 100 ) #Covert from % to (-100 to 100)

	@classmethod
	def settingList(cls,setting,*args):
		so = getSpeechDSpeaker()
		if setting == 'voice':
			module = cls.setting('module')
			if module: so.set_output_module(module)
			voices = so.list_synthesis_voices()
			return [(v[0],v[0]) for v in voices]
		elif setting == 'module':
			return [(m,m) for m in so.list_output_modules()]
			
	def close(self):
		if self.speechdObject: self.speechdObject.close()
		del self.speechdObject
		self.speechdObject = None
		
	@staticmethod
	def available():
		return bool(getSpeechDSpeaker(test=True))

