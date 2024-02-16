[![PyPI version](https://badge.fury.io/py/pysikuli.svg)](https://badge.fury.io/py/pysikuli)
# Pysikuli
This is a fast cross-platform python module for gui automation

<details open>
    <summary><h2>Table Of Content</h2></summary>

-  [Documentation](#documentation)
-  [Introduction](#introduction)
-  [Quickstart](#quickstart)
-  [Small Example](#small-example)
-  [How reach the max speed](#how-reach-the-max-speed)
-  [Instalation](#installation)
-  [VS Code add-ons](#vs-code-add-ons)

</details>

## Documentation
Full documentation and some tutorials is available here: [Documentation](https://pysikuli.readthedocs.io/en/latest/)

## Introduction
Pysikuli initially inspired by [Sikuli Project](http://sikulix.com/) and secondly by python automation tools such as [pyautogui](https://github.com/asweigart/pyautogui) and the quick image search in [python-imagesearch](https://github.com/drov0/python-imagesearch) library. So if you already know about **Sikuli** or **pyautogui**, but want to speed up your scripts to the max, you're in the right place.

Pysikuli helps to automate almost every user actions in Windows, Linux and MacOS.

In short, Pysikuli can :
- Search for an image on the entire screen as well as on a specific part of the screen (`Region`)
- Emulate user acivity via **Keyboard** and **Mouse**
- Make some manipulation with app's **window**s, e.g. **move**, **maximize** or **close**
- Use **clipboard**
- Call **popup**
- Delete files

## Quickstart
Once the installation is complete, import the main classes into your project:
```python
import pysikuli as sik
from pysikuli import Key, Button, Region, config
```
### For keyboard presses use:
`tap()`, `write()` or `hotkey()`
```python
sik.tap(Key.backspace)
sik.write("pysikuli")
sik.hotkey(Key.ctrl, Key.shift, Key.esc)
```
### For mouse movement use:
`click()`, `mouseMove()` or `scroll()`
```python
sik.mouseMove((100,100))
sik.click(button=Button.left)
sik.scroll(duration=0.5, horizontal_speed=0.1, vertical_speed=0.1)
sik.dragDrop(destination_loc=(200, 200), start_location=(100, 100), speed=1)
```
### Image searching:
```python
sik.find(image="/some_path", max_search_time=5)
sik.exist(image="/path_to_image")
sik.wait(image="/path_to_image")
sik.existAny()
```
The search functions will return a `Match` object (if found successfully), where you can get the center coordinates, set offset, show found image or region (more details in the [Documentation](#documentation)). Also, you can pass an image pattern to almost every mouse-related function, instead of `Location`.
### Clipboard management:
```python
sik.copyToClip("test")
text = sik.pasteFromClip()
sik.paste("paste text directly in active window")
```
### Other useful functions:
```python
sik.deleteFile("/file/path")
sik.popupAlert(text="some popup breakpoint in your script", title="alert")
sik.cleanupPics(pics_folder_path="/pics")
sik.activateWindow("Google Chrome")
sik.getWindowRegion("Google Chrome")
```

### Location 
`Location` is a tuple with 2 values - **X** and **Y**, which represent posistion of one pixel on the screen. The **X** axis is directed from left side to right, as usual, but The **Y** is axis directed from top to bottom. 

For example `Location` with value `(0, 0)`, is located in the left top corner of the screen, and `Location` with `(1920, 1080)` value is located in the right bottom corner of the Full HD screen.
### Region
`Region` (rectangular pixel area on a screen) does not know anything about it’s visual content. It only knows the position on the screen and its dimension.

`Region` let to determine a specific screen are, where you want to find some GUI elements. It increase search speed and let you avoid missfinding similiar objects. Region is defined by top left and right bottom corner points of the area. `(x1, y1, x2, y2)`

```
(0,0)               (960,0)              (1920,0)
  +--------------------+---------------------+
  |                    |                     |
  |                    |                     |
  |                    |                     |
  |                    |                     |
  |--------------------+                     |
  |                 (960,540)                |
  |                                          |
  |                                          |
  |                                          | 
  +------------------------------------------+
(0, 1080)                               (1920,1080)
```

For example how you can determine top left quarter of the Full HD screen:
```python
#                        (x1, y1, x2, y2)   
top_left_quarter = Region(0, 0, 960, 540)
```
And use all search functions:
```python
top_left_quarter.find(image="/some_path/to_image")
top_left_quarter.wait(image="/some_path/to_image")
```
### Capture Region and Location
You can use `getLocation()` which tracks the mouse position and after holding the mouse in the same spot for 1.5 seconds (by default) you will get the `Location` printed in the terminal and already copied to your clipboard. `getRegion()` works in the same way, but uses 2 spots to define the region.

To have quick and easy access to the `getRegion()` and `getLocation()` functions, I would recommend creating two `.py` files with the same names and put in the code below:

getRegion.py: 

```python
from pysikuli import getRegion

if __name__ == "__main__":
    getRegion()

```
getLocation.py:
```python
from pysikuli import getLocation

if __name__ == "__main__":
    getLocation()

```

After that, all you have to do is run one of these `.py` files and you will get `Region` or `Location`
## Small Example 

The code below runs the calculator, presses 2 + 2 and gets the result
```python
import pysikuli as sik

from pysikuli import Region, Key, Button

if __name__ == "__main__":

    sik.config.MOUSE_SPEED = 2

    pic_2 = "pics/pic_2.png"
    pic_plus = "pics/pic_plus.png"
    pic_equal = "pics/pic_equal.png"

    sik.tap(Key.win), sik.sleep(0.02)
    sik.paste("calculator"), sik.sleep(0.3)
    sik.tap(Key.enter)

    sik.click(pic_2, precision=0.9)
    sik.click(pic_plus)
    sik.click(pic_2, precision=0.9)
    sik.click(pic_equal)
```

![Result](https://github.com/OlegSmoliakov/pysikuli/blob/main/docs/source/tutorials/calculator/calculator_result.gif)

## How reach the max speed?
Pysikuli has `config` variable, which one you can import in this way:
```
from pysikuli import config
``` 
Below is a list of parameters that can impact on search time:
- `config.COMPRESSION_RATIO`: default: 2 - resize image, e.g. if this variable was set to 2, it means that pics become 4 time smaller (height / 2) and (width / 2). Increase search speed almost double, but after the value 4 the speed increases slightly, but accuracy is lost significantly.
- `config.GRAYSCALE`: default: True - it turn on all pics to grayscale. Increase search speed by ~30%. 
- `config.MIN_SLEEP_TIME`: default: 0.02 - is used as a constant minimum delay in some functions on macOS, changing this value may affect the correctness of the OS response.

Other ways to speed up:
- `config.MOUSE_SPEED`: default: 1, it is abstract measure and ≈ 1000 px per second. For instant move set to 1000 or 10000. 
- use `Region`s to narrow the search area of your patterns

## Installation

```
pip install pysikuli
```
### External dependencies

External dependencies mostly belong to the sounddevice module, which is used to user-friendly capture `Region` or `Location`. However, pysikuli can work normally without them.

#### Windows:
sounddevice dependence:
- [Microsoft C++ build tools](https://visualstudio.microsoft.com/visual-cpp-build-tools)


#### Linux:
- sounddevice dependence:
    ```console
    sudo apt install libportaudio2
    ```
    Also, pysikuli will try to install this package on its own the first time you run it

#### MacOS:
You need to enable **Accessibility** and **Screen capture** permissions to terminal or python itself.


## VS Code add-ons
I would also recommend installing these VS Code's add-ons:
- [Paste Image](https://marketplace.visualstudio.com/items?itemName=mushan.vscode-paste-image), for pasting screenshots directly in the code from clipboard. You can also set up a specific folder to store your pics.
- [Image preview](https://marketplace.visualstudio.com/items?itemName=kisstkondoros.vscode-gutter-preview), for preview captured photos
- [luna-paint](https://marketplace.visualstudio.com/items?itemName=Tyriar.luna-paint), useful tool for fast cropping captured images inside VS Code

---
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)