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
import subprocess

from .config import config
from .dialogs import ConfirmDialog
from .graphics import Graphic, TextGraphic, SliderGraphic
from .menu_functions import assign_cv, assign_button, assign_rotary
from .menu_functions import model_play, model_select, model_reload, model_benchmark


class MenuItem(Graphic):
    '''
    Represents a menu item
    '''

    function_dispatcher = {
        'model_play': model_play,
        'model_select': model_select,
        'model_reload': model_reload,
        'model_benchmark': model_benchmark,
        'assign_cv': assign_cv,
        'assign_button': assign_button,
        'assign_rotary': assign_rotary
    }

    # region constructor
    def __init__(self,
                 title: str,
                 signals: dict,
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
        self._signals: dict = signals
        self._command: str = command
        self._output: str = ''
        self._confirm: bool = confirm
        self._running: bool = False
        self._active: bool = False
        self._graphic: Graphic = None
        if self._type == 'menu' or self._type == 'shell' or self._type == 'function':
            self._graphic = TextGraphic(title)
        elif self._type == 'slider':
            self._graphic = SliderGraphic(title, None)
        elif self._type == 'list':
            self._graphic = TextGraphic(title)

    def render(self, ctx):
        return self._graphic.render(ctx)

    def get_height(self):
        return self._graphic.get_height()

    def get_width(self):
        return self._graphic.get_width()

    @staticmethod
    def create_item(title, data, signals):
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
            signals,
            type=data["type"],
            command=data["command"],
            confirm=data["confirm"] if "confirm" in data.keys() else False
        )
        return command

    def run(self, state, menu, params=None, confirmed=config.menu.confirm_cancel):
        """
            Runs the command.
            Parameters:
                display:    Display
                            Reference to a Display instance. This can be NONE if Command.Type is COMMAND_SHELL
                confirmed:  int
                            Optional. Pass CONFIRM_OK to indicate the command has been confirmed. 
        """
        print('[Pushed command ' + self._title)
        if self._confirm and confirmed == config.menu.confirm_cancel:
            dial = ConfirmDialog()
            menu._current_dialog = dial
            menu._mode = config.menu.mode_dialog
        else:
            self._running = True
            if self._type == 'function':
                self.function_dispatcher[self._command](state, self._signals, params)
            elif self._type == 'shell':
                self._output = subprocess.check_output(self._command, shell=True).decode()
                self.__returnCode = 0
                self.__running = False


class MenuBar():
    def __init__(self):
        pass
