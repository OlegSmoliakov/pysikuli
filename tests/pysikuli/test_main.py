import pytest
import os
import time
import numpy as np
import multiprocessing

from ...src import pysikuli as sik
from ...src.pysikuli import _main as main, Config
from ...src.pysikuli._main import Region, Match


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


@pytest.fixture()
def test_reg_ndarray(test_reg_reg):
    return np.array(main.sct.grab(test_reg_reg))


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

        assert isinstance(exist(image=test_img_ndarray), Match)

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
    return test_class_region.find(test_img_ScreenShot, grayscale=False)


@pytest.fixture()
def show_region(test_match):
    process = multiprocessing.Process(target=test_match.showRegion)
    process.start()
    time.sleep(0.2)


@pytest.fixture()
def show_image(test_match):
    process = multiprocessing.Process(target=test_match.showImage)
    process.start()
    time.sleep(0.2)


class TestMatch:
    def test_accessibleNames(self):
        Match.exit_keys_cv2
        Match._showImageCV2
        Match.setTargetOffset
        Match.showImage
        Match.showRegion

    def test_init(
        self,
        test_match,
        test_img_ndarray,
        test_reg_ndarray,
    ):
        assert test_match.x == 958
        assert test_match.y == 538
        assert test_match.up_left_loc == (957, 537)
        assert test_match.loc == (958, 538)
        assert test_match.offset_loc == (958, 538)
        assert test_match.offset_x == 958
        assert test_match.offset_y == 538
        assert test_match.score == 1
        assert test_match.precision == 0.8
        assert np.array_equal(test_match.np_image, test_img_ndarray)
        assert np.array_equal(test_match.np_region, test_reg_ndarray)

    def test_repr(self, test_match):
        assert (
            f"Match(location={test_match.loc}, score={test_match.score}, precision={Config.DEFAULT_PRECISION})"
            == repr(test_match)
        )

    @pytest.mark.parametrize(
        "key", ["q", sik.Key.esc, sik.Key.backspace, sik.Key.space]
    )
    @pytest.mark.usefixtures("show_image")
    def test_showImage_key_closure(self, key):
        sik.tap(key)

    @pytest.mark.parametrize(
        "key", ["q", sik.Key.esc, sik.Key.backspace, sik.Key.space]
    )
    @pytest.mark.usefixtures("show_region")
    def test_showRegion_key_closure(self, key):
        sik.tap(key)

    @pytest.mark.usefixtures("show_region")
    def test_showRegion_click_closure(self):
        sik.click((1140, 370))

    @pytest.mark.parametrize("offset", [50, 100, 150])
    def test_setTargetOffset(self, test_match, offset):
        x, y = test_match.loc
        expected_loc = (x + offset, y + offset)
        assert expected_loc == test_match.setTargetOffset(offset, offset)

    @pytest.mark.parametrize(
        "offset_x,offset_y",
        [(50, 2000), (2000, 50), (-50, -2000), (-2000, -50)],
    )
    def test_setTargetOffset_ValueError(self, test_match, offset_x, offset_y):
        x, y = test_match.loc
        expected_loc = (x + offset_x, y + offset_y)
        with pytest.raises(ValueError):
            assert expected_loc == test_match.setTargetOffset(offset_x, offset_y)


class TestRegion:
    def test_accessibleNames(self):
        Region.COMPRESSION_RATIO
        Region.TIME_STEP
        Region.click
        Region.exist
        Region.find
        Region.findAny
        Region.has
        Region.rightClick
        Region.wait

    def test_init(self, test_reg_reg):
        reg = Region(*test_reg_reg)
        assert reg.reg == test_reg_reg
        assert reg.x1 == test_reg_reg[0]
        assert reg.y1 == test_reg_reg[1]
        assert reg.x2 == test_reg_reg[2]
        assert reg.y2 == test_reg_reg[3]

    def test_click(self):
        pass

    def test_exist(self):
        pass

    def test_click(self):
        pass

    def test_click(self):
        pass

    def test_click(self):
        pass

    def test_click(self):
        pass

    def test_click(self):
        pass

    def test_has(self):
        pass

    def test_wait(self):
        pass
