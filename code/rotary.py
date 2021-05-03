#!/usr/bin/env python3
import time
import colorsys
import ioexpander as io

class Rotary():
    I2C_ADDR = 0x0F  # 0x0F for the encoder breakout
    # LED output pins
    PIN_RED, PIN_GREEN, PIN_BLUE = 1, 7, 2
    # Rotary encoder pins
    POT_ENC_A, POT_ENC_B, POT_ENC_C = 12, 3, 11
    # Maximum fraction of LED will be on
    BRIGHTNESS = 0.5
    # Period to get 0-255 range in brightness
    PERIOD = int(255 / BRIGHTNESS)

    def __init__(self):
        self.ioe = io.IOE(i2c_addr=self.I2C_ADDR, interrupt_pin=8)
        # Swap the interrupt pin for the Rotary Encoder breakout
        if self.I2C_ADDR == 0x0F:
            self.ioe.enable_interrupt_out(pin_swap=True)
        self.ioe.setup_rotary_encoder(1, self.POT_ENC_A, self.POT_ENC_B, pin_c=self.POT_ENC_C)
        self.ioe.set_pwm_period(self.PERIOD)
        # PWM as fast as we can to avoid LED flicker
        self.ioe.set_pwm_control(divider=2) 
        # Set RGB modes
        self.ioe.set_mode(self.PIN_RED, io.PWM, invert=True)
        self.ioe.set_mode(self.PIN_GREEN, io.PWM, invert=True)
        self.ioe.set_mode(self.PIN_BLUE, io.PWM, invert=True)
        self.count = 0
        self.r, self.g, self.b, = 0, 0, 0

    def callback(self, args):
        while True:
            #if self.ioe.get_interrupt():
            count = self.ioe.read_rotary_encoder(1)
            if (count == self.count):
                time.sleep(1.0 / 30)
                continue
            self.count = count
            #ioe.clear_interrupt()
            h = (self.count % 360) / 360.0
            # Compute new RGB values
            r, g, b = [int(c * self.PERIOD * self.BRIGHTNESS) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            self.ioe.output(self.PIN_RED, r)
            self.ioe.output(self.PIN_GREEN, g)
            self.ioe.output(self.PIN_BLUE, b)
            print(self.count, r, g, b)
            
if __name__ == '__main__':
    #import Jetson.GPIO as gpio
    #gpio.setwarnings(False)
    #gpio.setmode(gpio.BOARD)
    #gpio.setup(24, gpio.IN)
    #gpio.add_event_detect(24, gpio.BOTH, callback=activate_reading)
    rotary = Rotary()
    rotary.callback(None)
