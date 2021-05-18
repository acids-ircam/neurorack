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
import yaml
from .graphics import ScrollableGraphicScene, TextGraphic
from .config import config

class Menu(ScrollableGraphicScene):
    '''
        Main class for the LCD Menu. 
        Handles loading and running the menu and commands. 
    '''
    
    def __init__(self, 
                 config_file = "./menu.yaml",
                 x:int = 0,
                 y:int = 0,
                 height = 240,
                 width = 180,
                 absolute = True):
        '''
            Constructor. Creates a new instance of the ContollerMenu class. 
            Paramters: 
                config:     str
                            Name of the config file for the controller menu. Defaults to ./controllerMenu.yaml. 
        '''
        super().__init__(x, y, absolute, True, height, width)
        self._config_file = config_file
        self._config = None
        self._root_menu = None
        self._items = {}
        self._current_items = []
        self._history = [""]
        self._mode = config.menu.mode_basic
        self.load()

    def load(self):
        '''
            Loads the controller menu configuration and boots the menu. 
        '''
        # Load the menu
        with open(self._config_file) as file:
            # The FullLoader handles conversion from scalar values to Python dict
            self._config = yaml.load(file, Loader=yaml.FullLoader)
        self._root_menu = self._config["root"]
        self._current_menu = self._root_menu
        for item in self._current_menu: 
            self._elements.append(TextGraphic(item))
        # Generate items menu
        for item in self._config["items"]:
            self._items[item] = MenuItem.create_item(item, self._config["items"][item])
        self._elements = self._current_items

    def process_select(self, 
                       select_index: int, 
                       select_item: str):
        """
            Delegate to respond to a select event on the controller tactile select button. Invokes either
            navigation to a submenu or command execution. 
            Paramters: 
                select_index:   [int]
                                Index of the menu item selected.
                select_item:    [str]
                                The selected menu item
        """
        items = [".."]
        if type(self._current_menu[select_item]) is TextGraphic:
            print(f"Execute {self._current_menu[select_item]}")
            self._items[self._current_menu[select_item]].run(display=self.__disp)
        else:
            print(f"Load {self._current_menu[select_item]}")
            self._current_menu = self._current_menu[select_item]
            self._history.append(select_item)
            self._elements = []
            for item in self._current_menu: 
                self._elements.append(TextGraphic(item))

    def process_history(self):
        """
            Delegate to respond to the navigate uo event on the controller tactile Up button. Loads the 
            previous menu. 
        """
        items = []
        self._history.pop()
        for level in self._history:
            if level == "": 
                self._current_menu = self._root_menu
            else: 
                self._current_menu = self._current_menu[level]
                items.append(config.menu.back_element)
        for item in self._current_menu: 
            items.append(item)
        self._elements = items

    def process_confirm(self, command:any, confirmState: int):
        """
            Delegate to respond to the confirmation event from the confirmation screen. Depending on event state, 
            either reloads the previous menu (confirmState==CONFIRM_CAMCEL) or run the commmand (CONFIRM_OK)
            Parameters:
                command:        Command
                                The command to run if confirmed
                confirmState:   int
                                The confirm state. Either CONFIRM_OK or CONFIRM_CANCEL
        """
        if confirmState == config.menu.confirm_cancel: self.__disp.DrawMenu()
        else:
            command.Run(display=self.__disp, confirmed=config.menu.confirm_ok)    
        
    def Spinner(self, run=True):
        """
            Loads the spinner screen while a command executes. This will start a background thread when invoked with run=True and 
            derminate the thread (and spinner) when invoked with run=False
            Parameters:
                run:    bool
                        Optional. Pass True to start the spinner, false to derminate the spinner.
        """
        if run==True:
            self.__stopSpinner = False
            self.__spinnerThread = threading.Thread(target=self.__drawSpinner, name="spinner", args=(lambda : self.__stopSpinner, ))
            self.__spinnerThread.start()
        else:
            if self.__spinnerThread is None: return
            self.__stopSpinner = True
            self.__spinnerThread.join()

    def navigation_callback(self, state, event_type):
        """
            Delegate called by the Navigation model when a navigation event occurs on the GPIO. Handles 
            corresponding invokation of the various display draw and/or command execution delegates. 
            Parameters:
                eventType:  int
                            The type of event that occured. One of the following:
                                DOWN_CLICK
                                UP_CLICK
                                LEFT_CLICK
                                RIGHT_CLICK
                                SELECT_CLICK
        """
        if (event_type == 'rotary'):
            direction = state['rotary_delta'].value
        if (self._mode == config.menu.mode_basic):
            if (event_type == 'rotary' and direction > 0):
                if self._selected_index == self._max_index - 1 and self._scroll_down is False: 
                    return
                if (self._selected_index >= 0):
                    self._elements[self._selected_index]._selected = False
                if self._selected_index == self._max_index - 1: 
                    self._scroll_start +=1
                self._selected_index += 1
                print('yasss')
                print(self._selected_index)
                self._elements[self._selected_index]._selected = True
                return
            if (event_type == 'rotary' and direction < 0):
                if self._selected_index == 0 and self._scroll_up is False: 
                    return
                if self._selected_index == -1: 
                    self._selected_index = 0
                    self._scroll_start = 0
                else:
                    self._elements[self._selected_index]._selected = False
                    if self._selected_index == self._scroll_start: 
                        self._scroll_start -= 1
                    self._selected_index -= 1
                    self._elements[self._selected_index]._selected = True
                return
            if (event_type == 'button'):
                if self._selected_index == 0 and self._elements[0] == config.menu.back_element:
                    self.process_history
                elif self._selected_index > -1: 
                    self.process_select(self._selected_index, self._elements[self._selected_index])
                return
        
        """
        if eventType is LEFT_CLICK and self.__mode == MODE_MENU and self.__upCallback: 
            self.__upCallback()
            return
        if eventType is SELECT_CLICK and self.__mode == MODE_CONFIRM and self.__confirmCallback:
            self.__confirmCallback(self.__confirmCommand, self.__confirmState)
            return
        if eventType is SELECT_CLICK and self.__mode == MODE_OUTPUT:
            self.DrawMenu()
            return
        if self.__mode == MODE_EXTERNAL and (eventType is SELECT_CLICK or eventType is LEFT_CLICK):
            self.__stopCommand = True
            return
        if eventType is LEFT_CLICK and self.__mode == MODE_CONFIRM: 
            self.DrawConfirmation(state=CONFIRM_OK)
            return
        if eventType is RIGHT_CLICK and self.__mode == MODE_CONFIRM: 
            self.DrawConfirmation(state=CONFIRM_CANCEL)
            return
        """

    def ResetMenu(self):
        """
            Resets the current menu to an unselected state.
        """
        self.__selectedIndex = -1
        self.DrawMenu()

class MenuItem():    
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
    
    def render(self, ctx):
        ctx = self.graphic.render(ctx)
        
    
    def Run(self, confirmed=config.menu.confirm_cancel):
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
            if self.__type == COMMAND_BUILTIN:
                if self.__command in Command.builtInCommands:
                    x = Command.builtInCommands[self.__command](display)
                    x.Run(stop=lambda : display.StopCommand, completed=self.__complete)
    #endregion

    #region public class (static) methods
    

class MenuBar():
    def __init__(self):
        pass

if __name__ == '__main__':
    menu = Menu('../menu.yaml')
    