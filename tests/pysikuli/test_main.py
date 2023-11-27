import pytest
import os
import time
import numpy as np

from ...src import pysikuli as sik
from ...src.pysikuli import _main as main

from ...src.pysikuli import Config


# TODO: unittest sound


@pytest.fixture()
def test_img_reg():
    half_reg_monitor = [
        main.MONITOR_RESOLUTION[0] // 2,
        main.MONITOR_RESOLUTION[1] // 2,
    ]
    test_img_reg = (
        half_reg_monitor[0] - 2,
        half_reg_monitor[1] - 2,
        half_reg_monitor[0],
        half_reg_monitor[1],
    )
    return test_img_reg


@pytest.fixture()
def test_reg_reg(test_img_reg):
    test_reg_reg = (
        test_img_reg[0] - 2,
        test_img_reg[1] - 2,
        test_img_reg[2] + 2,
        test_img_reg[3] + 2,
    )
    return test_reg_reg


@pytest.fixture()
def test_img_ScreenShot(test_img_reg):
    return main.sct.grab(test_img_reg)


@pytest.fixture()
def test_class_region(test_reg_reg):
    return sik.Region(*test_reg_reg)


@pytest.fixture()
def test_img_ndarray(test_img_ScreenShot):
    return np.array(test_img_ScreenShot)


