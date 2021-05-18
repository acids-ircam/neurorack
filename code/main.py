"""

 ~ Neurorack project ~
 Neurorack : Main class for the module
 
 This file contains the code for the main class in the Neurorack
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.
 
"""

import Jetson.GPIO as GPIO
from rotary import Rotary
from cv import CVChannels
from audio import Audio
from button import Button
import multiprocessing as mp
from multiprocessing import Process, Manager, Queue, Value
from ctypes import c_char_p

class Neurorack():
    '''
        The Neurorack main class is responsible for starting all processes.
            - Audio engine
            - Rotary encoder
            - CV Channels
            - Screen
    '''

    def __init__(self):
        '''
            Constructor - Creates a new instance of the Neurorack class.
        '''
        # Main properties
        self._N_CVs = 6
        # Init states of information
        self.init_state()
        # Create audio engine
        self._audio = Audio(self.callback_audio)
        # Create rotary
        self._rotary = Rotary(self.callback_rotary)
        # Create CV channels
        self._cvs = CVChannels(self.callback_cv)
        # Perform GPIO cleanup
        GPIO.cleanup()
        # Need to import Screen after cleanup
        from screen import Screen
        self._screen = Screen(self.callback_screen)
        # Create push button
        self._button = Button(self.callback_button)
        # List of objects to create processes
        self._objects = [self._audio, self._screen, self._rotary, self._cvs, self._button]
        # Find number of CPUs
        self._nb_cpus = mp.cpu_count()
        # Create a pool of jobs
        self._pool = mp.Pool(self._nb_cpus)
        # Handle signal informations
        self.set_signals()
        # Create a queue for sharing information
        self._queue = Queue()
        self._processes = []
        for o in self._objects:
            self._processes.append(Process(target=o.callback, args=(self._state, self._queue)))

    def init_state(self):
        '''
            Initialize the shared memory state for the full rack.
            The global properties are shared by a multiprocessing manager.
        '''
        # Use a multi-processing Manager
        self._manager = Manager()
        self._state = self._manager.dict()
        self._state['global'] = self._manager.dict()
        self._state['cv'] = self._manager.list([0.0] * self._N_CVs)
        self._state['rotary'] = self._manager.Value(int, 0)
        self._state['rotary_delta'] = self._manager.Value(int, 0)
        self._state['button'] = self._manager.Value(int, 0)
        # Menu-related parameters (dict)
        self._state['menu'] = self._manager.dict()
        # Audio-related parameters (dict)
        self._state['audio'] = self._manager.dict()
        # Stats (cpu, memory) computing
        self._state['stats'] = self._manager.dict()
        self._state['stats']['ip'] = self._manager.Value(c_char_p, "ip".encode('utf-8'))
        self._state['stats']['cpu'] =  self._manager.Value(c_char_p, "cpu".encode('utf-8'))
        self._state['stats']['memory'] =  self._manager.Value(c_char_p, "memory".encode('utf-8'))
        self._state['stats']['disk'] =  self._manager.Value(c_char_p, "disk".encode('utf-8'))
        self._state['stats']['temperature'] =  self._manager.Value(c_char_p, "temperature".encode('utf-8'))
        
    def set_signals(self):
        '''
            Set the complete signaling mechanism.
        '''
        self._signal_audio = self._audio._signal
        self._signal_rotary  = self._rotary._signal
        self._signal_cvs =  self._cvs._signal
        self._signal_screen = self._screen._signal
        self._signal_button = self._button._signal
    
    def set_callbacks(self):
        '''
            Set the complete signaling mechanism.
            Currently unused but for further versions
        '''
        pass
    
    def callback_audio(self):
        '''
            Callback for handling events from the audio engine
        '''
        print('Audio callback')
    
    def callback_button(self, channel, value):
        '''
            Callback for handling events from the button
        '''
        print('Button callback')
        self._screen.button_callback()
        self._signal_screen.set()
    
    def callback_cv(self, channel, value):
        '''
            Callback for handling events from the CV
        '''
        print('CV callback')
        
    def callback_rotary(self, channel, value):
        '''
            Callback for handling events from the rotary
        '''
        print('Rotary callback')
        self._signal_screen.set()
        
    def callback_screen(self, channel, value):
        '''
            Callback for handling events from the screen
        '''
        print('Screen callback')
            
    def start(self):
        '''
            Start all parallel processses
        '''
        for p in self._processes:
            p.start()

    def run(self):
        '''
            Wait (join) on all parallel processses
        '''
        for p in self._processes:
            p.join()

    def __del__(self):
        '''
            Destructor - cleans up GPIO resources when the object is destroyed. 
        '''
        GPIO.cleanup()      

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Neurorack')
    # Device Information
    parser.add_argument('--device',         type=str, default='cuda:0',     help='device cuda or cpu')
    # Parse the arguments
    args = parser.parse_args()
    neuro = Neurorack()
    neuro.start()
    neuro.run()
