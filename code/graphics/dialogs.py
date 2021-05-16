# -*- coding: utf-8 -*-
"""

 ~ Neurorack project ~
 Dialogs : Set of classes for dialogs graphical objects
 
 This dialogs are items that take the full screen for interaction.
 Examples are "confirm" (ok/cancel) or "spinner" (loading) dialogs
 
 Author               : Philippe Esling, Ninon Devis, Martin Vert
                        <{esling, devis}@ircam.fr>

"""

class Dialog():
    
    def __init__(self):
        pass

    def render(self, ctx=None):
        raise NotImplementedError
        
class ConfirmDialog(Dialog):
    
    def __init__(self):
        super().__init__()

    def render(self, ctx=None):
        raise NotImplementedError
        
class SpinnerDialog(Dialog):
    
    def __init__(self):
        super().__init__()

    def render(self, ctx=None):
        raise NotImplementedError