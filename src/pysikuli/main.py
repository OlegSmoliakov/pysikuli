import pyperclip as clip
import pyautogui as ag
import numpy as np
import subprocess
import platform
import logging
import time
import mss
import mss.tools
import cv2
import sys
import re
import os

from .keys import Key
from .refresh_rate import getRefreshRate
from send2trash import send2trash
from PyHotKey import keyboard_manager as manager

class pysikuliException(Exception):
    """
    pysikuli code will raise this exception class for any invalid actions. If pysikuli raises some other exception,
    you should assume that this is caused by a bug in pysikuli itself. (Including a failure to catch potential
    exceptions raised by pysikuli.)
    """

class FailSafeException(pysikuliException):
    """
    This exception is raised by pysikuli functions when the user puts the mouse cursor into one of the "failsafe
    points" (by default, one of the four corners of the primary monitor). This exception shouldn't be caught; it's
    meant to provide a way to terminate a misbehaving script.
    """

class ActiveWindow:
    final_hwnd = 0

    def winEnumHandler(self, hwnd, ctx):
        if w32.IsWindowVisible(hwnd) and self.name in w32.GetWindowText(hwnd).lower():
            self.final_hwnd = hwnd
            print(hwnd, w32.GetWindowText(hwnd))

    def set_foreground(self, name: str):
        self.name = name.lower()
        w32.EnumWindows(self.winEnumHandler, None)
        """put the window in the foreground"""
        print(self.final_hwnd, "selected")
        w32.SetForegroundWindow(self.final_hwnd)


def _mouseFailSafeCheck():
    if tuple(ag.position()) in FAILSAFE_POINTS:
        return True
    
def _hotkeyFailSafeCheck():
    pressed = 0
    ans = manager.pressed_keys
    for key in FAILSAFE_HOTKEY:
        if key in ans:
            pressed += 1
    if pressed == 3:
        return True

def failSafeCheck():
    if FAILSAFE:
        if _hotkeyFailSafeCheck() or _mouseFailSafeCheck():
            raise FailSafeException(
                "pysikuli fail-safe triggered from mouse moving to a corner of the screen. To disable this fail-safe, set pysikuli.FAILSAFE to False. DISABLING FAIL-SAFE IS NOT RECOMMENDED."
            )

def _failSafeCheck(wrappedFunction):
    """
    A decorator that calls failSafeCheck() before the decorated function
    """

    def failSafeWrapper(*args, **kwargs):
        failSafeCheck()
        returnVal = wrappedFunction(*args, **kwargs)
        return returnVal

    return failSafeWrapper

#TODO: calculate time_step via fps for all function i think it's doesn't affect speed

sct = mss.mss()    # is an alias for mss.mss()
MONITOR_RESOLUTION = sct.grab(sct.monitors[0]).size
MONITOR_REGION = (0, 0, MONITOR_RESOLUTION[0] - 1, MONITOR_RESOLUTION[1] - 1)
# MAXIMUM_REFRESH_RATE = getRefreshRate()
MAXIMUM_REFRESH_RATE = 60
MOUSE_MOVE_SPEED = 0.0
COMPRESSION_RATIO = 2       # at 1 - the image size doesn't change
DEFAULT_PRECISION = 0.8
DEFAULT_MAX_SEARCH_TIME = 2.0
DEFAULT_TIME_STEP = round(1 / MAXIMUM_REFRESH_RATE, 5)

FAILSAFE = True
FAILSAFE_POINTS = [(0, 0)]
FAILSAFE_HOTKEY = [Key.ctrl, Key.alt, "k"]

# The number of seconds to pause after EVERY public function call. Useful for debugging:
PAUSE_BETWEEN_ACTION = 0.001         #for pyautogui module 
ag.PAUSE = PAUSE_BETWEEN_ACTION 
ag.FAILSAFE = False

OSX = 0
WIN = 0
UNIX = 0

system = platform.system()
if system == "Darwin":
    OSX = 1
elif system == "Windows":
    WIN = 1
elif system == "Linux":
    UNIX = 1
else:
    raise OSError("Can't recognize system os")

