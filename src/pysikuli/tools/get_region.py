import pyautogui
import time
import pyperclip
import os

from playsound import playsound

sound_capture_path = os.path.join("tools", "_capture.mp3")
sound_success_path = os.path.join("tools", "_success.mp3")


def getRegion(pos_count, interval):
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
            
            playsound(sound_capture_path)
            print(f"Corner captured {points} left")
        
        time.sleep(interval)
    
    leftUpLoc = [min(first_pos[0], second_pos[0]), min(first_pos[1], second_pos[1])]
    rightDownLoc = [max(first_pos[0], second_pos[0]), max(first_pos[1], second_pos[1])]

    if pos_count == 2:
        reg = [leftUpLoc[0], leftUpLoc[1], rightDownLoc[0], rightDownLoc[1]]
        print("\nRegion format: x1y1x2y2")
    elif pos_count == 1:
        reg = [leftUpLoc[0], leftUpLoc[1], rightDownLoc[0] - leftUpLoc[0], rightDownLoc[1] - leftUpLoc[1]]
        print("\nRegion format: x1y1wh")
    else:
        raise ValueError("wrong pos_count")
    
    pyperclip.copy(f"{reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}")
    print(f"Region = ({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}), already copied to the clipboard")

    playsound(sound_success_path)

if __name__ == "__main__":
    getRegion(2, 0.5)
