import torch
import librosa
import random
import numpy as np
import soundfile as sf
from pathlib import Path
from scipy.interpolate import interp1d

models = ['/Users/esling/Coding/acids/team/philippe/raster/output/model_nsf_sinc_ema_impacts_waveform_5.0.th',
          '/Users/esling/Coding/acids/team/philippe/raster/output/model_nsf_sinc_impacts_waveform_5.0.th']


def spectral_features(y, sr):
    features = [None] * 7
    features[0] = librosa.feature.rms(y)
    features[1] = librosa.feature.zero_crossing_rate(y)
    # Spectral features
    S, phase = librosa.magphase(librosa.stft(y=y))
    # Compute all descriptors
    features[2] = librosa.feature.spectral_rolloff(S = S)
    features[3] = librosa.feature.spectral_flatness(S = S)
    features[4] = librosa.feature.spectral_bandwidth(S = S)
    features[5] = librosa.feature.spectral_centroid(S = S)
    #print(features[5].shape)
    features[6] = librosa.yin(y, 50, 5000, sr=sr)[np.newaxis, :]
    #features[6] = np.array(main(y, sr, f0_min=50, f0_max=2000))[np.newaxis, :]
    #print(features[6].shape)
    features = np.concatenate(features).transpose()
    features[np.isnan(features)] = 1
    features = features[:-1, :]
    return features


def inference(model, features):
    out = model(features)
    out = out #self.model.denormalize_output(out)
    return out.squeeze().detach().numpy()

# Import model
model_impacts = torch.load(models[0], map_location='cpu')
# Reference sample to use
wav_file = 'reference_impact.wav'
# Load wav file
y, sr = librosa.load(wav_file)
# Compute spectral features
feats = torch.tensor(spectral_features(y, sr)[np.newaxis, :, :]).float()
# Perform inference
audio = inference(model_impacts, feats)
