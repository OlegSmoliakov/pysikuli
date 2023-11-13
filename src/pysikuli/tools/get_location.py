import pyautogui
import time
import pyperclip
import os
import mss
import numpy as np

from playsound import playsound


sound_capture_path = os.path.join("tools", "_capture.mp3")
sound_success_path = os.path.join("tools", "_success.mp3")


def getPixel(x, y):
    sct = mss.mss()

    tmp_reg = sct.grab((x, y, x+1, y+1))
    tmp_reg= np.array(tmp_reg)
    R = tmp_reg[0][0][2]
    G = tmp_reg[0][0][1]
    B = tmp_reg[0][0][0]
    return (R, G, B)


def getLocation(interval):
    check_3 = [0, 0, 0]

    while True:
        x, y = pyautogui.position()
        text = f"Current XY: [{x}, {y}]  RGB: {getPixel(x, y)}"
        print(text)

        check_3[0] = check_3[1]
        check_3[1] = check_3[2]
        check_3[2] = [x, y]
        
        if check_3[0] == check_3[1] == check_3[2]:
            text = f"\nCaptured XY: [{x}, {y}]"
            print(text)

            pyperclip.copy(f"({x}, {y})")
            playsound(sound_capture_path)
            break
        
        time.sleep(interval)


if __name__ == "__main__":
    getLocation(0.5)