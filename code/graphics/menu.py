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

MODE_MENU = 0
MODE_CONFIRM = 1
MODE_OUTPUT = 2
MODE_EXTERNAL = 3
CONFIRM_CANCEL = 0
CONFIRM_OK = 1
MSG_OK = "OK"
MSG_CANCEL = "CANCEL"
MSG_RUN = "You are about to run"
MSG_PROCEED = "Proceed?"
MSG_RESULTS = "'%s'"
MSG_CODE = "Return Code: %x"
MSG_OUTPUT = "Output:"

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
        # Generate items menu
        for item in self._config["items"]:
            self._items[item] = Command.FromJSON(self._config["items"][item])

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
    
    def DrawMenu(self, items:list=None):
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
        self.__mode = MODE_MENU
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)

        x = self.__padding
        y = self.__padding
        if items != None: self.__items = items
        self.__scrollDown = False
        self.__scrollUp = self.__scrollStartIndex > 0
        idx = self.__scrollStartIndex
        while idx < len(self.__items):
            item = self.__items[idx]
            __y = self.__font.getsize(item)[1]
            if y + __y > self.__height: 
                self.__scrollDown = True
                break

            self.__draw.text((x, y), item, font=self.__font, 
                fill= self.__selectedColor if idx == self.__selectedIndex else self.__textColor)
            idx += 1
            y += __y + self.__padding
        self.__maxIndex = idx
        self.__drawScrollArrows()
        self.__disp.LCD_ShowImage(self.__image)
    

    def DrawOutput(self, command:str, code:int, message:str=""):
        """
            Draws the output of a command (or any string, really).
            Parameters:
                command:    str
                            Contains the name (command line) of the command whose output is shown
                code:       int
                            The command exit code.
                message:    str
                            Optional. Output to display.  
        """
        self.__mode = MODE_OUTPUT
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
        x = self.__padding
        y = self.__padding
        self.__draw.text((x, y), MSG_RESULTS %command, font=self.__font, fill=self.__textColor)
        y += self.__font.getsize(MSG_RESULTS)[1] + self.__padding
        self.__draw.text((x, y), MSG_CODE %code, font=self.__font, fill=self.__textColor)                
        y += self.__font.getsize(MSG_CODE)[1] + self.__padding 
        if message != "":
            self.__draw.text((x, y), MSG_OUTPUT, font=self.__font, fill=self.__textColor)
            y += self.__font.getsize(MSG_OUTPUT)[1] + self.__padding
            self.__draw.multiline_text((x + self.__padding,y), message, fill=self.__textColor)

        c1 = [(self.__width/2 + 10, self.__height-40), (self.__width - 10, self.__height-15)]
        c2 = (3*self.__width/4 - self.__draw.textsize(MSG_OK, font=self.__font)[0]/2, self.__height-35)
        self.__draw.rectangle(c1, fill=self.__textColor)
        self.__draw.text(c2, MSG_OK, font=self.__font, fill="#000000")        
        self.__disp.LCD_ShowImage(self.__image)
        
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

    def ProcessNavigationEvent(self, eventType):
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
    """
    Represents a command to be executed
    """

    builtInCommands: dict = {
        "sysInfo": SysInfo,
        "netInfo": NetInfo
    }

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
        self.__processor: str = processor
        self.__returnCode: int = 0
        self.__output: str = ''
        self.__confirm: bool = confirm
        self.__confirmationHandler: callable = None
        self.__spinHandler: callable = None
        self.__outputHandler: callable = None
        self.__running: bool = False
        self.__cwd: str = cwd
    #endregion

    #region public instance methods
    def Run(self, display: Display, confirmed=CONFIRM_CANCEL):
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
    def create_item(data) -> MenuItem:
        """
            Deserialized a command from YAML. 
            Parameters:
                data:   object
                        Representation of the Command data.
            Returns:
                Instance of Command
        """
        if "type" not in data.keys() or (data["type"] != "shell" and data["type"] != "builtin"):
            message = "Menu item is of unexpected type " + data["type"]
            raise Exception(message)
        if "command" not in data.keys() or data["command"] == "":
            message = """Data not in the appropriate format. 
                Expect 'command' attribute to be present and have a value."""
            logging.exception(message)
            raise Exception(message)
        command = MenuItem(
            type=COMMAND_BUILTIN if data["type"] == "builtin" else COMMAND_SHELL,
            command = data["command"],
            processor = data["processor"] if "processor" in data.keys() else None,
            confirm = data["confirm"] if "confirm" in data.keys() else False,
            cwd = data["cwd"] if "cwd" in data.keys() else None
          )
        logging.info(f"Deserialized command {command.Command} successfully")
        return command

class MenuBar():
    def __init__(self):
        pass

if __name__ == '__main__':
    menu = Menu('../menu.yaml')
    