import os
import re
import time

from send2trash import send2trash
from gitignore_parser import parse_gitignore as pgi

from ._main import getPixel, copyToClip, mousePosition, mouseMoveRelative
from ._config import config, _SUPPORTED_PIC_FORMATS


def _setPlaysound():
    def _playsound(sound):
        pass

    if config.SOUND_ON:
        try:
            from playsound import playsound
        except ModuleNotFoundError as e:
            print(
                "Playsound install error, please try to use this commmand: \n"
                "pip install git+https://github.com/killjoy1221/playsound.git \n"
                "or disable this notification by this code: \n"
                "pysikuli.config.SOUND_ON = False \n\n"
            )
            return _playsound

        return playsound
    else:
        return _playsound


def getLocation(interval=0.5):
    playsound = _setPlaysound()
    check_3 = [0, 0, 0]

    while True:
        x, y = mousePosition()
        text = f"Current XY: [{x}, {y}]  RGB: {getPixel((x, y))}"
        print(text)

        check_3[0] = check_3[1]
        check_3[1] = check_3[2]
        check_3[2] = [x, y]

        if check_3[0] == check_3[1] == check_3[2]:
            text = f"\nCaptured XY: [{x}, {y}]"
            print(text)

            copyToClip(f"({x}, {y})")
            playsound(config.SOUND_CAPTURE_PATH)
            break

        time.sleep(interval)

    playsound(config.SOUND_FINISH_PATH)


def _getRegion(reg_format, interval=0.5, test_interrupt_offset=0):
    """
    getRigion helps to determine the Region coordinates.

    Simply by hovering your mouse over points on the screen.
    The region requires 2 points, left-top and right-bottom.
    If you hold the mouse on the same spot for 3 `intervals`
    the point will be captured and capture sound will be played by default

    Args:
        `interval` (float): time in seconds, which uses for delay
        between each mouse posuition capture  . Defaults to 0.5.

    Returns:
        updated clipboard with prepared region like: "Region(1, 2, 3, 4)"
        also print this region in console
    """
    playsound = _setPlaysound()
    points = 2
    check_3 = [0, 0, 0]
    lastLoc = [0, 0]

    while points > 0:
        x, y = mousePosition()
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

            playsound(config.SOUND_CAPTURE_PATH)
            print(f"Corner captured {points} left")

        time.sleep(interval)

        if points < 2 and test_interrupt_offset:
            mouseMoveRelative(test_interrupt_offset, test_interrupt_offset)
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

    copyToClip(f"Region({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]})")
    print(
        f"Region = ({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}), already copied to the clipboard"
    )

    playsound(config.SOUND_FINISH_PATH)


def cleanupPics(pics_folder_path):
    assert os.path.isabs(pics_folder_path)
    pics_folder_name = os.path.basename(pics_folder_path)
    root_path = os.getcwd()
    ignore = pgi(os.path.join(root_path, ".gitignore"))
    ignore_list = [".git", ".github"]

    formats = ""
    for format in _SUPPORTED_PIC_FORMATS:
        formats += f"{format}|"
    formats = formats[:-1]

    def isIgnored(file):
        return ignore(file) if file not in ignore_list else True

    def isDir(file_path):
        return os.path.isdir(file_path) and "__" not in os.path.basename(file_path)

    def isPyFile(file):
        return re.search(r"\.py", file)

    def picParse(file_path: str):
        found_paths = []
        found_names = []

        with open(file_path) as f:
            code = f.read()

        #                     # (pics/image_name.png)   # (pics[\\\\\/]\S*.)(png|jpg|tif)
        matches = re.findall(rf"({pics_folder_name}[\\\\\/]\S*\.)({formats})", code)

        for match in matches:
            match_name = match[0] + match[1]
            match_name = os.path.normpath(match_name)
            match_path = os.path.join(root_path, match_name)
            found_paths.append(match_path)
            found_names.append(match_name)
        return found_paths, found_names

    def findAllPicsPathsInProject(path):
        found_paths = []
        found_names = []
        files = os.listdir(path)
        for file in files:
            file_path = os.path.join(path, file)
            if isIgnored(file):
                pass
            elif isDir(file_path):
                findAllPicsPathsInProject(file_path)
            elif isPyFile(file):
                fnd_paths, fnd_names = picParse(file_path)
                found_paths += fnd_paths
                found_names += fnd_names

        return found_paths, found_names

    def getStoredPics():
        stored = os.listdir(pics_folder_path)
        stored = [
            file_name for file_name in stored if re.search(f".{formats}", file_name)
        ]
        stored = [os.path.join(pics_folder_path, file_name) for file_name in stored]
        return stored

    def getUnusedPics():
        stored = getStoredPics()
        used, _ = findAllPicsPathsInProject(root_path)
        return set(stored) - set(used)

    def prompt_user(pic: str):
        bold = "\033[1m"
        end = "\033[0m"

        print(
            f"\nAre you sure that you want to move to trash '{os.path.basename(pic)}'?\n"
            f"enter {bold}0{end} to skip\n"
            f"enter {bold}1{end} to skip all\n"
            f"enter {bold}2{end} to delete\n"
            f"enter {bold}3{end} to delete all unused pictures\n"
        )

        while True:
            try:
                user_input = int(input())
                if user_input in [0, 1, 2, 3]:
                    return user_input
                else:
                    print("Invalid input. Please enter 0, 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def deleteUnused():
        deleted_files = 0
        unused = getUnusedPics()

        if len(unused) < 1:
            print("Cleanup completed, 0 files to delete")
            return None

        print("List of unused pictures:")
        for pic in unused:
            print(f"- {pic}")

        temp_unused = set(unused)
        for pic in unused:
            user_choice = prompt_user(pic)

            if user_choice == 0:
                print("Skipping operation.")
                pass
            elif user_choice == 1:
                print(f"Skipping {len(temp_unused)} files. Exiting.")
                break
            elif user_choice == 2:
                print(f"Deleting {pic}.")
                deleted_files += 1
                temp_unused.remove(pic)
                send2trash(pic)
            elif user_choice == 3:
                print("Deleting all unused pictures.")
                for _pic in temp_unused:
                    send2trash(_pic)
                    deleted_files += 1
                break
            else:
                print("Unexpected error. Please try again.")

        print(f"Cleanup completed, {deleted_files} files deleted")

    return deleteUnused()
