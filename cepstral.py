# -*- coding: utf-8 -*-

import os, subprocess
import base
from lib import util

class CepstralTTSBackend(base.SimpleTTSBackendBase):
	provider = 'Cepstral'
	displayName = 'Cepstral'
	interval = 100
	settings = {	'voice':''
					
	}
	
	def __init__(self):
		base.SimpleTTSBackendBase.__init__(self,mode=base.SimpleTTSBackendBase.ENGINESPEAK)
		if hasattr(subprocess,'STARTUPINFO'): #Windows
			self.startupinfo = subprocess.STARTUPINFO()
			self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW #Suppress terminal window
		else:
			self.startupinfo = None
		self.voice = self.setting('voice')
		self.process = None

	def runCommandAndSpeak(self,text):
		args = ['swift']
		if self.voice: args.extend(('-n',self.voice))
		args.append(text)
		self.process = subprocess.Popen(args, startupinfo=self.startupinfo, stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		while self.process.poll() == None and self.active: util.sleep(10)	

	def update(self):
		self.voice = self.setting('voice')

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass
	
	def voices(self):
		import re
		ret = []
		out = subprocess.check_output(['swift','--voices']).splitlines()
		for l in reversed(out):
			if l.startswith(' ') or l.startswith('-'): break
			ret.append(re.split('\s+\|\s+',l.strip(),6)[0])
		return ret
		
	@staticmethod
	def available():
		try:
			subprocess.call(['swift', '-V'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True
