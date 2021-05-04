import numpy as np
import sounddevice as sd
from base import InputProcess

class Audio(InputProcess):

    def __init__(self):
        super().__init__('audio')
        self.sr = 22050
        sd.default.samplerate = sr
        sd.default.device = 1

    def play_noise(self, length = 4):
        audio = np.random.randn(length * self.sr)
        sd.play(audio, self.sr)
        sd.wait()


