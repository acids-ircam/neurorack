"""

 ~ Neurorack project ~
 Menu : Set of classes for handling the menus
 
 This file defines the main operations for graphical menus
 The functions here will be used for the LCD display.
 Parts of this code have been inspired by the great piControllerMenu code:
     https://github.com/Avanade/piControllerMenu
 
 Author               : Philippe Esling, Ninon Devis, Martin Vert
                        <{esling, devis}@ircam.fr>

"""
import yaml

class Menu():
    '''
        Main class for the LCD Menu. 
        Handles loading and running the menu and commands. 
    '''
    
    def __init__(self, config = "./menu.yaml"):
        '''
            Constructor. Creates a new instance of the ContollerMenu class. 
            Paramters: 
                config:     str
                            Name of the config file for the controller menu. Defaults to ./controllerMenu.yaml. 
        '''
        self._config_file = config
        self._config = None
        self._root_menu = None
        self._items = {}
        self._current_items = []
        self._breadcrumb = [""]
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

        # initialize Display
        self.__disp: Display = Display()
        self.__disp.Items = items
        self.__disp.ResetMenu()
        self.__disp.SelectCallback = self.process_select
        self.__disp.UpCallback = self.process_history
        self.__disp.ConfirmCallback = self.process_confirm

        # load configured commands
        for item in self._config["commands"]:
            self._items[item] = Command.FromJSON(self._config["commands"][item])
            self._items[item].SpinHandler = self.__disp.Spinner
            if self._items[item].Type == COMMAND_SHELL: 
                    self._items[item].OutputHandler = self.__disp.DrawOutput
            if self._items[item].Confirm == True:
                    self._items[item].ConfirmationHandler = self.__disp.DrawConfirmation

        # initialize Navigation buttons
        self.__nav: Navigation = Navigation(self.__disp.ProcessNavigationEvent)

    def process_select(self, selectIndex: int, selectItem: str):
        """
            Delegate to respond to a select event on the controller tactile select button. Invokes either
            navigation to a submenu or command execution. 
            Paramters: 
                selectedIndex:  int
                                Index of the menu item selected.
                selectedItem:   str
                                The selected menu item
        """
        items = [".."]
        if type(self._current_menu[selectItem]) is str:
            logging.info(f"Execute {self._current_menu[selectItem]}")
            self._items[self._current_menu[selectItem]].Run(display=self.__disp)
        else:
            logging.info(f"Load {self._current_menu[selectItem]}")
            self._current_menu = self._current_menu[selectItem]
            self._breadcrumb.append(selectItem)
            for item in self._current_menu: items.append(item)
            self.__disp.Items = items

    def process_history(self):
        """
            Delegate to respond to the navigate uo event on the controller tactile Up button. Loads the 
            previous menu. 
        """
        items = []
        self._breadcrumb.pop()
        for level in self._breadcrumb:
            if level == "": self._current_menu = self._root_menu
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
        if confirmState == CONFIRM_CANCEL: self.__disp.DrawMenu()
        else:
            command.Run(display=self.__disp, confirmed=CONFIRM_OK)

class MenuItem():
    def __init__(self):
        pass

class MenuBar():
    def __init__(self):
        pass

if __name__ == '__main__':
    menu = Menu('../menu.yaml')
    