#!/usr/bin/env python
import time
from ads1015 import ADS1015

class CVChannels:
    i2c_addresses = [0x48, 0x49]
    channels = ['in0/ref', 'in1/ref', 'in2/ref']
    description = 'Reading ADC Channels'

    def __init__(self):
        self.cv_0 = ADS1015(self.i2c_addresses[0])
        self.cv_1 = ADS1015(self.i2c_addresses[1])
        self.cvs = [self.cv_0, self.cv_1]
        for c in self.cvs:
            c.set_mode('single')
            c.set_programmable_gain(2.048)
            c.set_sample_rate(1600)
        self.ref = self.cv_0.get_reference_voltage()
        print("Initialized CVs with reference voltage: {:6.3f}v \n".format(self.ref))

    def read(self):
        values = [None] * (len(self.cvs) * len(self.channels))
        cur_v = 0
        for cv in self.cvs:
            for chan in self.channels:
                values[cur_v] = int(cv.get_compensated_voltage(channel=chan, reference_voltage=self.ref) * 50) / 50.0
                cur_v += 1
        return values

    def read_loop(self, delay=0.1):
        prev_vals = self.read()
        try:
            while True:
                vals = self.read()
                sum = 0
                for (v1, v2) in zip(vals, prev_vals):
                    sum += abs(v1 - v2)
                if (sum == 0):
                    continue
                prev_vals = vals
                print(vals)
                time.sleep(delay)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    cv = CVChannels()
    cv.read_loop()
