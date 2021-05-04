import Jetson.GPIO as gpio
from rotary import Rotary
from cv import CVChannels
from audio import Audio
#from button import Button
import multiprocessing as mp
from multiprocessing import Process, Manager, Queue

class Neurorack():
    N_CVs = 6

    def __init__(self):
        # Init states of information
        self.init_state()
        # Create audio engine
        self.audio = Audio()
        # Create rotary
        self.rotary = Rotary()
        # Create CV channels
        self.cvs = CVChannels()
        gpio.cleanup()
        # Need to import Screen after cleanup
        from screen import Screen
        self.screen = Screen()
        # List of objects to create processes
        self.objects = [self.screen, self.rotary, self.cvs]
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
        # Use a MP Manager
        self.manager = Manager()
        self.state = self.manager.dict()
        self.state['cv'] = self.manager.list([0.0] * self.N_CVs)
        self.state['rotary'] = 0
        self.state['button'] = 0
        self.state['menu'] = 0
        self.state['audio'] = 0
            
    def start(self):
        for p in self.processes:
            p.start()

    def run(self):
        for p in self.processes:
            p.join()

if __name__ == '__main__':
    neuro = Neurorack()
    neuro.start()
    neuro.run()
