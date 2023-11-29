import pyperclip as clip
import pyautogui as ag
import numpy as np
import functools
import logging
import time
import cv2
import sys
import os
import tkinter as tk

from mss import mss, tools
from mss.screenshot import ScreenShot
from send2trash import send2trash
from PyHotKey import keyboard_manager as manager
from ._config import Config, Key


class PysikuliException(Exception):
    """
    pysikuli code will raise this exception class for any invalid actions. If pysikuli raises some other exception,
    you should assume that this is caused by a bug in pysikuli itself. (Including a failure to catch potential
    exceptions raised by pysikuli.)
    """


class FailSafeException(PysikuliException):
    """
    This exception is raised by pysikuli functions when the user puts the mouse cursor into one of the "failsafe
    points" (by default, one of the four corners of the primary monitor). This exception shouldn't be caught; it's
    meant to provide a way to terminate a misbehaving script.
    """


sct = mss()  # is an alias for mss()
MONITOR_RESOLUTION = sct.grab(sct.monitors[0]).size
MONITOR_REGION = (0, 0, MONITOR_RESOLUTION[0], MONITOR_RESOLUTION[1])


def _mouseFailSafeCheck():
    if tuple(ag.position()) in Config.FAILSAFE_POINTS:
        return True


def _hotkeyFailSafeCheck():
    pressed = 0
    ans = manager.pressed_keys
    for key in Config.FAILSAFE_HOTKEY:
        if key in ans:
            pressed += 1
    if pressed == len(Config.FAILSAFE_HOTKEY):
        return True


def _failSafeCheck():
    if Config.FAILSAFE:
        if _hotkeyFailSafeCheck() or _mouseFailSafeCheck():
            raise FailSafeException(
                "pysikuli fail-safe triggered from mouse moving to a corner of the screen. To disable this fail-safe, set pysikuli.FAILSAFE to False. DISABLING FAIL-SAFE IS NOT RECOMMENDED."
            )


def failSafeCheck(wrappedFunction):
    """
    A decorator that calls failSafeCheck() before the decorated function
    """

    @functools.wraps(wrappedFunction)
    def failSafeWrapper(*args, **kwargs):
        _failSafeCheck()
        return wrappedFunction(*args, **kwargs)

    return failSafeWrapper


class Region(object):
    # TODO: change has() to use _exist instead of _find
    TIME_STEP = Config.DEFAULT_TIME_STEP
    COMPRESSION_RATIO = Config.COMPRESSION_RATIO

    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.reg = _regionValidation((x1, y1, x2, y2))
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def has(
        self,
        image: str,
        max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
        pixel_colors: tuple = None,
    ):
        if pixel_colors:
            _match = _find(
                image,
                self.reg,
                max_search_time,
                self.TIME_STEP,
                grayscale,
                precision,
                pixel_colors,
            )
            if not _match:
                logging.info(
                    f"has() couldn't find the specific pixel in the region: {image}"
                )
                return False
            return True

        _match = self.find(image, max_search_time, grayscale, precision)
        if not _match:
            logging.debug(f"has() couldn't find the image: {image}")
            return False
        return True

    def wait(
        self,
        image: str,
        max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
        pixel_colors=None,
    ) -> bool | None:
        return _wait(
            image,
            self.reg,
            max_search_time,
            self.TIME_STEP,
            grayscale,
            precision,
            pixel_colors,
        )

    def click(
        self,
        # search variables
        loc_or_pic,
        max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
        # click variables
        clicks=1,
        interval=0.0,
        button=ag.PRIMARY,
    ):
        _click(
            loc_or_pic,
            self.reg,
            max_search_time,
            self.TIME_STEP,
            grayscale,
            precision,
            clicks,
            interval,
            button,
        )

    def rightClick(
        self,
        loc_or_pic,
        max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
        clicks=1,
        interval=0.0,
    ):
        _rightClick(
            loc_or_pic,
            self.reg,
            max_search_time,
            self.TIME_STEP,
            grayscale,
            precision,
            clicks,
            interval,
        )

    def find(
        self,
        image,
        max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
    ):
        return _find(
            image, self.reg, max_search_time, self.TIME_STEP, grayscale, precision
        )

    def findAny(
        self,
        image,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
    ):
        return _findAny(image, self.reg, grayscale, precision=precision)

    def exist(
        self,
        image,
        grayscale=Config.DEFAULT_GRAYSCALE,
        precision=Config.DEFAULT_PRECISION,
        pixel_colors: tuple = None,
    ):
        return _exist(image, self.reg, grayscale, precision, pixel_colors)


