# -*- coding: utf-8 -*-
import base
import subprocess
import os


class TermuxTTSBackend(base.SimpleTTSBackendBase):
    provider = 'termux'
    displayName = 'Termux'

    def init(self):
        self.process = None

    def runCommandAndSpeak(self, text):
        args = ['termux-tts-speak', text]

        self.process = subprocess.Popen(args)
        while self.process.poll() == None and self.active: util.sleep(10)

    def stop(self):
        if not self.process: return
        try:
            self.process.terminate()
        except:
            pass

    @staticmethod
    def available():
        try:
            subprocess.call(['termux-tts-speak','-h'], stdout=(open(os.path.devnull, 'w')), stderr=subprocess.STDOUT)
        except:
            return False
        return True
