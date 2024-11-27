import functools
import logging
import math
import os
import time
from typing import Sequence

import cv2
import numpy as np
import pymsgbox as pmb
import pyperclip
import pywinctl as pwc

from mss.screenshot import ScreenShot
from mss import mss, tools
from PyHotKey import keyboard
from pynput.mouse import Controller as mouse_manager
from send2trash import send2trash

from ._config import config, Key, Button, _SUPPORTED_PIC_FORMATS, _MAX_SPEED

mouse = mouse_manager()


class PysikuliException(Exception):
    """
    pysikuli code will raise this exception class for any invalid actions. If pysikuli raises some other exception,
    you should assume that this is caused by a bug in pysikuli itself. (Including a failure to catch potential
    exceptions raised by pysikuli.)
    """

    pass


class FailSafeException(PysikuliException):
    """
    This exception is raised by pysikuli functions when the user puts the mouse cursor into one of the "failsafe
    points" (by default, one of the four corners of the primary monitor). This exception shouldn't be caught; it's
    meant to provide a way to terminate a misbehaving script.
    """

    pass


def _mouseFailSafeCheck():
    mousePos = mousePosition()
    for region in config.FAILSAFE_REGIONS:
        if region[0] <= mousePos[0] <= region[2] and region[1] <= mousePos[1] <= region[3]:
            return (
                "pysikuli fail-safe triggered when " "moving the mouse within the fail-safe region."
            )


def hotkeyFailSafeCheck():
    pressed = 0
    pressed_keys = keyboard.pressed_keys
    for hotkey in config.FAILSAFE_HOTKEY:
        for key in hotkey:
            if key in pressed_keys:
                pressed += 1
        if pressed == len(hotkey):
            return "pysikuli fail-safe triggered when pressing the fail-safe hotkey."


def _failSafeCheck():
    if config.FAILSAFE:
        hotkeyCheck = hotkeyFailSafeCheck()
        mouseCheck = _mouseFailSafeCheck()
        if hotkeyCheck or mouseCheck:
            raise FailSafeException(
                f"{hotkeyCheck or mouseCheck}\nTo disable the fail-safe, "
                "set pysikuli.config.FAILSAFE to False. DISABLING FAIL-SAFE IS "
                "NOT RECOMMENDED."
            )


def failSafeCheck(wrappedFunction):
    """
    A decorator that calls failSafeCheck() before the decorated function
    """

    @functools.wraps(wrappedFunction)
    def failSafeWrapper(*args, **kwargs):
        if config.PAUSE_BETWEEN_ACTION:
            time.sleep(config.PAUSE_BETWEEN_ACTION)
        _failSafeCheck()
        return wrappedFunction(*args, **kwargs)

    return failSafeWrapper


