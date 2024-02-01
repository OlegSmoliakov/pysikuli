import re
import subprocess
import logging

import pyperclip

from AppKit import NSScreen
from pynput.keyboard import Key


class MacKey:
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

    cmd = Key.cmd
    cmd_r = Key.cmd_r
    delete = Key.backspace

    option = Key.alt
    option_r = Key.alt_r
    return_r = Key.enter


# NOTE depricated
def _getRefreshRate():
    maxRefreshRate = 0
    for each in NSScreen.screens():
        if each.maximumFramesPerSecond() > maxRefreshRate:
            maxRefreshRate = each.maximumFramesPerSecond()
            # print(f"{each.localizedName()}: {each.maximumFramesPerSecond()}Hz")
    else:
        return maxRefreshRate


# NOTE depricated
def _activateWindow(app_name: str):
    # TODO: activate only if the application has not been activated before
    cmd = f"osascript -e 'activate application \"{app_name}\"'"
    ans = subprocess.call(cmd, shell=True)
    if ans:
        logging.warning(f"activateWindow(): {app_name} failed")
        return 1
    logging.debug(f"activateWindow(): {app_name} activated")
    return 0


# NOTE depricated
def _getWindowRegion(app_name: str):
    APPLESCRIPT = f"""
    tell application "{app_name}" to get the bounds of window 1
    """
    response = str(
        subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True).stdout
    )
    if response == "b''":
        error_text = f"Couldn't find '{app_name}' window, current response: {response}"
        logging.fatal(error_text)
        raise OSError(error_text)
    response = [int(i) for i in re.sub(r"[^0-9,]", "", response).split(",")]
    region = [response[0], response[1], response[2] - 1, response[3] - 1]
    return region


# NOTE depricated
def _minimizeWindow(app_name: str):
    APPLESCRIPT = f"""
    tell application "{app_name}" 
        set miniaturized of window 1 to true
    end tell
    """
    print(subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True))


# NOTE depricated
def _unminimizeWindow(app_name: str):
    # TODO: doesn't work
    APPLESCRIPT = f"""
    tell application "{app_name}"
        activate
        delay 1
        end tell
    tell application "System Events" to set visible of process "{app_name}" to true
    """
    print(subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True))


def _copy(text):
    return pyperclip.copy(text)


def _paste():
    return pyperclip.paste()
