# -*- coding: utf-8 -*-

def model_play(state, signals, params):
    print('[Function] - Play model')
    state["audio"]["event"].value = 'play_model'
    signals["audio"].set()

def model_select(state, signals, params):
    print('[Function] - Select model')
    pass

def model_reload(state, signals, params):
    print('[Function] - Reload model')
    pass

def model_benchmark(state, signal, params):
    pass

def params_volume(state, signal, params):
    pass

def params_stereo(state, signal, params):
    pass

def params_range(state, signal, params):
    pass

def assign_cv(state, signal, params):
    pass

def assign_button(state, signal, params):
    pass

def assign_rotary(state, signal, params):
    pass

def admin_stats(state, signal, params):
    pass

def about(state, signal, params):
    pass