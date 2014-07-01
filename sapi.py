# -*- coding: utf-8 -*-
import os, sys, wave, array, StringIO
from base import SimpleTTSBackendBase
from lib import util
from xml.sax import saxutils

class SAPITTSBackend(SimpleTTSBackendBase):
	provider = 'SAPI'
	displayName = 'SAPI (Windows Internal)'
	settings = {		'speak_via_xbmc':True,
					'voice':'',
					'speed':0,
					'pitch':0,
					'volume':100
	}
	canStreamWav = True
	interval = 100
	speedConstraints = (-10,0,10,True)
	pitchConstraints = (-10,0,10,True)
	volumeConstraints = (0,100,100,True)
	volumeExternalEndpoints = (0,100)
	volumeStep = 5
	volumeSuffix = '%'
	baseSSML = u'''<?xml version="1.0"?>
<speak version="1.0"
         xmlns="http://www.w3.org/2001/10/synthesis"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.w3.org/2001/10/synthesis
                   http://www.w3.org/TR/speech-synthesis/synthesis.xsd"
         xml:lang="en-US">
  <volume level="{volume}" />
  <pitch absmiddle="{pitch}" />
  <rate absspeed="{speed}" />
  <p>{text}</p>
</speak>'''
	
	def init(self):
		self.SpVoice = None
		try:
			from comtypes.client._code_cache import _find_gen_dir
			gen = _find_gen_dir()
			import stat, shutil
			os.chmod(gen,stat.S_IWRITE)
			shutil.rmtree(gen,ignore_errors=True)
			os.makedirs(gen)
		except:
			util.ERROR('Failed to empty comtypes gen dir')

		import comtypes.client
		from _ctypes import COMError
		self.comtypesClient = comtypes.client
		self.COMError = COMError
		self.resetSAPI()
		self.update()
		
	def resetSAPI(self):
		self.flags = 137
		self.streamFlags = 136
		self.SpVoice = self.comtypesClient.CreateObject("SAPI.SpVoice")
		try:
			self.SpVoice.Speak('',self.flags)
		except self.COMError,e:
			if util.DEBUG:
				self.logSAPIError(e)
				util.LOG('SAPI: XP Detected - changing flags')
			self.flags = 1
			self.streamFlags = 2
		
	def logSAPIError(self,com_error):
		try:
			errno = str(com_error.hresult)
			with open(os.path.join(util.backendsDirectory(),'sapi_comerrors.txt'),'r') as f:
				lines = f.read().splitlines()
			for l1,l2 in zip(lines[0::2],lines[1::2]):
				bits = l1.split()
				if errno in bits:
					util.LOG('SAPI Comtypes error ({0})[{1}]: {2}'.format(errno,bits[0],l2 or '?'))
					break
		except:
			util.ERROR('Error looking up SAPI error: {0}'.format(com_error))
		util.LOG('Failed to lookup SAPI error: {0}'.format(com_error))
		util.LOG('Line: {1} In: {0}'.format(sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno))


	def runCommand(self,text,outFile):
		if not self.SpVoice: return
		stream = self.comtypesClient.CreateObject("SAPI.SpFileStream")
		stream.Open(outFile, 3) #3=SSFMCreateForWrite
		ssml = self.ssml.format(text=saxutils.escape(text))
		self.SpVoice.Speak(ssml,self.streamFlags)
		stream.close()
		return True

	def runCommandAndSpeak(self,text):
		if not self.SpVoice: return
		ssml = self.ssml.format(text=saxutils.escape(text))
		try:
			self.SpVoice.Speak(ssml,self.flags)
		except self.COMError,e:
			util.ERROR('SAPI: COMError: RESETTING',hide_tb=True)
			self.logSAPIError(e)
			self.resetSAPI()
			try:
				self.SpVoice.Speak(ssml,self.flags)
			except self.COMError,e:
				util.LOG('SAPI: COMError: Failed after reset')
				self.logSAPIError(e)
		
	def getWavStream(self,text):
		fmt = self.comtypesClient.CreateObject("SAPI.SpAudioFormat")
		fmt.Type = 22
		
		stream = self.comtypesClient.CreateObject("SAPI.SpMemoryStream")
		stream.Format = fmt
		self.SpVoice.AudioOutputStream = stream
		
		ssml = self.ssml.format(text=saxutils.escape(text))
		self.SpVoice.Speak(ssml,self.streamFlags)
		
		wavIO = StringIO.StringIO()
		self.createWavFileObject(wavIO,stream)
		return wavIO
	
	def createWavFileObject(self,wavIO,stream):
		#Write wave via the wave module
		wavFileObj = wave.open(wavIO,'wb')
		wavFileObj.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
		wavFileObj.writeframes(array.array('B',stream.GetData()).tostring())
		wavFileObj.close()

	def stop(self):
		if not self.SpVoice: return
		if not self.inWavStreamMode:
			try:
				self.SpVoice.Speak('',3)
			except self.COMError, e:
				self.logSAPIError(e)
		
	def update(self):
		self.setMode(self.getMode())
		self.ssml = self.baseSSML.format(text='{text}',volume=self.setting('volume'),speed=self.setting('speed'),pitch=self.setting('pitch'))
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
		
	def getMode(self):
		if self.setting('speak_via_xbmc'):
			return SimpleTTSBackendBase.WAVOUT
		else:
			if self.SpVoice: self.SpVoice.AudioOutputStream = None
			return SimpleTTSBackendBase.ENGINESPEAK
	
	@classmethod
	def settingList(cls,setting,*args):
		self = cls()
		if setting == 'voice':
			voices=[]
			v=self.SpVoice.getVoices()
			for i in xrange(len(v)):
				try:
					name=v[i].GetDescription()
				except COMError,e: #analysis:ignore
					self.logSAPIError(e)
				voices.append((name,name))
			return voices

	@staticmethod
	def available():
		return sys.platform.lower().startswith('win')

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