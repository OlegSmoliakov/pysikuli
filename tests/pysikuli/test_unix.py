import pytest
import platform
import os
import subprocess
from ...src import pysikuli as sik

if not platform.system() == "Linux":
    pytest.skip("skipping Linux-only tests", allow_module_level=True)

from ...src.pysikuli import _unix as unix

TEST_REFRESH_RATE = 60


@pytest.fixture
def openTextEditor():
    text = "some test text bla bla bla"

    # run text editor
    subprocess.Popen("xed", shell=True)
    sik.sleep(1)

    # cleanup clipboard
    sik.tap(sik.Key.space)
    sik.hotkey(sik.Key.shift, sik.Key.left)
    sik.hotkey(sik.Key.ctrl, "c")
    sik.tap(sik.Key.backspace)

    return text


class TestUnix:
    def test_accessibleNames(self):
        unix._apt_pkgs_installation_check
        unix._copy
        unix._getRefreshRate
        unix._paste

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

    def test_apt_pkgs_installation_check_return_none(self):
        assert (
            unix._apt_pkgs_installation_check(
                ["libgirepository1.0-dev", "libcairo2-dev", "xinput"]
            )
            is None
        )

    @pytest.mark.parametrize("test_pkgs", [["test"], ["test", "test_pkg_test"]])
    def test_apt_pkgs_installation_check_return_print(self, capsys, test_pkgs):
        unix._apt_pkgs_installation_check(test_pkgs)
        captured = capsys.readouterr().out

        str_test_pkgs = ""
        for pkg in test_pkgs:
            str_test_pkgs = f"{str_test_pkgs} {pkg}"

        str_test_pkgs_reversed = ""
        test_pkgs = test_pkgs[::-1]
        for pkg in test_pkgs:
            str_test_pkgs_reversed = f"{str_test_pkgs_reversed} {pkg}"

        try:
            expected_output = (
                f"\n\nPlease install the missing packages:{str_test_pkgs}\n\n"
                f"On Ubuntu/Debian use this command: sudo apt install{str_test_pkgs}\n"
            )
            assert captured == expected_output
        except AssertionError:
            expected_output = (
                f"\n\nPlease install the missing packages:{str_test_pkgs_reversed}\n\n"
                f"On Ubuntu/Debian use this command: sudo apt install{str_test_pkgs_reversed}\n"
            )
            assert captured == expected_output

    def test_getRefreshRate(self):
        assert isinstance(unix._getRefreshRate(), int)
        assert unix._getRefreshRate() == TEST_REFRESH_RATE
