import time
import torch
# Testing DDSP
print('Putting model on CUDA')
model = torch.jit.load("/home/martin/Desktop/ddsp_pytorch/models/ddsp_demo_pretrained.ts").cuda()
print('Flatten')
#model = model.flatten_parameters()
print('Pitch and loudness to CUDA')
pitch = torch.randn(1, 2, 1).cuda()
loudness = torch.randn(1, 2, 1).cuda()
for i in range(5):
    print('Forwaaaaaaaaaard')
    cur = time.time()
    with torch.no_grad():
        audio = model(pitch, loudness)
    print(time.time() - cur)
