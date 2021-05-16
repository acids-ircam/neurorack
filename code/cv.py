#!/usr/bin/env python3
"""

 ~ Neurorack project ~
 CV : Allows to interact with the CV channels
 
 This file contains the main interaction with Control Voltage (CV) channels
 
 Author               : Philippe Esling, Ninon Devis, Martin Vert
                        <{esling, devis}@ircam.fr>

"""

import time
from ads1015 import ADS1015
from parallel import ProcessInput

class CVChannels(ProcessInput):
    '''
        The CV class allows to handle reading the Control Voltage (CV) inputs.
        It is based on the ProcessInput system for multiprocessing
    '''

    def __init__(self, 
            callback: callable,
            signal: any = None,
            i2c_addr: list = [0x48, 0x49],
            channels: list = ['in0/ref', 'in1/ref', 'in2/ref']):
        '''
            Constructor - Creates a new instance of the CV class.
            Parameters:
                callbak:    [callable]
                            Outside function to call on button push
                signal:     [any], optional 
                            Eventual signal to wake up a thread waiting on button
                i2c_addr:   [list], optional
                            List of I2C addresses to find mapped CVs
                channels:   [list], optional
                            List of channel references to read
        '''
        super().__init__('cv')
        self._callback = callback
        self._signal = signal
        self._i2c_addresses = i2c_addr
        self._cvs = []
        for address in i2c_addr:
            c = ADS1015(address)
            c.set_mode('single')
            c.set_programmable_gain(2.048)
            c.set_sample_rate(16000)
            self._cvs.append(c)
        self._ref = self._cvs[0].get_reference_voltage()
        print("Initialized CVs with reference voltage: {:6.3f}v \n".format(self._ref))

    def read(self, state):
        '''
            Function for reading the current CV values.
            Also updates the shared memory (state) with all CV values
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
        '''
        values = [None] * (len(self._cvs) * len(self._channels))
        cur_v = 0
        for cv in self._cvs:
            for chan in self._channels:
                values[cur_v] = int(cv.get_compensated_voltage(channel=chan, reference_voltage=self._ref))
                state['cv'][cur_v] = values[cur_v]
                cur_v += 1
        return values

    def callback(self, state, queue, delay=0.001):
        '''
            Function for reading the current CV values.
            Also updates the shared memory (state) with all CV values
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
                delay:      [int], optional
                            Specifies the wait delay between read operations [default: 0.001s]
        '''
        vals = self.read(state)
        c_time = time.time()
        try:
            while True:
                vals = self.read(state)
                c_time = time.time()
                time.sleep(delay)
        except KeyboardInterrupt:
            pass
        
    def adafruit_example():
        # Data collection setup
        RATE = 3300
        SAMPLES = 1000
        # Create the I2C bus with a fast frequency
        i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
        # Create the ADC object using the I2C bus
        ads = ADS.ADS1015(i2c)
        # Create single-ended input on channel 0
        chan0 = AnalogIn(ads, ADS.P0)
        # ADC Configuration
        ads.mode = Mode.CONTINUOUS
        ads.data_rate = RATE
        # First ADC channel read in continuous mode configures device
        # and waits 2 conversion cycles
        _ = chan0.value
        sample_interval = 1.0 / ads.data_rate
        repeats = 0
        skips = 0
        data = [None] * SAMPLES
        start = time.monotonic()
        time_next_sample = start + sample_interval
        # Read the same channel over and over
        for i in range(SAMPLES):
            # !
            # !
            # Wait for expected conversion finish time
            while time.monotonic() < (time_next_sample):
                pass
            # Read conversion value for ADC channel
            data[i] = chan0.value
            # Loop timing
            time_last_sample = time.monotonic()
            time_next_sample = time_next_sample + sample_interval
            if time_last_sample > (time_next_sample + sample_interval):
                skips += 1
                time_next_sample = time.monotonic() + sample_interval
            # Detect repeated values due to over polling
            if data[i] == data[i - 1]:
                repeats += 1
        end = time.monotonic()
        total_time = end - start
        rate_reported = SAMPLES / total_time
        rate_actual = (SAMPLES - repeats) / total_time
        # NOTE: leave input floating to pickup some random noise
        #       This cannot estimate conversion rates higher than polling rate
        print("Took {:5.3f} s to acquire {:d} samples.".format(total_time, SAMPLES))
        print("")
        print("Configured:")
        print("    Requested       = {:5d}    sps".format(RATE))
        print("    Reported        = {:5d}    sps".format(ads.data_rate))
        print("")
        print("Actual:")
        print("    Polling Rate    = {:8.2f} sps".format(rate_reported))
        print("                      {:9.2%}".format(rate_reported / RATE))
        print("    Skipped         = {:5d}".format(skips))
        print("    Repeats         = {:5d}".format(repeats))
        print("    Conversion Rate = {:8.2f} sps   (estimated)".format(rate_actual))

if __name__ == "__main__":
    cv = CVChannels()
    cv.read_loop()
