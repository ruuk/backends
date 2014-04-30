# -*- coding: utf-8 -*-
import os, subprocess
import base
import audio

class Pico2WaveTTSBackend(base.SimpleTTSBackendBase):
	provider = 'pico2wave'
	displayName = 'pico2wave'
	interval = 100
	speedMin = 20
	speedMax = 200
	speedMid = 100
	settings = {	'language':'',
					'speed':0,
					'player':None
	}

	def __init__(self):
		preferred = self.setting('player') or None
		player = audio.WavPlayer(audio.UnixExternalPlayerHandler,preferred,True)
		base.SimpleTTSBackendBase.__init__(self,player)
		self.update()
		
	def runCommand(self,text,outFile):
		args = ['pico2wave']
		if self.language: args.extend(['-l',self.language])
		args.extend(['-w', u'{0}'.format(outFile), u'{0}'.format(text)])
		subprocess.call(args)
		return True
		
	def languages(self):
		try:
			out = subprocess.check_output(['pico2wave','-l','NONE','-w','/dev/null','X'],stderr=subprocess.STDOUT)
		except subprocess.CalledProcessError, e:
			out = e.output
		if not 'languages:' in out: return None
		
		return out.split('languages:',1)[-1].split('\n\n')[0].strip('\n').split('\n')

	def update(self):
		self.language = self.setting('language')
		self.setSpeed(self.setting('speed'))
		
	@staticmethod
	def available():
		try:
			subprocess.call(['pico2wave', '--help'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
		except (OSError, IOError):
			return False
		return True