import re

import pymonctl as pmc

from subprocess import run
from pynput.keyboard import Key


class UnixKey:
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

    win = Key.cmd
    enter = Key.enter
    delete = Key.delete
    backspace = Key.backspace
    ctrl = Key.ctrl
    ctrl_r = Key.ctrl_r

    insert = Key.insert
    menu = Key.menu
    num_lock = Key.num_lock
    pause = Key.pause
    print_screen = Key.print_screen
    scroll_lock = Key.scroll_lock


def _apt_install(packages: list | tuple):
    command = ["sudo", "apt-get", "install"]
    for package in packages:
        command.append(package)

    run(["sudo", "apt-get", "update"], encoding="utf-8")
    run(command, encoding="utf-8")


def _apt_check(required_pkgs_name: tuple[str] | list[str]):
    command = ["apt", "list", "--installed"]
    missing_pkgs = []

    for pkg in required_pkgs_name:
        temp_command = command.copy()
        temp_command.append(pkg)

        output = run(
            temp_command,
            capture_output=True,
            encoding="utf-8",
        ).stdout

        if not "installed" in output:
            missing_pkgs.append(pkg)

    if missing_pkgs == []:
        print("The requirements have already been installed")
    else:
        print("Installing packages: " + ", ".join(missing_pkgs))
        _apt_install(missing_pkgs)


def _getRefreshRate():
    return int(pmc.getPrimary().frequency)


def _getMonitorRegion():
    return tuple(int(x) for x in pmc.getPrimary().box)
