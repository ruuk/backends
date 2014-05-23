# -*- coding: utf-8 -*-

import os, subprocess
import base
from lib import util

def getStartupInfo():
	if hasattr(subprocess,'STARTUPINFO'): #Windows
		startupinfo = subprocess.STARTUPINFO()
		try:
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW #Suppress terminal window
		except:
			startupinfo.dwFlags |= 1
		return startupinfo

	return None
			
class CepstralTTSBackend(base.SimpleTTSBackendBase):
	provider = 'Cepstral'
	displayName = 'Cepstral'
	interval = 100
	canStreamWav = False
	settings = {	'voice':'',
					'use_aoss':False,
					'speed':170,
					'volume':0,
					'pitch':0
					
	}
	
	def __init__(self):
		base.SimpleTTSBackendBase.__init__(self,mode=base.SimpleTTSBackendBase.ENGINESPEAK)
		self.startupinfo = getStartupInfo()
		self.update()
		self.process = None

	def runCommandAndSpeak(self,text):
		args = ['swift']
		if self.useAOSS: args.insert(0,'aoss')
		if self.voice: args.extend(('-n',self.voice))
		args.extend(('-p','audio/volume={0},speech/rate={1},speech/pitch/shift={2}'.format(self.volume,self.rate,self.pitch)))
		args.append(text.encode('utf-8'))
		self.process = subprocess.Popen(args, startupinfo=self.startupinfo, stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		while self.process.poll() == None and self.active: util.sleep(10)	

	def update(self):
		self.voice = self.setting('voice')
		self.rate = self.setting('speed')
		self.useAOSS = self.setting('use_aoss')
		if self.useAOSS and not util.commandIsAvailable('aoss'):
			util.LOG('Cepstral: Use aoss is enabled, but aoss is not found. Disabling.')
			self.useAOSS = False
		volume = self.setting('volume')
		self.volume = int(round(100 * (10**(volume/20.0)))) #convert from dB to percent
		pitch = self.setting('pitch')
		self.pitch = 0.4 + ((pitch+6)/20.0) * 2 #Convert from (-6 to +14) value to (0.4 to 2.4)

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass
	
	@classmethod
	def getVoiceLines(cls):
		import re
		ret = []
		out = subprocess.check_output(['swift','--voices'],startupinfo=getStartupInfo()).splitlines()
		for l in reversed(out):
			if l.startswith(' ') or l.startswith('-'): break
			ret.append(re.split('\s+\|\s+',l.strip(),6))
		return ret
	
	@classmethod	
	def voices(cls):
		ret = []
		for v in cls.getVoiceLines():
			voice = v[0]
			ret.append((voice,voice))
		return ret
			
	@classmethod
	def settingList(cls,setting,*args):
		if setting == 'voice':
			return cls.voices()
		return None
		
	@staticmethod
	def available():
		try:
			subprocess.call(['swift', '-V'], startupinfo=getStartupInfo(),stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True
