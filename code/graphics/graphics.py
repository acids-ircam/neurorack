"""

 ~ Neurorack project ~
 Graphics : Set of classes for graphical objects
 
 This file defines the main operations for the graphical objects.
 The functions here will be used for the LCD display.
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

from config import config
from .utils import get_resized_image
from PIL import ImageFont

class Graphic():
    
    def __init__(self, 
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False):
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
        self.elements = elements
        
    def add(self, e: Graphic):
        self.elements.append(e)
        
    def load(self, ctx=None):
        for e in self.elements:
            ctx = e.load(ctx)
        return ctx

    def render(self, ctx=None):
        if (self._absolute):
            ctx["x"], ctx["y"] = self._x, self._y
        for e in self.elements:
            ctx = e.render(ctx)
        return ctx
            
    def get_height(self):
        height = 0
        for e in self.elements:
            height += e.get_height()
        return height
            
    def get_width(self):
        width = 0
        for e in self.elements:
            width += e.get_width()
        return width
        
class TextGraphic(Graphic):
    
    def __init__(self, 
                 text:str,
                 x:int = config.screen.main_x, 
                 y:int = config.screen.padding,
                 absolute: bool = False,
                 font: ImageFont = None,
                 color: str = config.text.color_main,
                 selected: bool = False):
        super().__init__(x, y, absolute)
        self._text = text
        self._font = font
        self._selected = selected
        self._color = color
        self.load()
    
    def load(self, ctx=None):
        if (self._font is None):
            self._font = ImageFont.truetype(config.text.font_main, config.text.size_main)
        elif (type(self._font) == str):
            self._font = ImageFont.truetype(self._font, config.text.size_main)
        return ctx
    
    def render(self, ctx=None):
        color = self._color
        x, y = ctx["x"], ctx["y"]
        if (self._absolute):
            x, y = self._x, self._y
        if (self._selected):
            color = config.text.color_select
            ctx["draw"].rectangle((x, y, self.get_width(), self.get_height()), outline=color, fill=config.colors.main)
        print((x, y), self._text, self._font, color)
        ctx["draw"].text((x, y), self._text, font = self._font, fill=color)
        if (not self._absolute):
            ctx["y"] += self.get_height()
        return ctx
    
    def get_height(self):
        return self._font.getsize(self._text)[1]
    
    def get_width(self):
        return self._font.getsize(self._text)[0]
        
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
        
        
        