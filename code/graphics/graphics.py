"""

 ~ Neurorack project ~
 Graphics : Set of classes for graphical objects
 
 This file defines the main operations for the graphical objects.
 The functions here will be used for the LCD display.
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

import multiprocessing
from config import config
from .utils import get_resized_image
from PIL import ImageFont

class Graphic():
    
    def __init__(self, 
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False):
        '''
            Constructor. Creates a new instance of the ContollerMenu class. 
            Paramters: 
                x:          [int]
                            Absolute X position
                y:          [int]
                            Absolute Y position
                absolute:   [bool]
                            Draw in absolute position
        '''
        self._x = x
        self._y = y
        self._absolute = absolute

    def load(self, ctx=None):
        ''' Perform any necessary pre-loading actions '''
        raise NotImplementedError
        
    def render(self, ctx=None):
        ''' Perform graphic rendering based on context '''
        raise NotImplementedError
        
    def get_height(self, ctx=None):
        ''' Get height of the graphic element '''
        raise NotImplementedError
        
    def get_width(self, ctx=None):
        ''' Get width of the graphic element '''
        raise NotImplementedError

class GraphicScene(Graphic):
    
    def __init__(self,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 elements: list = []):
        super().__init__(x, y, absolute)
        self._elements = elements
        
    def add(self, e: Graphic):
        self._elements.append(e)
        
    def load(self, ctx=None):
        for e in self._elements:
            ctx = e.load(ctx)
        return ctx

    def render(self, ctx=None):
        if (self._absolute):
            ctx["x"], ctx["y"] = self._x, self._y
        for e in self._elements:
            ctx = e.render(ctx)
        return ctx
            
    def get_height(self):
        height = 0
        for e in self._elements:
            height += e.get_height()
        return height
            
    def get_width(self):
        width = 0
        for e in self._elements:
            width += e.get_width()
        return width
    
class ScrollableGraphicScene(GraphicScene):
    
    def __init__(self,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 selectable: bool = True,
                 height:int = config.screen.height, 
                 width:int = config.screen.width,
                 padding:int = 5,
                 elements: list = []):
        super().__init__(x, y, absolute, elements)
        self._elements = elements
        # Scrolling properties
        self._scroll_start = 0
        self._scroll_down = False
        self._scroll_up = False
        # Index properties
        self._selected_index = -1
        self._max_index = -1
        # General size
        self._height = height
        self._width = width
        self._padding = 5
    
    def render(self, ctx):
        """
            Draws a menu based on the items contained in Display.Items. Setting Display.Items will implicitely 
            call this method, so it should only be necessary to call this explicitely if the display has been 
            changed by the user since it was last drawn. 
            Parameters:
                items:      list(str)
                            Optional. A list of items to be used for the menu. If not specified, the list currently 
                            contained in Display.Items will be used. If specified, the supplied list will be stored in 
                            Display.Items. 
        """
        self._scroll_down = False
        self._scroll_up = self._scroll_start > 0
        idx = self._scroll_start
        while idx < len(self._elements):
            item = self._elements[idx]
            height = item.get_height()
            if ctx["y"] + height > self._height: 
                self._scroll_down = True
                break
            ctx = item.render(ctx)
            ctx["y"] += self._padding
            idx += 1
        self._max_index = idx
        #self.draw_scrollbars(ctx["draw"])
        
class TextGraphic(Graphic):
    
    def __init__(self, 
                 text:str,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 font: ImageFont = None,
                 color: str = config.text.color_main,
                 width: int = config.screen.width+60,
                 selected: bool = False,
                 active:bool = False):
        super().__init__(x, y, absolute)
        self._text = text
        self._font = font
        self._selected = selected
        self._active = active
        self._color = color
        self._width = width
        self.load()
    
    def load(self, ctx=None):
        if (self._font is None):
            self._font = ImageFont.truetype(config.text.font_main, config.text.size_large)
        elif (type(self._font) == str):
            self._font = ImageFont.truetype(self._font, config.text.size_main)
        return ctx
    
    def render(self, ctx=None):
        color = self._color
        x, y = ctx["x"], ctx["y"]
        if (self._absolute):
            x, y = self._x, self._y
        if (self._selected and not self._active):
            color = config.text.color_select
            ctx["draw"].rectangle((x, y, x + self._width - 5, y+self.get_height()), outline=color, fill=config.colors.main)
        if (self._active):
            color = config.text.color_alt
            ctx["draw"].rectangle((x, y, x + self._width - 5, y+self.get_height()), outline=color, fill=config.colors.main)
        ctx["draw"].text((x, y), self._text, font = self._font, fill=color)
        if (not self._absolute):
            ctx["y"] += self._font.getsize(self._text)[1]
        return ctx
    
    def get_height(self):
        return self._font.getsize(self._text)[1]
    
    def get_width(self):
        return self._font.getsize(self._text)[0]
    
class DynamicTextGraphic(TextGraphic):
    
    def __init__(self, 
                 text:multiprocessing.Value,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 font: ImageFont = None,
                 color: str = config.text.color_main,
                 width: int = config.screen.width+40,
                 selected: bool = False,
                 active:bool = False):
        super().__init__('', x, y, absolute, font, color, width, selected, active)
        self._dynamic_text = text
        self._text = text.value
    
    def render(self, ctx=None):
        self._text = str(self._dynamic_text.value)
        return super().render(ctx)
    
class ButtonGraphic(TextGraphic):
    
    def __init__(self, 
                 text:str,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 font: ImageFont = None,
                 color: str = config.text.color_main,
                 height: int = 40,
                 width: int = config.screen.width+40,
                 selected: bool = False,
                 active: bool = False):
        super().__init__(text, x, y, absolute, font, color, width, selected)
        self._height = height
    
    def render(self, ctx=None):
        x, y = self._x, self._y
        ctx["draw"].rounded_rectangle((x, y, x + self._width, y + self._height), radius = 2, outline=config.colors.main, fill='#000000')
        if (self._selected):
            ctx["draw"].rounded_rectangle((x, y, x + self._width, y + self._height), outline=config.colors.main, fill=config.colors.alt)
        select = self._selected
        self._selected = False
        ctx = super().render(ctx)
        self._selected = select
        return ctx
    
class SliderGraphic(TextGraphic):
    
    def __init__(self, 
                 text:str,
                 value:multiprocessing.Value,
                 range_value:list = [0.0, 1.0],
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 font: ImageFont = None,
                 color: str = config.text.color_main,
                 width: int = config.screen.width+40,
                 selected: bool = False,
                 active:bool = False):
        super().__init__(text, x, y, absolute, font, color, width, selected, active)
        self._value = value
        self._range = range_value
    
    def render(self, ctx=None):
        ctx = super().render(ctx)
        x, y = ctx["x"], ctx["y"]
        cur_value = self._value.value
        self._range_v = self._range[1] - self._range[0]
        range_draw = ((cur_value - self._range[0]) / (self._range_v)) * self._width
        ctx["draw"].rounded_rectangle((x + 10, y, x + self._width - 10, y + 10), outline=config.colors.alt, fill='#000000')
        ctx["draw"].rectangle((x + 10, y, x + range_draw, y + 10), outline=None, fill=config.colors.alt)
        ctx["y"] += 15
        return ctx
    
    def get_height(self):
        return self._font.getsize(self._text)[1] + 15
        
class ImageGraphic(Graphic):
    
    def __init__(self,
                 image: str,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False):
        super().__init__(x, y, absolute)
        self.load()
    
    def load(self, ctx=None):
        if (self._font is None):
            self._font = ImageFont.truetype(config.text.font_main, config.text.size_main)
        elif (type(self._font) == str):
            self._font = ImageFont.truetype(self._font, config.text.size_main)
        return ctx
    
    def render(self, ctx=None):
        color = self._color
        if (self._selected):
            color = config.text.color_select
            ctx["draw"].rectangle()
        if (self._absolute):
            ctx["draw"].text((ctx["x"], ctx["y"]), self._text, font = self._font, fill=color)
        else:
            ctx["draw"].text((ctx["x"], ctx["y"]), self._text, font = self._font, fill=color)
        ctx["y"] += self.get_height()
        return ctx
    
    def get_height(self):
        self._font.getsize(self._text)[1]
    
    def get_width(self):
        self._font.getsize(self._text)[0]
        
        
        