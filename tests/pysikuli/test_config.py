import pytest
import platform
import PyHotKey
from ...src import pysikuli as sik
from ...src.pysikuli import config, Key


class TestConfig:
    def test_accessibleNames(self):
        config.COMPRESSION_RATIO
        config.GRAYSCALE
        config.MAX_SEARCH_TIME
        config.PRECISION
        config.TIME_STEP
        config.FAILSAFE
        config.FAILSAFE_HOTKEY
        config.FAILSAFE_REGIONS
        config.REFRESH_RATE
        config.MOUSE_PRIMARY_BUTTON
        config.MOUSE_SECONDARY_BUTTON
        config.MOUSE_SPEED
        config.OSX
        config.PAUSE_BETWEEN_ACTION
        config.SOUND_CAPTURE_PATH
        config.SOUND_FINISH_PATH
        config.SOUND_ON
        config.UNIX
        config.WIN
        config.platformModule

    @pytest.mark.skipif(platform.system() != "Darwin", reason="OS specific test")
    def test_OSX(slef):
        assert config.OSX is True
        assert config.platformModule == sik._osx

    @pytest.mark.skipif(platform.system() != "Windows", reason="OS specific test")
    def test_OSX(slef):
        assert config.WIN is True
        assert config.platformModule == sik._win

    @pytest.mark.skipif(platform.system() != "Linux", reason="OS specific test")
    def test_OSX(slef):
        assert config.UNIX is True
        assert config.platformModule == sik._unix


class TestKey:
    def test_accessibleNames(self):
        Key.alt
        Key.alt_gr
        Key.alt_r
        Key.caps_lock
        Key.ctrl
        Key.ctrl_r
        Key.delete
        Key.down
        Key.end
        Key.enter
        Key.esc
        Key.f1
        Key.f2
        Key.f3
        Key.f4
        Key.f5
        Key.f6
        Key.f7
        Key.f8
        Key.f9
        Key.f10
        Key.f11
        Key.f12
        Key.f13
        Key.f14
        Key.f15
        Key.f16
        Key.f17
        Key.f18
        Key.f19
        Key.f20
        Key.home
        Key.left
        Key.media_next
        Key.media_play_pause
        Key.media_previous
        Key.media_volume_down
        Key.media_volume_mute
        Key.media_volume_up
        Key.page_down
        Key.page_up
        Key.right
        Key.shift
        Key.shift_r
        Key.space
        Key.tab
        Key.up

    @pytest.mark.skipif(platform.system() == "Darwin", reason="OS specific test")
    def test_notMacOsKeys(self):
        Key.enter
        Key.insert
        Key.menu
        Key.num_lock
        Key.pause
        Key.print_screen
        Key.scroll_lock

        assert Key.delete == PyHotKey.Key.delete
        assert Key.backspace == PyHotKey.Key.backspace
        assert Key.win == PyHotKey.Key.cmd

    @pytest.mark.skipif(platform.system() != "Darwin", reason="OS specific test")
    def test_macOsKeys(self):
        Key.cmd
        Key.cmd_r

        assert Key.delete == PyHotKey.Key.backspace
        assert Key.option == PyHotKey.Key.alt
        assert Key.option_r == PyHotKey.Key.alt_r
        assert Key.return_r == PyHotKey.Key.enter
