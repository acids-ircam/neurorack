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

    def interp_trio(self, cv_list, features_list):
        # Simulate CVs
        # cv_list = [random.sample(range(-4, 4), 1)[0]] * 4
        # cv_list = [(x + 4) / 8 for x in cv_list]
        cv_sum = sum(cv_list)
        cv_list = [x / cv_sum for x in cv_list]
        #if (abs(2 - cv_sum) < 0.1):
        #    cv_list = [1, 0, 0, 0]
        print(cv_list)
        # Run through CV values
        #interp = torch.zeros_like(features_list[0])
        #for i, snd in enumerate(features_list):
        #    interp += (snd * cv_list[i]) #/ cv_sum
        interp = cv_list[0] * features_list[0] + cv_list[1] * features_list[1]
        self._features = interp
        print('End of interpolate')
        return interp


if __name__ == '__main__':
    model = NSF()
    model.preload()
    # for wav in wav_adresses:
    wav_list = ['160_Bpm_Cinematic_Impact_6.wav',
                'ACEAURA_FX_impact_star_03_stripped.wav',
                'ANIMAL_HOUSE_fx_impacter_G.wav',
                'dce_synth_one_shot_bumper_G#min.wav',
                'JORDY_DAZZ_fx_impact_sword.wav',
                'reference_impact.wav',
                'SH_FFX_123BPM_IMPACT_01.wav']
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
    t_len = [t.shape[1] for t in feats]
    min_size = min(t_len)
    for f in range(len(feats)):
        feats[f] = feats[f][:, :min_size, :]
    from itertools import combinations
    possible_sets = list(combinations(range(len(wav_list)),2))
    print('Possible : ' + str(len(possible_sets)))
    base_comb = [[0, 1.0], [0.25, 0.75], [0.5, 0.5], [0.75, 0.25], [1.0, 0]]
    """
    t = np.linspace(0, 2 * np.pi, min_size)
    slow_sin = np.sin(t * 2)
    fast_sin = np.sin(t * 10)
    slow_square = slow_sin.copy()
    slow_square[slow_square < 0] = -1
    slow_square[slow_square > 0] = 1
    fast_square = fast_sin.copy()
    fast_square[fast_square < 0] = -1
    fast_square[fast_square > 0] = 1
    slow_sin = torch.tensor(slow_sin).cuda()
    fast_sin = torch.tensor(fast_sin).cuda()
    slow_square = torch.tensor(slow_square).cuda()
    fast_square = torch.tensor(fast_square).cuda()
    for f in range(len(feats)):
        s_path = "generation_testing/" + str(f)
        for k, v in {6:'f0', 0:'rms', 2:'rolloff', 3:'flatness', 4:'bandwidth', 5:'centroid'}.items():
            cur_path = s_path + '_' + v
            for f_name, func in {'slow_sin':slow_sin, 'fast_sin':fast_sin, 'slow_square':slow_square, 'fast_square':fast_square}.items():
                fin_path = cur_path + '_' + f_name
                rep_feat = feats[f].clone()
                rep_feat[:, :, k] = (((func + torch.min(func)) / torch.std(func)) * 0.5) + 0.25
                audio = model.generate(rep_feat)
                sf.write(fin_path + '.wav', audio, sr)
                rep_feat = feats[f].clone()
                rep_feat[:, :, k] *= func
                audio = model.generate(rep_feat)
                sf.write(fin_path + '_modulate.wav', audio, sr)
                rep_feat = feats[f].clone()
                rep_feat[:, :, k] *= (((func + torch.min(func)) / torch.std(func)) * 0.5) + 0.25
                audio = model.generate(rep_feat)
                sf.write(fin_path + '_modulate_normed.wav', audio, sr)
    """
    #%% Now interpolate
    for s in possible_sets:
        s_path = "generation_testing/"
        f_feats = []
        print(s)
        for n in s:
            s_path += str(n) + '_'
            f_feats.append(feats[n])
        print(s_path)
        for c in base_comb:
            cur_path = s_path
            print(c)
            for v in c :
                cur_path += str(v) + '_'
            cur_path = cur_path[:-1] + '.wav'
            feats_interp = model.interp_trio(c, f_feats)
            audio = model.generate(feats_interp)
            print(cur_path)
            sf.write(cur_path, audio, sr)
