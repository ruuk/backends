# -*- coding: utf-8 -*-
import sys, wave, array, StringIO
from base import ThreadedTTSBackend
from lib import util
from xml.sax import saxutils

class SAPITTSBackend(ThreadedTTSBackend):
	provider = 'SAPI'
	displayName = 'SAPI (Windows Internal)'
	settings = {	'voice':'',
					'speed':0,
					'volume':100
	
	}
	canStreamWav = True
	interval = 100
	speedMin = -10
	speedMax = 10
	speedMid = 0
	
	baseSSML = u'''<?xml version="1.0"?>
<speak version="1.0"
         xmlns="http://www.w3.org/2001/10/synthesis"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                   http://www.w3.org/TR/speech-synthesis/synthesis.xsd"
         xml:lang="en-US">
  <p>{0}</p>
</speak>'''
	
	def __init__(self):
		import comtypes.client
		from _ctypes import COMError
		self.comtypesClient = comtypes.client
		self.COMError = COMError
		self.resetSAPI()
		self.update()
		self.threadedInit()
		
	def resetSAPI(self):
		self.SpVoice = self.comtypesClient.CreateObject("SAPI.SpVoice")
		
	def threadedSay(self,text):
		if not self.SpVoice: return
		ssml = self.baseSSML.format(saxutils.escape(text))
		try:
			self.SpVoice.Speak(ssml,1)
		except self.COMError:
			util.ERROR('COMError: RESETTING SAPI',hide_tb=True)
			self.resetSAPI()
			try:
				self.SpVoice.Speak(ssml,1)
			except self.COMError:
				util.ERROR('COMError: SAPI Failed after reset')
#	def getWavStream(self,text):
#		#Have SAPI write to file
#		stream = self.comtypesClient.CreateObject("SAPI.SpFileStream")
#		fpath = os.path.join(util.getTmpfs(),'speech.wav')
#		open(fpath,'w').close()
#		stream.Open(fpath,3)
#		self.SpVoice.AudioOutputStream = stream
#		self.SpVoice.Speak(text,0)
#		stream.close()
#		return open(fpath,'rb')
		
	def getWavStream(self,text):
		fmt = self.comtypesClient.CreateObject("SAPI.SpAudioFormat")
		fmt.Type = 22
		
		stream = self.comtypesClient.CreateObject("SAPI.SpMemoryStream")
		stream.Format = fmt
		self.SpVoice.AudioOutputStream = stream
		
		self.SpVoice.Speak(text,0)
		
		wavIO = StringIO.StringIO()
		self.createWavFileObject(wavIO,stream)
		return wavIO
	
	def createWavFileObject(self,wavIO,stream):
		#Write wave via the wave module
		wavFileObj = wave.open(wavIO,'wb')
		wavFileObj.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
		wavFileObj.writeframes(array.array('B',stream.GetData()).tostring())
		wavFileObj.close()
	
#	def createWavFileObject(self,wavIO,stream):
#		#Write wave headers manually
#		import struct
#		data = array.array('B',stream.GetData()).tostring()
#		dlen = len(data)
#		header = struct.pack(		'4sl8slhhllhh4sl',
#											'RIFF',
#											dlen+36,
#											'WAVEfmt ',
#											16, #Bits
#											1, #Mode
#											1, #Channels
#											22050, #Samplerate
#											22050*16/8, #Samplerate*Bits/8
#											1*16/8, #Channels*Bits/8
#											16,
#											'data',
#											dlen
#		)
#		wavIO.write(header)
#		wavIO.write(data)

	def stop(self):
		if not self.SpVoice: return
		self.SpVoice.Speak('',3)

	def isSpeaking(self):
		return ThreadedTTSBackend.isSpeaking(self) or None
		
	def update(self):
		self.speed = self.setting('speed')
		self.volume = self.setting('volume')
		self.SpVoice.Rate = self.speed
		self.SpVoice.Volume = self.volume
		voice_name = self.setting('voice')
		if voice_name:
			v=self.SpVoice.getVoices()
			for i in xrange(len(v)):
				voice=v[i]
				if voice_name==voice.GetDescription():
					break
			else:
				# Voice not found.
				return
			self.SpVoice.Voice = voice
		
	def close(self):
		del self.SpVoice
		self.SpVoice = None
	
	@classmethod
	def settingList(cls,setting,*args):
		self = cls()
		if setting == 'voice':
			voices=[]
			v=self.SpVoice.getVoices()
			for i in xrange(len(v)):
				try:
					name=v[i].GetDescription()
				except COMError: #analysis:ignore
					pass
				voices.append((name,name))
			return voices

	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')
