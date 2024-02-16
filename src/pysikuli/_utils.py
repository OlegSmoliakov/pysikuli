import os
import re
import time

import soundfile as sf

from gitignore_parser import parse_gitignore as pgi

from ._main import getPixelRGB, copyToClip, mousePosition, mouseMoveRelative, deleteFile
from ._config import config, _SUPPORTED_PIC_FORMATS, _REG_FORMAT

try:
    import sounddevice as sd
except:
    if config.UNIX:
        from ._unix import _apt_check
        from ._config import _REQUIRED_PKGS_LINUX

        _apt_check(_REQUIRED_PKGS_LINUX)


def playSound(file_path):
    if config.SOUND_ON:
        wave, sample_rate = sf.read(file_path)

        sd.play(wave, sample_rate)
        sd.wait()


def getLocation(interval=0.5):
    check_3 = [0, 0, 0]

    while True:
        if interval > 0.4:
            playSound(config.SOUND_BLEEP_PATH)

        x, y = mousePosition()
        text = f"Current XY: [{x}, {y}]  RGB: {getPixelRGB((x, y))}"
        print(text)

        check_3[0] = check_3[1]
        check_3[1] = check_3[2]
        check_3[2] = [x, y]

        if check_3[0] == check_3[1] == check_3[2]:
            text = f"\nCaptured XY: [{x}, {y}]"
            print(text)

            copyToClip(f"({x}, {y})")
            playSound(config.SOUND_CAPTURE_PATH)
            break

        time.sleep(interval)

    playSound(config.SOUND_FINISH_PATH)


def getRegion(interval=0.5):
    """
    getRigion helps to determine the Region coordinates.

    Simply by hovering your mouse over points on the screen.
    The region requires 2 points, left-top and right-bottom.
    If you hold the mouse on the same spot for 3 `intervals`
    the point will be captured and capture sound will be played by default

    Args:
        `interval` (float): time in seconds, which uses for delay
        between each mouse posuition capture. Defaults to 0.5.

    Returns:
        updated clipboard with prepared region like: "Region(1, 2, 3, 4)"
        also print this region in console
    """
    return _getRegion(_REG_FORMAT, interval)


def _getRegion(reg_format, interval=0.5, test_interrupt_offset=0):
    points = 2
    check_3 = [0, 0, 0]
    lastLoc = [0, 0]

    while points > 0:
        if interval > 0.4:
            playSound(config.SOUND_BLEEP_PATH)

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

            playSound(config.SOUND_CAPTURE_PATH)
            print(f"Corner captured {points} left")

        time.sleep(interval)

        if points < 2 and test_interrupt_offset:
            mouseMoveRelative(test_interrupt_offset, test_interrupt_offset)
            test_interrupt_offset = 0

    leftUpLoc = [min(first_pos[0], second_pos[0]), min(first_pos[1], second_pos[1])]
    rightDownLoc = [max(first_pos[0], second_pos[0]), max(first_pos[1], second_pos[1])]

    if reg_format == "x1y1x2y2":
        reg = [leftUpLoc[0], leftUpLoc[1], rightDownLoc[0], rightDownLoc[1]]
    elif reg_format == "x1y1wh":
        reg = [
            leftUpLoc[0],
            leftUpLoc[1],
            rightDownLoc[0] - leftUpLoc[0],
            rightDownLoc[1] - leftUpLoc[1],
        ]
    else:
        raise ValueError("wrong reg_format")
    print(f"\nRegion format is set to: {reg_format}")

    copyToClip(f"Region({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]})")
    print(
        f"Region({reg[0]}, {reg[1]}, {reg[2]}, {reg[3]}), already copied to the clipboard"
    )

    playSound(config.SOUND_FINISH_PATH)


