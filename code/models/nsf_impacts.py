import sklearn
import torch
import librosa
import numpy as np
import time
import os
import tqdm
import torchaudio
import soundfile as sf


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
    # m_path = "/home/martin/Desktop/Impact-Synth-Hardware/code/models/model_nsf_sinc_ema_impacts_waveform_5.0.th"
    m_path = "/home/hime/Work/Neurorack/Impact-Synth-Hardware/code/models/model_nsf_sinc_ema_impacts_waveform_5.0.th"
    f_pass = 3

    def __init__(self):
        # Testing NSF
        print('Creating empty NSF')
        self._model = None
        self._wav_file = 'reference_impact.wav'

    def dummy_features(self, wav):
        y, sr = librosa.load(wav)
        features = spectral_features(y, sr)
        return features

    def preload(self):
        self._model = torch.load(self.m_path, map_location="cuda")
        self._model = self._model.cuda()
        print("loaded")
        features = self.dummy_features(self._wav_file)
        features = torch.tensor(features[:10, :]).unsqueeze(0).cuda().float()
        for p in range(self.f_pass):
            print("pass")
            with torch.no_grad():
                self._model(features)

    def generate_random(self, length=200):
        print('Generating random length ' + str(length))
        features = [torch.randn(1, length, 1).cuda()] * 7
        with torch.no_grad():
            audio = self._model(features)
        return audio.squeeze().detach().cpu().numpy()

    def generate(self, features):
        # features = self.dummy_features(wav)
        # features = torch.tensor(features).unsqueeze(0).cuda().float()
        with torch.no_grad():
            audio = self._model(features)
        return audio.squeeze().detach().cpu().numpy()


if __name__ == '__main__':
    root_dir = "/home/hime/Work/dataset/toydataset"
    wav_adresses = [files_names for files_names in os.listdir(root_dir) if
                    (files_names.endswith('.wav') or files_names.endswith('.mp3'))]
    model = NSF()
    model.preload()
    for wav in wav_adresses:
        y, sr = librosa.load(root_dir + '/' + wav)
        features = spectral_features(y, sr)
        print(features.shape)
        features = torch.tensor(features).unsqueeze(0).cuda().float()
        audio = model.generate(features)
        sf.write("generate" + str(wav) + ".wav", audio, sr)


