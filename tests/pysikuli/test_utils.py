import os
import random
import shutil
import string
import time

import pytest
import soundfile as sf

import src.pysikuli as sik
from src.pysikuli import _utils as utils
from src.pysikuli import config

DIVIDER = 1.1 if config.UNIX else 1.2 if config.OSX else 2


def getSoundDuration(file_path: str):
    wave, sample_rate = sf.read(file_path)
    duration = len(wave) / sample_rate
    return duration


@pytest.fixture()
def testLoc():
    config.MONITOR_RESOLUTION
    testLoc = (
        random.randrange(1, config.MONITOR_RESOLUTION[0] - 100),
        random.randrange(1, config.MONITOR_RESOLUTION[1] - 100),
    )
    return testLoc


@pytest.fixture()
def testMoveOffset():
    return random.randrange(90, 100)


@pytest.fixture()
def getLocationSoundDuration():
    duration = getSoundDuration(config.SOUND_FINISH_PATH) + getSoundDuration(
        config.SOUND_CAPTURE_PATH
    )

    return duration


@pytest.fixture()
def getRegionSoundDuration(getLocationSoundDuration):
    duration = getLocationSoundDuration * 2 - getSoundDuration(config.SOUND_FINISH_PATH)
    return duration


@pytest.fixture()
def getLocationDuration(testLoc):
    assert config.SOUND_ON

    sik.mouseMove(testLoc)
    start_time = time.time()
    utils.getLocation(config.MIN_SLEEP_TIME)
    duration = time.time() - start_time
    return duration


@pytest.fixture()
def getRegionDuration(testLoc, testMoveOffset):
    sik.mouseMove(testLoc)
    start_time = time.time()
    utils._getRegion(utils._REG_FORMAT, config.MIN_SLEEP_TIME, testMoveOffset)
    duration = time.time() - start_time
    return duration


@pytest.fixture()
def soundOff():
    config.SOUND_ON = False
    yield
    config.SOUND_ON = True


@pytest.fixture()
def getLocationSoundOFFDuration():
    config.SOUND_ON = False

    start_time = time.time()
    utils.getLocation(config.MIN_SLEEP_TIME)
    elapsed = time.time() - start_time

    config.SOUND_ON = True
    return elapsed


@pytest.fixture()
def getRegionSoundOFFDuration(testMoveOffset):
    config.SOUND_ON = False
    time.sleep(0.0001)

    start_time = time.time()
    utils._getRegion(utils._REG_FORMAT, config.MIN_SLEEP_TIME, testMoveOffset)
    elapsed = time.time() - start_time

    config.SOUND_ON = True
    return elapsed


class TestUtils:
    def test_getLocation_SOUND_OFF_and_clipboard(
        self,
        testLoc,
        getLocationSoundDuration,
        getLocationSoundOFFDuration,
        getLocationDuration,
    ):
        diff = abs(getLocationDuration - getLocationSoundDuration)
        assert sik.pasteFromClip() == str(testLoc)
        assert 0 < getLocationSoundOFFDuration <= 0.1

        if config.WIN:
            assert 0 < diff <= 0.4
        else:
            assert 0 < diff <= 0.1

    def test_getRegion_SOUND_OFF_and_clipboard(
        self,
        testLoc,
        getRegionSoundDuration,
        getRegionSoundOFFDuration,
        getRegionDuration,
        testMoveOffset,
    ):
        diff = getRegionDuration - getRegionSoundDuration
        assert 0 < getRegionSoundOFFDuration <= 0.3

        if config.WIN:
            assert 0 < diff <= 0.5
        else:
            assert 0 < diff <= 0.3

        captured_reg = sik.pasteFromClip()
        expected_reg = (
            f"Region("
            f"{testLoc[0]}, "
            f"{testLoc[1]}, "
            f"{testLoc[0] + testMoveOffset}, "
            f"{testLoc[1] + testMoveOffset})"
        )
        assert captured_reg == expected_reg

    @pytest.mark.parametrize(
        "sound",
        [
            config.SOUND_BLEEP_PATH,
            config.SOUND_CAPTURE_PATH,
            config.SOUND_FINISH_PATH,
        ],
    )
    def test_playSound(self, sound):
        duration = getSoundDuration(sound)
        start_time = time.time()
        utils.playSound(sound)
        stop_time = time.time() - start_time

        # add divider to even out processing time
        if config.UNIX:
            divider = 1.1
        elif config.OSX:
            divider = 1.2

        assert round(stop_time / divider, 1) <= round(duration, 1)

    @pytest.mark.parametrize(
        "sound",
        [
            config.SOUND_BLEEP_PATH,
            config.SOUND_CAPTURE_PATH,
            config.SOUND_FINISH_PATH,
        ],
    )
    def test_playSound_off(self, sound):
        config.SOUND_ON = False

        start_time = time.time()
        utils.playSound(sound)
        assert round(time.time() - start_time, 2) <= 0

        config.SOUND_ON = True


@pytest.fixture()
def cleanupObj():
    cleanup = utils.Cleanup(os.getcwd(), "pics", utils._SUPPORTED_PIC_FORMATS)
    return cleanup