class Region(object):
    """Represent specific part of the screen

    e.g. Region(0, 0, 100, 100) define up left part of the screen
    with heigh and width equal to 100 pixels.

    Args:
        Region(x1, y1, x2, y2) (int): class initialization

    Returns:
        _type_: _description_
    """

    __slots__ = ("time_step", "reg", "x1", "y1", "x2", "y2")

    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.reg = _regionValidation(reg=(x1, y1, x2, y2))
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.time_step = config.TIME_STEP

    def __repr__(self) -> str:
        return f"{type(self).__name__}(reg={self.reg}, time_step={self.time_step})"

    def __str__(self):
        return f"{type(self).__name__}(reg={self.reg}, time_step={self.time_step})"

    def __eq__(self, other):
        return self.reg == other.reg

    def __ne__(self, other):
        return self.reg != other.reg

    def _area(self):
        return abs(self.x2 - self.x1) * abs(self.y2 - self.y1)

    def __lt__(self, other):
        return self._area() < other._area()

    def __le__(self, other):
        return self._area() <= other._area()

    def __gt__(self, other):
        return self._area() > other._area()

    def __ge__(self, other):
        return self._area() >= other._area()

    def has(
        self,
        image: str,
        grayscale: bool = None,
        precision: float = None,
        rgb_diff: float = None,
    ):
        _match = exist(
            image=image,
            region=self.reg,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )
        if not _match:
            if rgb_diff:
                logging.info(f"has() couldn't find the specific pixel in the region: {image}")
            else:
                logging.debug(f"has() couldn't find the image: {image}")
            return False
        return True

    def wait(
        self,
        image: str,
        max_search_time: float = None,
        grayscale: bool = None,
        precision: float = None,
        rgb_diff: float = None,
    ):
        return wait(
            image=image,
            region=self.reg,
            max_search_time=max_search_time,
            time_step=self.time_step,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )

    def waitWhileExist(
        self,
        image: str,
        max_search_time: float = None,
        grayscale: bool = None,
        precision: float = None,
        rgb_diff: float = None,
    ):
        return waitWhileExist(
            image=image,
            region=self.reg,
            max_search_time=max_search_time,
            time_step=self.time_step,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )

    def click(
        self,
        # search variables
        loc_or_pic,
        max_search_time: float = None,
        grayscale: bool = None,
        precision: float = None,
        # click variables
        clicks=1,
        interval=0.0,
        button=Button.left,
    ):
        click(
            loc_or_pic=loc_or_pic,
            region=self.reg,
            max_search_time=max_search_time,
            time_step=self.time_step,
            grayscale=grayscale,
            precision=precision,
            button=button,
            clicks=clicks,
            interval=interval,
        )

    def rightClick(
        self,
        # search variables
        loc_or_pic,
        max_search_time: float = None,
        grayscale: bool = None,
        precision: float = None,
        # click variables
        clicks=1,
        interval=0.0,
    ):
        rightClick(
            loc_or_pic=loc_or_pic,
            region=self.reg,
            max_search_time=max_search_time,
            time_step=self.time_step,
            grayscale=grayscale,
            precision=precision,
            clicks=clicks,
            interval=interval,
        )

    def find(
        self,
        image,
        max_search_time: float = None,
        grayscale: bool = None,
        precision: float = None,
        rgb_diff: float = None,
    ):
        """find an image pattern

        Args:
            image (_type_): _description_
            max_search_time (float, optional): _description_. Defaults to None.
            grayscale (bool, optional): _description_. Defaults to None.
            precision (float, optional): _description_. Defaults to None.
            rgb_diff (float, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        return find(
            image=image,
            region=self.reg,
            max_search_time=max_search_time,
            time_step=self.time_step,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )

    def existAny(
        self,
        image,
        grayscale: bool = None,
        precision: float = None,
    ):
        return existAny(image=image, region=self.reg, grayscale=grayscale, precision=precision)

    def waitStaticRegion(
        self,
        time_without_changes=0.5,
        max_checking_time=-1,
        check_interval=0.2,
    ):
        return waitStaticRegion(
            region=self.reg,
            time_without_changes=time_without_changes,
            max_checking_time=max_checking_time,
            check_interval=check_interval,
        )


class Match(Region):
    __slots__ = (
        "up_left_loc",
        "center_loc",
        "x",
        "y",
        "offset_loc",
        "offset_x",
        "offset_y",
        "score",
        "precision",
        "np_image",
        "np_region",
        "center_pixel",
        "exit_keys_cv2",
    )

    def __init__(
        self,
        up_left_loc: tuple,
        center_loc: tuple,
        score: float,
        precision: float,
        np_image: np.ndarray,
        np_region: np.ndarray,
        tuple_region: tuple,
    ):
        super().__init__(*tuple_region)
        self.up_left_loc = up_left_loc
        self.center_loc = center_loc
        self.offset_loc = center_loc
        self.x = center_loc[0]
        self.y = center_loc[1]
        self.offset_x = center_loc[0]
        self.offset_y = center_loc[1]
        self.score = score
        self.precision = precision
        self.np_image = np_image
        self.np_region = np_region
        rel_loc_center = (self.x - up_left_loc[0], self.y - up_left_loc[1])
        self.center_pixel = getPixelRGB(rel_loc_center, np_image)

        # q, esc, space, backspace
        self.exit_keys_cv2 = [113, 27, 32, 8]

    def __str__(self):
        return f"{type(self).__name__}(location={self.center_loc}, score={self.score}, center_pixel={self.center_pixel})"

    def __repr__(self) -> str:
        args = [
            f"up_left_loc={self.up_left_loc}",
            f"center_loc={self.center_loc}",
            f"score={self.score}",
            f"precision={self.precision}",
            f"center_pixel={self.center_pixel}",
        ]
        return f"{type(self).__name__}({', '.join(args)})"

    def __eq__(self, other):
        return str(self) == other

    def __ne__(self, other):
        return str(self) != other

    def _showImageCV2(self, window_name, np_img):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, np_img)

        while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
            if cv2.waitKey(1) & 0xFF in self.exit_keys_cv2:
                break

        cv2.destroyAllWindows()

    def showRegion(self):
        self._showImageCV2("Region", self.np_region)

    def showImage(self):
        self._showImageCV2("Pattern", self.np_image)

    def setTargetOffset(self, x, y):
        self.offset_x += x
        self.offset_y += y
        self.offset_loc = (self.offset_x, self.offset_y)
        _locationValidation(self.offset_loc)
        return self.offset_loc


class Picture:
    # TODO
    def __init__():
        pass


class Location:
    # TODO
    def __init__():
        pass


def grab(region: tuple[int, int, int, int]):
    region = _regionNormalization(region)
    with mss() as sct:
        return sct.grab(region)


def wait(
    image: str,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
):
    if find(
        image=image,
        region=region,
        max_search_time=max_search_time,
        time_step=time_step,
        grayscale=grayscale,
        precision=precision,
        rgb_diff=rgb_diff,
    ):
        return True
    else:
        error_text = f"wait(): couldn't find the picture: {image}"
        logging.fatal(error_text)
        raise TimeoutError(error_text)


def waitWhileExist(
    image,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
):
    max_search_time = max_search_time if max_search_time is not None else config.MAX_SEARCH_TIME
    time_step = time_step if time_step is not None else config.TIME_STEP

    start_time = time.time()
    while time.time() - start_time < max_search_time:
        _match = exist(
            image=image,
            region=region,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )
        if _match == None:
            logging.info(f"waitWhileExist finished due to the pic disappearing")
            return True
        time.sleep(time_step)

    logging.info(f"waitWhileExist finished due to MAX_SEARCH_TIME = {config.MAX_SEARCH_TIME} limit")
    return False


def find(
    image,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
):
    """find an image pattern on the screen or specific region

    Args:
        image (_type_): _description_
        region (_type_, optional): _description_. Defaults to None.
        max_search_time (float, optional): _description_. Defaults to None.
        time_step (float, optional): _description_. Defaults to None.
        grayscale (bool, optional): _description_. Defaults to None.
        precision (float, optional): _description_. Defaults to None.
        rgb_diff (float, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    max_search_time = max_search_time if max_search_time is not None else config.MAX_SEARCH_TIME
    time_step = time_step if time_step is not None else config.TIME_STEP

    start_time = time.time()
    while time.time() - start_time < max_search_time:
        _match = exist(
            image=image,
            region=region,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )
        if _match != None:
            return _match
        time.sleep(time_step)
    return None


def waitStaticRegion(region, time_without_changes=0.5, max_checking_time=-1, check_interval=0.2):
    """
    Waits for a static content in region by continuously capturing screenshots and checking for changes.

    Args:

        region (Region): The region to monitor for changes.
        time_without_changes (float, optional): The time in seconds to wait without any changes before considering the region as static. Defaults to 0.5.
        max_checking_time (float, optional): The maximum time in seconds to wait for changes. If set to -1, it will wait indefinitely. Defaults to -1.
        check_interval (float, optional): The time interval in seconds between each check for changes. Defaults to 0.2.

    Returns:

        bool: True if the region remains static for the specified time, False otherwise.
    """

    tuple_reg = _regionNormalization(region)
    screenshot = grab(tuple_reg)
    _start_time = start_time = time.time()
    while time.time() - start_time < time_without_changes:
        iteration_start = time.time()
        new_screenshot = grab(tuple_reg)
        if not np.array_equal(screenshot.pixels, new_screenshot.pixels):
            screenshot = new_screenshot
            start_time = time.time()
        if max_checking_time != -1 and time.time() - _start_time > max_checking_time:
            return False

        logging.debug(
            f"waitStaticRegion(): {round(time.time() - start_time, 2)} sec without changes"
        )

        iteration_time = time.time() - iteration_start
        if iteration_time < check_interval:
            time.sleep(check_interval - iteration_time)

    logging.debug(
        f"waitStaticRegion() finished: nothing has been changed for {time_without_changes} sec"
    )
    return True


def _imgDownsize(img: np.ndarray, scale_percent: int):
    """
    divider must be positive
    does not make sense with a divider greater than 4 because of the small speed increase.
    """
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dsize = (width, height)

    return cv2.resize(img, dsize, interpolation=cv2.INTER_AREA)


def _coordinateNormalization(
    loc_or_pic,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
):
    if isinstance(loc_or_pic, (tuple | list)):
        return loc_or_pic
    elif loc_or_pic is None:
        return None, None
    elif isinstance(loc_or_pic, str):
        _match = find(
            image=loc_or_pic,
            region=region,
            max_search_time=max_search_time,
            time_step=time_step,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
        )
        if _match is None:
            error_text = f"Couldn't find the picture: {loc_or_pic}"
            logging.fatal(error_text)
            raise TimeoutError(error_text)
        return _match.center_loc
    else:
        logging.warning(f"getCoordinates: can't recognize this type of data: {loc_or_pic}")
        return None, None


def _regionValidation(reg: tuple | list):
    try:
        x1, y1, x2, y2 = reg
    except ValueError:
        raise TypeError(f"Entered region is incorrect: {reg}")
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)

    if any(
        coord < config.MONITOR_REGION[i] or coord > config.MONITOR_REGION[i + 2]
        for coord, i in zip([x1, y1, x2, y2], [0, 1, 0, 1])
    ):
        raise TypeError(f"Region is outside the screen: {(x1, y1, x2, y2)}")
    if not (x1 < x2 and y1 < y2):
        raise TypeError(f"Entered region is incorrect: {(x1, y1, x2, y2)}")
    return (x1, y1, x2, y2)


