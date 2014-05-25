# -*- coding: utf-8 -*-

import urllib, urllib2, shutil, os, subprocess
import base, audio
from lib import util
import textwrap

LANGUAGES = [	('af', 'Afrikaans'),
				('sq', 'Albanian'),
				('ca', 'Catalan'),
				('zh', 'Chinese (Mandarin)'),
				('hr', 'Croatian'),
				('cs', 'Czech'),
				('da', 'Danish'),
				('nl', 'Dutch'),
				('en', 'English'),
				('fi', 'Finnish'),
				('fr', 'French'),
				('de', 'German'),
				('el', 'Greek'),
				('ht', 'Haitian Creole'),
				('hu', 'Hungarian'),
				('is', 'Icelandic'),
				('id', 'Indonesian'),
				('it', 'Italian'),
				('lv', 'Latvian'),
				('mk', 'Macedonian'),
				('no', 'Norwegian'),
				('pl', 'Polish'),
				('pt', 'Portuguese'),
				('ro', 'Romanian'),
				('ru', 'Russian'),
				('sr', 'Serbian'),
				('sk', 'Slovak'),
				('sw', 'Swahili'),
				('sv', 'Swedish'),
				('tr', 'Turkish'),
				('vi', 'Vietnamese'),
				('cy', 'Welsh')
]
				
class GoogleTTSBackend(base.SimpleTTSBackendBase):
	provider = 'Google'
	displayName = 'Google'
	ttsURL = 'http://translate.google.com/translate_tts?tl={0}&q={1}'
	canStreamWav = util.commandIsAvailable('mpg123')
	interval = 100
	settings = {	'language':'en',
					'player':None,
					'volume':0
	}
	
	def __init__(self):
		self.process = None
		preferred = self.setting('player') or 'mpg123'
		player = audio.MP3AudioPlayerHandler(preferred=preferred)
		base.SimpleTTSBackendBase.__init__(self,player,mode=base.SimpleTTSBackendBase.WAVOUT)
		self.update()

	def threadedSay(self,text):
		if not text: return
		sections = textwrap.wrap(text,100)
		for text in sections:
			outFile = self.player.getOutFile(text)
			if not self.runCommand(text,outFile): return
			self.player.play()

	def runCommand(self,text,outFile):
		url = self.ttsURL.format(self.language,urllib.quote(text.encode('utf-8')))
		req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36' })
		try:
			resp = urllib2.urlopen(req)
		except:
			util.ERROR('Failed to open Google TTS URL',hide_tb=True)
			return False
			
		with open(outFile,'wb') as out:
			shutil.copyfileobj(resp,out)
		return True

	def getWavStream(self,text):
		wav_path = os.path.join(util.getTmpfs(),'speech.wav')
		mp3_path = os.path.join(util.getTmpfs(),'speech.mp3')
		self.runCommand(text,mp3_path)
		self.process = subprocess.Popen(['mpg123','-w',wav_path,mp3_path],stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		while self.process.poll() == None and self.active: util.sleep(10)	
		os.remove(mp3_path)
		return open(wav_path,'rb')
		
	def update(self):
		self.language = self.setting('language')
		self.setPlayer(self.setting('player'))
		self.setVolume(self.setting('volume'))

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	@classmethod
	def settingList(cls,setting,*args):
		if setting == 'language':
			return LANGUAGES
		return None

	@staticmethod
	def available():
		return audio.MP3AudioPlayerHandler.canPlay()
