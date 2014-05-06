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
					'use_aoss':False
					
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
		args.append(text)
		self.process = subprocess.Popen(args, startupinfo=self.startupinfo, stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		while self.process.poll() == None and self.active: util.sleep(10)	

	def update(self):
		self.voice = self.setting('voice')
		self.useAOSS = self.setting('use_aoss')
		if self.useAOSS and not util.commandIsAvailable('aoss'):
			util.LOG('Cepstral: Use aoss is enabled, but aoss is not found. Disabling.')
			self.useAOSS = False

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass
	
	def getVoiceLines(self):
		import re
		ret = []
		out = subprocess.check_output(['swift','--voices'],startupinfo=self.startupinfo).splitlines()
		for l in reversed(out):
			if l.startswith(' ') or l.startswith('-'): break
			ret.append(re.split('\s+\|\s+',l.strip(),6))
		return ret
			
	def voices(self):
		ret = []
		for v in self.getVoiceLines():
			ret.append(v[0])
		return ret
			
	@staticmethod
	def available():
		try:
			subprocess.call(['swift', '-V'], startupinfo=getStartupInfo(),stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True
