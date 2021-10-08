import sklearn
import torch
import librosa
import numpy as np
import time
import os
import random
import tqdm
# import torchaudio
import soundfile as sf
import threading
from multiprocessing import Event, Process
from torch2trt import torch2trt
from torch2trt import TRTModule

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
    # m_path = "/home/hime/Work/Neurorack/Impact-Synth-Hardware/code/models/model_nsf_sinc_ema_impacts_waveform_5.0.th"
    trt_path = "/home/martin/Desktop/Impact-Synth-Hardware/code/models/model_trt_5.0.th"
    f_pass = 1

    def __init__(self):
        # Testing NSF
        print('Creating empty NSF')
        self._model = None
        self._wav_file = 'reference_impact.wav'
        self._n_blocks = 15
        self._n_batch = 1
        self._thread = None
        self._last_gen_block = 0
        self._last_request_block = -1
        self._block_lookahead = 1
        self._last_val = None
        self._current_chunk = None
        self._next_chunk = None
        self._generated_queue = []
        self._generate_end = False
        self._generate_signal = Event()
        self._features = None
        self._features_list = None

    def dummy_features(self, wav):
        y, sr = librosa.load(wav)
        features = spectral_features(y, sr)
        return features

    def preload(self):
        torch.backends.cudnn.benchmark = True
        #if (not os.path.exists(self.trt_path)):
        self._model = torch.load(self.m_path, map_location="cuda")
        self._model = self._model.cuda()
        #else:
        #    self._model = TRTModule()
        #    self._model.load_state_dict(torch.load(self.trt_path))
        #    self._model = self._model.cuda()
        self._model.eval()
        print("NSF model loaded")
        self.features_loading()
        self._features = self._features_list[0]
        tmp_features = []
        for b in range(self._n_batch):
            tmp_features.append(self._features[:, (b*self._n_blocks):((b+1)*self._n_blocks)+1, :])
        tmp_features = torch.cat(tmp_features)
        print(tmp_features.shape)
        for p in range(self.f_pass):
            print("Starting NSF pass")
            cur_time = time.monotonic()
            with torch.no_grad():
                cur_blocks = self._model(tmp_features).squeeze().cpu()#.numpy()
            print('Time : ' + str(time.monotonic() - cur_time))
        # for b in range(self._n_blocks):
        #    self._generated_queue.append(cur_blocks[(b * 512):((b+1)*512)])
        #    self._last_gen_block = self._n_blocks
        #if (not os.path.exists(self.trt_path)):
        #    print("Switching model to TRT")
        #    self._model = torch2trt(self._model, [tmp_features])
        #    print("Saving TRT model")
        #    torch.save(self._model.state_dict(), self.trt_path)
        # print(len(self._features))
        self.start_generation_thread_full()

    def generate_random(self, length=200):
        print('Generating random length ' + str(length))
        features = [torch.randn(1, length, 1).cuda()] * 7
        with torch.no_grad():
            audio = self._model(features)
        return audio.squeeze().detach().cpu().numpy()

    def generate(self, features):
        with torch.no_grad():
            audio = self._model(features)
        return audio.squeeze().detach().cpu().numpy()

    def start_generation_thread_full(self):
        self._thread = threading.Thread(target=self.generate_thread_full, args=(1,))
        self._thread.start()

    def signal_start_stream(self):
        # Update requested block
        self._last_request_block = 0
        # Signal the generation thread
        # self._generate_signal.set()
        
    def generate_block(self, block_id):
        cur_feats = self._features[:, block_id:(block_id + self._n_blocks + 1), :]
        # print(cur_feats.shape)
        with torch.no_grad():
            cur_audio = self._model(cur_feats).squeeze().detach().cpu().numpy()
        if self._last_val is not None:
            cur_audio[:512] = (self._last_val * np.linspace(1, 0, 512)) + (cur_audio[:512] * np.linspace(0, 1, 512))
        self._last_val = cur_audio[-512:]
        cur_audio = cur_audio[:-512]
        block_audio = []
        # print('CV ' + str(cv_id) + ' going active')
        for b in range(self._n_blocks):
            block_audio.append(cur_audio[(b * 512):((b+1)*512)])
        return block_audio
    
    def generate_thread_full(self, args):
        # First do a full generation
        while True:
            # We have generated the full queue
            if (self._last_gen_block + self._n_blocks + 1) > self._features.shape[1]:
                self.generate_end = True
                # print('Generated full')
                break
            # Generate a new block
            cur_audio = self.generate_block(self._last_gen_block)
            # Append blocks to queue
            for b in range(self._n_blocks):
                self._generated_queue.append(cur_audio[b])
            self._last_gen_block += self._n_blocks
        # Then switch to block-wise mode
        self.generate_thread_block(args)
    
    def generate_thread_block(self, args):
        self._generate_signal.clear()
        while True:
            # We have generated the full queue
            if (self._last_gen_block + self._n_blocks + 1) > self._features.shape[1]:
                self._generate_end = True
                # print('Generate thread going to sleep')
                self._generate_signal.wait()
            # Waking up to generate
            if self._generate_signal.is_set():
                self._generate_signal.clear()
                self._last_gen_block = 0
            # Infer which block to generate
            # gen_block = (self.last_request_block // self._n_blocks) * self.n_blocks
            # gen_block += (self.block_lookahead * self._n_blocks)
            gen_block = self._last_gen_block
            if gen_block == 0:
                self._last_val = None
            else:
                self._last_val = self._generated_queue[gen_block]
            if gen_block + self._n_blocks > len(self._generated_queue):
                continue
            cur_audio = self.generate_block(self._last_gen_block)
            # Change blocks to queue
            for b in range(self._n_blocks):
                self._generated_queue[gen_block+b] = cur_audio[b]
            if gen_block + self._n_blocks < len(self._generated_queue):
                n_block = self._generated_queue[gen_block + self._n_blocks]
                self._generated_queue[gen_block + self._n_blocks] = (self._last_val * np.linspace(1, 0, 512)) + (n_block * np.linspace(0, 1, 512))
            #print('Finished update from ' + str(gen_block) + ' to ' + str(gen_block + self._n_blocks))
            self._last_gen_block += self._n_blocks
                          
    def request_block_direct(self, block_idx):
        print('Request block : ' + str(block_idx))
        print(len(self._features))
        self._last_request_block = block_idx
        if block_idx + self._n_blocks > self._features.shape[1]:
            return None
        if block_idx % self._n_blocks == 0:
            print('Need next block')
            self._current_chunk = self.generate_block(block_idx)
            print('Block generated')
        return self._current_chunk[block_idx % self._n_blocks]
    
    def request_block_threaded(self, block_idx):
        # print('Request block : ' + str(block_idx))
        # Update requested block
        self._last_request_block = block_idx
        # Signal the generation thread
        # self._generate_signal.set()
        # Check if we have ended
        if len(self._generated_queue) <= block_idx:
            return None
        return self._generated_queue[block_idx]

    def features_loading(self):
        wav_list = ['dce_synth_one_shot_bumper_G#min.wav', 'SH_FFX_123BPM_IMPACT_01.wav',
                    'FF_ET_whoosh_hit_little.wav', 'Afro_FX_Oneshot_Impact_3.wav']
        for wav in wav_list:
            if not os.path.exists("models/features_interp" + str(wav) + ".th"):
                y, sr = librosa.load("data/" + wav)
                features = spectral_features(y, sr)
                features = torch.tensor(features).unsqueeze(0).cuda().float()
                torch.save(features, "models/features_interp" + str(wav) + ".th")
        feats = []
        for wav in wav_list:
            ft = torch.load("models/features_interp" + str(wav) + ".th")
            feats.append(ft)
        # Create sounds list
        snd_list = [] * 4
        # print('CV ' + str(cv_id) + ' going active')
        min_size = np.inf
        for i in range(3):
            snd_list.append(feats[i])
            if feats[i].shape[1] < min_size:
                min_size = feats[i].shape[1]
                # Crop to the min size
        for i in range(len(snd_list)):
            snd_list[i] = snd_list[i][:, :min_size, :]
        self._features_list = snd_list

    def interp_duo(self, cv_list):
        # Simulate CVs
        # cv_list = [random.sample(range(-4, 4), 1)[0]] * 4
        cv_list = [(x + 4) / 8 for x in cv_list]
        print(cv_list)
        snd_1 = self._features_list[0]
        snd_2 = self._features_list[1]
        # Run through CV values
        # TODO: cv1 = rms [0], cv2 = flatness [3], cv3 = centroid [5], ccv4 = pitch [6]
        feats_list = [0, 3, 5, 6]
        x_interp = snd_1.clone()
        for i, alpha in zip(feats_list, cv_list):
            x_interp[:, :, i] = (1 - alpha) * snd_2[:, :, i] + alpha * snd_1[:, :, i]
        self._features = x_interp
        print(torch.mean(self._features, dim=(0, 1)))
        print('End of interpolate')
        self._generate_signal.set()

    def interp_trio(self, cv_list):
        # Simulate CVs
        # cv_list = [random.sample(range(-4, 4), 1)[0]] * 4
        cv_list = [(x + 4) / 8 for x in cv_list]
        cv_sum = sum(cv_list)
        if abs(2 - cv_sum) < 0.1:
            cv_list = [1, 0, 0, 0]
        print(cv_list)
        # Run through CV values
        interp = torch.zeros_like(self._features_list[0])
        for i, snd in enumerate(self._features_list):
            interp += snd * cv_list[i] / cv_sum
        self._features = interp
        print('End of interpolate')
        self._generate_signal.set()
        
    def interp_final(self, cv_control, cv3, cv4, cv5):
        print('Interpolating sounds')
        print(cv_control)
        print(cv3)
        print(cv4)
        print(cv5)
        alpha = (cv_control + 4) / 8
        # Run through CV values
        interp = (1 - alpha) * self._features_list[0] + (alpha * self._features_list[1])
        interp[:, :, 2] = interp[:, :, 2] * torch.tensor(cv3).unsqueeze(0).cuda()
        interp[:, :, 3] = interp[:, :, 3] * torch.tensor(cv4).unsqueeze(0).cuda()
        interp[:, :, 4] = interp[:, :, 4] * torch.tensor(cv5).unsqueeze(0).cuda()
        self._features = interp
        print('End of interpolate')
        self._generate_signal.set()
        


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


