import logging
import enum

try:
    import win32gui as w32
except:
    raise ImportError("Please install win32gui")

import pyperclip

from pynput.keyboard import Key


class WinKey(enum.Enum):
    alt = Key.alt
    alt_r = Key.alt_r
    alt_gr = Key.alt_gr
    caps_lock = Key.caps_lock
    ctrl = Key.ctrl
    ctrl_r = Key.ctrl_r
    down = Key.down
    end = Key.end
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

    win = Key.cmd
    enter = Key.enter
    delete = Key.delete
    backspace = Key.backspace

    insert = Key.insert
    menu = Key.menu
    num_lock = Key.num_lock
    pause = Key.pause
    print_screen = Key.print_screen
    scroll_lock = Key.scroll_lock


# NOTE depricated
class ActiveWindow:
    final_hwnd = 0

    def winEnumHandler(self, hwnd, ctx):
        if w32.IsWindowVisible(hwnd) and self.name in w32.GetWindowText(hwnd).lower():
            self.final_hwnd = hwnd
            print(hwnd, w32.GetWindowText(hwnd))

    def set_foreground(self, name: str):
        self.name = name.lower()
        w32.EnumWindows(self.winEnumHandler, None)
        """put the window in the foreground"""
        print(self.final_hwnd, "selected")
        w32.SetForegroundWindow(self.final_hwnd)


def _copy(text):
    return pyperclip.copy(text)


def _paste():
    return pyperclip.paste()


# NOTE depricated
def _activateWindow(app_name: str):
    ActiveWindow().set_foreground(app_name)
    logging.debug("{0} activated".format(app_name))
