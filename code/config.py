# -*- coding: utf-8 -*-

from graphics.config import config as graph_cfg

class config:
    # Global neurorack info
    class neurorack:
        device      = 'Neurorack'
        version     =  0.01
    
    # Global screen info
    class screen:
        # Screen modes
        mode_init   = 0
        mode_main   = 1
        mode_menu   = 2
        # General screen properties
        height      = 240
        width       = 180
        # Display config
        padding     = -2
        main_x      = 0
        bg_image    = './data/acids.png' 
    
    # Global audio info
    class audio:
        # Screen modes
        mode_idle   = 0
        mode_burnin = 1
        mode_play   = 2
        mode_rec    = 3
        mode_busy   = 4
        # General screen properties
        volume      = 1.0
        stereo      = 0.0
    
    class events:
        none        = -1
        button      = 0
        rotary      = 1
        gate0       = 2
        gate1       = 3
        cv2         = 4
        cv3         = 5
        cv4         = 6
        cv5         = 7

    # Add the graphics classes
    colors = graph_cfg.colors
    text = graph_cfg.text
    