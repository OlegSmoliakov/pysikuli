import logging
import re
import subprocess
import time

import Quartz
from AppKit import NSApplicationActivateIgnoringOtherApps, NSWorkspace
from pynput.keyboard import Key
from Quartz import CoreGraphics as CG

log = logging.getLogger(__name__)


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
    # NOTE can be used to hide, terminate

    # store info about all apps
    element = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
    )
    element = [x for x in element if x[Quartz.kCGWindowLayer] == 0]

    for window_info in element:
        if window_info[Quartz.kCGWindowName] == window_title:
            owner_pid = window_info[Quartz.kCGWindowOwnerPID]
            owner_name = window_info[Quartz.kCGWindowOwnerName]

    if "owner_pid" not in locals():
        return False

    apps = NSWorkspace.sharedWorkspace().runningApplications()

    for app in apps:
        if app.processIdentifier() == owner_pid or app.localizedName() == owner_name:
            window = app

    window.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
    time.sleep(0.0001)  # wait for the window to activate

    return is_window_active(window_title)


def is_window_active(window_title):
    """
    Check if a window with the specified title is active.

    Args:
        window_title (str): The title of the window.

    Returns:
        bool: True if the window is active, False otherwise.
    """
    # Get the active application
    active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
    active_app_name = active_app.localizedName()

    # Get the list of on-screen windows
    options = Quartz.kCGWindowListOptionOnScreenOnly
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    for window in window_list:
        if (
            window.get("kCGWindowName", "") == window_title
            and window.get("kCGWindowOwnerName", "") == active_app_name
        ):
            return True
    return False


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


def getAllTitles() -> list[str]:
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


def is_hidpi_enabled() -> bool:
    main_display_id = Quartz.CGMainDisplayID()
    display_mode = Quartz.CGDisplayCopyDisplayMode(main_display_id)

    pixel_width = Quartz.CGDisplayPixelsWide(main_display_id)
    pixel_height = Quartz.CGDisplayPixelsHigh(main_display_id)

    point_width = Quartz.CGDisplayModeGetPixelWidth(display_mode)
    point_height = Quartz.CGDisplayModeGetPixelHeight(display_mode)

    log.debug(f"pixel_width: {pixel_width}, pixel_height: {pixel_height}")
    log.debug(f"point_width: {point_width}, point_height: {point_height}")

    result = pixel_width != point_width or pixel_height != point_height

    return result
