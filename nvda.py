# -*- coding: utf-8 -*-
import os, ctypes
from lib import util
from base import TTSBackendBase

DLL_PATH = os.path.join(util.backendsDirectory(),'nvda','nvdaControllerClient32.dll')

try:
	from ctypes import windll
except ImportError:
	windll =None

class NVDATTSBackend(TTSBackendBase):
	provider = 'nvda'
	displayName = 'NVDA'

	@staticmethod
	def available():
		if not windll:
			return False
		try:
			dll = ctypes.windll.LoadLibrary(DLL_PATH)
			res = dll.nvdaController_testIfRunning() == 0
			ctypes.windll.kernel32.FreeLibrary(dll._handle)
			del dll
			return res
		except:
			return False

	def init(self):
		try:
			self.dll = ctypes.windll.LoadLibrary(DLL_PATH)
		except:
			self.dll = None

	def isRunning(self):
		return self.dll.nvdaController_testIfRunning() == 0

	def say(self,text,interrupt=False):
		if not self.dll:
			return

		if interrupt:
			self.stop()
		if not self.dll.nvdaController_speakText(text) == 0:
			if not self.isRunning():
				self.flagAsDead('Not running')
				return

	def stop(self):
		if not self.dll: return
		self.dll.nvdaController_cancelSpeech()
		
	def close(self):
		if not self.dll: return
		ctypes.windll.kernel32.FreeLibrary(self.dll._handle)
		del self.dll
		self.dll = None

