# module for storing pysikuli global variables with user access

import pyautogui as ag
import platform
import os

from PyHotKey import Key

# TODO: Sleep value should vary with the platform. http://stackoverflow.com/q/1133857
# TODO: calculate time_step via fps for all function i think it's doesn't affect speed

MOUSE_MOVE_SPEED = 0.0

# This option almost doubles the speed by using compressed images in image recognition,
# but degrades unambiguous image recognition.
# Use this parameter as a compression multiplier, for instance:
# if the value is 1 - the image size doesn't change (width / 1 and height / 1)
# if the value is 2 - the image will become x4 times smaller, (width / 2 and height / 2).
COMPRESSION_RATIO = 2

# This parameter increases speed by about 30%, but degrades unambiguous image recognition
DEFAULT_GRAYSCALE = True

# Main score for detection match
DEFAULT_PRECISION = 0.8
# After this time a image search will return a None result
DEFAULT_MAX_SEARCH_TIME = 2.0

# Not fully implemented CONSTANTS for automation calculation time_step
# MAX_REFRESH_RATE = getRefreshRate()
MAX_REFRESH_RATE = 60

# Each TIME_STEP in seconds a image searching takes a new screenshot for next analysis
DEFAULT_TIME_STEP = round(1 / MAX_REFRESH_RATE, 5)


# Constants for pyautogui module

# If the mouse is over a coordinate in FAILSAFE_POINTS and FAILSAFE is True, the FailSafeException is raised.
# The rest of the points are added to the FAILSAFE_POINTS list at the bottom of this file, after size() has been defined.
# The points are for the corners of the screen, but note that these points don't automatically change if the screen resolution changes.
FAILSAFE = True
FAILSAFE_POINTS = [(0, 0)]
FAILSAFE_HOTKEY = None
ag.FAILSAFE = FAILSAFE
ag.FAILSAFE_POINTS = FAILSAFE_POINTS


# The number of seconds to pause after EVERY public function call. Useful for debugging:
# TODO: implement this parameter for whole module
PAUSE_BETWEEN_ACTION = 0.001
ag.PAUSE = PAUSE_BETWEEN_ACTION


# Constants for the mouse button names:
MOUSE_LEFT = "left"
MOUSE_MIDDLE = "middle"
MOUSE_RIGHT = "right"


# Constants for tools module
SOUND_CAPTURE_PATH = os.path.join(os.path.dirname(__file__), "tools_data/_capture.mp3")
SOUND_FINISH_PATH = os.path.join(os.path.dirname(__file__), "tools_data/_finish.mp3")


OSX, WIN, UNIX = 0, 0, 0

system = platform.system()
if system == "Darwin":
    OSX = 1
    if not FAILSAFE_HOTKEY:
        FAILSAFE_HOTKEY = [Key.option, Key.shift, "c"]
elif system == "Windows":
    WIN = 1
    if not FAILSAFE_HOTKEY:
        FAILSAFE_HOTKEY = [Key.ctrl, Key.alt, "k"]
elif system == "Linux":
    UNIX = 1
    if not FAILSAFE_HOTKEY:
        FAILSAFE_HOTKEY = [Key.ctrl, Key.alt, "k"]
else:
    raise OSError("Can't recognize system OS")


class Key:
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
