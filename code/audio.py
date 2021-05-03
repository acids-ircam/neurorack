import torch
import time
from pyo import *

# Check audio host APIs
#print("Audio host APIS:")
#pa_list_host_apis()
#pa_list_devices()
#print("Default input device: %i" % pa_get_default_input())
#print("Default output device: %i" % pa_get_default_output())

# Create audio server
s = Server(duplex=0)
s.setOutputDevice(1)
s.boot()

# Select amplitude
s.amp = 0.1
# Creates a source (white noise)
n = Noise()
# Sends the bass frequencies (below 1000 Hz) to the left
lp = ButLP(n).out()
# Sends the high frequencies (above 1000 Hz) to the right
hp = ButHP(n).out(1)
time.sleep(2)
# Testing DDSP
model = torch.jit.load("/home/martin/Desktop/ddsp_pytorch/models/ddsp_demo_pretrained.ts")
pitch = torch.randn(1, 200, 1)
loudness = torch.randn(1, 200, 1)
audio = model(pitch, loudness)
