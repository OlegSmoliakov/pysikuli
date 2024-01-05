import re

from subprocess import run


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
