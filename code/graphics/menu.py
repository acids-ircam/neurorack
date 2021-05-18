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
from .graphics import GraphicScene
from .config import config

class Menu(GraphicScene):
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
        self._config_file = config_file
        self._config = None
        self._root_menu = None
        self._items = {}
        self._current_items = []
        self._history = [""]
        self._mode = config.menu.mode_basic
        # Scrolling properties
        self._scroll_start = 0
        self._scroll_down = False
        self._scroll_up = False
        # Index properties
        self._selected_index = -1
        self._max_index = -1
        self.load()

    def load(self):
        '''
            Loads the controller menu configuration and boots the menu. 
        '''
        # Load the menu
        with open(self._config_file) as file:
            # The FullLoader handles conversion from scalar values to Python dict
            self._config = yaml.load(file, Loader=yaml.FullLoader)
        print(self._config)
        self._root_menu = self._config["root"]
        self._current_menu = self._root_menu
        self._current_items = []
        for item in self._current_menu: 
            self._current_items.append(item)
        print(self._current_items)
        # Generate items menu
        for item in self._config["items"]:
            self._items[item] = MenuItem.create_item(self._config["items"][item])
    
    def render(self, draw, ctx):
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
        self._mode = config.menu.mode_basic
        self._scroll_down = False
        self._scroll_up = self._scroll_start > 0
        idx = self._scroll_start
        while idx < len(self._current_items):
            item = self._current_items[idx]
            item_size = item.getsize()[1]
            if ctx.y + item_size > self.max_height: 
                self._scroll_down = True
                break
            item.render(draw, ctx)
            idx += 1
            ctx.y += item_size
        self._max_index = idx
        self.__draw_scrollbars(draw)

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
        if type(self._current_menu[select_item]) is str:
            print(f"Execute {self._current_menu[select_item]}")
            self._items[self._current_menu[select_item]].run(display=self.__disp)
        else:
            print(f"Load {self._current_menu[select_item]}")
            self._current_menu = self._current_menu[select_item]
            self._history.append(select_item)
            for item in self._current_menu: 
                items.append(item)
            self.__disp.Items = items

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
                items.append("..")
        for item in self._current_menu: items.append(item)
        self.__disp.Items = items

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

    def navigation_callback(self, event):
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
        if eventType is DOWN_CLICK and self.__mode == MODE_MENU:
            if self.__selectedIndex == self.__maxIndex-1 and self.__scrollDown is False: return
            if self.__selectedIndex == self.__maxIndex-1: self.__scrollStartIndex +=1
            self.__selectedIndex += 1
            self.DrawMenu()
            return

        if eventType is UP_CLICK and self.__mode == MODE_MENU:
            if self.__selectedIndex == 0 and self.__scrollUp is False: return
            if self.__selectedIndex == -1: 
                self.__selectedIndex = 0
                self.__scrollStartIndex = 0
            else:
                if self.__selectedIndex == self.__scrollStartIndex: self.__scrollStartIndex -= 1
                self.__selectedIndex -= 1
            self.DrawMenu()
            return

        if eventType is LEFT_CLICK and self.__mode == MODE_MENU and self.__upCallback: 
            self.__upCallback()
            return
        if eventType is LEFT_CLICK and self.__mode == MODE_CONFIRM: 
            self.DrawConfirmation(state=CONFIRM_OK)
            return
        if eventType is RIGHT_CLICK and self.__mode == MODE_CONFIRM: 
            self.DrawConfirmation(state=CONFIRM_CANCEL)
            return

        if eventType is SELECT_CLICK and self.__mode == MODE_MENU:
            if self.__selectedIndex == 0 and self.__items[0] == ".." and self.__upCallback:
                self.__upCallback()
            elif self.__selectCallback and self.__selectedIndex > -1: 
                self.__selectCallback(self.__selectedIndex, self.__items[self.__selectedIndex])
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
                 type: int, 
                 command: str, 
                 confirm: bool = False):
        """
            Initializes a new instance of the Command class
            Parameters:
                type:       int
                            The type of command. Either COMMAND_BUILTIN or COMMAND_SHELL
                command:    str
                            The actual command to execute. If type is COMMAND_BUILTIN the value must be a valid key inhte 
                            Command.buildInCommands list. If type is COMMAND_SHELL the value must be a command that can be 
                            executed at a shell command prompt
                processor:  str
                            Optional, for future functionality. Not currently used.
                confirm:    bool
                            True to require confirmation before the command is executed, false otherwise. 
                cwd:        str
                            Current Working Directory to execute the command in
        """
        self.__type: int = type
        self.__command: str = command
        self.__returnCode: int = 0
        self.__output: str = ''
        self.__confirm: bool = confirm
        self.__confirmationHandler: callable = None
        self.__spinHandler: callable = None
        self.__outputHandler: callable = None
        self.__running: bool = False
    #endregion

    #region public instance methods
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
    @staticmethod
    def create_item(data):
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
            type= data["type"],
            command = data["command"],
            confirm = data["confirm"] if "confirm" in data.keys() else False
          )
        return command

class MenuBar():
    def __init__(self):
        pass

if __name__ == '__main__':
    menu = Menu('../menu.yaml')
    