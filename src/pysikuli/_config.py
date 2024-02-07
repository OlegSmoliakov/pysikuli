import os
import platform

import pymonctl as pmc
import pymsgbox as pmb

from pynput.keyboard import Key
from pynput.mouse import Button


_REQUIRED_PKGS_LINUX = ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]
_MONITOR_REGION = pmc.getPrimary().box
_MONITOR_RESOLUTION = (
    _MONITOR_REGION[2],
    _MONITOR_REGION[3],
)
_SUPPORTED_PIC_FORMATS = [
    "bmp",
    "jfif",
    "jpeg",
    "jpe",
    "jpg",
    "png",
    "tiff",
    "tif",
]


def getOS():
    OSX, WIN, UNIX = False, False, False
    system = platform.system()

    if system == "Darwin":
        OSX = True
    elif system == "Windows":
        WIN = True
    elif system == "Linux":
        UNIX = True
    else:
        raise OSError(f"Can't recognize OS: {system}")

    return OSX, WIN, UNIX


def getPlatformModule(OSX, WIN, UNIX):
    if OSX:
        from . import _osx as platformModule
    elif WIN:
        from . import _win as platformModule
    elif UNIX:
        from . import _unix as platformModule
    else:
        raise OSError(f"No OS is selected")
    return platformModule


def getDefaultFailsafeHotkey(OSX):
    if OSX:
        return [Key.alt, Key.shift, "c"]
    else:
        return [Key.ctrl, Key.alt, "z"]


