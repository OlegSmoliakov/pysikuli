import pytest
import platform
import os
import subprocess
from subprocess import run
from ...src import pysikuli as sik

if not platform.system() == "Linux":
    pytest.skip("skipping Linux-only tests", allow_module_level=True)

from ...src.pysikuli import _unix as unix


class TestUnix:
    def test_accessibleNames(self):
        unix._activateWindow
        unix._apt_pkgs_installation_check
        unix._copy
        unix._getRefreshRate
        unix._getWindowRegion
        unix._minimizeWindow
        unix._paste
        unix._unminimizeWindow

    def test_copy(self):
        text = "some test text bla bla bla"

        # run text editor
        subprocess.Popen("xed", shell=True)
        sik.sleep(0.5)

        # cleanup clipboard
        sik.tap(sik.Key.space)
        sik.hotkey(sik.Key.shift, sik.Key.left)
        sik.hotkey(sik.Key.ctrl, "c")
        sik.tap(sik.Key.backspace)

        # insert text into clipboard
        unix._copy(text)
        sik.hotkey(sik.Key.ctrl, "v")

        # close and save
        sik.hotkey(sik.Key.ctrl, "q")
        sik.tap(sik.Key.enter), sik.sleep(0.3)
        path = os.path.join(os.getcwd(), "test.txt")
        sik.write(path)
        sik.tap(sik.Key.enter), sik.sleep(1.5)

        # save the result
        with open(path) as f:
            result = f.read()

        # cleaning
        os.remove(path)

        # test
        assert result == f"{text}\n"

    def test_paste(self):
        text = "some test text bla bla bla"

        # run text editor
        subprocess.Popen("xed", shell=True)
        sik.sleep(0.5)

        # cleanup clipboard
        sik.tap(sik.Key.space)
        sik.hotkey(sik.Key.shift, sik.Key.left)
        sik.hotkey(sik.Key.ctrl, "c")

        # type text
        sik.write(text)
        sik.hotkey(sik.Key.ctrl, "a")
        sik.hotkey(sik.Key.ctrl, "c")

        result = unix._paste()

        # close and save
        sik.hotkey(sik.Key.ctrl, "q"), sik.sleep(0.3)
        sik.tap(sik.Key.tab)
        sik.tap(sik.Key.enter)

        assert result == text

    # def test_apt_pkgs_installation_check(self):

    # def test_getRefreshRate(self):

    # def test_1(self):
    #     pass
