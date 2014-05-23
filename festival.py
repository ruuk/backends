# -*- coding: utf-8 -*-
import os, subprocess
from base import TTSBackendBase

class FestivalTTSBackend(TTSBackendBase):
	provider = 'Festival'
	displayName = 'Festival'
	settings = {	'voice':'',
					'volume':0,
					'speed':0,
	}
	
	def __init__(self):
		self.update()
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
		durMult = ''
		if self.voice: voice = '(voice_{0})\n'.format(self.voice)
		if self.durationMultiplier: durMult = "(Parameter.set 'Duration_Stretch {0})\n".format(self.durationMultiplier)
		self.festivalProcess = subprocess.Popen(['festival','--pipe'],shell=True,stdin=subprocess.PIPE)
		out = '{0}{1}(utt.play (utt.wave.rescale (SynthText "{2}") {3:.2f} nil))\n'.format(voice,durMult,text.encode('utf-8'),self.volume)
		self.festivalProcess.communicate(out)
		#if self.festivalProcess.poll() != None: self.startFestivalProcess()
		self._isSpeaking = False
		
	def isSpeaking(self):
		return self._isSpeaking
		
	def update(self):
		self.voice = self.setting('voice')
		volume = self.setting('volume')
		self.volume = 1 * (10**(volume/20.0)) #convert from dB to percent
		speed = self.setting('speed')
		self.durationMultiplier = 1.8 - (((speed + 16)/28.0) * 1.4) #Convert from (-16 to +12) value to (1.8 to 0.4)

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