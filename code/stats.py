"""

 ~ Neurorack project ~
 Stats : Retrieve a set of system properties
 
 This allows to check the system state (to be used on the LCD display).
 Currently, the stats retrieved are :
     - IP of the board
     - CPU Load
     - Memory use
     - Disk Use
     - CPU Temperature
 
 Author               :  Ninon Devis, Philippe Esling, Martin Vert
                        <{devis, esling}@ircam.fr>
 
 All authors contributed equally to the project and are listed aphabetically.

"""

import time
import subprocess

class Stats():
    '''
        The Stats class contains system properties and allows to retrieve them
    '''
    def __init__(self):
        '''
            Constructor - Creates new instance and retrieve initial stats
        '''
        # Retrieve stats
        self.retrieve_stats()

    def retrieve_stats(self):
        '''
            Constructor - Creates a new instance of the Navigation class.
            Shell scripts for system monitoring from here:
            https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
            @TODO: Would be useful to monitor GPU states and also audio engine 
        '''
        cmd = "hostname -I | cut -d\' \' -f1"
        self.ip = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        self.cpu = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        self.memory = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
        self.disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'"
        self.temperature = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return self.ip, self.cpu, self.memory, self.disk, self.temperature
