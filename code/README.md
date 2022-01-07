# Neurorack // Python code

## Hardware libraries

* Screen [ST7789 library](https://github.com/pimoroni/st7789-python)
* Encoder [IOE library](https://github.com/pimoroni/ioe-python)
* Control voltage [ADS1015 library](https://github.com/pimoroni/ads1015-python)


## Software troubleshooting

* Install Pytorch from source or [NVIDIA wheels](https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-8-0-now-available/72048)
* Need to rebuild libtorch (C++) [from source](https://github.com/pytorch/pytorch/blob/master/docs/libtorch.rst]
* Need to rebuild [PureData from GitHub](https://github.com/pure-data/pure-data) (apt-get install is faulty)
* Installing [latest CUDA](https://www.seeedstudio.com/blog/2020/07/29/install-cuda-11-on-jetson-nano-and-xavier-nx/) on Jetson
* Fixing [Numba and LLVM install](https://github.com/jefflgaol/Install-Packages-Jetson-ARM-Family/issues/2)
* Fixing [Librosa install](https://learninone209186366.wordpress.com/2019/07/24/how-to-install-the-librosa-library-in-jetson-nano-or-aarch64-module/) (Warning: Replace with LLVM 10)

### Currently known issues

- Problem with latest Pip (waiting on them to resolve)
https://github.com/pypa/pip/issues/9617
- Problem with latest Numpy (waiting on them)

## Useful commands

Launching python with debugging info on ARM64
```shell
python -q -X faulthandler
```
