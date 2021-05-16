"""

 ~ Neurorack project ~
 Screen : Main class for handling the LCD SPI Display
 
 This file contains the main process for using the LCD display.
 
 Author               : Philippe Esling, Ninon Devis, Martin Vert
                        <{esling, devis}@ircam.fr>

"""

import time
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from parallel import ProcessInput
from graphics.utils import get_resized_image
from stats import Stats

SCREEN_MODE_INIT = 0
SCREEN_MODE_MAIN = 1
SCREEN_MODE_MENU = 2

class Screen(ProcessInput):
    '''
        The screen class allows to handle an LCD SPI Display
        It is based on the ProcessInput system for multiprocessing
    '''
    
    def __init__(self, 
                 height: int = 240,
                 rotation: int = 180,
                 x_offset: int = 0,
                 y_offset: int = 80,
                 background:bool = True):
        '''
            Constructor - Initialize the screen object
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
        super().__init__('screen')
        # Configuration for CS and DC pins (these are PiTFT defaults)
        self._cs_pin = digitalio.DigitalInOut(board.CE0)
        self._dc_pin = digitalio.DigitalInOut(board.D25)
        self._reset_pin = digitalio.DigitalInOut(board.D24)
        # Store configuration
        self._baudrate = 24000000
        self._height = 240
        self._rotation = rotation
        self._x_offset = x_offset
        self._y_offset = y_offset
        # Setup SPI bus using hardware SPI:
        self._spi = board.SPI()
        # Create the 1.3", 1.54" ST7789 display object
        self._disp = st7789.ST7789(self._spi, height = self._height, 
                                  rotation = self._rotation, baudrate = self._baudrate,
                                  x_offset = self._x_offset, y_offset = self._y_offset, 
                                  cs = self._cs_pin, dc = self._dc_pin, rst = self._reset_pin)
        # Handle landscape mode.
        if self._disp.rotation % 180 == 90:
            self._height = self._disp.width
            self._width = self._disp.height
        else:
            self._width = self._disp.width
            self._height = self._disp.height
        # Potentially set a background
        self._background = background
        # Object for system statistics
        self._stats = Stats()
        # Perform initial settings
        self.reset_screen()
        self.init_text_properties()
        self._mode = SCREEN_MODE_INIT

    def reset_screen(self):
        '''
            Reset screen with either a background image or just empty black 
        '''
        self._image = None
        if (self._background):
            self._bg_image = get_resized_image('data/acids.png')
            self._image = self._bg_image.copy()
        else:
            self._image = Image.new('RGB', (self._width, self._width))
        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)
        # Draw a black filled box to clear the image.
        if (not self._background):
            self._draw.rectangle((0, 0, self._width, self._height), outline=0, fill=(0, 0, 0))
        self._disp.image(self._image)

    def clean_screen(self):
        '''
            Clean screen with image or just empty black 
        '''
        if (self._background):
            self._image = self._bg_image.copy()
        else:
            self._image = Image.new('RGB', (self._width, self._width))
        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)

    def init_text_properties(self):
        '''
            Init the global text properties (shared across )
        '''
        # Define some constants to allow easy positioning of text.
        self.padding = -2
        self.x_text = 0
        # Load a TTF font (needs to be in same directory as script)
        self.font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
        self.font_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)

    def startup_animation(self):
        header = 'Neurorack'
        head_f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        version = '0.01'
        v_f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
        for i in range(20):
            self.clean_screen()
            c = int((255.0 * i) / 20)
            self._draw.text((55, int(self._height / 4)), header, align='center', font = head_f, fill=(c,c,c))
            self._draw.text((95, int(self._height / 4) + 28), 'v.' + version, align='center', font = v_f, fill=(c,c,c))
            # Display image.
            self._disp.image(self._image)
            time.sleep(.025)
        time.sleep(0.5)

    def draw_cvs(self, state, y):
        cv_vals = state['cv']
        
    def callback(self, state, queue):
        # Begin screen startup animation
        self.startup_animation()
        self._mode = SCREEN_MODE_MAIN
        # Perform display loop
        while True:
            self.clean_screen()
            cur_stats = self._stats.retrieve_stats()
            # Write four lines of text.
            y = self.padding
            for s in cur_stats:
                self._draw.text((self.x_text, y), s, font = self.font, fill="#FFFFFF")
                y += self.font.getsize(s)[1]
            self._draw.text((self.x_text, y), str(state['rotary']), font = self.font_big, fill="#FF0000")
            self._draw_cvs(state, y)
            # Display image.
            self._disp.image(self._image)
            time.sleep(.02)

if __name__ == '__main__':
    screen = Screen()
    screen.callback({'rotary':0}, None)
