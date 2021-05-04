import multiprocessing as mp
from multiprocessing import Process, Queue

class Input:
    
    def __init__(self, name):
        print('Initializing input ' + name)
        self.name = name

    def callback(self, state, queue):
        print(self.name)
        
class ThreadInput(Input):

    def __init__(self):
        super().__init__(name)

class ProcessInput(Input):

    def __init__(self, name):
        super().__init__(name)

    def callback(self, state, queue):
        super().callback(state, queue)
        print(mp.current_process())

class InterruptInput(Input):

    def __init__(self):
        print('Init')

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
