"""

 ~ Neurorack project ~
 Parallel : Base classes for handling parallel system
 
 This file defines all multiprocessing and multi-threading classes.
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

import multiprocessing as mp
from multiprocessing import Process, Queue

class Input:
    '''
        The Input class defines basic functions for neurorack input.
    '''
    
    def __init__(self, 
                 name: str):
        '''
            Constructor - Creates a new instance of the Input class.
            Parameters:
                name:       [str]
                            Name of the input
        '''
        print('Initializing input ' + name)
        self.name = name

    def callback(self, state, queue):
        '''
            Function for starting the input.
            Here it will be a sequential (blocking) input
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
        '''
        print(self.name)
        
class ThreadInput(Input):
    '''
        The ThreadInput class defines threaded versions of the inputs.
    '''

    def __init__(self, 
                 name: str):
        '''
            Constructor - Creates a new instance of the ThreadInput class.
            Parameters:
                name:       [str]
                            Name of the input
        '''
        super().__init__(name)

    def callback(self, state, queue):
        '''
            Function for starting the input.
            Here it will be a threaded input
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
        '''
        super().callback(state, queue)
        print(mp.current_process())

class ProcessInput(Input):

    def __init__(self, 
                 name: str):
        '''
            Constructor - Creates a new instance of the ProcessInput class.
            Parameters:
                name:       [str]
                            Name of the input
        '''
        super().__init__(name)

    def callback(self, state, queue):
        '''
            Function for starting the input.
            Here it will be an independent process input
            Parameters:
                state:      [Manager]
                            Shared memory through a Multiprocessing manager
                queue:      [Queue]
                            Shared memory queue through a Multiprocessing queue
        '''
        super().callback(state, queue)
        print(mp.current_process())

class InterruptInput(Input):

    def __init__(self, 
                 name: str):
        '''
            Constructor - Creates a new instance of the InterruptInput class.
            Parameters:
                name:       [str]
                            Name of the input
        '''
        super().__init__(name)

if __name__ == '__main__':
    print('Testing parallel system')
    nb_cpus = mp.cpu_count()
    print('Detected ' + str(nb_cpus) + ' CPUs')
    queue = Queue()
    pool = mp.Pool(nb_cpus)
    input_types = ['cvs', 'rotary', 'screen']
    processes = []
    for in_v in input_types:
        cur_o = ProcessInput(in_v)
        cur_p = Process(target=cur_o.callback, args=(None, queue))
        processes.append(cur_p)
    for p in processes:
        p.start()
    for p in processes:
        p.join()
