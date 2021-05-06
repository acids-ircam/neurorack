import time
import Jetson.GPIO as GPIO
from parallel import InterruptInput

led_pin = 12  # Board pin 12
but_pin = 18  # Board pin 18

class Button(InterruptInput):
    base_pin = 11

    def __init__(self):
        # Pin Setup:
        #GPIO.cleanup() 
        GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
        GPIO.setup(self.base_pin, GPIO.IN)  # button pin set as input
        
    def callback(self):
        while True:
            print("Waiting for button event")
            value = GPIO.input(self.base_pin)
            print(value)
            GPIO.wait_for_edge(self.base_pin, GPIO.RISING)
            #GPIO.add_event_detect(but_pin, GPIO.FALLING, callback=blink, bouncetime=10)
            # event received when button pressed
            print("Button Pressed!")
            value = GPIO.input(self.base_pin)
            print(value)
            time.sleep(1)
            
    def clean(self):
        GPIO.cleanup()  # cleanup all GPIOs

if __name__ == '__main__':
    button = Button()
    button.callback()

    
