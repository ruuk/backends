# -*- coding: utf-8 -*-

from lib import util
from base import LogOnlyTTSBackend
from nvda import NVDATTSBackend
from festival import FestivalTTSBackend
from pico2wave import Pico2WaveTTSBackend
from flite import FliteTTSBackend
from osxsay import OSXSayTTSBackend
from sapi import SAPITTSBackend
from espeak import ESpeakTTSBackend, ESpeakCtypesTTSBackend
from speechdispatcher import SpeechDispatcherTTSBackend
from jaws import JAWSTTSBackend
from sjhttsd import SJHttsdTTSBackend
from cepstral import CepstralTTSBackend
from google import GoogleTTSBackend

backendsByPriority = [JAWSTTSBackend,NVDATTSBackend,SAPITTSBackend,SpeechDispatcherTTSBackend,FliteTTSBackend,ESpeakTTSBackend,Pico2WaveTTSBackend,FestivalTTSBackend,CepstralTTSBackend,OSXSayTTSBackend,SJHttsdTTSBackend,GoogleTTSBackend,ESpeakCtypesTTSBackend,LogOnlyTTSBackend]

def getAvailableBackends(can_stream_wav=False):
	available = []
	for b in backendsByPriority:
		if not b._available(): continue
		if can_stream_wav and not b.canStreamWav: continue
		available.append(b)
	return available
			
def getBackendFallback():
	if util.isATV2():
		return FliteTTSBackend 
	elif util.isWindows():
		return SAPITTSBackend
	elif util.isOSX():
		return OSXSayTTSBackend
	elif util.isOpenElec():
		return ESpeakTTSBackend
	for b in backendsByPriority:
		if b._available(): return b
	return None
	
def getVoices(provider):
	voices = None
	bClass = getBackendByProvider(provider)
	if bClass:
		b = bClass()
		voices = b.voices()
	return voices
	
def getLanguages(provider):
	languages = None
	bClass = getBackendByProvider(provider)
	if bClass:
		b = bClass()
		languages = b.languages()
	return languages
	
def getSettingsList(provider,setting):
	settings = None
	bClass = getBackendByProvider(provider)
	if bClass:
		b = bClass()
		settings = b.settingList(setting)
	return settings

def getPlayers(provider):
	players = None
	bClass = getBackendByProvider(provider)
	if bClass and hasattr(bClass,'players'):
		b = bClass()
		players = b.players()
	return players
		
def getBackend(provider='auto'):
	provider = util.getSetting('backend') or provider
	b = getBackendByProvider(provider)
	if not b or not b._available():
 		for b in backendsByPriority:
			if b._available(): break
	return b

def getWavStreamBackend(provider='auto'):
	b = getBackendByProvider(provider)
	if not b or not b._available() or not b.canStreamWav:
 		for b in backendsByPriority:
			if b._available() and b.canStreamWav: break
	return b
	
def getBackendByProvider(name):
	if name == 'auto': return None
	for b in backendsByPriority:
		if b.provider == name and b._available():
			return b
	return None
