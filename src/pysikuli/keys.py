import platform

from PyHotKey import Key

OSX, WIN, UNIX = 0, 0, 0

system = platform.system()
if system == "Darwin":
    OSX = 1
elif system == "Windows":
    WIN = 1
elif system == "Linux":
    UNIX = 1
else:
    raise NameError("Can't recognize system os")

class Key():
    alt = Key.alt
    alt_r = Key.alt_r
    option = Key.alt
    option_r = Key.alt_r
    alt_gr = Key.alt_gr
    backspace = Key.backspace
    caps_lock = Key.caps_lock
    cmd = Key.cmd
    win = Key.cmd
    cmd_r = Key.cmd_r
    win_r = Key.cmd_r
    ctrl = Key.ctrl
    ctrl_r = Key.ctrl_r
    delete = Key.delete
    down = Key.down
    end = Key.end
    enter = Key.enter
    return_r = Key.enter
    esc = Key.esc
    f1 = Key.f1
    f2 = Key.f2
    f3 = Key.f3
    f4 = Key.f4
    f5 = Key.f5
    f6 = Key.f6
    f7 = Key.f7
    f8 = Key.f8
    f9 = Key.f9
    f10 = Key.f10
    f11 = Key.f11
    f12 = Key.f12
    f13 = Key.f13
    f14 = Key.f14
    f15 = Key.f15
    f16 = Key.f16
    f17 = Key.f17
    f18 = Key.f18
    f19 = Key.f19
    f20 = Key.f20
    home = Key.home
    left = Key.left
    page_down = Key.page_down
    page_up = Key.page_up
    right = Key.right
    shift = Key.shift
    shift_r = Key.shift_r
    space = Key.space
    tab = Key.tab
    up = Key.up

    media_play_pause = Key.media_play_pause
    media_volume_mute = Key.media_volume_mute
    media_volume_down = Key.media_volume_down
    media_volume_up = Key.media_volume_up
    media_previous = Key.media_previous
    media_next = Key.media_next

    if not OSX:
        insert = Key.insert
        menu = Key.menu
        num_lock = Key.num_lock
        pause = Key.pause
        print_screen = Key.print_screen
        scroll_lock = Key.scroll_lock


if __name__ == "__main__":
    pass