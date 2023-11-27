from AppKit import NSScreen
import subprocess
import logging
import re


def _getRefreshRate():
    maxRefreshRate = 0
    for each in NSScreen.screens():
        if each.maximumFramesPerSecond() > maxRefreshRate:
            maxRefreshRate = each.maximumFramesPerSecond()
            # print(f"{each.localizedName()}: {each.maximumFramesPerSecond()}Hz")
    else:
        return maxRefreshRate


def _activateWindow(app_name: str):
    # TODO: activate only if the application has not been activated before
    cmd = f"osascript -e 'activate application \"{app_name}\"'"
    ans = subprocess.call(cmd, shell=True)
    if ans:
        logging.warning(f"activateWindow(): {app_name} failed")
        return 1
    logging.debug(f"activateWindow(): {app_name} activated")
    return 0


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


def _minimizeWindow(app_name: str):
    APPLESCRIPT = f"""
    tell application "{app_name}" 
        set miniaturized of window 1 to true
    end tell
    """
    print(subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True))


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
