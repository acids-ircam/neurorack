"""
Configuration constants used across the graphical interface system.
Includes color definitions, font paths, screen settings, and menu messages.
"""

class config:
    class colors:
        main = '#B80F0A'
        alt = '#581845'
        select = '#B8A9C9'
        white = '#FFFFFF'

    class text:
        font_main = './fonts/keanubold.ttf'
        font_alt = './fonts/dmpopmin.ttf'
        size_main = 18
        size_big = 24
        size_large = 30
        size_small = 16
        color_main = colors.main
        color_alt = colors.alt
        color_select = colors.select

    class menu:
        mode_basic = 0
        mode_dialog = 1
        mode_parameter = 2
        mode_wait = 3
        mode_hidden = 4

        confirm_cancel = 0
        confirm_ok = 1

        back_element = "< Back"
        exit_element = "< Exit"
        msg_ok = "Ok"
        msg_cancel = "Cancel"
        msg_run = "You are about to run"
        msg_proceed = "Proceed?"
        msg_results = "'%s'"
        msg_code = "Return Code: %x"
        msg_output = "Output:"
        accepted_types = ["function", "list", "parameter", "shell", "slider"]

    class events:
        none = -1
        button = 0
        rotary = 1

    class screen:
        mode_init = 0
        mode_main = 1
        mode_menu = 2
        height = 240
        width = 180
        padding = -2
        main_x = 0
        bg_image = './data/acids.png'