def _locationValidation(loc: tuple[int, int]):
    x, y = loc
    if any(
        coord < config.MONITOR_REGION[i] or coord > config.MONITOR_REGION[i + 2]
        for coord, i in zip([x, y], [0, 1])
    ):
        raise ValueError(f"location {loc} is outside the screen")
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError(f"location {loc} must contain integer value")


def _regionNormalization(reg: ScreenShot | Region | Sequence | np.ndarray = None):
    """
    Normalize the input region.

    Args:
        reg (ScreenShot | Region | Sequence | np.ndarray, optional): The input region to be normalized. Defaults to None.

    Returns:
        The normalized region.

    Raises:
        TypeError: If the entered region's type is incorrect.

    Supported types for `reg`:
    - ScreenShot: A screenshot region.
    - Region: A region object.
    - Sequence: A sequence object. (List or Tuple with 4 integers)
    - np.ndarray: A NumPy array.

    If `reg` is None, the default monitor region will be returned.
    """

    if isinstance(reg, ScreenShot):
        reg = (
            reg.left,
            reg.top,
            reg.left + reg.width,
            reg.top + reg.height,
        )
        reg = _regionValidation(reg)
    elif isinstance(reg, Region):
        reg = reg.reg
    elif isinstance(reg, (list | tuple)):
        reg = _regionValidation(reg)
    elif isinstance(reg, np.ndarray):
        return None
    elif reg is None:
        return config.MONITOR_REGION
    else:
        raise TypeError(
            f"Entered region's type is incorrect: {reg.__class__.__name__}"
            "\nSupported types: ScreenShot, region, None, tuple or list"
        )
    return reg


def _handleNpRegion(np_region: np.ndarray, tuple_region: tuple[int, int, int, int]):
    """handler for validation np.array as region for further _matchProcessing

    Args:
        np_region (np.ndarray): np_region
        tuple_region (tuple[int, int, int, int]): the borders of this np_region

    Raises:
        TypeError: in case there is no tuple_region

    Returns:
        tuple[np.ndarray, tuple[int, int, int, int]]: validated array and tuple
    """
    if tuple_region is None:
        raise TypeError("Can't use np.array as region without tuple_reg")

    tuple_region = _regionValidation(tuple_region)
    x1, y1, x2, y2 = tuple_region

    assert (y2 - y1) == np_region.shape[0], "Mismatch in height"
    assert (x2 - x1) == np_region.shape[1], "Mismatch in width"

    return np_region, tuple_region


def _regionToNumpyArray(reg=None, tuple_region=None):
    tuple_reg = _regionNormalization(reg)

    with mss() as sct:
        if isinstance(reg, np.ndarray):
            return _handleNpRegion(reg, tuple_region)
        if isinstance(reg, ScreenShot):
            grab_reg = reg
        elif isinstance(reg, Region):
            grab_reg = sct.grab(tuple_reg)
        elif reg is None:
            grab_reg = sct.grab(tuple_reg)
        elif isinstance(reg, (tuple | list)):
            grab_reg = sct.grab(tuple_reg)
        else:
            raise TypeError(
                f"Entered region's type is incorrect: {reg.__class__.__name__}"
                "\nSupported types: ScreenShot, region, None, tuple or list"
            )
    return np.array(grab_reg), tuple_reg


