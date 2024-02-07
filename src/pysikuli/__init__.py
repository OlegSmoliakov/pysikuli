"""
Fast cross-platform python module for desktop gui automation
"""

from time import sleep

# import config file constants and classes
from ._config import Button, config

if config.OSX:
    from ._osx import MacKey as Key
elif config.WIN:
    from ._win import WinKey as Key
elif config.UNIX:
    from ._unix import UnixKey as Key
else:
    raise OSError("Can't recognize OS")

# import optional helpfull utils for the user
from ._utils import (
    getLocation,
    _getRegion,
    cleanupPics,
)

if config.UNIX:
    from ._unix import _apt_pkgs_installation_check

    def apt_pkgs_installation_check():
        return _apt_pkgs_installation_check(_config._REQUIRED_PKGS_LINUX)


from ._main import Region

# import keyboard-related functions
from ._main import (
    tap,
    keyUp,
    keyDown,
    hotkey,
    write,
    paste,
    copyToClip,
    pasteFromClip,
    pressedKeys,
)


# import mouse-related functions
from ._main import (
    click,
    rightClick,
    mouseDown,
    mouseUp,
    mouseMove,
    mouseSmoothMove,
    mouseMoveRelative,
    mousePosition,
    scroll,
    hscroll,
    vscroll,
    dragDrop,
)


# import Screenshot-related functions
from ._main import (
    exist,
    existAny,
    existCount,
    existFromFolder,
    find,
    grab,
    getPixel,
    wait,
    waitWhileExist,
)


# import the window control functions
from ._main import (
    activateWindow,
    activateWindowUnderMouse,
    activateWindowAt,
    getWindowRegion,
    getWindowWithTitle,
    getWindowUnderMouse,
    getAllWindowsTitle,
    minimizeWindow,
    maximizeWindow,
    closeWindow,
    windowExist,
)


# import pymsgbox functions
from ._main import (
    popupAlert,
    popupPassword,
    popupConfirm,
    popupPrompt,
)


# importing the file management functions
from ._main import (
    saveNumpyImg,
    saveScreenshot,
    deleteFile,
)

MONITOR_REGION = config.MONITOR_REGION
MONITOR_RESOLUTION = config.MONITOR_RESOLUTION

__author__ = "Oleg Smoliakov"
__version__ = "0.0.17"

_REG_FORMAT = "x1y1x2y2"


def getRegion(interval=0.5):
    """
    getRigion helps to determine the Region coordinates.

    Simply by hovering your mouse over points on the screen.
    The region requires 2 points, left-top and right-bottom.
    If you hold the mouse on the same spot for 3 `intervals`
    the point will be captured and capture sound will be played by default

    Args:
        `interval` (float): time in seconds, which uses for delay
        between each mouse posuition capture  . Defaults to 0.5.

    Returns:
        updated clipboard with prepared region like: "Region(1, 2, 3, 4)"
        also print this region in console
    """
    return _getRegion(_REG_FORMAT, interval)
