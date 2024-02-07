import re

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


def _copy(text: str):
    run(
        ["xsel", "-b"],
        input=text,
        encoding="utf-8",
    )


def _paste():
    return run(["xsel", "-b"], capture_output=True, encoding="utf-8").stdout


def _apt_pkgs_installation_check(required_pkgs_name: tuple[str] or list):
    installed_pkgs = run(
        ["apt", "list", "--installed"],
        capture_output=True,
        encoding="utf-8",
    ).stdout

    # prepare pattern from required pakages for re search
    pattern = b"\n" + required_pkgs_name[0].encode("utf-8") + b"/"
    for x in range(1, len(required_pkgs_name)):
        pattern += b"|\n" + required_pkgs_name[x].encode("utf-8") + b"/"

    # get and prepare found pakages for re search
    found_pkgs = re.findall(pattern, installed_pkgs.encode("utf-8"))
    format_required_pkgs_name = [
        b"\n" + x.encode("utf-8") + b"/" for x in required_pkgs_name
    ]

    missing_pkgs = set(format_required_pkgs_name).symmetric_difference(set(found_pkgs))

    if missing_pkgs == set():
        return None
    else:
        text = ""
        for pkg in missing_pkgs:
            pkg = pkg.strip(b"\n").strip(b"/").decode("utf-8")
            text = f"{text} {pkg}"
        print(
            f"\n\nPlease install the missing packages:{text}\n\nOn Ubuntu/Debian use this command: sudo apt install{text}"
        )


# NOTE depricated
def _getRefreshRate():
    output = run(
        ["xrandr"],
        capture_output=True,
        encoding="utf-8",
    ).stdout
    current_refrash_rate = re.findall(".{6}\*", output)[0]
    current_refrash_rate = re.sub("\..+", "", current_refrash_rate)
    return int(current_refrash_rate)
