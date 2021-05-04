#!/usr/bin/env python
import time
from ads1015 import ADS1015
from base import ProcessInput

class CVChannels(ProcessInput):
    i2c_addresses = [0x48, 0x49]
    channels = ['in0/ref', 'in1/ref', 'in2/ref']
    description = 'Reading ADC Channels'

    def __init__(self):
        super().__init__('cv')
        self.cv_0 = ADS1015(self.i2c_addresses[0])
        self.cv_1 = ADS1015(self.i2c_addresses[1])
        self.cvs = [self.cv_0]
        for c in self.cvs:
            c.set_mode('single')
            c.set_programmable_gain(2.048)
            c.set_sample_rate(16000)
        self.ref = self.cv_0.get_reference_voltage()
        print("Initialized CVs with reference voltage: {:6.3f}v \n".format(self.ref))

    def read(self, state):
        values = [None] * (len(self.cvs) * len(self.channels))
        cur_v = 0
        for cv in self.cvs:
            for chan in self.channels:
                values[cur_v] = int(cv.get_compensated_voltage(channel=chan, reference_voltage=self.ref))
                state['cv'][cur_v] = values[cur_v]
                cur_v += 1
        return values

    def callback(self, state, queue, delay=0.0001):
        prev_vals = self.read()
        prev_time = time.time()
        try:
            while True:
                vals = self.read(state)
                #sum = 0
                #for (v1, v2) in zip(vals, prev_vals):
                #    sum += abs(v1 - v2)
                #if (sum == 0):
                #    continue
                time.sleep(delay)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    cv = CVChannels()
    cv.read_loop()
