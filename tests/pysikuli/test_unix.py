import pytest
import platform
import os
import subprocess
from subprocess import run
from ...src import pysikuli as sik

if not platform.system() == "Linux":
    pytest.skip("skipping Linux-only tests", allow_module_level=True)

from ...src.pysikuli import _unix as unix


@pytest.fixture
def openTextEditor():
    text = "some test text bla bla bla"

    # run text editor
    subprocess.Popen("xed", shell=True)
    sik.sleep(0.5)

    # cleanup clipboard
    sik.tap(sik.Key.space)
    sik.hotkey(sik.Key.shift, sik.Key.left)
    sik.hotkey(sik.Key.ctrl, "c")
    sik.tap(sik.Key.backspace)

    return text


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

    def test_copy(self, openTextEditor):
        # insert text into clipboard
        unix._copy(openTextEditor)
        sik.hotkey(sik.Key.ctrl, "v")

        # close and save
        sik.hotkey(sik.Key.ctrl, "q")
        sik.tap(sik.Key.enter), sik.sleep(0.3)
        path = os.path.join(os.getcwd(), "test.txt")
        sik.write(path)
        sik.tap(sik.Key.enter), sik.sleep(1.5)

        # get the result
        with open(path) as f:
            result = f.read()

        # cleaning
        os.remove(path)

        assert result == f"{openTextEditor}\n"

    def test_paste(self, openTextEditor):
        # type text
        sik.write(openTextEditor)
        sik.hotkey(sik.Key.ctrl, "a")
        sik.hotkey(sik.Key.ctrl, "c")

        result = unix._paste()

        # close and save
        sik.hotkey(sik.Key.ctrl, "q"), sik.sleep(0.3)
        sik.tap(sik.Key.tab)
        sik.tap(sik.Key.enter)

        assert result == openTextEditor

    def test_apt_pkgs_installation_check(self):
        assert (
            unix._apt_pkgs_installation_check(
                ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]
            )
            is None
        )
        assert (
            unix._apt_pkgs_installation_check(
                ["libgirepository1.0-dev", "libcairo2-dev", "test"]
            )
            is None
        )

    def test_getRefreshRate(self):
        assert isinstance(unix._getRefreshRate(), int)
        # for honor
        assert unix._getRefreshRate() == 60