def _imageToNumpyArray(image):
    if isinstance(image, np.ndarray):
        return image
    elif isinstance(image, ScreenShot):
        return np.array(image)
    elif isinstance(image, str) and os.path.isfile(image):
        return cv2.imread(image, cv2.IMREAD_COLOR)
    else:
        raise TypeError(
            f"Can't use '{image.__class__.__name__}' with '{str(image)}' value, "
            "supported types: image_path, ndarray or ScreenShot"
        )


def _matchProcessing(
    image,
    region=None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
    tuple_region: tuple | list = None,
):
    grayscale = grayscale if grayscale is not None else config.GRAYSCALE
    precision = precision if precision is not None else config.MIN_PRECISION

    np_region, tuple_region = _regionToNumpyArray(region, tuple_region)
    np_image = _imageToNumpyArray(image)

    img_height, img_width, _ = np_image.shape
    reg_height, reg_width, _ = np_region.shape

    if img_height > reg_height or img_width > reg_width:
        raise ValueError(
            f"The region ({np_region.shape}) is smaller than the image ({np_image.shape}) you are looking for"
        )

    if grayscale and not rgb_diff:
        np_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
        np_region = cv2.cvtColor(np_region, cv2.COLOR_RGB2GRAY)

        image_capture = np_image
        region_capture = np_region
    else:
        image_capture = np_image
        region_capture = np_region
        # both images must be stored in BGR format for further matchTemplate
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        np_region = cv2.cvtColor(np_region, cv2.COLOR_RGB2BGR)

        # imread from np_image must create always BGR images, but in my case it is RGB
        # sct.grab from np_region create always RGB images

    if config.PERCENT_IMAGE_DOWNSIZING < 100:
        np_image = _imgDownsize(np_image, config.PERCENT_IMAGE_DOWNSIZING)
        np_region = _imgDownsize(np_region, config.PERCENT_IMAGE_DOWNSIZING)
    elif config.PERCENT_IMAGE_DOWNSIZING > 100:
        raise ValueError(
            f"Couldn't recognize PERCENT_IMAGE_DOWNSIZING: {config.PERCENT_IMAGE_DOWNSIZING}"
        )

    # also can use cv2.TM_CCOEFF, TM_CCORR_NORMED and TM_CCOEFF_NORMED in descending order of speed
    # for TM_CCORR_NORMED, minimum precision ~ 0.991

    cv2_match = cv2.matchTemplate(np_region, np_image, cv2.TM_CCOEFF_NORMED)

    match_result = (
        image_capture,
        region_capture,
        cv2_match,
        img_width,
        img_height,
        tuple_region,
        precision,
    )

    return match_result


def avgRgbValues(np_image, np_cropped_region):
    img_avg_RGB = np.mean(np_image, axis=(0, 1))
    reg_avg_RGB = np.mean(np_cropped_region, axis=(0, 1))
    diffs = []
    for i in range(3):
        counting = img_avg_RGB[i] / reg_avg_RGB[i]
        if counting > 1:
            counting -= 1
        else:
            counting = 1 - counting

        diffs.append(round(counting * 100, 2))

    return diffs


def cropRegToImgShape(np_region, tuple_region, max_loc_abs, img_width, img_height):
    start_x = abs(tuple_region[0] - max_loc_abs[0])
    end_x = abs(tuple_region[0] - (max_loc_abs[0] + img_width))

    start_y = abs(tuple_region[1] - max_loc_abs[1])
    end_y = abs(tuple_region[1] - (max_loc_abs[1] + img_height))

    cropped_reg = np_region[start_y:end_y, start_x:end_x]
    return cropped_reg


