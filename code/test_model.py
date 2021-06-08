import sklearn
import torch
import librosa
import numpy as np
import time
import os
import tqdm
import soundfile as sf
import matplotlib.pyplot as plt

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
    m_path = "models/model_nsf_sinc_ema_impacts_waveform_5.0.th"
    f_pass = 3

    def __init__(self):
        # Testing NSF
        print('Creating empty NSF')
        self._model = None
        self._wav_file = 'data/reference_impact.wav'

    def dummy_features(self, wav):
        y, sr = librosa.load(wav)
        features = spectral_features(y, sr)
        return features

    def preload(self):
        self._model = torch.load(self.m_path, map_location="cuda")
        self._model = self._model.cuda()
        print("loaded")
        # features = self.dummy_features(self._wav_file)
        # features = torch.tensor(features[:10, :]).unsqueeze(0).cuda().float()
        #for p in range(self.f_pass):
        #    print("pass")
        #    with torch.no_grad():
        #        self._model(features)

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

    def interp_trio(self, cv_list):
        # Simulate CVs
        # cv_list = [random.sample(range(-4, 4), 1)[0]] * 4
        cv_list = [(x + 4) / 8 for x in cv_list]
        cv_sum = sum(cv_list)
        if (abs(2 - cv_sum) < 0.1):
            cv_list = [1, 0, 0, 0]
        print(cv_list)
        # Run through CV values
        interp = torch.zeros_like(self._features_list[0])
        for i, snd in enumerate(self._features_list):
            interp += snd * cv_list[i] / cv_sum
        self._features = interp
        print('End of interpolate')
        return interp


if __name__ == '__main__':
    model = NSF()
    model.preload()
    # for wav in wav_adresses:
    wav_list = ['160_Bpm_Cinematic_Impact_6.wav',
                'ABSB_Impact__Deep_Impact.wav',
                'ACEAURA_FX_impact_star_03_stripped.wav', 
                'Afro_FX_Oneshot_Impact_3.wav',
                'ANIMAL_HOUSE_fx_impacter_G.wav',
                'ASD_Transition_Loop_95_Buzz_Impact.wav',
                'AW2_Churning_Storm_Impact.wav',
                'dce_synth_one_shot_bumper_G#min.wav', 
                'ESM_Braaam_Strike_2_Hit_One_Shot_Dark_Dealthy_Horror_Laugh_Impact_Stinger_Movie_Trailer.wav',
                'FL_AFX_123BPM_IMPACT_02_C#.wav',
                'JORDY_DAZZ_fx_impact_sword.wav',
                'MODE_BE2_fx_impact_hard_07.wav',
                'MRTNWVE_fx_impact_mclaren.wav',
                'SH_FFX_123BPM_IMPACT_01.wav',
                'FF_ET_whoosh_hit_little.wav']
    feats = []
    cur_imp = 0
    for wav in wav_list:
        y, sr = librosa.load('data/' + wav)
        features = spectral_features(y, sr)
        features = torch.tensor(features).unsqueeze(0).float().cuda()#.cuda().float()
        torch.save(features, "models/features_interp" + str(wav) + ".th")
        print('Generate ' + wav)
        audio = model.generate(features)
        sf.write("generation_testing/" + str(cur_imp) + ".wav", audio, sr)
        feats.append(features)
        cur_imp += 1
    exit()
    #%%
    import random
    from itertools import combinations
    possible_sets = list(combinations(range(len(wav_list)), 4))
    vals = random.sample(possible_sets, min(20, len(wav_list) // 4))
    print(vals)
    print('Possible : ' + len(possible_sets))
    base_comb = [[0.25, 0.25, 0.25, 0.25],
                 [0.5, 0.5, 0, 0],
                 [0.5, 0, 0.5, 0],
                 [0.5, 0, 0.0, 0.5],
                 [0, 0.5, 0.5, 0],
                 [0, 0.5, 0, 0.5],
                 [0, 0, 0.5, 0.5]]
    for r 
    # Run through alpha values
    interp = []
    n_steps = 11
    size = min(x_a.shape[1], x_b.shape[1])
    x_a = x_a[:, :size, :]
    x_b = x_b[:, :size, :]
    alpha_values = np.linspace(0, 1, n_steps)
    for i, alpha in enumerate(alpha_values):
        x_interp = (1 - alpha) * x_b + alpha * x_a
        x_interp = model.generate(x_interp)
        interp.append(x_interp)
        sf.write("generation_testing/interp_" + str(i) + ".wav", x_interp, sr)




