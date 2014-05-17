# -*- coding: utf-8 -*-
import sys, subprocess, os
from lib import util
from base import ThreadedTTSBackend

class OSXSayTTSBackend(ThreadedTTSBackend):
	provider = 'OSXSay'
	displayName = 'OSX Say (OSX Internal)'
	canStreamWav = True
	interval = 100
	
	def __init__(self):
		self.process = None
		self.threadedInit()
		
	def threadedSay(self,text):
		if not text: return
		self.process = subprocess.Popen(['say', text.encode('utf-8')])
		while self.process.poll() == None and self.active: util.sleep(10)
		
	def getWavStream(self,text):
		wav_path = os.path.join(util.getTmpfs(),'speech.wav')
		subprocess.call(['say', '-o', wav_path,'--file-format','WAVE','--data-format','LEI16@22050',text.encode('utf-8')])
		return open(wav_path,'rb')
		
	def isSpeaking(self):
		return (self.process and self.process.poll() == None) or ThreadedTTSBackend.isSpeaking(self)

	def stop(self):
		if not self.process: return
		try:
			self.process.terminate()
		except:
			pass

	@staticmethod
	def available():
		return sys.platform == 'darwin' and not util.isATV2()