def exist(
    image,
    region=None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
    _tuple_region: tuple | list = None,
):
    # TODO: create full description
    # TODO: find out simple way to debug from main or other scripts
    """
    Searches for an image within an area or on the screen

    input :

    image : path to the image file (see opencv imread for supported types)
    region : (x1, y1, x2, y2)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    numpy_region : a PIL or numpy image, useful if you intend to search the same unchanging region for several elements, must be stored in `RGB format`

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not

    if exist find several patterns with same score, will return the most right and the most bottom match
    """

    (
        image_capture,
        region_capture,
        cv2_match,
        img_width,
        img_height,
        tuple_region,
        precision,
    ) = _matchProcessing(
        image=image,
        region=region,
        grayscale=grayscale,
        precision=precision,
        rgb_diff=rgb_diff,
        tuple_region=_tuple_region,
    )

    _, max_val, _, max_loc = cv2.minMaxLoc(cv2_match)

    max_val = round(max_val, 6)

    if isinstance(image, np.ndarray):
        image = f"{type(image).__name__}(shape={image.shape})"
    elif isinstance(image, ScreenShot):
        image = repr(image)

    logging.debug(f"search result: {max_val} precision: {precision} img: {image}")
    if max_val < precision:
        return None

    max_loc_rel = tuple(int(point / config.PERCENT_IMAGE_DOWNSIZING * 100) for point in max_loc)

    if config.HIDPI:
        max_loc_rel = (max_loc_rel[0] // 2, max_loc_rel[1] // 2)
        img_width //= 2
        img_height //= 2

    max_loc_abs = (tuple_region[0] + max_loc_rel[0], tuple_region[1] + max_loc_rel[1])
    max_loc_abs_center = _getCenterLoc(img_width, img_height, max_loc_abs)

    match_class = Match(
        up_left_loc=max_loc_abs,
        center_loc=max_loc_abs_center,
        score=max_val,
        precision=precision,
        np_image=image_capture,
        np_region=region_capture,
        tuple_region=tuple_region,
    )

    if not rgb_diff:
        logging.debug(f"search result: {max_val} precision: {precision} img: {image}")
        return match_class
    else:
        cropped_reg = cropRegToImgShape(
            region_capture, tuple_region, max_loc_abs, img_width, img_height
        )

        for counting in avgRgbValues(image_capture, cropped_reg):
            if counting > config.PERCENT_RGB_DIFFERENCE:
                logging.debug(
                    f"search result: {max_val} precision: {precision} img: {image} rgb_diff: {counting} "
                )
                return None

        logging.debug(
            f"search result: {max_val} precision: {precision} img: {image} rgb_diff: {counting} "
        )
        return match_class


def existAny(
    image_list,
    region=None,
    grayscale: bool = None,
    precision: float = None,
    rgb_diff: float = None,
):
    region, tuple_region = _regionToNumpyArray(reg=region)
    matches = []

    for image in image_list:
        match = exist(
            image=image,
            region=region,
            grayscale=grayscale,
            precision=precision,
            rgb_diff=rgb_diff,
            _tuple_region=tuple_region,
        )
        if match:
            matches.append(match)
    return matches


def existFromFolder(path, region=None, grayscale=None, precision=None):
    """
    Get all pictures from the provided folder and search them on screen.

    input :
    path : path of the folder with the images to be searched on screen like pics/
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

    returns :
    A dictionary where the key is the path to image file and the value is the position where it was found.
    """
    imagesPos = {}
    files = [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and os.path.splitext(f)[1].lower()[1:] in _SUPPORTED_PIC_FORMATS
    ]
    for file in files:
        full_path = os.path.join(path, file)
        match = exist(
            image=full_path,
            region=region,
            grayscale=grayscale,
            precision=precision,
        )
        pos = None
        if match != None:
            pos = match.center_loc
        imagesPos[full_path] = pos
    return imagesPos


def existCount(
    image,
    region=None,
    precision: float = None,
    grayscale: bool = None,
    rgb_diff: float = None,
    tuple_region: tuple[int, int, int, int] = None,
):
    # TODO: not yet debugged
    """
    Searches for an image on the screen and counts the number of occurrences.

    input :
    image : path to the target image file (see opencv imread for supported types)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.9

    returns :
    the number of times a given image appears on the screen.
    optionally an output image with all the occurrences boxed with a red outline.
    """

    precision = precision if precision is not None else config.MIN_PRECISION

    _, _, cv2_match, img_width, img_height, _, _ = _matchProcessing(
        image=image,
        region=region,
        grayscale=grayscale,
        precision=precision,
        rgb_diff=rgb_diff,
        tuple_region=tuple_region,
    )
    location = np.where(cv2_match >= precision)

    count = 0
    match_dict = {}

    half_width = img_width / 2
    half_height = img_height / 2

    for pt in zip(*location[::-1]):  # Swap columns and rows
        x = int(pt[0] * config.PERCENT_IMAGE_DOWNSIZING + half_width)
        y = int(pt[1] * config.PERCENT_IMAGE_DOWNSIZING + half_height)

        if count:
            prev_loc = match_dict[count - 1]
            if x - prev_loc[0] < img_width and y - prev_loc[1] < img_height:
                continue

        match_dict[count] = (x, y)
        count += 1

    return match_dict


def _getCenterLoc(img_width, img_height, loc: tuple):
    x = int(loc[0] + img_width / 2)
    y = int(loc[1] + img_height / 2)
    return x, y


def saveNumpyImg(image: np.ndarray, image_name: str = None, path: str = None):
    """Save a numpy array into png image in root directory

    Args:
        image (np.ndarray): the variable with pic, that you want to save
        image_name (str): file's name
        path (str): path where the pic will be saved
    """

    if image_name:
        output = f"{image_name}.png"
    else:
        output = f"image_{time.strftime('%H_%M_%S')}.png"

    if path:
        if not os.path.isdir(path):
            raise FileExistsError(f"{path} doesn't exist")
        if not os.path.isabs(path):
            raise FileExistsError("Path must be absolute")
    else:
        path = os.getcwd()

    path = os.path.join(path, output)
    cv2.imwrite(path, image)

    print(f"Image: {path} successfully saved")

    return path


def saveScreenshot(region=None):
    region = _regionNormalization(region)
    output = f"Screenshot_{time.strftime('%H_%M_%S')}.png"
    with mss() as sct:
        screenshot = sct.grab(region)
        tools.to_png(screenshot.rgb, screenshot.size, output=output)
    path = os.path.join(os.getcwd(), output)
    print(f"Image '{path}' successfully saved")
    return path


def getPixelRGB(
    rel_location: tuple[int, int] | list[int, int], np_image: np.ndarray = None
) -> tuple[int, int, int]:
    x, y = rel_location
    x = int(x)
    y = int(y)
    if np_image is None:
        reg = (x, y, x + 1, y + 1)
        np_image = grab(reg)
        np_image = np.array(np_image)
        x, y = 0, 0
    elif len(np_image.shape) < 3:
        gray = np_image[y][x]
        return (gray, gray, gray)

    r = np_image[y][x][2]
    g = np_image[y][x][1]
    b = np_image[y][x][0]
    return (r, g, b)


def pressedKeys():
    return keyboard.pressed_keys


def hotkey(*keys, interval=0.0):
    if config.OSX:
        if interval < config.MIN_SLEEP_TIME:
            interval = config.MIN_SLEEP_TIME

    logging.debug(f"{keys}, interval: {interval}")

    for key in keys:
        if isinstance(key, str):
            key = key.lower()
        keyDown(key)
        time.sleep(interval)

    logging.debug(f"Pressed: {keyboard.pressed_keys}")

    for key in reversed(keys):
        if isinstance(key, str):
            key = key.lower()
        keyUp(key)
        time.sleep(interval)

    logging.debug(f"Released: {keyboard.pressed_keys}")


def tap(key, presses=1, interval=0.0, time_step: float = None):
    """taps a single key on keyboard

    Args:
        key (_type_): _description_
        presses (int, optional): number of times the entered key is pressed. Defaults to 1.
        interval (float, optional): time interval after each tap. Defaults to 0.0.
        time_step (float, optional): time interval after each key press and each key release. Defaults to None.
    """
    time_step = time_step if time_step is not None else config.TIME_STEP

    if config.OSX and interval < config.MIN_SLEEP_TIME:
        interval = config.MIN_SLEEP_TIME
    for x in range(presses):
        logging.debug(f"tap: {key}")
        logging.debug(keyboard.pressed_keys)

        keyDown(key)
        time.sleep(time_step)
        keyUp(key)
        time.sleep(time_step + interval)


@failSafeCheck
def keyUp(key):
    keyboard.release(key)


@failSafeCheck
def keyDown(key):
    keyboard.press(key)


@failSafeCheck
def write(message, time_step: float = None):
    time_step = time_step if time_step is not None else config.TIME_STEP
    if time_step > config.MIN_SLEEP_TIME:
        for sign in message:
            keyboard.tap(sign)
            time.sleep(time_step)
    else:
        keyboard.type(message)


@failSafeCheck
def paste(text: str):
    """fast paste text into selected window. Equivalent copyToClip + (ctrl or cmd + v)

    Args:
        text (str): text, which one will be entered into active window
    """
    copyToClip(text)
    if config.OSX:
        hotkey(Key.cmd, "v")
    else:
        hotkey(Key.ctrl, "v")


def copyToClip(text: str):
    return pyperclip.copy(text)


def pasteFromClip():
    return pyperclip.paste()


def mousePosition():
    return (int(mouse.position[0]), int(mouse.position[1]))


@failSafeCheck
def scroll(dx=0, dy=0):
    """Sends scroll events.

    Args

        dx (int, optional): The horizontal scroll. The units of scrolling is
        undefined.
        dy (int, optional): The vertical scroll. The units of scrolling is
        undefined.
    """
    mouse.scroll(dx, dy)


@failSafeCheck
def smoothScroll(ticks=1, speed_x=0, speed_y=1):
    """Sends scroll events depend on ticks and speed

    Args:
    -
        ticks (int, optional): roughly equivalent of 1 scroll tick.
        speed_x (int, optional): horizontal scrolling speed.
        speed_y (int, optional): vertical scrolling speed.
    """
    step_x, step_y = 1, 1

    if speed_x > 50:
        step_x += speed_x - 50
        sleep_x = 0.02
    else:
        sleep_x = round(1 / speed_x, 2)

    if speed_y > 50:
        step_y += speed_y - 50
        sleep_y = 0.02
    else:
        sleep_y = round(1 / speed_y, 2)

    for _ in range(ticks):

        s_time = time.time()
        mouse.scroll(step_x, step_y)
        exec_time = time.time() - s_time

        sleep = max(sleep_y, sleep_x)
        delay = sleep - exec_time if exec_time <= sleep else 0
        time.sleep(delay)


def hscroll(duration=0.1, speed=1):
    scroll(duration, speed, 0)


def vscroll(duration=0.1, speed=1):
    scroll(duration, 0, speed)


@failSafeCheck
def mouseMove(destination_loc):
    mouse.position = destination_loc


def vector_diff(vec1, vec2):
    return vec2[0] - vec1[0], vec2[1] - vec1[1]


def vector_abs(vector):
    return (abs(vector[0]), abs(vector[1]))


@failSafeCheck
def mouseSmoothMove(
    destination_loc,
    speed: float = None,
):
    speed = speed if speed is not None else config.MOUSE_SPEED

    if speed >= _MAX_SPEED:
        mouse.position = destination_loc
        return None

    start_time = time.time()

    interruptions = 0
    speed_multiplier = 1000

    speed *= speed_multiplier
    if speed <= 0:
        speed = 1

    start_x, start_y = mouse.position
    direction_vector = vector_diff(mouse.position, destination_loc)

    distance = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)
    distance = round(distance)

    duration = distance / speed

    steps = round(0.0618 * distance * speed_multiplier / speed)

    if steps < 1:
        steps = 1

    delta_x = direction_vector[0] / steps
    delta_y = direction_vector[1] / steps

    # if we use sleep lower than this value, we can't expect accurately sleep duration
    min_delay = 0.015
    execute_time = time.time() - start_time
    sleep_time = (duration - execute_time) / steps

    if sleep_time < min_delay:
        mouse.position = destination_loc
        return None

    for step in range(steps):
        start_time = time.time()

        new_x = int(start_x + delta_x * step)
        new_y = int(start_y + delta_y * step)
        mouse.position = (new_x, new_y)

        execute_time = time.time() - start_time
        if execute_time < sleep_time and step != steps - 1:
            time.sleep(sleep_time - execute_time)

        dist2NewPoint = vector_diff(mouse.position, (new_x, new_y))

        if abs(dist2NewPoint[0]) > abs(delta_x) * 2 and abs(dist2NewPoint[1]) > abs(delta_y) * 2:
            interruptions += 1

        if interruptions > steps * 0.5:
            raise PysikuliException("Mouse movement has been interrupted")

    dist2point = vector_diff(mouse.position, destination_loc)

    if abs(dist2point[0]) <= abs(delta_x) * 2 and abs(dist2point[1]) <= abs(delta_y) * 2:
        mouse.position = destination_loc
    else:
        raise PysikuliException("Mouse movement has been interrupted")


