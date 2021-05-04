import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from base import ProcessInput
from stats import Stats

class Screen(ProcessInput):
    # Configuration for CS and DC pins (these are PiTFT defaults):
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)
    # Config for display baudrate (default max is 24mhz):
    BAUDRATE = 24000000
    # Base configuration
    height = 240
    rotation = 180
    x_offset = 0
    y_offset = 80

    """
    Initialize screen function
    """
    def __init__(self, background=True):
        super().__init__('screen')
        # Setup SPI bus using hardware SPI:
        self.spi = board.SPI()
        print(self.height)
        # 1.3", 1.54" ST7789
        self.disp = st7789.ST7789(self.spi, height = self.height, rotation = self.rotation, x_offset = self.x_offset, y_offset = self.y_offset, cs = self.cs_pin, dc = self.dc_pin, rst = self.reset_pin, baudrate = self.BAUDRATE)
        # Handle landscape mode.
        if self.disp.rotation % 180 == 90:
            self.height = self.disp.width
            self.width = self.disp.height
        else:
            self.width = self.disp.width
            self.height = self.disp.height
        # Potentially set a background
        self.background = background
        # Object for system statistics
        self.stats = Stats()
        # Perform initial settings
        self.reset_screen()
        self.init_text_properties()

    """
    Reset screen with either 
    """
    def reset_screen(self):
        self.image = None
        if (self.background):
            self.bg_image = self.get_screen_image('data/acids.png')
            self.image = self.bg_image.copy()
        else:
            self.image = Image.new('RGB', (self.width, self.width))
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
        # Draw a black filled box to clear the image.
        if (not self.background):
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        self.disp.image(self.image)

    """
    Clean screen before filling
    """
    def clean_screen(self):
        if (self.background):
            self.image = self.bg_image.copy()
        else:
            self.image = Image.new('RGB', (self.width, self.width))
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
          
    """
    Create an image that fits into screen properties
    """
    def get_screen_image(self, filename, ratio=0):
        image = Image.open(filename)
        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = self.width / self.height
        if screen_ratio < image_ratio:
            scaled_width = image.width * self.height // image.height
            scaled_height = self.height
        else:
            scaled_width = self.width
            scaled_height = image.height * self.width // image.width
        if (ratio > 0):
            scaled_width = (scaled_width * ratio)
            scaled_height = (scaled_height * ratio)
            image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
            image = image.crop((0, 0, scaled_width, scaled_height))
            return image
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)
        # Crop and center the image
        x = scaled_width // 2 - self.width // 2
        y = scaled_height // 2 - self.height // 2
        image = image.crop((x, y, x + self.width, y + self.height))
        # Return image.
        return image

    def init_text_properties(self):
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
        cur_text = ''
        y = int(self.height / 4)
        x = 50
        for i in range(20):
            self.clean_screen()
            c = int((255.0 * i) / 20)
            self.draw.text((55, int(self.height / 4)), header, align='center', font = head_f, fill=(c,c,c))
            self.draw.text((95, int(self.height / 4) + 28), 'v.' + version, align='center', font = v_f, fill=(c,c,c))
            # Display image.
            self.disp.image(self.image)
            time.sleep(.025)
        time.sleep(0.5)

    def draw_cvs(self, state):
        cv_vals = state['cv']
        
    def callback(self, state, queue):
        # Begin screen startup animation
        self.startup_animation()
        # Perform display loop
        while True:
            self.clean_screen()
            cur_stats = self.stats.retrieve_stats()
            # Write four lines of text.
            y = self.padding
            for s in cur_stats:
                self.draw.text((self.x_text, y), s, font = self.font, fill="#FFFFFF")
                y += self.font.getsize(s)[1]
            self.draw.text((self.x_text, y), str(state['rotary']), font = self.font_big, fill="#FF0000")
            self.draw_cvs(state)
            # Display image.
            self.disp.image(self.image)
            time.sleep(.02)

if __name__ == '__main__':
    screen = Screen()
    screen.callback(None)
