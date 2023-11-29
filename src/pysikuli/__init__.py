"""
:author: Oleg Smoliakov
:license: GNU GENERAL PUBLIC LICENSE Version 3
:copyright (c) 2023 Oleg Smoliakov
"""

# import config file constants and classes
from ._config import Key, Config

# import optional helpfull utils for user
from ._utils import _getLocation as getLocation
from ._utils import _getRegion


from ._main import Region, MONITOR_REGION, MONITOR_RESOLUTION

# import keyboard-related functions
from ._main import _tap as tap
from ._main import _keyUp as keyUp
from ._main import _keyDown as keyDown
from ._main import _hotkey as hotkey
from ._main import _write as write
from ._main import _paste as paste
from ._main import _copyToClip as copyToClip
from ._main import _pasteFromClip as pasteFromClip

# import mouse-related functions
from ._main import _click as click
from ._main import _rightClick as rightClick
from ._main import _mouseDown as mouseDown
from ._main import _mouseUp as mouseUp
from ._main import _mouseMove as mouseMove
from ._main import _mouseMoveRelative as mouseMoveRealive
from ._main import _dragDrop as dragDrop


# import Screenshot-related functions
from ._main import _find as find
from ._main import _findAny as findAny
from ._main import _getPixel as getPixel
from ._main import _wait as wait
from ._main import _sleep as sleep
from ._main import _exist as exist

# import the window management function
from ._main import _activateWindow as activateWindow
from ._main import _getWindowRegion as getWindowRegion
from ._main import _minimizeWindow as minimizeWindow
from ._main import _unminimizeWindow as unminimizeWindow

# importing the file management function
from ._main import _saveNumpyImg as saveNumpyImg
from ._main import _saveScreenshot as saveScreenshot
from ._main import _deleteFile as deleteFile


__author__ = "Oleg Smoliakov"
__version__ = "0.0.2"

_REGION_FORMAT = "x1y1x2y2"


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
        also print this region in terminal
    """
    return _getRegion(_REGION_FORMAT, interval)


if Config.UNIX:
    REQUIRED_PKGS_LINUX = ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]
    from ._unix import _apt_pkgs_installation_check

    _apt_pkgs_installation_check(REQUIRED_PKGS_LINUX)