class region(object):
    TIME_STEP = DEFAULT_TIME_STEP
    COMPRESSION_RATIO = COMPRESSION_RATIO 
    
    def __init__(self, x1: int, y1: int, x2: int, y2: int): 
        checkRegion(x1, y1, x2, y2)
        self.reg = (x1, y1, x2, y2)
    
            
    def has(self,
            image: str,
            max_search_time = DEFAULT_MAX_SEARCH_TIME,
            grayscale = True,
            precision = DEFAULT_PRECISION,
            pixel_colors: tuple = None):
        
        if pixel_colors:
            _match = find(image,
                          self.reg,
                          max_search_time,
                          self.TIME_STEP,
                          grayscale,
                          precision,
                          pixel_colors)
            if not _match:
                logging.info(f"has() couldn't find the specific pixel in the region: {image}")
                return False
            return True
            
        _match = self.find(image, max_search_time, grayscale, precision)
        if not _match:
            logging.debug(f"has() couldn't find the image: {image}")
            return False
        return True
    
    
    def wait(self,
            image: str,
            max_search_time = DEFAULT_MAX_SEARCH_TIME,
            grayscale = True,
            precision = DEFAULT_PRECISION,
            pixel_colors = None) -> bool | None:
        
        return wait(image, self.reg, max_search_time, self.TIME_STEP, grayscale, precision, pixel_colors)
    
    
    def click(self,
            #search variables
            loc_or_pic,
            max_search_time = DEFAULT_MAX_SEARCH_TIME,
            grayscale = True,
            precision = DEFAULT_PRECISION,
            
            #click variables
            clicks = 1,
            interval = 0.0,
            button = ag.PRIMARY):
        click(loc_or_pic, self.reg, max_search_time, self.TIME_STEP, grayscale, precision, clicks, interval, button)
    
    
    def rightClick(self, loc_or_pic, max_search_time = DEFAULT_MAX_SEARCH_TIME, grayscale=True, precision=DEFAULT_PRECISION, clicks=1, interval=0.0):
        rightClick(loc_or_pic, self.reg, max_search_time, self.TIME_STEP, grayscale, precision, clicks, interval)
    
    
    def find(self, image, max_search_time = DEFAULT_MAX_SEARCH_TIME, grayscale = True, precision = DEFAULT_PRECISION):
        return find(image, self.reg, max_search_time, self.TIME_STEP, grayscale, precision) 
    
    
    def findAny(self, image, grayscale=True, precision=DEFAULT_PRECISION):
        return findAny(image, self.reg, grayscale, precision=precision)
    
    
    def exist(self, image, grayscale=True, precision = DEFAULT_PRECISION):
        return exist(image, self.reg, grayscale, precision)


class match(object):
    def __init__(self,
                 up_left_loc: tuple,
                 target_loc: tuple,
                 score: float,
                 precision: float) -> None:
        self.up_left_loc = up_left_loc
        self.target_loc = target_loc
        self.target_x = target_loc[0]
        self.target_y = target_loc[1]
        self.score = score
        self.precision = precision
    
    
    def getScore(self):
        return self.score
    
    
    def getPrecision(self):
        return
    
    
    def getTarget(self):
        return self.target_loc
    
    
    def setTargetOffset(self, x, y):
        self.target_x += x
        self.target_y += y
        self.target_loc = (self.target_x, self.target_y)
        return self.target_loc


def checkRegion(x1, y1, x2, y2):
    if not (x1 < x2 and y1 < y2):
        raise TypeError("Entered region is incorrect")


def imgDownsize(img, multiplier):
    """
    multiplier must be even [2-8]
    a small boost if the multiplier is greater than 4
    """
    width = int(img.shape[1] / multiplier)
    height = int(img.shape[0] / multiplier)
    dim = (width, height)
    
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


def wait(image: str,
        region = None,
        max_search_time = DEFAULT_MAX_SEARCH_TIME,
        time_step = DEFAULT_TIME_STEP,
        grayscale = True,
        precision = DEFAULT_PRECISION,
        pixel_colors = None) -> bool | None:
        
        if find(image, region, max_search_time, time_step, grayscale, precision, pixel_colors):
            return True 
        else:
            error_text = f"wait(): couldn't find the picture: {image}"
            logging.fatal(error_text)
            raise TimeoutError(error_text)

