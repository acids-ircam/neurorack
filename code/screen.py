"""

 ~ Neurorack project ~
 Screen : Main class for handling the LCD SPI Display
 
 This file contains the main process for using the LCD display.
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

import time
import board
import digitalio
import multiprocessing
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from parallel import ProcessInput
from graphics.utils import get_resized_image
from graphics.graphics import GraphicScene, TextGraphic, DynamicTextGraphic
from graphics.menu import Menu
from stats import Stats
from multiprocessing import Event
from config import config
from ctypes import c_char_p

class Screen(ProcessInput):
    '''
        The screen class allows to handle an LCD SPI Display
        It is based on the ProcessInput system for multiprocessing
    '''
    
    def __init__(self, 
                 callback: callable,
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
        # Setup button callback 
        self._callback = callback
        # Create our own event signal
        self._signal = Event()
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
        # Reset the screen rendering
        self.reset_screen()
        # Initialize text properties
        self.init_text_properties()
        # Set initial screen mode
        self._mode = config.screen.mode_init

    def reset_screen(self):
        '''
            Reset screen with either a background image or just empty black 
        '''
        # Create a new PIL image 
        self._image = Image.new('RGB', (self._width, self._width))
        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)
        if (self._background):
            self._bg_image = get_resized_image(config.screen.bg_image, self._width, self._height)
            self._image.paste(self._bg_image)
        else:
            # Draw a black filled box to clear the image.
            self._draw.rectangle((0, 0, self._width, self._height), outline=0, fill=(0, 0, 0))
        self._disp.image(self._image)

    def clean_screen(self):
        '''
            Clean screen with image or just empty black 
        '''
        if (self._background):
            self._image.paste(self._bg_image)
        else:
            self._draw.rectangle((0, 0, self._width, self._height), outline=0, fill=(0, 0, 0))
        self._ctx = {}
        self._ctx['draw'] = self._draw
        self._ctx['x'] = config.screen.main_x
        self._ctx['y'] = config.screen.padding

    def init_text_properties(self):
        '''
            Init the global text properties (shared across )
        '''
        # Load a TTF font (needs to be in same directory as script)
        self._font = ImageFont.truetype(config.text.font_main, config.text.size_main)
        self._font_big = ImageFont.truetype(config.text.font_main, config.text.size_big)
        self._font_large = ImageFont.truetype(config.text.font_main, config.text.size_large)
        
    def init_graphic_scenes(self, state):
        self._main_scene = GraphicScene(
            x = config.screen.main_x,
            y = config.screen.padding,
            absolute = True,
            elements = [DynamicTextGraphic(state['stats']['ip'], color=config.colors.white),
                        DynamicTextGraphic(state['stats']['cpu'], color=config.colors.white),
                        DynamicTextGraphic(state['stats']['memory'], color=config.colors.white),
                        DynamicTextGraphic(state['stats']['disk'], color=config.colors.white),
                        DynamicTextGraphic(state['stats']['temperature'], color=config.colors.white),
                        DynamicTextGraphic(state['rotary'], font=self._font_large, color=config.text.color_main)]
            )
        self._menu_scene = Menu(
            config_file = "./menu.yaml",
            x = config.screen.main_x,
            y = config.screen.padding,
            height = self._height,
            width = self._width,
            absolute = True)

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
        
    def perform_update(self, state):
        self._cur_stats = self._stats.retrieve_stats()
        print(state)
        state['stats']['ip'].value = self._cur_stats[0]
        state['stats']['cpu'].value = self._cur_stats[1]
        state['stats']['memory'].value =  self._cur_stats[2]
        state['stats']['disk'].value = self._cur_stats[3]
        state['stats']['temperature'].value = self._cur_stats[4]
        
    def button_callback(self):
        if (self._mode == config.screen.mode_main):
            self._mode = config.screen.mode_menu
        if (self._mode == config.screen.mode_menu):
            self._menu_scene.button_callback()
        
    def callback(self, state, queue):
        # Perform a first heavy update
        self.perform_update(state)
        # Initialize all graphic scenes
        self.init_graphic_scenes(state)
        # Begin screen startup animation
        # self.startup_animation()
        self._mode = config.screen.mode_main
        # Perform display loop
        while True:
            self._signal.wait(1.0)
            if (self._signal.is_set()):
                # The refresh comes from an external signal
                self._signal.clear()
            else:
                # Otherwise we can do heavy processing
                if (self._mode == config.screen.mode_main):
                    self.perform_update(state)
            self.clean_screen()
            # Write four lines of text.
            if (self._mode == config.screen.mode_main):
                self._main_scene.render(self._ctx)
            elif (self._mode == config.screen.mode_menu):
                self._menu_scene.render(self._ctx)
            # Display image.
            self._disp.image(self._image)

if __name__ == '__main__':
    screen = Screen(None)
    screen.callback({'rotary':0, 'cv':0}, None)
