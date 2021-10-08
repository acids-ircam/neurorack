# -*- coding: utf-8 -*-
"""

 ~ Neurorack project ~
 Dialogs : Set of classes for dialogs graphical objects
 
 This dialogs are items that take the full screen for interaction.
 Examples are "confirm" (ok/cancel) or "spinner" (loading) dialogs
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

from .graphics import ScrollableGraphicScene, ButtonGraphic, TextGraphic
from .config import config


class Dialog(ScrollableGraphicScene):

    def __init__(self,
                 x: int = config.screen.main_x,
                 y: int = config.screen.padding,
                 absolute: bool = True,
                 selectable: bool = True,
                 height: int = config.screen.height,
                 width: int = config.screen.width,
                 padding: int = 5,
                 elements: list = []):
        super().__init__(x, y, absolute, selectable, height, width, padding, elements)

    def render(self, ctx=None):
        x, y = self._x, self._y
        ctx["draw"].rounded_rectangle((x, y, x + self._width, y + self._height), radius=2, outline=config.colors.main,
                                      fill='#000000')
        return super().render(ctx)


class ConfirmDialog(Dialog):

    def __init__(self,
                 text: str = None,
                 x: int = config.screen.main_x,
                 y: int = config.screen.padding,
                 absolute: bool = True,
                 selectable: bool = False,
                 height: int = config.screen.height,
                 width: int = config.screen.width,
                 padding: int = 5,
                 elements: list = []):
        super().__init__(x, y, absolute, selectable, height, width, padding, elements)
        # Add title
        if text is None:
            text = config.menu.msg_proceed
        self._text = text
        self._elements.append(TextGraphic(self._text, x=x // 4, y=y // 3, absolute=True))
        # Add OK button
        self._elements.append(ButtonGraphic(config.menu.msg_ok, x=x // 4, y=2 * y // 3, width=x // 5, absolute=True))
        self._elements.append(
            ButtonGraphic(config.menu.msg_cancel, x=3 * x // 4, y=2 * y // 3, width=x // 5, absolute=True))

    def render(self, ctx=None):
        """
            Draws the confirmation dialog on the display. 
            Parameters:
                command:    Command
                            A reference to the command for which to display the confirmation
                state:      int
                            The current confirmation state. Used to set the focus for the OK/Cancel buttone. 
                            Pass COMFIRM_CANCEL to put the focus on the Cancel button, CONFIRM_OK to put the 
                            focus on the Ok button. 
        self.__mode = MODE_CONFIRM
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
        if command != None: self.__confirmCommand = command
        self.__confirmState = state
        """
        return super().render(ctx)


class SpinnerDialog(Dialog):

    def __init__(self):
        super().__init__()

    def render(self, stop: callable):
        """
            Thread entry point for the spinner thread started by Display.Spinner()
            Parameters:
                stop:   callable
                        A delegate called to determine whether to terminate the spinner thread. The delegate is 
                        expected to return a boolean: () -> bool. If the delegate returns True, teh spinner thread
                        will terminate. If the delegate returns False, the spinner will continue. The delegate is 
                        evaluated roughly every 2-3ms
        """
        box = [(self.__width - self.__height) / 2 + 25, 25, (self.__width + self.__height) / 2 - 25, self.__height - 25]
        while True:
            if stop(): break
            deg = 1
            self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
            while deg <= 360:
                if stop(): break
                self.__draw.pieslice(box, -90, -90 + deg, outline=self.__textColor, fill=self.__textColor)
                self.__disp.LCD_ShowImage(self.__image)
                deg += 1
                time.sleep(0.001)
        self.__draw.pieslice(box, -90, 270, outline=self.__textColor, fill=self.__textColor)
        self.__disp.LCD_ShowImage(self.__image)