@_failSafeCheck
def click(loc_or_pic,
        region = None,
        max_search_time = DEFAULT_MAX_SEARCH_TIME,
        time_step = DEFAULT_TIME_STEP,
        grayscale = True,
        precision = 0.9,
        
        #click variables
        clicks = 1,
        interval = 0.0,
        button = ag.PRIMARY):
    
    if OSX and interval < 0.02:
        interval = 0.02

    _type = type(loc_or_pic)
    
    if _type == list or _type == tuple:
        x, y = loc_or_pic
    elif _type == str:
        _match = find(loc_or_pic, region, max_search_time, time_step, grayscale, precision)
        if not _match:
            error_text = f"click(): couldn't find the picture: {loc_or_pic}"
            logging.fatal(error_text)
            raise TimeoutError(error_text)
        x, y = _match.getTarget()
    else:
        raise TypeError(f"can't recognize this type of data: {loc_or_pic}")
    logging.debug(f"click: {x, y}, clicks: {clicks} interval: {interval} button: {button}, mouse_move_speed: {MOUSE_MOVE_SPEED}")
    ag.click(x, y, clicks, interval, button, MOUSE_MOVE_SPEED)


def find(image,
        region = None,
        max_search_time = DEFAULT_MAX_SEARCH_TIME,
        time_step = DEFAULT_TIME_STEP,   
        grayscale = True,
        precision = DEFAULT_PRECISION,
        pixel_colors = None):
    start_time = time.time()
    while time.time() - start_time < max_search_time:   
        _match = exist(image, region, grayscale, precision)
        if _match != None: 
            if pixel_colors:
                if getPixel(*_match.getTarget()) == pixel_colors:
                    return _match
            else:
                return _match
        time.sleep(time_step)
    return None


def findAny(image_list, region=None, grascale=True, precision = DEFAULT_PRECISION):
    if not region:
        tmp_region = sct.grab(sct.monitors[0]) 
    else:
        tmp_region = sct.grab(region)
    tmp_region = np.array(tmp_region)
    
    matches = []
    for image in image_list:
        matches.append(exist(image, region, grascale, precision=precision, nd_region=tmp_region))
    return [x for x in matches if x is not None]


def exist(image, region = None, grayscale = True, precision=DEFAULT_PRECISION, nd_region: np.ndarray = None):
    # TODO: create discription
    # simple way to debug from main or other scripts
    '''
    Searchs for an image within an area or on the screen

    input :

    image : path to the image file (see opencv imread for supported types)
    region : (x1, y1, x2, y2)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8
    nd_region : a PIL image, usefull if you intend to search the same unchanging region for several elements, must be stored in ``RGB format``

    returns :
    the top left corner coordinates of the element if found as an array [x,y] or [-1,-1] if not
    '''
    
    if isinstance(nd_region, np.ndarray):
        tmp_region = nd_region
    else: 
        if not region:
            tmp_region = sct.grab(sct.monitors[0])  
        else:
            tmp_region = sct.grab(region)
        tmp_region = np.array(tmp_region)
    
    if grayscale:
        tmp_image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        tmp_region = cv2.cvtColor(tmp_region, cv2.COLOR_RGB2GRAY)
    else:
        # RGB = tmp_region[1770][1223], maybe store it for pixel comparing
        
        #both images must be stored in BGR format for futher matchTemplate
        tmp_image = cv2.imread(image, cv2.IMREAD_COLOR)     #imread must create always BGR images, but in my case it is RGB
        tmp_image = cv2.cvtColor(tmp_image, cv2.COLOR_RGB2BGR)
        tmp_region = cv2.cvtColor(tmp_region, cv2.COLOR_RGB2BGR)    #sct.grab create always RGB images
    
    if tmp_image is None:
        raise FileNotFoundError(f"Image file not found: {image}")
    
    height = tmp_image.shape[0]
    width = tmp_image.shape[1]
    height_reg = tmp_region.shape[0]
    width_reg = tmp_region.shape[1]

    if height > height_reg or width > width_reg:
        raise InterruptedError(f"The region is smaller than the image you are looking for: {image}")

    if COMPRESSION_RATIO > 1:
        tmp_image = imgDownsize(tmp_image, COMPRESSION_RATIO)
        tmp_region = imgDownsize(tmp_region, COMPRESSION_RATIO)
    elif COMPRESSION_RATIO < 1:
        raise InterruptedError(f"Couldn't recognize COMPRESSION_RATIO: {COMPRESSION_RATIO}")
    
    # also can use cv2.TM_CCOEFF, TM_CCORR_NORMED and TM_CCOEFF_NORMED in descending order of speed
    # for TM_CCORR_NORMED, minimum precision is 0.991
    result = cv2.matchTemplate(tmp_region, tmp_image, cv2.TM_CCOEFF_NORMED)
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if COMPRESSION_RATIO > 1:
        max_loc = (max_loc[0] * COMPRESSION_RATIO + 1, max_loc[1] * COMPRESSION_RATIO + 1) 

    if region:
        max_loc =  (region[0] + max_loc[0], region[1] + max_loc[1])
    else:
        region = MONITOR_REGION
    
    x = round(max_loc[0] + width / 2 )
    y = round(max_loc[1] + height / 2)
    max_loc_center = x, y
    
    logging.debug(f"cur: {round(max_val, 6)} prec: {precision}  {image}")
    
    if max_val < precision:
        return None
    return match(max_loc, max_loc_center, max_val, precision)