class Match(object):
    # q, esc, space, backspace
    exit_keys_cv2 = [113, 27, 32, 8]

    def __init__(
        self,
        up_left_loc: tuple,
        loc: tuple,
        score: float,
        precision: float,
        np_image,
        np_region,
    ):
        self.up_left_loc = up_left_loc
        self.loc = loc
        self.offset_loc = loc
        self.x = loc[0]
        self.y = loc[1]
        self.offset_x = loc[0]
        self.offset_y = loc[1]
        self.score = round(score, 6)
        self.precision = precision
        self.np_image = np_image
        self.np_region = np_region

    def __repr__(self):
        args = [
            "location={!r}".format(self.loc),
            "score={!r}".format(self.score),
            "precision={!r}".format(self.precision),
        ]
        return "{}({})".format(type(self).__name__, ", ".join(args))

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


def _wait(
    image: str,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
    pixel_colors=None,
) -> bool | None:
    if _find(
        image, region, max_search_time, time_step, grayscale, precision, pixel_colors
    ):
        return True
    else:
        error_text = f"wait(): couldn't find the picture: {image}"
        logging.fatal(error_text)
        raise TimeoutError(error_text)


@failSafeCheck
def _click(
    loc_or_pic=None,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=0.9,
    # click variables
    clicks=1,
    interval=0.0,
    button=ag.PRIMARY,
):
    """
    Perform a click operation.

    :param max_search_time: Maximum time for searching, in seconds.
    :type max_search_time: float

    :param time_step: The location or picture to click.
    :type time_step: float
    """

    if Config.OSX and interval < 0.02:
        interval = 0.02

    x, y = _getCoordinates(
        loc_or_pic, region, max_search_time, time_step, grayscale, precision
    )

    logging.debug(
        f"click: {x, y}, clicks: {clicks} interval: {interval} button: {button}, mouse_move_speed: {Config.MOUSE_MOVE_SPEED}"
    )
    ag.click(x, y, clicks, interval, button, Config.MOUSE_MOVE_SPEED)


def _getCoordinates(
    loc_or_pic,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
    pixel_colors=None,
):
    if isinstance(loc_or_pic, (tuple | list)):
        return loc_or_pic
    elif loc_or_pic is None:
        return None, None
    elif isinstance(loc_or_pic, str):
        _match = _find(
            loc_or_pic,
            region,
            max_search_time,
            time_step,
            grayscale,
            precision,
            pixel_colors,
        )
        if not _match:
            error_text = f"Couldn't find the picture: {loc_or_pic}"
            logging.fatal(error_text)
            raise TimeoutError(error_text)
        return _match.getTarget()
    else:
        logging.warning(
            f"getCoordinates: can't recognize this type of data: {loc_or_pic}"
        )
        return None, None


def _find(
    image,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_PRECISION,
    precision=Config.DEFAULT_PRECISION,
    pixel_colors: tuple = None,
):
    start_time = time.time()
    while time.time() - start_time < max_search_time:
        _match = _exist(image, region, grayscale, precision, pixel_colors)
        if _match != None:
            return _match
        time.sleep(time_step)
    return None


def _findAny(
    image_list,
    region=None,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
    pixel_colors: tuple = None,
):
    np_region = _regionToNumpyArray(region)
    matches = []

    for image in image_list:
        matches.append(_exist(image, np_region, grayscale, precision, pixel_colors))
    return [x for x in matches if x is not None]


def _imgDownsize(img: np.ndarray, multiplier):
    """
    multiplier must be even [2-8]
    does not make sense with a multiplier greater than 4 because of the small increase in speed.
    """
    width = int(img.shape[1] / multiplier)
    height = int(img.shape[0] / multiplier)
    dim = (width, height)

    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


def _regionValidation(reg: tuple | list):
    x1, y1, x2, y2 = reg
    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)
    if (
        x1 < MONITOR_REGION[0]
        or y1 < MONITOR_REGION[1]
        or x2 < MONITOR_REGION[0]
        or y2 < MONITOR_REGION[1]
        or x1 > MONITOR_REGION[2]
        or y1 > MONITOR_REGION[3]
        or x2 > MONITOR_REGION[2]
        or y2 > MONITOR_REGION[3]
    ):
        raise TypeError(f"Region outside the screen: {(x1, y1, x2, y2)}")
    if not (x1 < x2 and y1 < y2):
        raise TypeError(f"Entered region is incorrect: {(x1, y1, x2, y2)}")
    return (x1, y1, x2, y2)


