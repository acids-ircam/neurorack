"""

 ~ Neurorack project ~
 Button : Main class for a push button
 
 This file contains the code for the main class in the Neurorack
 
 Author               : Philippe Esling, Ninon Devis, Martin Vert
                        <{esling, devis}@ircam.fr>

"""
import time
import Jetson.GPIO as GPIO
from parallel import InterruptInput

class Button(InterruptInput):    
    '''
        The Button class implements interaction with GPIO push buttons. 
        It configures GPIO pins with a callback and asynchronous signal
        to wake up some external processes
    '''
    
    def __init__(self, 
            callback: callable,
            signal: any=None,
            pins: list=[11], 
            debounce: int=250):
        '''
            Constructor - Creates a new instance of the Navigation class.
            Parameters:
                callbak:    [callable]
                            Outside function to call on button push
                signal:     [any], optional 
                            Eventual signal to wake up a thread waiting on button
                pins:       [int], optional
                            Specify GPIO pins that connect buttons [default: 11]
                debounce:   [int], optional
                            Debounce time to prevent multiple firings [default: 250ms]
        '''
        self._pins = pins
        self._debounce = debounce
        self._callback = callback
        self._signal = signal
        GPIO.setwarnings(False)                                     
        GPIO.setmode(GPIO.BOARD)                                      
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN)    
            GPIO.add_event_detect(pin, GPIO.RISING, callback=self.callback, bouncetime=self._debounce)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self.callback_fall, bouncetime=self._debounce)
    
    def callback(self, channel: int):
        print("Button event - pushed")
        value = GPIO.input(channel)
        print(value)
        time.sleep(1)
    
    def callback_fall(self, channel: int):
        print("Button event - released")
        value = GPIO.input(channel)

    def __del__(self):
        '''
            Destructor - cleans up the GPIO.
        '''
        GPIO.cleanup()

if __name__ == '__main__':
    button = Button()
    button.callback()

    