def getPixel(x, y):
    tmp_reg = sct.grab((x, y, x+1, y+1))
    tmp_reg= np.array(tmp_reg)
    r = tmp_reg[0][0][2]
    g = tmp_reg[0][0][1]
    b = tmp_reg[0][0][0]
    return (r, g, b)

 
#based on pyautogui, sometimes works wrong
def _hotkey(*args, interval=0.0):
    if OSX:
        if interval < 0.02:
            interval = 0.02
    logging.debug(f"{args}, interval: {interval}")
    ag.hotkey(args, interval=interval) 

@_failSafeCheck
def hotkey(*args, interval=0.0):
    if OSX:
        if interval < 0.02:
            interval = 0.02
            
    logging.debug(f"{args}, interval: {interval}")

    for key in args:
        if isinstance(key, str):
            key = key.lower()
        manager.press(key)
        time.sleep(interval)

    logging.debug(f"Pressed: {manager.pressed_keys}")

    for key in reversed(args):
        if isinstance(key, str):
            key = key.lower()
        manager.release(key)
        time.sleep(interval)

    logging.debug(f"Released: {manager.pressed_keys}")

@_failSafeCheck
def tap(key, presses = 1, interval = 0.0, time_step=DEFAULT_TIME_STEP):
    if OSX and interval < 0.02:
        interval = 0.02
    for x in range(presses):
        logging.debug(f"tap: {key}")
        logging.debug(manager.pressed_keys)

        manager.press(key)
        time.sleep(time_step)
        manager.release(key)
        time.sleep(time_step)

        time.sleep(interval)

@_failSafeCheck
def keyUp(key):
    manager.release(key)

@_failSafeCheck
def keyDown(key):
    manager.press(key)

@_failSafeCheck
def write(message):
    manager.type(message)

@_failSafeCheck
def mouseMove(loc, duration=0.0):
    # ag.moveTo(loc[0], loc[1], duration)
    x = loc[0]
    y = loc[1]
    ag._mouseMoveDrag("move", x, y, 0, 0, duration)

@_failSafeCheck
def mouseMoveRelative(xOffset, yOffset, duration=0.0):
    x, y = ag.position()
    x += xOffset
    y += yOffset
    ag._mouseMoveDrag("move", x, y, 0, 0, duration)


def rightClick(loc_or_pic, region=None, max_search_time = DEFAULT_MAX_SEARCH_TIME, time_step=DEFAULT_TIME_STEP, grayscale=True, precision=DEFAULT_PRECISION, clicks=1, interval=0.0):
    #TODO: correct discription
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
    click(loc_or_pic, region, max_search_time, time_step, grayscale, precision, clicks, interval, ag.SECONDARY)


def sleep(secs: float):
    time.sleep(secs)


def saveImg(image):
    "image: np.ndarray"
    
    output =  f"image_{time.strftime('%H_%M_%S')}.png"
    cv2.imwrite(output, image)


def saveScreenshot(region = None):
    output =  f"Screenshot_{time.strftime('%H_%M_%S')}.png" 
    if not region:
        screenshot = sct.grab(sct.monitors[0]) 
    else:
        screenshot = sct.grab(region)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output=output)
    
    print("Pic saved")


def imagesearchCount(image, precision=0.95):
    #TODO: not yet debugged
    '''
    Searches for an image on the screen and counts the number of occurrences.

    input :
    image : path to the target image file (see opencv imread for supported types)
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.9

    returns :
    the number of times a given image appears on the screen.
    optionally an output image with all the occurances boxed with a red outline.
    '''
    
    im = sct.grab(sct.monitors[0])
    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    if template is None:
        raise FileNotFoundError('Image file not found: {}'.format(image))
    template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= precision)
    count = 0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        count = count + 1
    return count