class Cleanup(object):
    def __init__(self, root_path, pics_folder_prefix_in_code, formats: list) -> None:
        self.ROOT_PATH = root_path
        self.PICS_FOLDER_PREFIX_IN_CODE = pics_folder_prefix_in_code
        self.PREPARED_FORMATS = "|".join(formats)

    def isIgnored(self, file_name: str):
        ignored = pgi(os.path.join(self.ROOT_PATH, ".gitignore"))
        ans = (
            ignored(file_name)
            if file_name not in config.IGNORE_LIST_FOR_CLEANUP_PICS
            else True
        )
        return ans

    def picParse(self, file_path: os.PathLike):
        with open(file_path) as f:
            code = f.read()
        #        # e.g. (pics/image_name.png)     # ["']pics[\\\/]\S*\.(?:png|jpg|tif)["']
        pattern = rf"""["']{self.PICS_FOLDER_PREFIX_IN_CODE}[\\\/]\S*\.(?:{self.PREPARED_FORMATS})["']"""
        matches = re.findall(pattern, code)

        found_paths = []

        pattern = """['"]"""
        for match in matches:
            relative_path = os.path.normpath(re.sub(pattern, "", match))
            found_paths.append(relative_path)

        return found_paths

    def findAllPicsPathsInProject(self, path):
        found_paths = []
        files = os.listdir(path)
        for file_name in files:
            file_path = os.path.join(path, file_name)
            if self.isIgnored(file_name):
                pass
            elif os.path.isdir(file_path):
                self.findAllPicsPathsInProject(file_path)
            elif file_name.endswith(".py"):
                fnd_paths = self.picParse(file_path)
                found_paths += fnd_paths

        return found_paths

    def getStoredPics(self, pics_folder_path):
        stored = os.listdir(pics_folder_path)
        stored = [
            os.path.join(pics_folder_path, file_name)
            for file_name in stored
            if re.search(f".{self.PREPARED_FORMATS}", file_name)
        ]
        return stored

    @staticmethod
    def promptUser(pic: str):
        bold = "\033[1m"
        end = "\033[0m"

        print(
            f"\nAre you sure that you want to move to trash '{os.path.basename(pic)}'?\n"
            f"enter {bold}1{end} to skip\n"
            f"enter {bold}2{end} to skip all\n"
            f"enter {bold}3{end} to delete\n"
            f"enter {bold}4{end} to delete all unused pictures\n"
        )

        while True:
            try:
                user_input = int(input())
                if user_input in [1, 2, 3, 4]:
                    return user_input
                else:
                    print("Invalid input. Please enter 1, 2, 3, or 4.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def deleteUnused(self, unused):
        deleted_files = 0

        if len(unused) < 1:
            print("Cleanup completed, 0 files to delete")
            return None

        print("List of unused pictures:")
        for pic in unused:
            print(f"- {pic}")

        temp_unused = set(unused)
        for pic in unused:
            user_choice = self.promptUser(pic)

            if user_choice == 1:
                print("Skipping operation.")
                pass
            elif user_choice == 2:
                print(f"Skipping {len(temp_unused)} files. Exiting.")
                break
            elif user_choice == 3:
                print(f"Deleting {pic}.")
                deleted_files += 1
                temp_unused.remove(pic)
                deleteFile(pic)
            elif user_choice == 4:
                print("Deleting all unused pictures.")
                for _pic in temp_unused:
                    deleteFile(_pic)
                    deleted_files += 1
                break
            else:
                print("Unexpected error. Please try again.")

        print(f"Cleanup completed, {deleted_files} files deleted")


def cleanupPics(
    pics_folder_path="pics",
    pics_folder_prefix_in_code="pics",
    root_path=os.getcwd(),
    formats: list = _SUPPORTED_PIC_FORMATS,
):
    if not os.path.isabs(pics_folder_path):
        os.path.abspath(pics_folder_path)
    assert os.path.isdir(pics_folder_path)
    assert os.path.isdir(root_path)

    cleanup = Cleanup(root_path, pics_folder_prefix_in_code, formats)

    pics_folder_path = os.path.normpath(pics_folder_path)

    stored = cleanup.getStoredPics(pics_folder_path)
    used = cleanup.findAllPicsPathsInProject(root_path)

    unused = set(stored) - set(used)

    return cleanup.deleteUnused(unused)
