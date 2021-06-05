import sklearn
import torch
import librosa
import numpy as np


def spectral_features(y, sr):
    features = [None] * 7
    features[0] = librosa.feature.rms(y)
    features[1] = librosa.feature.zero_crossing_rate(y)
    # Spectral features
    S, phase = librosa.magphase(librosa.stft(y=y))
    # Compute all descriptors
    features[2] = librosa.feature.spectral_rolloff(S=S)
    features[3] = librosa.feature.spectral_flatness(S=S)
    features[4] = librosa.feature.spectral_bandwidth(S=S)
    features[5] = librosa.feature.spectral_centroid(S=S)
    features[6] = librosa.yin(y, 50, 5000, sr=sr)[np.newaxis, :]
    features = np.concatenate(features).transpose()
    features[np.isnan(features)] = 1
    features = features[:-1, :]
    return features


class NSF:
    m_path = "/home/martin/Desktop/Impact-Synth-Hardware/code/models/model_nsf_sinc_ema_impacts_waveform_5.0.th"
    f_pass = 3

    def __init__(self):
        # Testing NSF
        print('Creating empty NSF')
        self._model = None
        self._wav_file = 'reference_impact.wav'

    def dummy_features(self):
        y, sr = librosa.load(self._wav_file)
        features = spectral_features(y, sr)
        return features

    def preload(self):
        self._model = torch.load(self.m_path, map_location="cuda")
        self._model = self._model.cuda()
        print("loaded")
        features = self.dummy_features()
        features = torch.tensor(features[:2, :]).unsqueeze(0).cuda().float()
        for p in range(self.f_pass):
            print("pass")
            with torch.no_grad():
                self._model(features)

    def generate_random(self, length=200):
        print('Generating random length ' + str(length))
        features = [torch.randn(1, length, 1).cuda()] * 7
        with torch.no_grad():
            audio = self._model(features)
        return audio.squeeze().detach().numpy()

    def generate(self):
        features = self.dummy_features()
        with torch.no_grad():
            audio = self._model(features)
        return audio.squeeze().detach().numpy()