def imageExistFromFolder(path, precision):
    #TODO: figure out an easy way to get the result of this func
    '''
    Get all screens on the provided folder and search them on screen.

    input :
    path : path of the folder with the images to be searched on screen like pics/
    precision : the higher, the lesser tolerant and fewer false positives are found default is 0.8

    returns :
    A dictionary where the key is the path to image file and the value is the position where was found.
    '''
    
    imagesPos = {}
    path = path if path[-1] == '/' or '\\' else path+'/'
    valid_images = [".jpg", ".gif", ".png", ".jpeg"]
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1].lower() in valid_images]
    for file in files:
        ans = exist(path+file, precision=precision)
        pos = None
        if ans != None:
            pos = ans.getTarget()
        imagesPos[path+file] = pos
    return imagesPos

@_failSafeCheck
def paste(text: str):
    """fast paste text into selected window. Alternative ctrl + v, works in all platform*
    * Linux has not been tested yet

    Args:
        text (str): text, which one will be entered into active window
    """
    clip.copy(text)
    if OSX:
        hotkey(Key.cmd, "v")
    else:
        hotkey(Key.ctrl, "v")


def dragDrop(start_location: list, end_location: list, duration = 0.3, button = "left"):
    """_summary_

    Args:
        start_location (list): x, y start location example: [1200, 700]
        end_location (list): x, y end location example: [1400, 700]
        butt (str, optional): Which button will be holded. Defaults to "left".
    """
    
    ag.moveTo(start_location[0], start_location[1])
    # time.sleep(0.2)
    ag.dragTo(end_location[0], end_location[1], duration, button=button)
   
@_failSafeCheck
def activateWindow(app_name: str):
    """focus window with name of application

    Args:
        app_name (str): can be used Firefox, Chrome, Manycam, Finder and other
    """

    #TODO: activate only if the application has not been activated before
    if OSX:
        cmd = f'osascript -e \'activate application "{app_name}"\''
        ans = subprocess.call(cmd, shell=True)
        if ans:
            logging.warning(f"activateWindow(): {app_name} failed")
            return 1
        logging.debug(f"activateWindow(): {app_name} activated")
        return 0
    
    elif WIN:
        import win32gui as w32
        ActiveWindow().set_foreground(app_name)
        logging.debug("{0} activated".format(app_name))
        return 0
    

def getWindowRegion(app_name: str):
    """
    get the region of a window by its name in the 
    """
    if OSX:
        APPLESCRIPT = f"""
        tell application "{app_name}" to get the bounds of window 1
        """
        response = str(subprocess.run(['osascript', '-e', APPLESCRIPT], capture_output=True).stdout)
        if response == "b''":
            error_text = f"Couldn't find '{app_name}' window, current response: {response}"
            logging.fatal(error_text)
            raise OSError(error_text)
        response = [int(i) for i in re.sub(r'[^0-9,]', '', response).split(",")]
        region = [response[0], response[1], response[2]-1, response[3]-1]
        return region


def minimizeWindow(app_name: str):
    
    if OSX:
        APPLESCRIPT = f"""
        tell application "{app_name}" 
            set miniaturized of window 1 to true
        end tell
        """
        print(subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True))


def unminimazeWindow(app_name: str):
    #TODO: doesn't work
    if OSX:
        APPLESCRIPT = f"""
        tell application "{app_name}"
            activate
            delay 1
            end tell
        tell application "System Events" to set visible of process "{app_name}" to true
        """
        print(subprocess.run(["osascript", "-e", APPLESCRIPT], capture_output=True)) 

@_failSafeCheck
def deleteFile(file_path):
    logging.debug(f"deleting {file_path}")
    # os.remove(file_path)  previous version
    send2trash(file_path)


if __name__ == "__main__":
    logging.basicConfig(
        # filemode= str(datetime.now()) + ".log", 
        level=logging.INFO,
        format= "%(asctime)s: %(levelname)s: %(message)s")
    
    img = "pics/opencv_test.png"

    # tmp_region = sct.grab((1288, 31, 2875, 828))
    # tmp_region = np.array(tmp_region)
    from pyinstrument import Profiler
    with Profiler(interval=0.0001) as profiler:
        for k in range(1):
            pass

            # image = image[:, :, ::-1]     #do the same as RGB2BGR
            #both images must be stored in BGR format for futher matchTemplate
            

            # ans = exist(img, region=(1288, 31, 2875, 828), grayscale= True, precision=DEFAULT_PRECISION, nd_region=tmp_region)
            # testreg = region(1288, 31, 2875, 828)
            # ans = testreg.click(img)
            # print(ans)

            # hotkey(Key.cmd, "a")
    activateWindow("ManyCam")
    # w32.SetForegroundWindow("2951236")
                
    # profiler.open_in_browser()