def _locationValidation(loc: tuple):
    x, y = loc
    if (
        x < MONITOR_REGION[0]
        or y < MONITOR_REGION[1]
        or x > MONITOR_REGION[2]
        or y > MONITOR_REGION[3]
    ):
        raise ValueError(f"location {loc} is outside the screen")


def _regionNormalization(reg=None):
    if isinstance(reg, ScreenShot):
        reg = (
            reg.left,
            reg.top,
            reg.left + reg.width,
            reg.top + reg.height,
        )
        # maybe remove this
        reg = _regionValidation(reg)
    elif isinstance(reg, Region):
        reg = reg.reg
    elif isinstance(reg, (list | tuple)):
        reg = _regionValidation(reg)
        pass
    elif reg is None:
        return None
    else:
        raise TypeError(
            f"Entered region's type is incorrect: {reg.__class__.__name__}"
            "\nSupported types: ScreenShot, region, None, tuple or list"
        )
    return reg


def _regionToNumpyArray(reg=None):
    tuple_region = _regionNormalization(reg)
    if isinstance(reg, ScreenShot):
        grab_reg = reg
    elif isinstance(reg, Region):
        grab_reg = sct.grab(tuple_region)
    elif reg is None:
        grab_reg = sct.grab(sct.monitors[0])
        tuple_region = None
    elif isinstance(reg, (tuple | list)):
        grab_reg = sct.grab(tuple_region)
    else:
        raise TypeError(
            f"Entered region's type is incorrect: {reg.__class__.__name__}"
            "\nSupported types: ScreenShot, region, None, tuple or list"
        )
    return np.array(grab_reg), tuple_region


def _imageToNumpyArray(image):
    if isinstance(image, np.ndarray):
        return image
    elif isinstance(image, ScreenShot):
        return np.array(image)
    elif isinstance(image, str) and os.path.isfile(image):
        return cv2.imread(image, cv2.IMREAD_COLOR)
    else:
        raise TypeError(
            f"Can't use '{image.__class__.__name__}' with '{image}' value, supported types: image_path, ndarray or ScreenShot types"
        )


