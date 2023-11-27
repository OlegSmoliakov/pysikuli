import pyautogui
import time
from ._main import _getPixel, _copyToClip
from ._config import Config


def _setPlaysound():
    def _playsound(sound):
        pass

    if Config.SOUND_ON:
        from playsound import playsound

        return playsound
    else:
        return _playsound


def _getLocation(interval=0.5):
    playsound = _setPlaysound()
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

            _copyToClip(f"({x}, {y})")
            playsound(Config.SOUND_CAPTURE_PATH)
            break

        time.sleep(interval)

    playsound(Config.SOUND_FINISH_PATH)


def _getRegion(reg_format, interval=0.5, test_interrupt_offset=0):
    playsound = _setPlaysound()
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

            playsound(Config.SOUND_CAPTURE_PATH)
            print(f"Corner captured {points} left")

        time.sleep(interval)

        if points < 2 and test_interrupt_offset:
            pyautogui.moveRel(test_interrupt_offset, test_interrupt_offset)
            test_interrupt_offset = 0

    leftUpLoc = [min(first_pos[0], second_pos[0]), min(first_pos[1], second_pos[1])]
    rightDownLoc = [max(first_pos[0], second_pos[0]), max(first_pos[1], second_pos[1])]

    if reg_format == "x1y1x2y2":
        reg = [leftUpLoc[0], leftUpLoc[1], rightDownLoc[0], rightDownLoc[1]]
        print(f"\nRegion format set: {reg_format}")
    elif reg_format == "x1y1wh":
        reg = [
            leftUpLoc[0],
            leftUpLoc[1],
            rightDownLoc[0] - leftUpLoc[0],
            rightDownLoc[1] - leftUpLoc[1],
        ]
        print(f"\nRegion format set: {reg_format}")
    else:
        raise ValueError("wrong reg_format")

    _copyToClip(f"{reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}")
    print(
        f"Region = ({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}), already copied to the clipboard"
    )

    playsound(Config.SOUND_FINISH_PATH)
