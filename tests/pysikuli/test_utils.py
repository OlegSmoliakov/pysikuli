from ...src.pysikuli import _utils as utils
from ...src.pysikuli import Config
from ...src import pysikuli as sik
import pytest
import random
import time
from mutagen.mp3 import MP3


@pytest.fixture()
def testLoc():
    sik.MONITOR_RESOLUTION
    testLoc = (
        random.randrange(0, sik.MONITOR_RESOLUTION[0]),
        random.randrange(0, sik.MONITOR_RESOLUTION[1]),
    )
    return testLoc


@pytest.fixture()
def getLocationSoundDuration():
    audio = MP3(Config.SOUND_FINISH_PATH)
    duration = audio.info.length
    audio = MP3(Config.SOUND_CAPTURE_PATH)
    duration += audio.info.length
    return duration


@pytest.fixture()
def getRegionSoundDuration(getLocationSoundDuration):
    audio = MP3(Config.SOUND_CAPTURE_PATH)
    getLocationSoundDuration += audio.info.length
    return getLocationSoundDuration


@pytest.fixture()
def getLocationDuration(testLoc):
    sik.Config.SOUND_ON = True
    sik.mouseMove(testLoc)
    start_time = time.time()
    utils._getLocation(0.02)
    duration = time.time() - start_time
    return duration


@pytest.fixture()
def getRegionDuration(testLoc):
    sik.Config.SOUND_ON = True
    sik.mouseMove(testLoc)
    start_time = time.time()
    utils._getRegion(sik._REGION_FORMAT, 0.02, 100)
    duration = time.time() - start_time
    return duration


@pytest.fixture()
def soundOff():
    Config.SOUND_ON = False
    yield
    Config.SOUND_ON = True


class TestUtils:
    def test_getLocation_clipboard(self, testLoc):
        sik.mouseMove(testLoc)
        utils._getLocation(0.02)
        assert sik.pasteFromClip() == str(testLoc)

    def test_getLocation_SOUND_OFF(
        self, testLoc, getLocationSoundDuration, getLocationDuration, soundOff
    ):
        sik.mouseMove(testLoc)
        start_time = time.time()
        utils._getLocation(0.02)
        duration_sound_off = time.time() - start_time
        assert duration_sound_off <= getLocationDuration - getLocationSoundDuration

    def test_getRegion_SOUND_OFF(
        self, testLoc, getRegionSoundDuration, getRegionDuration, soundOff
    ):
        sik.mouseMove(testLoc)
        start_time = time.time()
        utils._getRegion(sik._REGION_FORMAT, 0.02, 100)
        duration_sound_off = time.time() - start_time
        assert duration_sound_off <= getRegionDuration - getRegionSoundDuration
