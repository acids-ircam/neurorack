# Impact-Synth-Hardware based on the Jetson NANO dev kit in a EuroRack format

## Hardware libraries

* Screen: [https://github.com/pimoroni/st7789-python](ST7789)
* Encoder: [https://github.com/pimoroni/ioe-python](IOE)
* Control voltage: [https://github.com/pimoroni/ads1015-python](ADS1015)

## Software troubleshooting

* Install Pytorch from source or NVIDIA wheels [from forum](https://forums.developer.nvidia.com/t/pytorch-for-jetson-version-1-8-0-now-available/72048)
Need to rebuild libtorch (C++) from source - Instructions:
https://github.com/pytorch/pytorch/blob/master/docs/libtorch.rst
Need to rebuild PureData (apt-get install is faulty)
https://github.com/pure-data/pure-data
Installing latest CUDA
https://www.seeedstudio.com/blog/2020/07/29/install-cuda-11-on-jetson-nano-and-xavier-nx/
Fixing Numba and LLVM install
https://github.com/jefflgaol/Install-Packages-Jetson-ARM-Family/issues/2
Fixing Librosa install (WARN: Replace with LLVM 10)
https://learninone209186366.wordpress.com/2019/07/24/how-to-install-the-librosa-library-in-jetson-nano-or-aarch64-module/

Current known shitty issues
- Problem with latest Pip (waiting on them to resolve)
https://github.com/pypa/pip/issues/9617
- Problem with latest Numpy (waiting on them)

Useful command for debug ARM64
python -q -X faulthandler