def mouseMoveRelative(
    xOffset,
    yOffset,
    speed: float = None,
):
    x, y = mouse.position
    new_loc = (x + xOffset, y + yOffset)
    mouseSmoothMove(destination_loc=new_loc, speed=speed)


@failSafeCheck
def mousePress(button: Button = None):
    button = button if button is not None else config.MOUSE_PRIMARY_BUTTON
    mouse.press(button)


@failSafeCheck
def mouseRelease(button: Button = None):
    button = button if button is not None else config.MOUSE_PRIMARY_BUTTON
    mouse.release(button)


def mouseDown(
    button: Button = None,
    speed: float = None,
    loc_or_pic=None,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
):
    if loc_or_pic:
        x, y = _coordinateNormalization(
            loc_or_pic=loc_or_pic,
            region=region,
            max_search_time=max_search_time,
            time_step=time_step,
            grayscale=grayscale,
            precision=precision,
        )
        mouseSmoothMove(destination_loc=(x, y), speed=speed)
    mousePress(button)


def mouseUp(
    button: Button = None,
    speed: float = None,
    loc_or_pic=None,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
):
    if loc_or_pic:
        x, y = _coordinateNormalization(
            loc_or_pic=loc_or_pic,
            region=region,
            max_search_time=max_search_time,
            time_step=time_step,
            grayscale=grayscale,
            precision=precision,
        )
        mouseSmoothMove(destination_loc=(x, y), speed=speed)
    mouseRelease(button)


