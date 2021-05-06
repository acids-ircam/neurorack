import numpy as np
import sounddevice as sd
from parallel import ProcessInput
from models.ddsp import DDSP

class Audio(ProcessInput):

    def __init__(self, model='ddsp', sr=22050):
        super().__init__('audio')
        # Configure audio
        self.sr = sr
        sd.default.samplerate = self.sr
        sd.default.device = 1
        # Set model
        if (model == 'ddsp'):
            self.model = DDSP()
        else:
            raise NotImplementedError

    def play_noise(self, length = 4):
        audio = np.random.randn(length * self.sr)
        sd.play(audio, self.sr)
        sd.wait()

    def play_model(self):
        audio = self.model.generate_random()
        sd.play(audio, self.sr)
        sd.wait()


