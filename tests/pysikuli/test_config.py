import pytest
import platform
from ...src import pysikuli as sik
from ...src.pysikuli import Config, Key


class TestConfig:
    def test_accessibleNames(self):
        Config.COMPRESSION_RATIO
        Config.DEFAULT_GRAYSCALE
        Config.DEFAULT_MAX_SEARCH_TIME
        Config.DEFAULT_PRECISION
        Config.DEFAULT_TIME_STEP
        Config.FAILSAFE
        Config.FAILSAFE_HOTKEY
        Config.FAILSAFE_POINTS
        Config.MAX_REFRESH_RATE
        Config.MOUSE_LEFT
        Config.MOUSE_MIDDLE
        Config.MOUSE_MOVE_SPEED
        Config.MOUSE_RIGHT
        Config.OSX
        Config.PAUSE_BETWEEN_ACTION
        Config.SOUND_CAPTURE_PATH
        Config.SOUND_FINISH_PATH
        Config.SOUND_ON
        Config.UNIX
        Config.WIN
        Config.platformModule

    @pytest.mark.skipif(platform.system() != "Darwin", reason="OS specific test")
    def test_OSX(slef):
        assert Config.OSX is True
        assert Config.platformModule == sik._osx

    @pytest.mark.skipif(platform.system() != "Windows", reason="OS specific test")
    def test_OSX(slef):
        assert Config.WIN is True
        assert Config.platformModule == sik._win

    @pytest.mark.skipif(platform.system() != "Linux", reason="OS specific test")
    def test_OSX(slef):
        assert Config.UNIX is True
        assert Config.platformModule == sik._unix


class TestKey:
    def test_accessibleNames(self):
        Key.alt
        Key.alt_gr
        Key.alt_r
        Key.backspace
        Key.caps_lock
        Key.cmd
        Key.cmd_r
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
        Key.insert
        Key.left
        Key.media_next
        Key.media_play_pause
        Key.media_previous
        Key.media_volume_down
        Key.media_volume_mute
        Key.media_volume_up
        Key.menu
        Key.num_lock
        Key.option
        Key.option_r
        Key.page_down
        Key.page_up
        Key.pause
        Key.print_screen
        Key.return_r
        Key.right
        Key.scroll_lock
        Key.shift
        Key.shift_r
        Key.space
        Key.tab
        Key.up
        Key.win
        Key.win_r
