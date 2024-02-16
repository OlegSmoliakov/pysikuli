import pytest
import platform

from PyHotKey import Key as hKey

import src.pysikuli as sik
from src.pysikuli import Key


@pytest.fixture()
def test_setup():
    sik.config.MOUSE_SPEED = 1000


@pytest.mark.usefixtures("test_setup")
class TestPysikuli:
    def test_accessibleNames(self):
        # Check that all the functions are defined correct.

        # keyboard-related API
        sik.tap
        sik.keyUp
        sik.keyDown
        sik.hotkey
        sik.write
        sik.paste
        sik.pasteFromClip
        sik.copyToClip
        sik.pressedKeys

        # mouse-related API
        sik.click
        sik.rightClick
        sik.mouseDown
        sik.mouseUp
        sik.mouseMove
        sik.mouseSmoothMove
        sik.mouseMoveRelative
        sik.mousePosition
        sik.scroll
        sik.hscroll
        sik.vscroll
        sik.dragDrop

        # The functions implemented in the platform-specific modules should also show up in the sik namespace:
        sik.activateWindow
        sik.activateWindowUnderMouse
        sik.activateWindowAt
        sik.getWindowRegion
        sik.getWindowWithTitle
        sik.getWindowUnderMouse
        sik.getAllWindowsTitle
        sik.minimizeWindow
        sik.maximizeWindow
        sik.closeWindow
        sik.windowExist

        # file management API
        sik.saveScreenshot
        sik.saveNumpyImg
        sik.deleteFile

        # utils API
        sik.getLocation
        sik.getRegion
        sik.cleanupPics

        # poopup API
        sik.popupAlert
        sik.popupPassword
        sik.popupPrompt
        sik.popupConfirm

        # screenshot-related API
        sik.exist
        sik.existAny
        sik.existCount
        sik.existFromFolder
        sik.find
        sik.grab
        sik.getPixelRGB
        sik.wait
        sik.waitWhileExist

        # clases and constants
        sik.Key
        sik.Button
        sik.Region
        sik.config

        sik.sleep

        if platform.system() != "Linux":
            pytest.skip("OS specific test")
        sik.required_pkgs_check


class TestKey:
    def test_Key(self):
        if platform.system() == "Darwin":
            assert sik.Key == sik._osx.MacKey
        elif platform.system() == "Windows":
            assert sik.Key == sik._win.WinKey
        elif platform.system() == "Linux":
            assert sik.Key == sik._unix.UnixKey

    def test_commonKeys(self):
        # Assuming Key and hKey are objects with attributes representing keys

        assert Key.alt_r == hKey.alt_r
        assert Key.alt_gr == hKey.alt_gr
        assert Key.shift == hKey.shift
        assert Key.shift_r == hKey.shift_r
        assert Key.ctrl == hKey.ctrl
        assert Key.ctrl_r == hKey.ctrl_r
        assert Key.left == hKey.left
        assert Key.right == hKey.right
        assert Key.up == hKey.up
        assert Key.down == hKey.down
        assert Key.page_down == hKey.page_down
        assert Key.page_up == hKey.page_up
        assert Key.home == hKey.home
        assert Key.end == hKey.end
        assert Key.esc == hKey.esc
        assert Key.space == hKey.space
        assert Key.tab == hKey.tab
        assert Key.caps_lock == hKey.caps_lock

        assert Key.f1 == hKey.f1
        assert Key.f2 == hKey.f2
        assert Key.f3 == hKey.f3
        assert Key.f4 == hKey.f4
        assert Key.f5 == hKey.f5
        assert Key.f6 == hKey.f6
        assert Key.f7 == hKey.f7
        assert Key.f8 == hKey.f8
        assert Key.f9 == hKey.f9
        assert Key.f10 == hKey.f10
        assert Key.f11 == hKey.f11
        assert Key.f12 == hKey.f12
        assert Key.f13 == hKey.f13
        assert Key.f14 == hKey.f14
        assert Key.f15 == hKey.f15
        assert Key.f16 == hKey.f16
        assert Key.f17 == hKey.f17
        assert Key.f18 == hKey.f18
        assert Key.f19 == hKey.f19
        assert Key.f20 == hKey.f20

        assert Key.media_play_pause == hKey.media_play_pause
        assert Key.media_volume_mute == hKey.media_volume_mute
        assert Key.media_volume_down == hKey.media_volume_down
        assert Key.media_volume_up == hKey.media_volume_up
        assert Key.media_previous == hKey.media_previous
        assert Key.media_next == hKey.media_next

    @pytest.mark.skipif(platform.system() == "Darwin", reason="OS specific test")
    def test_notMacOsKeys(self):
        assert Key.win == hKey.cmd
        assert Key.enter == hKey.enter
        assert Key.delete == hKey.delete
        assert Key.backspace == hKey.backspace
        assert Key.ctrl == hKey.ctrl
        assert Key.ctrl_r == hKey.ctrl_r

        assert Key.insert == hKey.insert
        assert Key.menu == hKey.menu
        assert Key.num_lock == hKey.num_lock
        assert Key.pause == hKey.pause
        assert Key.print_screen == hKey.print_screen
        assert Key.scroll_lock == hKey.scroll_lock

    @pytest.mark.skipif(platform.system() != "Darwin", reason="OS specific test")
    def test_macOsKeys(self):
        assert Key.cmd == hKey.cmd
        assert Key.cmd_r == hKey.cmd_r
        assert Key.delete == hKey.backspace
        assert Key.option == hKey.alt
        assert Key.option_r == hKey.alt_r
        assert Key.return_r == hKey.enter