imgs = [
    "pics/test.png",
    "/home/work/pics/test.png",
    "test-test/test/test.png",
    "pics/test.tiff",
    "pics/test.jmp",
    "pics/test.test",
    "pics/test.pic",
    "pics/test.img",
]

test_unusedPath = os.path.abspath("pics_test")


@pytest.fixture()
def testUnused():
    unused = [
        os.path.join(test_unusedPath, os.path.basename(imgs[0])),
        os.path.join(test_unusedPath, os.path.basename(imgs[3])),
    ]
    return unused


@pytest.fixture()
def createUnused(testUnused):
    if not os.path.isdir(test_unusedPath):
        os.mkdir(test_unusedPath)
    for unused in testUnused:
        with open(unused, "w"):
            pass


def removeUnused():
    shutil.rmtree(test_unusedPath)


@pytest.fixture()
def unusedTesting(createUnused):
    yield
    removeUnused()


def random_str():
    random.seed(time.time())
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(random.randint(10, 15)))


@pytest.fixture()
def create_test_pics_folder(get_random_num):
    path_folder = os.getcwd()
    path_folder = os.path.join(path_folder, "test_pics")
    os.mkdir(path_folder)
    assert os.path.isdir(path_folder)

    ext = random.choice
    for _ in range(get_random_num):
        with open(f"test_pics/{random_str()}.{ext(sik._config._SUPPORTED_PIC_FORMATS)}", "w"):
            pass
        sik.sleep(0.02)

    for _ in range(get_random_num):
        with open(f"test_pics/{random_str()}.{random_str()}", "w"):
            pass
        sik.sleep(0.02)

    yield path_folder

    shutil.rmtree(path_folder)


@pytest.fixture()
def get_random_num():
    random.seed(time.time())
    return random.randint(3, 10)


class TestCleanup:
    def test_isIgnored(self, cleanupObj: utils.Cleanup):
        assert cleanupObj.isIgnored("__pycache__") == True
        assert cleanupObj.isIgnored("__init__.py") == False
        assert cleanupObj.isIgnored(".git") == True

    @pytest.mark.parametrize(
        "prefix, expected",
        [
            ("pics", imgs[0]),
            ("/home/work/pics", imgs[1]),
            ("test-test/test", imgs[2]),
        ],
    )
    def test_picParse_prefix(self, prefix, expected):
        cleanup = utils.Cleanup(os.getcwd(), prefix, ["png"])

        found_paths = cleanup.picParse(__file__)
        assert found_paths == [expected]

    @pytest.mark.parametrize(
        "formats, expected",
        [
            (["tiff"], [imgs[3]]),
            (["jfif", "tiff", "jmp"], [imgs[3], imgs[4]]),
            (["img", "pic", "test"], [imgs[5], imgs[6], imgs[7]]),
            (pytest.param(["0000"], [None], marks=pytest.mark.xfail)),
        ],
    )
    def test_picParse_formats(self, formats, expected):
        cleanup = utils.Cleanup(os.getcwd(), "pics", formats)

        found_paths = cleanup.picParse(__file__)
        assert found_paths == expected

    def test_findAllPicsPathsInProject(self, cleanupObj: utils.Cleanup):
        found_paths = cleanupObj.findAllPicsPathsInProject(os.path.dirname(__file__))
        assert found_paths == [imgs[0], imgs[3]]

    def test_getStoredPics(
        self, cleanupObj: utils.Cleanup, create_test_pics_folder, get_random_num
    ):
        stored = cleanupObj.getStoredPics(create_test_pics_folder)
        assert len(stored) == get_random_num

    @pytest.mark.parametrize(
        ("user_input", "expected"),
        [
            ("1\n", 1),
            ("2\n", 2),
            ("3\n", 3),
            ("4\n", 4),
        ],
    )
    def test_promptUser(self, mocker, user_input, expected, cleanupObj: utils.Cleanup):
        mocker.patch("builtins.input", lambda: user_input)
        result = cleanupObj.promptUser("some_picture.jpg")
        assert result == expected

    @pytest.mark.parametrize(
        "user_input, expected",
        [
            ([1, 1], 2),  # skip skip
            ([2], 2),  # skip all
            ([3, 1], 1),  # delete skip
            ([1, 3], 1),  # skip delete
            ([3, 3], 0),  # delete delete
            ([4], 0),  # delete all
        ],
    )
    def test_deleteUnused(
        self,
        unusedTesting,
        mocker,
        user_input,
        expected,
        cleanupObj: utils.Cleanup,
    ):
        mocker.patch("builtins.input", side_effect=user_input)
        unused = ["pics_test/test.png", "pics_test/test.tiff"]
        cleanupObj.deleteUnused(unused)
        assert len(os.listdir(test_unusedPath)) == expected

    def test_cleanupPics(self, mocker, unusedTesting):
        mocker.patch("builtins.input", lambda: 4)
        utils.cleanupPics(test_unusedPath, "pics_test")
        assert len(os.listdir(test_unusedPath)) == 0
