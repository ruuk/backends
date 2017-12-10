# -*- coding: utf-8 -*-
import base
import subprocess
import os
from lib import util


class TermuxTTSBackend(base.SimpleTTSBackendBase):
    provider = 'termux'
    displayName = 'Termux'

    def init(self):
        pass

    def runCommandAndSpeak(self, text):
        args = ['termux-tts-speak', text]

        process = subprocess.Popen(args)
        while process.poll() == None and self.active:
            util.sleep(10)

    def stop(self):
        pass

    @staticmethod
    def available():
        try:
            subprocess.call(['termux-tts-speak','-h'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
        except:
            return False
        return True