class TestMain:
    def test_accessibleNames(self):
        main.MONITOR_REGION
        main.MONITOR_RESOLUTION

    def test_activateWindow(self):
        pass

    def test_click(self):
        pass

    def test_copyToClip(self):
        pass

    def test_deleteFile(self):
        pass

    def test_dragDrop(self):
        pass

    def test_exist(self, test_img_ndarray, test_img_ScreenShot, test_reg_reg):
        exist = main._exist

        with pytest.raises(TypeError):
            exist(image=None)
            exist(image=1)
            exist(image=[1, 2])
            exist(image=(1, 2))

        assert isinstance(exist(image=test_img_ndarray), main.Match)

        exist(
            image=test_img_ScreenShot,
            region=test_reg_reg,
            grayscale=True,
            precision=0.8,
        )

    def test_exist_compression_ratio(self):
        # TODO: test all variants with compression
        pass

    def test_failSafeCheck(self):
        pass

    def test_find(self):
        pass

    def test_findAny(self):
        pass

    def test_getCoordinates(self):
        pass

    def test_getPixel(self):
        pass

    def test_getWindowRegion(self):
        pass

    def test_hotkey(self):
        pass

    def test_hotkeyFailSafeCheck(self):
        pass

    def test_imageExistFromFolder(self):
        pass

    def test_imageToNumpyArray(self):
        pass

    def test_imagesearchCount(self):
        pass

    def test_imgDownsize(self):
        pass

    def test_keyDown(self):
        pass

    def test_keyUp(self):
        pass

    def test_minimizeWindow(self):
        pass

    def test_mouseDown(self):
        pass

    def test_mouseFailSafeCheck(self):
        pass

    def test_mouseMove(self):
        pass

    def test_mouseMoveRelative(self):
        pass

    def test_mouseUp(self):
        pass

    def test_paste(self):
        pass

    def test_pasteFromClip(self):
        pass

    def test_regionNormalization(
        self, test_class_region, test_reg_reg, test_img_ScreenShot, test_img_reg
    ):
        regionNormalization = main._regionNormalization

        assert regionNormalization() == None
        assert regionNormalization(test_img_ScreenShot) == test_img_reg
        assert regionNormalization(test_class_region) == test_reg_reg

        assert regionNormalization([0, 5, 10, 15]) == (0, 5, 10, 15)
        assert regionNormalization(["0", "5", "10", "15"]) == (0, 5, 10, 15)
        assert regionNormalization((250, 500, 750, 1000)) == (250, 500, 750, 1000)

        with pytest.raises(TypeError):
            regionNormalization("fasdf")
            regionNormalization(main.Key)

    def test_regionToNumpyArray_tuple_1(self, test_reg_reg):
        regionToNumpyArray = main._regionToNumpyArray

        np_reg, tuple_reg = regionToNumpyArray(test_reg_reg)
        original_shape = (
            test_reg_reg[3] - test_reg_reg[1],
            test_reg_reg[2] - test_reg_reg[0],
        )
        returned_shape = (np_reg.shape[1], np_reg.shape[0])
        assert isinstance(np_reg, np.ndarray)
        assert (original_shape, returned_shape)
        assert (tuple_reg, test_reg_reg)

    def test_regionToNumpyArray_tuple_2(self, test_reg_reg):
        regionToNumpyArray = main._regionToNumpyArray

        np_reg, tuple_reg = regionToNumpyArray(list(test_reg_reg))
        original_shape = (
            test_reg_reg[3] - test_reg_reg[1],
            test_reg_reg[2] - test_reg_reg[0],
        )
        returned_shape = (np_reg.shape[1], np_reg.shape[0])
        assert isinstance(np_reg, np.ndarray)
        assert original_shape == returned_shape
        assert tuple_reg == test_reg_reg

    def test_regionToNumpyArray_tuple_3(self):
        regionToNumpyArray = main._regionToNumpyArray

        with pytest.raises(TypeError):
            regionToNumpyArray([0, 4, 4, 2])
            regionToNumpyArray((0, 4, 4, 2))
            regionToNumpyArray((0, 1, 4))

    def test_regionToNumpyArray_ScreenShot_1(self, test_img_ScreenShot, test_img_reg):
        regionToNumpyArray = main._regionToNumpyArray
        original_shape = (
            test_img_ScreenShot.width,
            test_img_ScreenShot.height,
        )

        np_reg, tuple_reg = regionToNumpyArray(test_img_ScreenShot)
        returned_shape = (np_reg.shape[1], np_reg.shape[0])

        assert isinstance(np_reg, np.ndarray)
        assert original_shape == returned_shape
        assert tuple_reg == test_img_reg

    def test_regionToNumpyArray_test_img_ScreenShot_2(self):
        regionToNumpyArray = main._regionToNumpyArray
        screenshot = main.ScreenShot([1, 2, 4, 5], main.sct.monitors[0])
        with pytest.raises(TypeError):
            regionToNumpyArray(screenshot)

    def test_regionValidation(self):
        regionValidation = main._regionValidation

        assert regionValidation((0, 0, 2, 2)) == (0, 0, 2, 2)
        assert regionValidation((50.0, 30.0, 60.0, 100.0)) == (50, 30, 60, 100)
        assert regionValidation([100, 150, 120, 300]) == (100, 150, 120, 300)
        assert regionValidation(["200", "300", "220", "600"]) == (200, 300, 220, 600)

        # incorrect values test
        with pytest.raises(TypeError):
            regionValidation(1, 3, 2, 2)
            regionValidation(3, 1, 2, 2)

            # outside the screen test
            regionValidation(-1, 1, 2, 2)
            regionValidation(1, 3000, -2, 2)
            regionValidation(1, 1, 2, 2000)

    def test_rightClick(self):
        pass

    def test_saveNumpyImg(self):
        pass

    def test_saveScreenshot(self):
        print("\n")
        path = sik.saveScreenshot()
        assert os.path.isfile(path)
        os.remove(path)

        path = sik.saveScreenshot([1, 2, 3, 4])
        assert os.path.isfile(path)
        os.remove(path)

        path = sik.saveScreenshot((1, 2, 3, 4))
        assert os.path.isfile(path)
        os.remove(path)

    def test_sleep(self):
        pass

    def test_tap(self):
        pass

    def test_unminimazeWindow(self):
        pass

    def test_wait(test_img_reg, test_img_ScreenShot, test_class_region):
        pass

    def test_write(self):
        pass


@pytest.fixture()
def test_match(test_class_region, test_img_ScreenShot):
    return test_class_region.find(test_img_ScreenShot)


class TestMatch:
    def test_showImage(self, test_match):
        sik.keyDown(sik.Key.esc)
        test_match.showImage()
        sik.keyUp(sik.Key.esc)

    def test_showRegion(self, test_match):
        sik.keyDown(sik.Key.esc)
        test_match.showRegion()
        sik.keyUp(sik.Key.esc)
