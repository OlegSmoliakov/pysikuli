"""
Fast cross-platform python module for desktop gui automation
"""

__author__ = "Oleg Smoliakov"
__version__ = "0.0.19"

from time import sleep

# import config file constants and classes
from ._config import Button, config

if config.OSX:
    from ._osx import MacKey as Key
elif config.WIN:
    from ._win import WinKey as Key
elif config.UNIX:
    from ._unix import UnixKey as Key
    from ._unix import _apt_check

    def required_pkgs_check():
        return _apt_check(_config._REQUIRED_PKGS_LINUX)

else:
    raise OSError("Can't recognize OS")

# import optional helpfull utils for the user
from ._utils import (
    getLocation,
    getRegion,
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
    exist,
    existAny,
    existCount,
    existFromFolder,
    find,
    grab,
    getPixelRGB,
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
    minimizeWindow,
    maximizeWindow,
    closeWindow,
    windowExist,
)


# HACK
def getAllTitles():
    """Retrieves a list of all window titles from all running applications on current screen."""
    return config._platformModule.getAllTitles()


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
