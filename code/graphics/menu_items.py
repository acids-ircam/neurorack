"""

 ~ Neurorack project ~
 Menu : Set of classes for handling the menus
 
 This file defines the main operations for graphical menus
 The functions here will be used for the LCD display.
 Parts of this code have been inspired by the great piControllerMenu code:
     https://github.com/Avanade/piControllerMenu
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""
from .graphics import Graphic, TextGraphic, SliderGraphic
from .config import config

class MenuItem(Graphic):    
    '''
    Represents a menu item
    '''

    #region constructor
    def __init__(self, 
                 title: str,
                 type: int, 
                 command: str, 
                 confirm: bool = False):
        """
            Initializes a new instance of the Command class
            Parameters:
                type:       int
                            The type of menu item. 
                command:    str
                            The actual command to execute.
                confirm:    bool
                            True to require confirmation before the command is executed, false otherwise. 
        """
        self._title = title
        self._type: int = type
        self._command: str = command
        self._output: str = ''
        self._confirm: bool = confirm
        self._running: bool = False
        self._graphic: Graphic = None
        if (self._type == 'menu' or self._type == 'shell' or self._type == 'function'):
            self._graphic = TextGraphic(title)
        elif (self._type == 'slider'):
            self._graphic = SliderGraphic(title, None)
        elif (self._type == 'list'):
            self._graphic = TextGraphic(title)
            
    def render(self, ctx):
        return self._graphic.render(ctx)
    
    def get_height(self):
        return self._graphic.get_height()
    
    def get_width(self):
        return self._graphic.get_width()
    
    @staticmethod
    def create_item(title, data):
        """
            Deserialized a command from YAML. 
            Parameters:
                data:   object
                        Representation of the Command data.
            Returns:
                Instance of Command
        """
        if "type" not in data.keys() or (data["type"] not in config.menu.accepted_types):
            message = "Menu item is of unexpected type " + data["type"]
            raise Exception(message)
        if "command" not in data.keys() or data["command"] == "":
            message = "Could not find attribute command"
            raise Exception(message)
        command = MenuItem(
            title,
            type = data["type"],
            command = data["command"],
            confirm = data["confirm"] if "confirm" in data.keys() else False
          )
        return command
    
    def run(self, confirmed=config.menu.confirm_cancel):
        """
            Runs the command.
            Parameters:
                display:    Display
                            Reference to a Display instance. This can be NONE if Command.Type is COMMAND_SHELL
                confirmed:  int
                            Optional. Pass CONFIRM_OK to indicate the command has been confirmed. 
        """
        if self.__confirm and self.__confirmationHandler is not None and confirmed==CONFIRM_CANCEL:
            self.__confirmationHandler(self)
        else:
            self.__running = True
            if self.__type == COMMAND_SHELL:
                if self.__spinHandler is not None: self.__spinHandler(True)
                try:
                    #breakpoint()
                    self.__output = subprocess.check_output(self.__command, shell=True,  cwd=self.__cwd).decode()
                    self.__returnCode = 0
                except subprocess.CalledProcessError as e:
                    self.__output = e.output.decode()
                    self.__returnCode = e.returncode
                    logging.exception(e)
                except Exception as e:
                    self.__output = str(e)
                    self.__returnCode = -1000
                    logging.exception(e)
                if self.__spinHandler is not None: self.__spinHandler(False)
                if self.__outputHandler is not None: self.__outputHandler(self.__command, self.__returnCode, self.__output)
                self.__running = False
            if self.__type == COMMAND_function:
                if self.__command in Command.functionCommands:
                    x = Command.functionCommands[self.__command](display)
                    x.Run(stop=lambda : display.StopCommand, completed=self.__complete)
    #endregion

    #region public class (static) methods
    

class MenuBar():
    def __init__(self):
        pass

if __name__ == '__main__':
    menu = Menu('../menu.yaml')
    