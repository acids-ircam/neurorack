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
        self.__commands = {}
        self.__currentMenu = None
        self.__breadcrumb = [""]
        self.load()

    def load(self):
        """
            Loads the controller menu configuration and boots the menu. 
        """
        # load the menu
        with open(self._config_file) as file:
            # The FullLoader handles conversion from scalar values to Python dict
            self._config = yaml.load(file, Loader=yaml.FullLoader)
        self._root_menu = self._config["root"]
        self.__currentMenu = self._root_menu
        items = []
        for item in self.__currentMenu: items.append(item)

        # initialize Display
        self.__disp: Display = Display()
        self.__disp.Items = items
        self.__disp.ResetMenu()
        self.__disp.SelectCallback = self.__processSelectEvent
        self.__disp.UpCallback = self.__processBreadcrumbEvent
        self.__disp.ConfirmCallback = self.__processConfirmEvent

        # load configured commands
        for item in self._config["commands"]:
            self.__commands[item] = Command.FromJSON(self._config["commands"][item])
            self.__commands[item].SpinHandler = self.__disp.Spinner
            if self.__commands[item].Type == COMMAND_SHELL: 
                    self.__commands[item].OutputHandler = self.__disp.DrawOutput
            if self.__commands[item].Confirm == True:
                    self.__commands[item].ConfirmationHandler = self.__disp.DrawConfirmation

        # initialize Navigation buttons
        self.__nav: Navigation = Navigation(self.__disp.ProcessNavigationEvent)

    def __processSelectEvent(self, selectIndex: int, selectItem: str):
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
        if type(self.__currentMenu[selectItem]) is str:
            logging.info(f"Execute {self.__currentMenu[selectItem]}")
            self.__commands[self.__currentMenu[selectItem]].Run(display=self.__disp)
        else:
            logging.info(f"Load {self.__currentMenu[selectItem]}")
            self.__currentMenu = self.__currentMenu[selectItem]
            self.__breadcrumb.append(selectItem)
            for item in self.__currentMenu: items.append(item)
            self.__disp.Items = items

    def __processBreadcrumbEvent(self):
        """
            Delegate to respond to the navigate uo event on the controller tactile Up button. Loads the 
            previous menu. 
        """
        items = []
        self.__breadcrumb.pop()
        for level in self.__breadcrumb:
            if level == "": self.__currentMenu = self._root_menu
            else: 
                self.__currentMenu = self.__currentMenu[level]
                items.append("..")
        for item in self.__currentMenu: items.append(item)
        self.__disp.Items = items

    def __processConfirmEvent(self, command:Command, confirmState: int):
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

