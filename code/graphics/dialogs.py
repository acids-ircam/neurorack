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

class Dialog():
    
    def __init__(self):
        pass

    def render(self, ctx=None):
        raise NotImplementedError
        
class ConfirmDialog(Dialog):
    
    def __init__(self):
        super().__init__()

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
        """
        self.__mode = MODE_CONFIRM
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
        if command != None: self.__confirmCommand = command
        self.__confirmState = state
        x = self.__padding
        y = self.__padding
        text = ""
        messages = []
        if self.__confirmCommand != None: 
            messages.append(MSG_RUN)
            messages.append("'%s'" %self.__confirmCommand.Command)
        messages.append(MSG_PROCEED)
        for message in messages: text += message + "\n"

        z = self.__draw.multiline_textsize(text, font=self.__font, spacing=10)
        x = (self.__width - z[0])/2
        c1 = [(10, self.__height-40), (self.__width/2 - 10, self.__height-15)]
        c2 = [(self.__width/2 + 10, self.__height-40), (self.__width - 10, self.__height-15)]
        c3 = (self.__width/4 - self.__draw.textsize(MSG_OK, font=self.__font)[0]/2  , self.__height-35)
        c4 = (3*self.__width/4 - self.__draw.textsize(MSG_CANCEL, font=self.__font)[0]/2, self.__height-35)
        self.__draw.multiline_text((x, y), text, font=self.__font, spacing=10, fill=self.__textColor, align="center")
        self.__draw.rectangle(c1, fill=self.__selectedColor if state==CONFIRM_OK else self.__textColor)
        self.__draw.rectangle(c2, fill=self.__selectedColor if state==CONFIRM_CANCEL else self.__textColor)
        self.__draw.text(c3, MSG_OK, font=self.__font, fill="#000000")
        self.__draw.text(c4, MSG_CANCEL, font=self.__font, fill="#000000")
        self.__disp.LCD_ShowImage(self.__image)
        
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
        box = [(self.__width - self.__height)/2+25, 25, (self.__width + self.__height)/2-25, self.__height-25]
        while True:
            if stop() : break
            deg = 1
            self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
            while deg<=360: 
                if stop(): break
                self.__draw.pieslice(box, -90, -90+deg, outline=self.__textColor, fill=self.__textColor)
                self.__disp.LCD_ShowImage(self.__image)
                deg += 1
                time.sleep(0.001)
        self.__draw.pieslice(box, -90, 270, outline=self.__textColor, fill=self.__textColor)
        self.__disp.LCD_ShowImage(self.__image)