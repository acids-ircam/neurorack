# -*- coding: utf-8 -*-

class config:
    class colors:
        main            = '#B80F0A'
        alt             = '#581845'
        select          = '#B8A9C9'
        white           = '#FFFFFF'
    
    class text:
        font_main       = './fonts/keanubold.ttf'
        font_alt        = './fonts/dmpopmin.ttf'
        size_main       = 18
        size_big        = 24
        size_large      = 30
        size_small      = 16
        color_main      = '#B80F0A'
        color_alt       = '#581845'
        color_select    = '#B8A9C9'
        
    class menu:
        mode_basic      = 0
        mode_confirm    = 1
        mode_output     = 2
        mode_hidden     = 3
        confirm_cancel  = 0
        confirm_ok      = 1
        back_element    = "< Back"
        exit_element    = "< Exit"
        msg_ok          = "OK"
        msg_cancel      = "CANCEL"
        msg_run         = "You are about to run"
        msg_proceed     = "Proceed?"
        msg_results     = "'%s'"
        msg_code        = "Return Code: %x"
        msg_output      = "Output:"
        accepted_types  = ["builtin", "list", "parameter", "shell"]
    
    class events:
        none        = -1
        button      = 0
        rotary      = 1