def click(
    loc_or_pic=None,
    # search variables
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
    # click variables
    button: Button = None,
    clicks: int = 1,
    interval: float = 0.0,
):
    """
    Perform a mouse click operation.

    :param max_search_time: Maximum time for searching, in seconds.
    :type max_search_time: float

    :param time_step: The location or picture to click.
    :type time_step: float
    """

    button = button if button is not None else config.MOUSE_PRIMARY_BUTTON

    if config.OSX and interval < config.MIN_SLEEP_TIME:
        interval = config.MIN_SLEEP_TIME

    if loc_or_pic:
        x, y = _coordinateNormalization(
            loc_or_pic=loc_or_pic,
            region=region,
            max_search_time=max_search_time,
            time_step=time_step,
            grayscale=grayscale,
            precision=precision,
        )

        logging.debug(f"click: {x, y}, clicks: {clicks} interval: {interval} button: {button}")

        mouseSmoothMove(destination_loc=(x, y))

        time.sleep(interval)

        if config.OSX:
            time.sleep(0.05)

    for _ in range(clicks):
        _failSafeCheck()
        mouse.click(button, 1)

        time.sleep(interval)


def rightClick(
    loc_or_pic=None,
    region=None,
    max_search_time: float = None,
    time_step: float = None,
    grayscale: bool = None,
    precision: float = None,
    clicks=1,
    interval=0.0,
):
    # TODO: correct the description
    """
    Performs a right mouse button click.

    This is a wrapper function for click('right', x, y).
    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
        x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.

        y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.

        interval: (float, optional): The number of seconds in between each click,
        if the number of clicks is greater than 1. 0.0 by default, for no
        pause in between clicks.

    Returns:
        None
    """
    click(
        loc_or_pic=loc_or_pic,
        region=region,
        max_search_time=max_search_time,
        time_step=time_step,
        grayscale=grayscale,
        precision=precision,
        button=config.MOUSE_SECONDARY_BUTTON,
        clicks=clicks,
        interval=interval,
    )


def dragDrop(
    destination_loc: list,
    start_location=None,
    speed: float = None,
    button: Button = None,
):
    """_summary_

    Args:
        start_location (list): x, y start location example: [1200, 700]
        end_location (list): x, y end location example: [1400, 700]
        butt (str, optional): Which button will be held down. Defaults to "left".
    """

    if not start_location:
        start_location = mouse.position

    mouseSmoothMove(destination_loc=start_location, speed=speed)
    mousePress(button)
    mouseSmoothMove(destination_loc=destination_loc, speed=speed)
    mouseRelease(button)


def titleCheck(wrappedFunction):
    """Decorator to window title searching

    Raises:
        NameError: raises if `windowExist` couldn't find the entered window_name and print all available windows titles
    """

    @functools.wraps(wrappedFunction)
    def titleCheckWrapper(*args, **kwargs):
        window_title = windowExist(*args)
        if window_title is not None:
            return wrappedFunction(window_title, **kwargs)
        else:
            titles = config._platformModule.getAllTitles()
            text = "\n"
            for title in titles:
                text += f"- {title}\n"
            raise NameError(f"Can't find '{args[0]}' window\nAvailable windows:{text}")

    return titleCheckWrapper


def windowExist(window_title: str):
    """check if entered window exists

    Args:
        window_title (str): full window name, e.g. "Mozilla Firefox".

    Returns:
        (str | None): The return value. True for success, False otherwise.

    To get all available titles, use `pysikuli.getAllTitles()`
    """
    if not isinstance(window_title, str):
        logging.debug(f"window title isn't string: {window_title}")
        return None

    title = None
    window_title = window_title.lower()
    titles = config._platformModule.getAllTitles()
    titles_lower = [title.lower() for title in titles]

    for i in range(len(titles_lower)):
        if window_title == titles_lower[i]:
            title = titles[i]
            break

    return title


@titleCheck
def getWindowWithTitle(window_title: str):
    """Get the window objects whose title match the given string

    Args:
        window_title (str): full window name, e.g. "Mozilla Firefox"

    Returns:
        (Window object | None)

    To get all available titles, use `pysikuli.getAllTitles()`
    """
    return pwc.getWindowsWithTitle(window_title)[0]


@failSafeCheck
@titleCheck
def activateWindow(window_title: str):
    """Activate entered window and make it the foreground (focused) window

    Args

        window_title (str): full window name, e.g. "Mozilla Firefox".
        To get all available titles, use `pysikuli.getAllTitles()`

    Returns

        bool: "True" if window activated
    """
    if config.OSX:
        return config._platformModule.activateWindow(window_title)

    win = pwc.getWindowsWithTitle(window_title)
    return win[0].activate(config.WINDOW_WAITING_CONFIRMATION)


def getWindowUnderMouse():
    """Get the Window object at the top of the stack under mouse position

    Returns:
        Window object | None
    """
    return pwc.getTopWindowAt(*mouse.position)


@failSafeCheck
def activateWindowUnderMouse():
    """Activate the top window under mouse position

    Returns:
        bool : "True" if window is activated
    """
    return pwc.getTopWindowAt(*mouse.position).activate(config.WINDOW_WAITING_CONFIRMATION)


@failSafeCheck
def activateWindowAt(location: tuple[int, int]):
    """Activate the top window under entered location(x, y)

    Args:
        location (tuple[int, int]): tuple with int coordinates (x, y)

    Returns:
        bool : "True" if window is activated
    """
    return pwc.getTopWindowAt(*location).activate(config.WINDOW_WAITING_CONFIRMATION)