def _exist(
    image,
    region=None,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
    pixel_colors: tuple = None,
):
    # TODO: region also must be saved in (x1,y1,x2,y2)
    # TODO: create full discription
    # TODO: find out simple way to debug from main or other scripts
    """
    Searchs for an image within an area or on the screen

    input :

    image : path to the image file (see opencv imread for supported types)
    region : (x1, y1, x2, y2)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    numpy_region : a PIL or numpy image, usefull if you intend to search the same unchanging region for several elements, must be stored in ``RGB format``

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not
    """

    np_region, tuple_region = _regionToNumpyArray(region)
    np_image = _imageToNumpyArray(image)

    height = np_image.shape[0]
    width = np_image.shape[1]
    height_reg = np_region.shape[0]
    width_reg = np_region.shape[1]

    if height > height_reg or width > width_reg:
        raise ValueError(
            f"The region ({np_region.shape}) is smaller than the image ({np_image.shape}) you are looking for"
        )

    if grayscale:
        np_image = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)
        np_region = cv2.cvtColor(np_region, cv2.COLOR_RGB2GRAY)

        image_capture = np_image
        region_capture = np_region
    else:
        # RGB = np_region[1770][1223], maybe store it for pixel comparing
        image_capture = np_image
        region_capture = np_region
        # both images must be stored in BGR format for futher matchTemplate
        np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        np_region = cv2.cvtColor(np_region, cv2.COLOR_RGB2BGR)

        # imread from np_image must create always BGR images, but in my case it is RGB
        # sct.grab from np_region create always RGB images

    if Config.COMPRESSION_RATIO > 1:
        np_image = _imgDownsize(np_image, Config.COMPRESSION_RATIO)
        np_region = _imgDownsize(np_region, Config.COMPRESSION_RATIO)
    elif Config.COMPRESSION_RATIO < 1:
        raise ValueError(
            f"Couldn't recognize COMPRESSION_RATIO: {Config.COMPRESSION_RATIO}"
        )

    # also can use cv2.TM_CCOEFF, TM_CCORR_NORMED and TM_CCOEFF_NORMED in descending order of speed
    # for TM_CCORR_NORMED, minimum precision is 0.991
    result = cv2.matchTemplate(np_region, np_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if Config.COMPRESSION_RATIO > 1:
        max_loc = (
            max_loc[0] * Config.COMPRESSION_RATIO + 1,
            max_loc[1] * Config.COMPRESSION_RATIO + 1,
        )

    if tuple_region:
        max_loc = (tuple_region[0] + max_loc[0], tuple_region[1] + max_loc[1])

    x = round(max_loc[0] + width / 2)
    y = round(max_loc[1] + height / 2)
    max_loc_center = x, y

    logging.debug(f"cur: {round(max_val, 6)} prec: {precision}  {image}")

    if max_val < precision:
        return None
    if not pixel_colors:
        return Match(
            max_loc, max_loc_center, max_val, precision, image_capture, region_capture
        )
    elif _getPixel(*max_loc_center) == pixel_colors:
        return Match(
            max_loc, max_loc_center, max_val, precision, image_capture, region_capture
        )


def _getPixel(x, y):
    # TODO: Add a way to work with the finished np_image to avoid second grab call
    tmp_reg = sct.grab((x, y, x + 1, y + 1))
    tmp_reg = np.array(tmp_reg)
    r = tmp_reg[0][0][2]
    g = tmp_reg[0][0][1]
    b = tmp_reg[0][0][0]
    return (r, g, b)


@failSafeCheck
def _hotkey(*keys, interval=0.0):
    if Config.OSX:
        if interval < 0.02:
            interval = 0.02

    logging.debug(f"{keys}, interval: {interval}")

    for key in keys:
        if isinstance(key, str):
            key = key.lower()
        manager.press(key)
        time.sleep(interval)

    logging.debug(f"Pressed: {manager.pressed_keys}")

    for key in reversed(keys):
        if isinstance(key, str):
            key = key.lower()
        manager.release(key)
        time.sleep(interval)

    logging.debug(f"Released: {manager.pressed_keys}")


@failSafeCheck
def _tap(key, presses=1, interval=0.0, time_step=Config.DEFAULT_TIME_STEP):
    """tap function for tapping

    Args:
        key (_type_): _description_
        presses (int, optional): _description_. Defaults to 1.
        interval (float, optional): _description_. Defaults to 0.0.
        time_step (_type_, optional): _description_. Defaults to DEFAULT_TIME_STEP.
    """

    if Config.OSX and interval < 0.02:
        interval = 0.02
    for x in range(presses):
        logging.debug(f"tap: {key}")
        logging.debug(manager.pressed_keys)

        manager.press(key)
        time.sleep(time_step)
        manager.release(key)
        time.sleep(time_step)

        time.sleep(interval)


@failSafeCheck
def _keyUp(key):
    manager.release(key)


@failSafeCheck
def _keyDown(key):
    manager.press(key)


@failSafeCheck
def _write(message):
    manager.type(message)


@failSafeCheck
def _mouseMove(loc, duration=0.0):
    ag.moveTo(loc[0], loc[1], duration)


@failSafeCheck
def _mouseMoveRelative(xOffset, yOffset, duration=0.0):
    ag.moveRel(xOffset, yOffset, duration)


@failSafeCheck
def _mouseDown(
    loc_or_pic=None,
    button=Config.MOUSE_LEFT,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
):
    x, y = _getCoordinates(
        loc_or_pic, region, max_search_time, time_step, grayscale, precision
    )

    ag.mouseDown(x, y, button)


@failSafeCheck
def _mouseUp(
    loc_or_pic=None,
    button=Config.MOUSE_LEFT,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
):
    x, y = _getCoordinates(
        loc_or_pic, region, max_search_time, time_step, grayscale, precision
    )

    ag.mouseUp(x, y, button)


def _rightClick(
    loc_or_pic,
    region=None,
    max_search_time=Config.DEFAULT_MAX_SEARCH_TIME,
    time_step=Config.DEFAULT_TIME_STEP,
    grayscale=Config.DEFAULT_GRAYSCALE,
    precision=Config.DEFAULT_PRECISION,
    clicks=1,
    interval=0.0,
):
    # TODO: correct discription
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
      interval (float, optional): The number of seconds in between each click,
        if the number of clicks is greater than 1. 0.0 by default, for no
        pause in between clicks.

    Returns:
      None
    """
    _click(
        loc_or_pic,
        region,
        max_search_time,
        time_step,
        grayscale,
        precision,
        clicks,
        interval,
        ag.SECONDARY,
    )


def _sleep(secs: float):
    time.sleep(secs)


def _saveNumpyImg(image: np.ndarray, name):
    "image: np.ndarray"
    if name:
        output = f"{name}_{time.strftime('%H_%M_%S')}.png"
    else:
        output = f"image_{time.strftime('%H_%M_%S')}.png"
    cv2.imwrite(output, image)
    path = os.path.join(os.getcwd(), output)
    print(f"Image {path} successfully saved")


def _saveScreenshot(region=None):
    region = _regionNormalization(region)
    output = f"Screenshot_{time.strftime('%H_%M_%S')}.png"
    if not region:
        sct.shot(output=output)
    else:
        screenshot = sct.grab(_regionValidation(region))
        tools.to_png(screenshot.rgb, screenshot.size, output=output)
    path = os.path.join(os.getcwd(), output)
    print(f"Image '{path}' successfully saved")
    return path


def _imagesearchCount(image, precision=0.95):
    # TODO: not yet debugged
    """
    Searches for an image on the screen and counts the number of occurrences.

    input :
    image : path to the target image file (see opencv imread for supported types)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.9

    returns :
    the number of times a given image appears on the screen.
    optionally an output image with all the occurances boxed with a red outline.
    """

    im = sct.grab(sct.monitors[0])
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    if template is None:
        raise FileNotFoundError("Image file not found: {}".format(image))
    template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= precision)
    count = 0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        count = count + 1
    return count


def _imageExistFromFolder(path, precision):
    # TODO: figure out an easy way to get the result of this func
    """
    Get all screens on the provided folder and search them on screen.

    input :
    path : path of the folder with the images to be searched on screen like pics/
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

    returns :
    A dictionary where the key is the path to image file and the value is the position where was found.
    """

    imagesPos = {}
    path = path if path[-1] == "/" or "\\" else path + "/"
    valid_images = [".jpg", ".gif", ".png", ".jpeg"]
    files = [
        f
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f))
        and os.path.splitext(f)[1].lower() in valid_images
    ]
    for file in files:
        ans = _exist(path + file, precision=precision)
        pos = None
        if ans != None:
            pos = ans.getTarget()
        imagesPos[path + file] = pos
    return imagesPos


@failSafeCheck
def _paste(text: str):
    """fast paste text into selected window. Alternative ctrl + v, works in all platform*
    * Linux has not been tested yet

    Args:
        text (str): text, which one will be entered into active window
    """
    _copyToClip(text)
    if Config.OSX:
        _hotkey(Key.cmd, "v")
    else:
        _hotkey(Key.ctrl, "v")


def _copyToClip(text):
    if Config.UNIX:
        return Config.platformModule._copy(text)
    else:
        return clip.copy(text)


def _pasteFromClip():
    if Config.UNIX:
        return Config.platformModule._paste()
    else:
        return clip.paste()


def _dragDrop(start_location: list, end_location: list, duration=0.3, button="left"):
    """_summary_

    Args:
        start_location (list): x, y start location example: [1200, 700]
        end_location (list): x, y end location example: [1400, 700]
        butt (str, optional): Which button will be holded. Defaults to "left".
    """

    ag.moveTo(start_location[0], start_location[1])
    # time.sleep(0.2)
    ag.dragTo(end_location[0], end_location[1], duration, button=button)


@failSafeCheck
def _activateWindow(app_name: str):
    """focus window with name of application

    Args:
        app_name (str): can be used Firefox, Chrome, Manycam, Finder and other
    """
    return Config.platformModule._activateWindow(app_name)


def _getWindowRegion(app_name: str):
    """
    get the region of a window by its name
    """
    return Config.platformModule._getWindowRegion(app_name)


def _minimizeWindow(app_name: str):
    Config.platformModule._minimizeWindow(app_name)


def _unminimizeWindow(app_name: str):
    Config.platformModule._unminimizeWindow(app_name)


@failSafeCheck
def _deleteFile(file_path):
    logging.debug(f"deleting {file_path}")
    send2trash(file_path)
