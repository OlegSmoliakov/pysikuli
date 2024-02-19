import time
import pytest
import platform

from copy import copy

import pymsgbox as pmb

import src.pysikuli as sik
from src.pysikuli import config, Key, _config as cfg


@pytest.fixture()
def OS():
    return platform.system()


def test_constant():
    assert isinstance(cfg._REQUIRED_PKGS_LINUX, (list, tuple))
    assert isinstance(cfg._SUPPORTED_PIC_FORMATS, (list, tuple))
    assert isinstance(cfg._REG_FORMAT, str)


def test_getOS(OS):
    OSX, WIN, UNIX = cfg.getOS()

    selected = 0

    if OS == "Darwin":
        assert OSX
        selected += 1
    if OS == "Windows":
        assert WIN
        selected += 1
    if OS == "Linux":
        assert UNIX
        selected += 1

    assert selected == 1


@pytest.mark.parametrize(
    "OS, expected",
    [
        ("Darwin", (1, 0, 0)),
        ("Windows", (0, 1, 0)),
        ("Linux", (0, 0, 1)),
        ("Test", (0, 0, 1)),
    ],
)
def test_getOS_mock(mocker, OS, expected):
    mocker.patch("platform.system", return_value=OS)

    if OS == "Test":
        with pytest.raises(OSError):
            cfg.getOS()
    else:
        assert cfg.getOS() == expected


@pytest.mark.skipif(platform.system() != "Darwin", reason="OS specific test")
def test_getPlatformModule_OSX():
    platform = cfg.getPlatformModule(*(1, 0, 0))
    assert platform == sik._osx


@pytest.mark.skipif(platform.system() != "Windows", reason="OS specific test")
def test_getPlatformModule_WIN():
    platform = cfg.getPlatformModule(*(0, 1, 0))
    assert platform == sik._win


@pytest.mark.skipif(platform.system() != "Linux", reason="OS specific test")
def test_getPlatformModule_UNIX():
    platform = cfg.getPlatformModule(*(0, 0, 1))
    assert platform == sik._unix


@pytest.mark.parametrize("OS", [(0, 0, 0), (0, 1, 1), (1, 1, 0), (1, 0, 1), (1, 1, 1)])
def test_getPlatformModule_TypeError(OS):
    with pytest.raises(TypeError):
        cfg.getPlatformModule(*OS)


def test_getDefaultFailsafeHotkey():
    hotkey = cfg.getDefaultFailsafeHotkey(OSX=False)
    assert hotkey == [(Key.ctrl, Key.alt, "z")]

    hotkey = cfg.getDefaultFailsafeHotkey(OSX=True)
    assert hotkey == [(Key.alt, Key.shift, "c")]


@pytest.fixture()
def test_config():
    test_cfg = copy(config)
    return test_cfg


@pytest.fixture()
def setAttribute(request):
    attrs_to_modify = {item[0]: item[1] for item in request.param}
    original_values = {attr: getattr(config, attr) for attr in attrs_to_modify.keys()}

    for attr, value in attrs_to_modify.items():
        setattr(config, attr, value)

    yield

    for attr, value in original_values.items():
        setattr(config, attr, value)


