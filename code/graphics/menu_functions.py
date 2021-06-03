# -*- coding: utf-8 -*-

def model_play(state, signals, params):
    print('[Function] - Play model')
    state["audio"]["event"].value = 'model_play'
    signals["audio"].set()


def model_select(state, signals, params):
    print('[Function] - Select model')
    state["audio"]["event"].value = 'model_play'
    state["audio"]["model"].value = params["model"]
    signals["audio"].set()
    pass


def model_reload(state, signals, params):
    print('[Function] - Reload model')
    state["audio"]["event"].value = 'model_reload'
    signals["audio"].set()


def model_benchmark(state, signal, params):
    pass


def assign_cv(state, signal, params):
    pass


def assign_button(state, signal, params):
    pass


def assign_rotary(state, signal, params):
    pass