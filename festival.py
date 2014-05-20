# -*- coding: utf-8 -*-
import os, subprocess
from base import TTSBackendBase

class FestivalTTSBackend(TTSBackendBase):
	provider = 'Festival'
	displayName = 'Festival'
	settings = {'voice':''}
	
	def __init__(self):
		self.voice = self.setting('voice')
		self.startFestivalProcess()
		self._isSpeaking = False
		
	def startFestivalProcess(self):
		#LOG('Starting Festival...')
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		pass
		
	def say(self,text,interrupt=False):
		if not text: return
		self._isSpeaking = True
		##self.festivalProcess.send_signal(signal.SIGINT)
		#self.festivalProcess = subprocess.Popen(['festival'],shell=True,stdin=subprocess.PIPE)
		voice = ''
		if self.voice: voice = '(voice_{0})\n'.format(self.voice)
		self.festivalProcess = subprocess.Popen(['festival','--pipe'],shell=True,stdin=subprocess.PIPE)
		self.festivalProcess.communicate('{0}(SayText "{1}")\n'.format(voice,text.encode('utf-8')))
		#if self.festivalProcess.poll() != None: self.startFestivalProcess()
		self._isSpeaking = False
		
	def isSpeaking(self):
		return self._isSpeaking
		
	def update(self):
		self.voice = self.setting('voice')
		
	def close(self):
		#if self.festivalProcess.poll() != None: return
		#self.festivalProcess.terminate()
		pass
	
	@classmethod
	def settingList(cls,setting,*args):
		if setting == 'voice':
			p = subprocess.Popen(['festival','-i'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			d = p.communicate('(voice.list)')
			l = map(str.strip,d[0].rsplit('> (',1)[-1].rsplit(')',1)[0].split('\n'))
			if l: return [(v,v) for v in l]
		return None
		
	@staticmethod
	def available():
		try:
			subprocess.call(['festival', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True