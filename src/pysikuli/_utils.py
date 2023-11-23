import pyautogui
import time
import pyperclip
from playsound import playsound
from ._main import _getPixel
from .config import SOUND_CAPTURE_PATH, SOUND_FINISH_PATH


def _getLocation(interval=0.5):
    check_3 = [0, 0, 0]

    while True:
        x, y = pyautogui.position()
        text = f"Current XY: [{x}, {y}]  RGB: {_getPixel(x, y)}"
        print(text)

        check_3[0] = check_3[1]
        check_3[1] = check_3[2]
        check_3[2] = [x, y]

        if check_3[0] == check_3[1] == check_3[2]:
            text = f"\nCaptured XY: [{x}, {y}]"
            print(text)

            pyperclip.copy(f"({x}, {y})")
            playsound(SOUND_CAPTURE_PATH)
            break

        time.sleep(interval)

    playsound(SOUND_FINISH_PATH)


def _getRegion(reg_format, interval=0.5):
    points = 2
    check_3 = [0, 0, 0]
    lastLoc = [0, 0]

    while points > 0:
        x, y = pyautogui.position()
        text = "Current XY: [" + str(x) + ", " + str(y) + "]"
        print(text)

        check_3[0] = check_3[1]
        check_3[1] = check_3[2]
        check_3[2] = [x, y]

        if check_3[0] == check_3[1] == check_3[2] and [x, y] != lastLoc:
            points -= 1
            if points:
                first_pos = [x, y]
            elif not points:
                second_pos = [x, y]
            lastLoc = [x, y]

            playsound(SOUND_CAPTURE_PATH)
            print(f"Corner captured {points} left")

        time.sleep(interval)

    leftUpLoc = [min(first_pos[0], second_pos[0]), min(first_pos[1], second_pos[1])]
    rightDownLoc = [max(first_pos[0], second_pos[0]), max(first_pos[1], second_pos[1])]

    if reg_format == 2:
        reg = [leftUpLoc[0], leftUpLoc[1], rightDownLoc[0], rightDownLoc[1]]
        print("\nRegion format: x1y1x2y2")
    elif reg_format == 1:
        reg = [
            leftUpLoc[0],
            leftUpLoc[1],
            rightDownLoc[0] - leftUpLoc[0],
            rightDownLoc[1] - leftUpLoc[1],
        ]
        print("\nRegion format: x1y1wh")
    else:
        raise ValueError("wrong reg_format")

    pyperclip.copy(f"{reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}")
    print(
        f"Region = ({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}), already copied to the clipboard"
    )

    playsound(SOUND_FINISH_PATH)
