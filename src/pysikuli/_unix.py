import re
from subprocess import run
from Xlib import display
from Xlib.ext import randr


def _copy(text: str):
    run(
        ["xsel", "-b"],
        input=text,
        encoding="utf-8",
    )


def _paste():
    return run(["xsel", "-b"], capture_output=True, encoding="utf-8").stdout


def _apt_pkgs_installation_check(required_pkgs_name: tuple or list):
    installed_pkgs = run(
        ["apt", "list", "--installed"],
        capture_output=True,
        encoding="utf-8",
    ).stdout

    pattern = b"\n" + required_pkgs_name[0].encode("utf-8") + b"/"
    for x in range(1, len(required_pkgs_name)):
        pattern += b"|\n" + required_pkgs_name[x].encode("utf-8") + b"/"

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


def _getRefreshRate():
    d = display.Display()
    default_screen = d.get_default_screen()
    info = d.screen(default_screen)

    resources = randr.get_screen_resources(info.root)
    active_modes = set()
    for crtc in resources.crtcs:
        crtc_info = randr.get_crtc_info(info.root, crtc, resources.config_timestamp)
        if crtc_info.mode:
            active_modes.add(crtc_info.mode)

    for mode in resources.modes:
        if mode.id in active_modes:
            return int(mode.dot_clock / (mode.h_total * mode.v_total))


def _activateWindow(app_name: str):
    raise NotImplementedError()


def _getWindowRegion(app_name: str):
    raise NotImplementedError()


def _minimizeWindow(app_name: str):
    raise NotImplementedError()


def _unminimizeWindow(app_name: str):
    raise NotImplementedError()