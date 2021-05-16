"""

 ~ Neurorack project ~
 Neurorack : Main class for the module
 
 This file contains the code for the main class in the Neurorack
 
 Author               : Philippe Esling, Ninon Devis, Martin Vert
                        <{esling, devis}@ircam.fr>

"""

import Jetson.GPIO as GPIO
from rotary import Rotary
from cv import CVChannels
from audio import Audio
from button import Button
import multiprocessing as mp
from multiprocessing import Process, Manager, Queue

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
        # Init states of information
        self.init_state()
        # Create audio engine
        self.audio = Audio()
        # Create rotary
        self.rotary = Rotary()
        # Create CV channels
        self.cvs = CVChannels()
        # Create push button
        self.button = Button()
        # Perform GPIO cleanup
        GPIO.cleanup()
        # Need to import Screen after cleanup
        from screen import Screen
        self.screen = Screen()
        # List of objects to create processes
        self.objects = [self.audio, self.screen, self.rotary, self.cvs, self.button]
        # Find number of CPUs
        self.nb_cpus = mp.cpu_count()
        # Create a pool of jobs
        self.pool = mp.Pool(self.nb_cpus)
        # Create a queue for sharing information
        self.queue = Queue()
        self.processes = []
        for o in self.objects:
            self.processes.append(Process(target=o.callback, args=(self.state, self.queue)))

    def init_state(self):
        '''
            Initialize the shared memory state for the full rack.
            The global properties are shared by a multiprocessing manager.
        '''
        # Use a multi-processing Manager
        self.manager = Manager()
        self.state = self.manager.dict()
        self.state['global'] = self.manager.dict()
        self.state['cv'] = self.manager.list([0.0] * self.N_CVs)
        self.state['rotary'] = 0
        self.state['button'] = 0
        self.state['menu'] = 0
        self.state['audio'] = 0
        
    def set_signals(self):
        pass
    
    def set_callbacks(self):
        pass
            
    def start(self):
        '''
            Start all parallel processses
        '''
        for p in self.processes:
            p.start()

    def run(self):
        '''
            Wait (join) on all parallel processses
        '''
        for p in self.processes:
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