@titleCheck
def getWindowRegion(window_title: str):
    """grab the window region window by it's name

    Args:
        window_title (str): full window name, e.g. "Mozilla Firefox".

    Returns:
        Region : an object of class `Region`, if the window is within the screen boundaries and exists

    To get all available titles, use `pysikuli.getAllTitles()`
    """
    # NOTE: got these values on my laptop, may be different
    x1_offset, x2_offset, y2_offset = 0, 0, 0
    if config.UNIX:
        x1_offset = 8
        x2_offset = -8
        y2_offset = -8

    windows = pwc.getWindowsWithTitle(window_title)
    return Region(
        windows[0].bbox.left + x1_offset,
        windows[0].bbox.top,
        windows[0].bbox.right + x2_offset,
        windows[0].bbox.bottom + y2_offset,
    )


@titleCheck
def closeWindow(window_title: str):
    """Closes this window. This is identical to clicking the X button on the window.

    This may trigger "Are you sure you want to quit?" dialogs or
    other actions that prevent the window from actually closing.

    Args:
        window_title (str): full window name, e.g. "Mozilla Firefox".

    Returns:
        bool: "True" if window is closed

    To get all available titles, use `pysikuli.getAllTitles()`
    """
    return pwc.getWindowsWithTitle(window_title)[0].close()


@titleCheck
def maximizeWindow(window_title: str):
    """Maximizes entered window

    Args:
        window_title (str): full window name, e.g. "Mozilla Firefox".

    Returns:
        bool: "True" if window is maximized

    To get all available titles, use `pysikuli.getAllTitles()`
    """
    window = pwc.getWindowsWithTitle(window_title)[0]
    return window.maximize(config.WINDOW_WAITING_CONFIRMATION)


@failSafeCheck
@titleCheck
def minimizeWindow(window_title: str):
    """Minimizes entered window

    Args:
        window_title (str): full window name, e.g. "Mozilla Firefox".

    Returns:
        bool : "True" if window minimized

    To get all available titles, use `pysikuli.getAllTitles()`
    """
    return pwc.getWindowsWithTitle(window_title)[0].minimize(config.WINDOW_WAITING_CONFIRMATION)


def _rootTimeoutNorm(root: tuple[int, int], timeout: float):
    """Applied rootWindowPosition and return `timeout` in milliseconds

    Args:
        root (tuple[int, int]): left top corner location.
        timeout (float): time in seconds after which message box will be closed.

    Returns:
        int : timeout in milliseconds
    """
    if root:
        pmb.rootWindowPosition = f"+{root[0]}+{root[1]}"

    if timeout:
        timeout = int(timeout * 1000)

    return timeout


def popupAlert(
    text="",
    title="",
    root: tuple[int, int] = None,
    timeout: float = None,
):
    """Displays a simple message box with text and a single OK button.

    Args:
        text (str, optional): message above input text.
        title (str, optional): message box title.
        root (tuple[int, int], optional): left top corner location. Defaults gets from `config.ROOT_WINDOW_POSITION`.
        timeout (float, optional): time in seconds after which message box will be closed.

    Returns:
        (str | None): the text of the button clicked on, or "Timeout" if time has elapsed.
    """
    timeout = _rootTimeoutNorm(root, timeout)
    return pmb.alert(text, title, timeout=timeout)


def popupPassword(
    text="",
    title="",
    default="",
    mask="*",
    root: tuple[int, int] = None,
    timeout: float = None,
):
    """Displays a message box with text input, and OK & Cancel buttons. Typed characters appear as \* by default.

    Args:
        text (str, optional): message above input text.
        title (str, optional): message box title.
        default (str, optional): default value for input text.
        mask (str, optional): mask symbol for entered text.
        root (tuple[int, int], optional): left top corner location. Defaults gets from `config.ROOT_WINDOW_POSITION`.
        timeout (float, optional): time in seconds after which message box will be closed.

    Returns:
        (str | None): the entered text, None if Cancel was clicked, or "Timeout" if time has elapsed.
    """
    timeout = _rootTimeoutNorm(root, timeout)
    return pmb.password(text, title, default, mask, timeout=timeout)


def popupPrompt(
    text="",
    title="",
    default="",
    root: tuple[int, int] = None,
    timeout: float = None,
):
    """Displays a message box with text input, and OK & Cancel buttons.

    Args:
        text (str, optional): message above input text.
        title (str, optional): message box title.
        default (str, optional): default value for input text.
        root (tuple[int, int], optional): left top corner location. Defaults gets from `config.ROOT_WINDOW_POSITION`.
        timeout (float, optional): time in seconds after which message box will be closed.

    Returns:
        (str | None): the entered text, None if Cancel was clicked, or "Timeout" if time has elapsed.
    """
    timeout = _rootTimeoutNorm(root, timeout)
    return pmb.prompt(text, title, default, timeout=timeout)


def popupConfirm(
    text="",
    title="",
    buttons=(config.OK_TEXT, config.CANCEL_TEXT),
    root: tuple[int, int] = None,
    timeout: float = None,
):
    """
    Displays a message box with OK and Cancel buttons. Number and text of buttons can be customized.

    Args:
        text (str, optional): message above buttons.
        title (str, optional): message box title.
        buttons (tuple, optional): tuple of strings, each string represent a button.
        root (tuple[int, int], optional): left top corner location. Defaults gets from `config.ROOT_WINDOW_POSITION`.
        timeout (float, optional): time in seconds after which message box will be closed.

    Returns:
        str: the text of the button clicked on, or "Timeout" if time has elapsed.
    """
    timeout = _rootTimeoutNorm(root, timeout)
    return pmb.confirm(text, title, buttons, timeout=timeout)


@failSafeCheck
def deleteFile(file_path: os.PathLike):
    """func first tries to move the file to the bin, otherwise uses os.remove for permanently deletion

    Args:
        file_path (PathLike): full path to the file
    """
    logging.debug(f"deleting {file_path}")
    try:
        send2trash(file_path)
    except:
        os.remove(file_path)
