"""

 ~ Neurorack project ~
 Button : Main class for a push button
 
 This file contains the code for the main class in the Neurorack
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""
import time
import Jetson.GPIO as GPIO
from parallel import InterruptInput
from multiprocessing import Event

class Button(InterruptInput):    
    '''
        The Button class implements interaction with GPIO push buttons. 
        It configures GPIO pins with a callback and asynchronous signal
        to wake up some external processes
    '''
    
    def __init__(self, 
            callback: callable,
            pins: list=[11], 
            debounce: int=250):
        '''
            Constructor - Creates a new instance of the Navigation class.
            Parameters:
                callback:   [callable]
                            Outside function to call on button push
                pins:       [int], optional
                            Specify GPIO pins that connect buttons [default: 11]
                debounce:   [int], optional
                            Debounce time to prevent multiple firings [default: 250ms]
        '''
        self._pins = pins
        self._debounce = debounce
        # Setup button callback 
        self._callback = callback
        # Create our own event signal
        self._signal = Event()
        GPIO.setwarnings(False)                                     
        GPIO.setmode(GPIO.TEGRA_SOC)   
        board_to_tegra = {
            k: list(GPIO.gpio_pin_data.get_data()[-1]['TEGRA_SOC'].keys())[i] 
            for i, k in enumerate(GPIO.gpio_pin_data.get_data()[-1]['BOARD'])}                                   
        for pin in self._pins:
            tegra_soc_name = board_to_tegra[pin]
            GPIO.setup(tegra_soc_name, GPIO.IN)    
            GPIO.add_event_detect(tegra_soc_name, GPIO.FALLING, callback=self.callback_event, bouncetime=self._debounce)
    
    def callback_event(self, channel: int):
        # print("Button event - pushed")
        value = GPIO.input(channel)
        if self._callback is not None:
            self._callback(channel, value)
            
    def callback(self, state, queue, delay=0.001):
        while not self._signal.is_set():
            self._signal.wait()

    def __del__(self):
        '''
            Destructor - cleans up the GPIO.
        '''
        GPIO.cleanup()

if __name__ == '__main__':
    button = Button(None)
    button.callback(None, None)

    
