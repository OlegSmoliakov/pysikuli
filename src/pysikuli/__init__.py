"""
:author: Oleg Smoliakov
:license: GNU GENERAL PUBLIC LICENSE Version 3
:copyright (c) 2023 Oleg Smoliakov
"""
import re
from subprocess import run, PIPE, Popen

# import config file constants and classes
from .config import Key
from .config import (
    MOUSE_MOVE_SPEED,
    MOUSE_LEFT,
    MOUSE_MIDDLE,
    MOUSE_RIGHT,
    DEFAULT_GRAYSCALE,
    COMPRESSION_RATIO,
    DEFAULT_PRECISION,
    DEFAULT_MAX_SEARCH_TIME,
    DEFAULT_TIME_STEP,
    FAILSAFE,
    FAILSAFE_POINTS,
    FAILSAFE_HOTKEY,
    OSX,
    WIN,
    UNIX,
    SOUND_CAPTURE_PATH,
    SOUND_FINISH_PATH,
)

# import optional helpfull utils for user
from ._utils import _getLocation as getLocation
from ._utils import _getRegion


from ._main import region

# import keyboard-related functions
from ._main import _tap as tap
from ._main import _keyUp as keyUp
from ._main import _keyDown as keyDown
from ._main import _hotkey as hotkey
from ._main import _write as write
from ._main import _paste as paste

# import mouse-related functions
from ._main import _click as click
from ._main import _rightClick as rightClick
from ._main import _mouseDown as mouseDown
from ._main import _mouseUp as mouseUp
from ._main import _mouseMove as mouseMove
from ._main import _mouseMoveRelative as mouseMoveRealive
from ._main import _dragDrop as dragDrop


# import Screenshot-related functions
from ._main import _exist as exist
from ._main import _find as find
from ._main import _findAny as findAny
from ._main import _getPixel as getPixel
from ._main import _regionValidate as regionValidate
from ._main import _wait as wait
from ._main import _sleep as sleep

# import the window management function
from ._main import _activateWindow as activateWindow
from ._main import _getWindowRegion as getWindowRegion
from ._main import _minimizeWindow as minimizeWindow
from ._main import _unminimazeWindow as unminimazeWindow

# importing the file management function
from ._main import _saveScreenshot as saveScreenshot
from ._main import _deleteFile as deleteFile


__author__ = "Oleg Smoliakov"
__version__ = "0.0.2"

REQUIRED_PKGS_LINUX = ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]


def getRegion(interval=0.5):
    return _getRegion(2, interval)


if UNIX:
    from ._unix import _apt_pkgs_installation_check

    _apt_pkgs_installation_check(REQUIRED_PKGS_LINUX)
