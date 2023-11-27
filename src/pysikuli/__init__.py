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
    return _getRegion(_REGION_FORMAT, interval)


if Config.UNIX:
    REQUIRED_PKGS_LINUX = ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]
    from ._unix import _apt_pkgs_installation_check

    _apt_pkgs_installation_check(REQUIRED_PKGS_LINUX)
