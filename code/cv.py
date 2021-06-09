#!/usr/bin/env python3
"""
 ~ Neurorack project ~
 CV : Allows to interact with the CV channels
 
 This file contains the main interaction with Control Voltage (CV) channels
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.
"""

import time
from ads1015 import ADS1015
from parallel import ProcessInput
from multiprocessing import Event
import concurrent.futures
import Jetson.GPIO as GPIO
import matplotlib.pyplot as plt
import numpy as np


class CVChannels(ProcessInput):
    """
        The CV class allows to handle reading the Control Voltage (CV) inputs.
        It is based on the ProcessInput system for multiprocessing
    """

    def __init__(self,
                 callback: callable,
                 i2c_addr=None,
                 channels=None):
        """
            Constructor - Creates a new instance of the CV class.
            Parameters:
                callback:   [callable]
                            Outside function to call on CV event
                i2c_addr:   [list], optional
                            List of I2C addresses to find mapped CVs
                channels:   [list], optional
                            List of channel references to read
        """
        super().__init__('cv')
        # Set signaling
        if channels is None:
            channels = ['in0/ref', 'in1/ref', 'in2/ref']
        if i2c_addr is None:
            i2c_addr = [0x48, 0x49]
        self._callback = callback
        self._signal = Event()
        # Configure I2C addresses and channels
        self._i2c_addresses = i2c_addr
        self._channels = channels
        self._cvs = []
        for address in i2c_addr:
            c = ADS1015(address)
            c.set_mode('single')
            c.set_programmable_gain(2.048)
            c.set_sample_rate(16000)
            self._cvs.append(c)
        self._ref = self._cvs[0].get_reference_voltage()
        print("Initialized CVs with reference voltage: {:6.3f}v \n".format(self._ref))
        self._cv_type = ["gate", "gate", "cv", "cv", "cv", "cv"]
        self._buffer = 10
        self._eps = 1
        self._gate_time = 0.1
        self._rate = 3300
        self._samples = 301
        self._plot = 1000

    # def irq_detect(self, channel):  # TODO: does not work.
    #     print('aaaaahaaahahahahahahah')

    def handle_gate(self, cv_id, value, state):
        cur_state = state['cv'][cv_id]
        cur_time = time.monotonic()
        if cur_state == 0:
            if value > self._ref + self._eps:
                state['cv'][cv_id] = cur_time
                self._callback("gate", cv_id, value)
        else:
            elapsed_time = cur_time - state['cv'][cv_id]
            if (value < self._ref + self._eps) and (elapsed_time > self._gate_time):
                state['cv'][cv_id] = 0

    def handle_cv(self, cv_id, value, buffer, state):
        # buffer.append(value)
        if len(buffer) == self._buffer:
            print('Buffer send from ' + str(cv_id))
            print(buffer)
            state['buffer'][cv_id] = buffer.copy()
            buffer.clear()
        #if len(plot[cv_id % 3]) == self._plot:
        #    np.save("plot_" + str(cv_id) + ".npy", plot[cv_id % 3])
        #    print('plot on ' + str(cv_id))
        #if (abs(state['cv'][cv_id] - value) > 0.1):
        #    self._callback("cv", cv_id, value)

    def update_line(self, hl, new_data):
        hl.set_xdata(np.append(hl.get_xdata(), new_data))
        hl.set_ydata(np.append(hl.get_ydata(), new_data))
        plt.draw()

    def thread_read(self, cv, cv_full_id, state):
        buffer = []
        for i in range(3):
            buffer.append([])
        # plot_points = []
        # for i in range(3):
        #     plot_points.append([])
        sample_interval = 1.0 / self._rate
        start = time.monotonic()
        # time_next_sample = start + sample_interval
        while True:
            c = 0
            for chan in self._channels:
                cv_id = (cv_full_id * 3) + c
                if self._cv_type[cv_id] == "gate":
                    value = cv.get_compensated_voltage(channel=chan, reference_voltage=self._ref)
                    self.handle_gate(cv_id, value, state)
                if self._cv_type[cv_id] == "cv":
                    #while time.monotonic() < time_next_sample:
                    #    pass
                    #time_next_sample = time.monotonic() + sample_interval
                    value = cv.get_compensated_voltage(channel=chan, reference_voltage=self._ref)
                    # Right now just append value to buffer
                    buffer[cv_id % 3].append(value)
                    self.handle_cv(cv_id, value, buffer[cv_id % 3], state)
                    state['cv'][cv_id] = value
                c += 1

    def read_loop(self, state):
        with concurrent.futures.ThreadPoolExecutor(max_workers=(len(self._cvs) * len(self._channels))) as executor:
                cur_v = 0
                futures_cv = []
                for cv in self._cvs:
                    futures_cv.append(executor.submit(self.thread_read, cv=cv, cv_full_id=cur_v, state=state))
                    cur_v += 1

                for futures_cv in concurrent.futures.as_completed(futures_cv):
                    futures_cv.result()

    def callback(self, state, queue, delay=0.001):
        """
            Function for reading the current CV values.
            Also updates the shared memory (state) with all CV values
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
                delay:      [int], optional
                            Specifies the wait delay between read operations [default: 0.001s]
        """
        #vals = self.read(state)
        c_time = time.time()
        try:
            self.read_loop(state)
            #self.read0(state)
            #while True:
            #    vals = self.read(state)
            #    c_time = time.time()
            #    time.sleep(delay)
        except KeyboardInterrupt:
            pass

    # def adafruit_example():
    #     # Data collection setup
    #     RATE = 3300
    #     SAMPLES = 1000
    #     # Create the I2C bus with a fast frequency
    #     i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
    #     # Create the ADC object using the I2C bus
    #     ads = ADS.ADS1015(i2c)
    #     # Create single-ended input on channel 0
    #     chan0 = AnalogIn(ads, ADS.P0)
    #     # ADC Configuration
    #     ads.mode = Mode.CONTINUOUS
    #     ads.data_rate = RATE
    #     # First ADC channel read in continuous mode configures device
    #     # and waits 2 conversion cycles
    #     _ = chan0.value
    #     sample_interval = 1.0 / ads.data_rate
    #     repeats = 0
    #     skips = 0
    #     data = [None] * SAMPLES
    #     start = time.monotonic()
    #     time_next_sample = start + sample_interval
    #     # Read the same channel over and over
    #     for i in range(SAMPLES):
    #         # !
    #         # !
    #         # Wait for expected conversion finish time
    #         while time.monotonic() < (time_next_sample):
    #             pass
    #         # Read conversion value for ADC channel
    #         data[i] = chan0.value
    #         # Loop timing
    #         time_last_sample = time.monotonic()
    #         time_next_sample = time_next_sample + sample_interval
    #         if time_last_sample > (time_next_sample + sample_interval):
    #             skips += 1
    #             time_next_sample = time.monotonic() + sample_interval
    #         # Detect repeated values due to over polling
    #         if data[i] == data[i - 1]:
    #             repeats += 1
    #     end = time.monotonic()
    #     total_time = end - start
    #     rate_reported = SAMPLES / total_time
    #     rate_actual = (SAMPLES - repeats) / total_time
    #     # NOTE: leave input floating to pickup some random noise
    #     #       This cannot estimate conversion rates higher than polling rate
    #     print("Took {:5.3f} s to acquire {:d} samples.".format(total_time, SAMPLES))
    #     print("")
    #     print("Configured:")
    #     print("    Requested       = {:5d}    sps".format(RATE))
    #     print("    Reported        = {:5d}    sps".format(ads.data_rate))
    #     print("")
    #     print("Actual:")
    #     print("    Polling Rate    = {:8.2f} sps".format(rate_reported))
    #     print("                      {:9.2%}".format(rate_reported / RATE))
    #     print("    Skipped         = {:5d}".format(skips))
    #     print("    Repeats         = {:5d}".format(repeats))
    #     print("    Conversion Rate = {:8.2f} sps   (estimated)".format(rate_actual))


if __name__ == "__main__":
    cv = CVChannels(None)
    cv.callback({'cv':[0, 0, 0, 0, 0, 0]}, None)
    #cv.read()
