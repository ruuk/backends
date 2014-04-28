# -*- coding: utf-8 -*-

import urllib, urllib2, shutil
import base, audio
from lib import util

class GoogleTTSBackend(base.SimpleTTSBackendBase):
	provider = 'Google'
	displayName = 'Google'
	ttsURL = 'http://translate.google.com/translate_tts?tl=en&q={0}'
	interval = 100
	
	def __init__(self):
		player = audio.WavPlayer(audio.UnixExternalPlayerHandler,preferred='mplayer')
		base.SimpleTTSBackendBase.__init__(self,player,mode=base.SimpleTTSBackendBase.WAVOUT)

	def runCommand(self,text,outFile):
		req = urllib2.Request(self.ttsURL.format(urllib.quote(text)), headers={ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36' })
		try:
			resp = urllib2.urlopen(req)
		except:
			util.ERROR('Failed to open Google TTS URL',hide_tb=True)
			
		with open(outFile,'wb') as out:
			shutil.copyfileobj(resp,out)
		return True

	def stop(self):
		pass
			
	@staticmethod
	def available():
		return True
