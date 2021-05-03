import torch

model = torch.jit.load("ddsp_pretrained_mytraining.ts")

pitch = torch.randn(1, 200, 1)
loudness = torch.randn(1, 200, 1)

audio = model(pitch, loudness)
