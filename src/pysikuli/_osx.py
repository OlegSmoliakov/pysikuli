import re
import subprocess
import logging

import Quartz

from Quartz import CoreGraphics as CG
from AppKit import NSWorkspace, NSApplicationActivateIgnoringOtherApps
from pynput.keyboard import Key


class MacKey:
    alt = Key.alt
    alt_r = Key.alt_r
    alt_gr = Key.alt_gr
    shift = Key.shift
    shift_r = Key.shift_r
    ctrl = Key.ctrl
    ctrl_r = Key.ctrl_r
    caps_lock = Key.caps_lock
    left = Key.left
    right = Key.right
    up = Key.up
    down = Key.down
    page_down = Key.page_down
    page_up = Key.page_up
    home = Key.home
    end = Key.end
    esc = Key.esc
    space = Key.space
    tab = Key.tab
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


def getRefreshRate():
    main_display_id = CG.CGMainDisplayID()
    mode = CG.CGDisplayCopyDisplayMode(main_display_id)
    refresh_rate = CG.CGDisplayModeGetRefreshRate(mode)

    return int(refresh_rate)


def getMonitorRegion():
    main_display_id = CG.CGMainDisplayID()
    display_bounds = CG.CGDisplayBounds(main_display_id)
    region = (
        int(display_bounds.origin.x),
        int(display_bounds.origin.y),
        int(display_bounds.size.width),
        int(display_bounds.size.height),
    )

    return region


def activateWindow(window_title: str):
    # store info about all apps
    element = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
    )
    element = [x for x in element if x[Quartz.kCGWindowLayer] == 0]

    for window_info in element:
        if window_info[Quartz.kCGWindowName] == window_title:
            owner_pid = window_info[Quartz.kCGWindowOwnerPID]

    apps = NSWorkspace.sharedWorkspace().runningApplications()

    for app in apps:
        if app.processIdentifier() == owner_pid:
            window = app

    window.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
    # NOTE can be used to hide, terminate


def getAllAppsWindowsTitles():
    """Get the list of titles of all visible windows

    Returns
    -------
        list[str]: list of titles as strings
    """

    apps = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
    )
    # sort by 0 layer, to avoid system applications and applications that are not on current screen
    apps = [app for app in apps if app[Quartz.kCGWindowLayer] == 0]

    apps_list = {}
    for app in apps:
        window_name = app[Quartz.kCGWindowName]
        app_name = app[Quartz.kCGWindowOwnerName]

        # skip icons
        if app_name == "Item-0":
            continue

        if app_name in apps_list:
            apps_list[app_name].append(window_name)
        else:
            apps_list[app_name] = [window_name]

    return apps_list


def getAllTitles():
    """Retrieves a list of all window titles from all running applications on current screen.

    Returns
    --------
        list: A list of unique window titles.
    """
    titles = []
    for value in getAllAppsWindowsTitles().values():
        titles.extend(value)
    titles = list(set(titles))
    return titles


def getAllAppsNames():
    """Get the list of names of all running applications on current screen

    Returns
    --------
        list[str]: list of names as strings
    """

    return list(getAllAppsWindowsTitles().keys())


# depricated
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


# depricated
def _minimizeWindow(app_name: str):
    APPLESCRIPT = f"""
    tell application "{app_name}" 
        set miniaturized of window 1 to true
    end tell
    """
    print(subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True))


# depricated
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
