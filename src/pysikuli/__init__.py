"""
:author: Oleg Smoliakov
:license: GNU GENERAL PUBLIC LICENSE Version 3
:copyright (c) 2023 Oleg Smoliakov
"""

__author__ = "Oleg Smoliakov"
__version__ = "0.0.1"


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
)


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
from ._main import _checkRegion as checkRegion
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