class TestConfig:
    @pytest.mark.parametrize(
        "setAttribute",
        [
            (["MIN_SLEEP_TIME", 2],),
        ],
        indirect=True,
    )
    def test_MIN_SLEEP_TIME(self, setAttribute):
        assert config.MIN_SLEEP_TIME == 2

        start_time = time.time()
        sik.write("", 1)
        elapse = time.time() - start_time

        assert elapse <= 0.1

    @pytest.mark.parametrize(
        "setAttribute",
        [(["PAUSE_BETWEEN_ACTION", 0.5],)],
        indirect=True,
    )
    def test_PAUSE_BETWEEN_ACTION(self, setAttribute):
        assert config.PAUSE_BETWEEN_ACTION == 0.5

        start_time = time.time()
        sik.mouseMoveRelative(1, 1, 10000)
        elapse = time.time() - start_time

        assert 0.5 <= elapse < 0.51

    @pytest.mark.parametrize(
        "setAttribute",
        [(["FAILSAFE", False],)],
        indirect=True,
    )
    def test_FAILSAFE(self, setAttribute):
        assert config.FAILSAFE == False

        sik.mouseMove((0, 0))
        sik.mouseMove((88, 80))

    @pytest.mark.parametrize(
        "setAttribute",
        [(["FAILSAFE", True],)],
        indirect=True,
    )
    def test_FAILSAFE_raises(self, setAttribute):
        assert config.FAILSAFE == True

        sik.mouseMove((0, 0))
        with pytest.raises(sik._main.FailSafeException):
            sik.mouseMove((88, 80))
        sik._main.mouse.position = (500, 500)

    def test_FAILSAFE_REGIONS(self):
        sik.mouseMove((200, 200))
        old_value = config.FAILSAFE_REGIONS
        config.FAILSAFE_REGIONS = [(0, 0, 100, 100)]

        sik.mouseMove((50, 50))
        with pytest.raises(sik._main.FailSafeException):
            sik.mouseMove((60, 60))

        config.FAILSAFE_REGIONS = old_value

    @pytest.mark.skip()
    @pytest.mark.parametrize(
        "setAttribute",
        [
            (["FAILSAFE_HOTKEY", [(Key.ctrl, Key.alt)]],),
        ],
        indirect=True,
    )
    def test_FAILSAFE_HOTKEY(self, setAttribute):
        assert config.FAILSAFE_HOTKEY == [(Key.ctrl, Key.alt)]

        sik.keyDown(Key.ctrl)
        sik.keyDown(Key.alt)

        with pytest.raises(sik._main.FailSafeException):
            sik.keyUp(Key.ctrl)

        assert sik._main.pressedKeys() == [(Key.ctrl, Key.alt)]

        config.FAILSAFE_HOTKEY = [(Key.win, Key.shift)]
        sik.keyUp(Key.ctrl)
        assert sik._main.pressedKeys() == [Key.alt]

        sik.keyUp(Key.alt)
        assert sik._main.pressedKeys() == []

    def test_FAILSAFE_HOTKEY_2(self):
        assert config.FAILSAFE_HOTKEY != []

    @pytest.mark.parametrize(
        "setAttribute, expected",
        [
            pytest.param((["OK_TEXT", "test"],), ["OK_TEXT", "test"], id="OK_TEXT"),
            pytest.param(
                (["CANCEL_TEXT", "test"],), ["CANCEL_TEXT", "test"], id="CANCEL_TEXT"
            ),
            pytest.param(
                (["ROOT_WINDOW_POSITION", [0, 0]],),
                ["rootWindowPosition", "+0+0"],
                id="ROOT_WINDOW_POSITION",
            ),
            pytest.param(
                (["PROPORTIONAL_FONT_SIZE", "test"],),
                ["PROPORTIONAL_FONT_SIZE", "test"],
                id="PROPORTIONAL_FONT_SIZE",
            ),
            pytest.param(
                (["MONOSPACE_FONT_SIZE", "test"],),
                ["MONOSPACE_FONT_SIZE", "test"],
                id="MONOSPACE_FONT_SIZE",
            ),
            pytest.param(
                (["TEXT_ENTRY_FONT_SIZE", "test"],),
                ["TEXT_ENTRY_FONT_SIZE", "test"],
                id="TEXT_ENTRY_FONT_SIZE",
            ),
        ],
        indirect=["setAttribute"],
    )
    def test_pymsgboxVariables(self, setAttribute, expected):
        value = getattr(pmb, expected[0])
        assert value == expected[1]

    @pytest.mark.parametrize(
        "setAttribute, expected",
        [
            pytest.param((["DEBUG", True],), config.DEBUG_SETTINGS, id="True"),
            pytest.param((["DEBUG", False],), config._DEFAULT_SETTINGS, id="False"),
        ],
        indirect=["setAttribute"],
    )
    def test_DEBUG(self, setAttribute, expected):
        assert config.PAUSE_BETWEEN_ACTION == expected["PAUSE_BETWEEN_ACTION"]
        assert config.TIME_STEP == expected["TIME_STEP"]
        assert config.MOUSE_SPEED == expected["MOUSE_SPEED"]

    @pytest.mark.parametrize(
        "setAttribute, expected",
        [
            pytest.param(
                (["MIN_PRECISION", 9],), ["MIN_PRECISION", 9], id="MIN_PRECISION"
            ),
            pytest.param((["GRAYSCALE", 9],), ["GRAYSCALE", 9], id="GRAYSCALE"),
            pytest.param(
                (["IGNORE_LIST_FOR_CLEANUP_PICS", 9],),
                ["IGNORE_LIST_FOR_CLEANUP_PICS", 9],
                id="IGNORE_LIST_FOR_CLEANUP_PICS",
            ),
            pytest.param(
                (["PERCENT_IMAGE_DOWNSIZING", 9],),
                ["PERCENT_IMAGE_DOWNSIZING", 9],
                id="PERCENT_IMAGE_DOWNSIZING",
            ),
            pytest.param(
                (["MAX_SEARCH_TIME", 9],), ["MAX_SEARCH_TIME", 9], id="MAX_SEARCH_TIME"
            ),
            pytest.param((["TIME_STEP", 9],), ["TIME_STEP", 9], id="TIME_STEP"),
            pytest.param(
                (["WINDOW_WAITING_CONFIRMATION", 9],),
                ["WINDOW_WAITING_CONFIRMATION", 9],
                id="WINDOW_WAITING_CONFIRMATION",
            ),
            pytest.param(
                (["MONITOR_REGION", 9],), ["MONITOR_REGION", 9], id="MONITOR_REGION"
            ),
            pytest.param(
                (["MONITOR_RESOLUTION", 9],),
                ["MONITOR_RESOLUTION", 9],
                id="MONITOR_RESOLUTION",
            ),
            pytest.param(
                (["MOUSE_PRIMARY_BUTTON", 9],),
                ["MOUSE_PRIMARY_BUTTON", 9],
                id="MOUSE_PRIMARY_BUTTON",
            ),
            pytest.param(
                (["MOUSE_SECONDARY_BUTTON", 9],),
                ["MOUSE_SECONDARY_BUTTON", 9],
                id="MOUSE_SECONDARY_BUTTON",
            ),
            pytest.param((["SOUND_ON", 9],), ["SOUND_ON", 9], id="SOUND_ON"),
            pytest.param(
                (["SOUND_CAPTURE_PATH", 9],),
                ["SOUND_CAPTURE_PATH", 9],
                id="SOUND_CAPTURE_PATH",
            ),
            pytest.param(
                (["SOUND_FINISH_PATH", 9],),
                ["SOUND_FINISH_PATH", 9],
                id="SOUND_FINISH_PATH",
            ),
            pytest.param(
                (["SOUND_BLEEP_PATH", 9],),
                ["SOUND_BLEEP_PATH", 9],
                id="SOUND_BLEEP_PATH",
            ),
            pytest.param(
                (["DEBUG_SETTINGS", 9],), ["DEBUG_SETTINGS", 9], id="DEBUG_SETTINGS"
            ),
        ],
        indirect=["setAttribute"],
    )
    def test_setConfig(self, setAttribute, expected):
        value = getattr(config, expected[0])
        assert value == expected[1]
