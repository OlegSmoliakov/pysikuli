"""
Fast cross-platform python module for desktop gui automation
"""

from time import sleep

# import config file constants and classes
from ._config import Key, Button, config

MONITOR_REGION = config.MONITOR_REGION
MONITOR_RESOLUTION = config.MONITOR_RESOLUTION

# import optional helpfull utils for the user
from ._utils import (
    getLocation,
    _getRegion,
    cleanupPics,
)

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
    grab,
    find,
    findAny,
    getPixel,
    wait,
    exist,
    imageExistFromFolder,
    existCount,
    waitWhileExist,
)


# import the window management functions
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


__author__ = "Oleg Smoliakov"
__version__ = "0.0.13"

_REG_FORMAT = "x1y1x2y2"


def getRegion(interval=0.5):
    """
    getRigion helps to determine the coordinates of a region by hovering
    the mouse over the points of the screen you want to see.

    the region requires 2 points: left-top and right-bottom.
    if you hold the mouse on the same spot for 3 `intervals`
    the point will be captured and capture sound will be played *by default

    Args:
        `interval` (float): time in seconds, which uses for delay
        between each mouse posuition capture  . Defaults to 0.5.

    Returns:
        updated clipboard with prepared region like: "1, 2, 3, 4"
        also print this region in console
    """
    return _getRegion(_REG_FORMAT, interval)


if config.UNIX:
    REQUIRED_PKGS_LINUX = ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]
    from ._unix import _apt_pkgs_installation_check

    _apt_pkgs_installation_check(REQUIRED_PKGS_LINUX)
