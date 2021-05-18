"""

 ~ Neurorack project ~
 Rotary : Allows to interact with the rotary encoder
 
 This file contains the main interaction with the rotary encoder
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

import time
import colorsys
import ioexpander as io
import Jetson.GPIO as GPIO
from parallel import ProcessInput

class Rotary(ProcessInput):
    '''
        The rotary class allows to handle reading the rotary inputs.
        It is based on the ProcessInput system for multiprocessing
    '''

    def __init__(self,
            callback: callable,
            signal: any = None,
            i2c_addr: int = 0x0F,
            rgb_pins: list = [1, 7, 2],
            enc_pins: list = [12, 3, 11],
            brightness: float = 0.5):
        '''
            Constructor - Creates a new instance of the Rotary class.
            Parameters:
                callbak:    [callable]
                            Outside function to call on button push
                signal:     [any], optional 
                            Eventual signal to wake up a thread waiting on button
                i2c_addr:   [int], optional
                            Integer of I2C addresses to find mapped rotary [default: 0x0F]
                rgb_pins:   [list], optional 
                            LED output pins [default: 1, 7, 2]
                enc_pins:   [list], optional 
                            Rotary encoder pins
                brightness: [float], optional
                            Maximum fraction of LED will be on
        '''
        super().__init__('rotary')
        self._i2c_address = i2c_addr
        self._rgb_pins = rgb_pins
        self._enc_pins = enc_pins
        self._brightness = brightness
        # Period to get 0-255 range in brightness
        self._period = int(255.0 / brightness)
        self._ioe = io.IOE(i2c_addr=self._i2c_address, interrupt_pin=18)
        # Swap the interrupt pin for the Rotary Encoder breakout
        if self._i2c_address == 0x0F:
            self._ioe.enable_interrupt_out(pin_swap=True)
        self._ioe.setup_rotary_encoder(1, self._enc_pins[0], self._enc_pins[1], pin_c=self._enc_pins[2])
        self._ioe.enable_interrupt_out()
        self._ioe.set_pwm_period(self._period) 
        self._ioe.clear_interrupt()
        # PWM as fast as we can to avoid LED flicker
        self._ioe.set_pwm_control(divider=2) 
        # Set RGB modes
        self._ioe.set_mode(self._rgb_pins[0], io.PWM, invert=True)
        self._ioe.set_mode(self._rgb_pins[1], io.PWM, invert=True)
        self._ioe.set_mode(self._rgb_pins[2], io.PWM, invert=True)
        # Current position value
        self._position = 0
        # Current RGB values
        self._r, self._g, self._b, = 0, 0, 0

    def startup_animation(self):
        '''
            Function for performing the init animation of the rotary knob
        '''
        for i in range(360):
            h = i / 360.0
            self._r, self._g, self._b = [int(i * self._period * self._brightness) for i in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            self._ioe.output(self._rgb_pins[0], self._r)
            self._ioe.output(self._rgb_pins[1], self._g)
            self._ioe.output(self._rgb_pins[2], self._b)           
            time.sleep(0.1 / 360.0)
        
    def callback(self, state, queue):
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
        #self.startup_animation()
        while True:
            if self._ioe.get_interrupt():
                print('Yaaaaay')
                self._ioe.clear_interrupt()
            new_pos = self._ioe.read_rotary_encoder(1)
            if (new_pos == self._position):
                time.sleep(1.0 / 30)
                continue
            self._position = new_pos
            state['rotary'] = self._position
            h = (self._position % 360) / 360.0
            # Compute new RGB values
            self._r, self._g, self._b = [int(c * self._period * self._brightness) for c in colorsys.hsv_to_rgb(h, 1.0, 1.0)]
            self._ioe.output(self._rgb_pins[0], self._r)
            self._ioe.output(self._rgb_pins[1], self._g)
            self._ioe.output(self._rgb_pins[2], self._b)
            print('Rotary moved - %i - %i,%i,%i'%(self._position, self._r, self._g, self._b))
            self.ioe.clear_interrupt()
            
    def test(self, channel: int):
        print('EAAYEAYRIUYAZIRUYRIAYIUR')
        
if __name__ == '__main__':
    rotary = Rotary(None)
    rotary.callback({'rotary':0}, None)