class Config:
    """
    Class for storing pysikuli global variables with user acces
    """

    # TODO: Sleep value should vary with the platform. http://stackoverflow.com/q/1133857

    # platform selection
    OSX, WIN, UNIX = getOS()
    _platformModule = getPlatformModule(OSX, WIN, UNIX)

    # if the time is less than this value, the sleep time isn't accurate enough
    MIN_SLEEP_TIME = 0.02

    # The number of seconds of pause after EVERY public function call. Useful for debugging
    PAUSE_BETWEEN_ACTION = 0

    # Failsafe constants

    # If the mouse is within FAILSAFE_REGIONS and FAILSAFE is True, a FailSafeException exception will be raised which will abort execution.
    FAILSAFE = True
    FAILSAFE_REGIONS = [(0, 0, 0, 0)]

    @property
    def FAILSAFE_HOTKEY(self):
        if self._FAILSAFE_HOTKEY is None:
            self._FAILSAFE_HOTKEY = getDefaultFailsafeHotkey(self.OSX)
        return self._FAILSAFE_HOTKEY

    @FAILSAFE_HOTKEY.setter
    def FAILSAFE_HOTKEY(self, val):
        self._FAILSAFE_HOTKEY = val

    # Constants for image search function

    # This option almost doubles the speed by using compressed images in image recognition,
    # but degrades unambiguous image recognition.
    # Use this parameter as a compression divider, for instance:
    # If the value is 1 - the image size doesn't change (width / 1 and height / 1)
    # If the value is 2 - the image will become x4 times smaller, (width / 2 and height / 2).
    # If the value greater than 4, the speed will increase slightly.
    # Divider must be positive and can be float
    COMPRESSION_RATIO = 2

    # This parameter increases speed by about 30%, but degrades unambiguous image recognition
    GRAYSCALE = True

    # The value after which all search functions return positive
    MIN_PRECISION = 0.8
    # The time limit for search functions. If it is exceeded, None is returned
    MAX_SEARCH_TIME = 2.0

    REFRESH_RATE = None
    if not REFRESH_RATE:
        REFRESH_RATE = int(pmc.getPrimary().frequency)
        if REFRESH_RATE <= 0:
            REFRESH_RATE = 60

    # Each TIME_STEP in seconds a image searching takes a new screenshot for next analysis
    # Each TIME_STEP in seconds tap and write takes after each key press
    TIME_STEP = 0

    # If active, pysikuli will wait for the window management functions to complete their execution.
    WINDOW_WAITING_CONFIRMATION = True

    @property
    def MONITOR_REGION(self) -> tuple[int, int, int, int]:
        return _MONITOR_REGION

    @property
    def MONITOR_RESOLUTION(self) -> tuple[int, int]:
        return _MONITOR_RESOLUTION

    # Constants for pymsgbox module
    @property
    def OK_TEXT(self):
        return self._OK_TEXT

    @OK_TEXT.setter
    def OK_TEXT(self, val: str):
        self._OK_TEXT = val
        pmb.OK_TEXT = str(val)

    @property
    def CANCEL_TEXT(self):
        return self._CANCEL_TEXT

    @CANCEL_TEXT.setter
    def CANCEL_TEXT(self, val: str):
        self._CANCEL_TEXT = val
        pmb.CANCEL_TEXT = str(val)

    @property
    def ROOT_WINDOW_POSITION(self):
        return self._ROOT_WINDOW_POSITION

    @ROOT_WINDOW_POSITION.setter
    def ROOT_WINDOW_POSITION(self, val: tuple[int]):
        self._ROOT_WINDOW_POSITION = val
        pmb.rootWindowPosition = f"+{val[0]}" f"+{val[1]}"

    @property
    def PROPORTIONAL_FONT_SIZE(self):
        return self._PROPORTIONAL_FONT_SIZE

    @PROPORTIONAL_FONT_SIZE.setter
    def PROPORTIONAL_FONT_SIZE(self, val: int):
        self._PROPORTIONAL_FONT_SIZE = val
        pmb.PROPORTIONAL_FONT_SIZE = val

    @property
    def MONOSPACE_FONT_SIZE(self):
        return self._MONOSPACE_FONT_SIZE

    @MONOSPACE_FONT_SIZE.setter
    def MONOSPACE_FONT_SIZE(self, val: int):
        self._MONOSPACE_FONT_SIZE = val
        pmb.MONOSPACE_FONT_SIZE = val

    @property
    def TEXT_ENTRY_FONT_SIZE(self):
        return self._TEXT_ENTRY_FONT_SIZE

    @TEXT_ENTRY_FONT_SIZE.setter
    def TEXT_ENTRY_FONT_SIZE(self, val: int):
        self._TEXT_ENTRY_FONT_SIZE = val
        pmb.TEXT_ENTRY_FONT_SIZE = val

    # Constants for the mouse button names:
    MOUSE_PRIMARY_BUTTON = Button.left
    MOUSE_SECONDARY_BUTTON = Button.right
    MOUSE_SPEED = 2

    # Constants for utils module
    SOUND_ON = True
    SOUND_CAPTURE_PATH = os.path.join(
        os.path.dirname(__file__), "tools_data/_capture.mp3"
    )
    SOUND_FINISH_PATH = os.path.join(
        os.path.dirname(__file__), "tools_data/_finish.mp3"
    )

    DEBUG_SETTINGS = {
        "PAUSE_BETWEEN_ACTION": 0.5,
        "TIME_STEP": round(1 / REFRESH_RATE, 5),
        "MOUSE_SPEED": 1,
    }

    _DEFAULT_SETTINGS = {
        "PAUSE_BETWEEN_ACTION": 0,
        "TIME_STEP": 0,
        "MOUSE_SPEED": 1,
    }

    @property
    def DEBUG(self):
        return self._DEBUG

    @DEBUG.setter
    def DEBUG(self, val):
        self._DEBUG = val
        if val == True:
            for key, value in self.DEBUG_SETTINGS.items():
                setattr(self, key, value)
        elif val == False:
            for key, value in self._DEFAULT_SETTINGS.items():
                setattr(self, key, value)

    def __init__(self):
        self._OK_TEXT = "OK"
        self._CANCEL_TEXT = "Cancel"

        # 400 and 100 is min size of pymsgbox window
        root_x = int(_MONITOR_RESOLUTION[0] / 2 - 400 / 2)
        root_y = int(_MONITOR_RESOLUTION[1] / 2 - 100 / 2)

        self._ROOT_WINDOW_POSITION = (root_x, root_y)
        self._PROPORTIONAL_FONT_SIZE = 10
        self._MONOSPACE_FONT_SIZE = 9
        self._TEXT_ENTRY_FONT_SIZE = 12

        self._DEBUG = False
        self._FAILSAFE_HOTKEY = None


config = Config()
