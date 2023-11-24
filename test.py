import unittest
import os
import numpy as np

import src.pysikuli as sik
import src.pysikuli._main as main
from src.pysikuli.config import (
    OSX,
    WIN,
    UNIX,
)

# TODO: unittest sound


class TestGeneral(unittest.TestCase):
    def setUp(self):
        self.oldFailsafeSetting = sik.FAILSAFE
        sik.FAILSAFE = False
        sik.mouseMove((42, 42))  # make sure failsafe isn't triggered during this test
        sik.FAILSAFE = True

    @classmethod
    def setUpClass(self):
        # currently using x1y1x2y2 region format
        reg_monitor = sik._main.MONITOR_RESOLUTION

        half_reg_monitor = [reg_monitor[0] // 2, reg_monitor[1] // 2]

        test_img_reg = (
            half_reg_monitor[0] - 2,
            half_reg_monitor[1] - 2,
            half_reg_monitor[0],
            half_reg_monitor[1],
        )

        test_reg_reg = (
            test_img_reg[0] - 2,
            test_img_reg[1] - 2,
            test_img_reg[2] + 2,
            test_img_reg[3] + 2,
        )

        self.test_img = sik._main.sct.grab(test_img_reg)
        self.test_reg = sik.region(*test_reg_reg)
        self.test_match = self.test_reg.find(self.test_img)

    def tearDown(self):
        sik.FAILSAFE = self.oldFailsafeSetting

    def test_accessibleNames(self):
        # Check that all the functions are defined.

        # keyboard-related API
        sik.tap
        sik.keyUp
        sik.keyDown
        sik.hotkey
        sik.write
        sik.paste

        # mouse-related API
        sik.click
        sik.rightClick
        sik.mouseDown
        sik.mouseUp
        sik.mouseMove
        sik.mouseMoveRealive
        sik.dragDrop

        # The functions implemented in the platform-specific modules should also show up in the sik namespace:
        # sik.position
        # sik.size
        # sik.scroll
        # sik.hscroll
        sik.activateWindow
        sik.getWindowRegion
        sik.minimizeWindow
        sik.unminimazeWindow

        # util API
        sik.Key
        sik.saveScreenshot
        sik.deleteFile

        # screenshot-related API
        sik.exist
        sik.find
        sik.findAny
        sik.getPixel
        sik.regionValidate
        sik.wait
        sik.sleep

        # tools-related API
        sik.getLocation
        sik.getRegion

    def test_regionValidate(self):
        regionValidateSize = main._regionValidate

        self.assertIsNone(regionValidateSize(0, 0, 2, 2))
        self.assertIsNone(regionValidateSize(*(50, 30, 60, 100)))
        self.assertIsNone(regionValidateSize(*[100, 150, 120, 300]))

        # incorrect values test
        with self.assertRaises(TypeError):
            regionValidateSize(1, 3, 2, 2)
            regionValidateSize(3, 1, 2, 2)
            regionValidateSize(1, 1, 2, 2.0)

            # outside the screen test
            regionValidateSize(-1, 1, 2, 2)
            regionValidateSize(1, 3000, -2, 2)
            regionValidateSize(1, 1, 2, 2000)

    def test_regionToNumpyArray_tuple_1(self):
        regionToNumpyArray = main._regionToNumpyArray

        np_reg, tuple_reg = regionToNumpyArray(self.test_reg.reg)
        original_shape = (
            self.test_reg.reg[3] - self.test_reg.reg[1],
            self.test_reg.reg[2] - self.test_reg.reg[0],
        )
        returned_shape = (np_reg.shape[1], np_reg.shape[0])
        self.assertIsInstance(np_reg, np.ndarray)
        self.assertTupleEqual(original_shape, returned_shape)
        self.assertTupleEqual(tuple_reg, self.test_reg.reg)

    def test_regionToNumpyArray_tuple_2(self):
        regionToNumpyArray = main._regionToNumpyArray

        np_reg, tuple_reg = regionToNumpyArray(list(self.test_reg.reg))
        original_shape = (
            self.test_reg.reg[3] - self.test_reg.reg[1],
            self.test_reg.reg[2] - self.test_reg.reg[0],
        )
        returned_shape = (np_reg.shape[1], np_reg.shape[0])
        self.assertIsInstance(np_reg, np.ndarray)
        self.assertTupleEqual(original_shape, returned_shape)
        self.assertTupleEqual(tuple_reg, self.test_reg.reg)

    def test_regionToNumpyArray_tuple_3(self):
        regionToNumpyArray = main._regionToNumpyArray

        with self.assertRaises(TypeError):
            regionToNumpyArray([0, 4, 4, 2])
            regionToNumpyArray((0, 4, 4, 2))
            regionToNumpyArray((0, 1, 4))

    def test_regionToNumpyArray_ScreenShot_1(self):
        regionToNumpyArray = main._regionToNumpyArray
        screenshot = main.sct.grab(self.test_reg.reg)
        original_shape = (
            screenshot.width,
            screenshot.height,
        )

        np_reg, tuple_reg = regionToNumpyArray(screenshot)
        returned_shape = (np_reg.shape[1], np_reg.shape[0])

        self.assertIsInstance(np_reg, np.ndarray)
        self.assertTupleEqual(original_shape, returned_shape)
        self.assertTupleEqual(tuple_reg, self.test_reg.reg)

    def test_regionToNumpyArray_ScreenShot_2(self):
        regionToNumpyArray = main._regionToNumpyArray

        with self.assertRaises(TypeError):
            screenshot = main.sct.grab((0, 1, 2))
            regionToNumpyArray(screenshot)

            screenshot = main.sct.grab((0, 1, 2, 3000))
            regionToNumpyArray(screenshot)

            screenshot = main.sct.grab((0, 1, 2))
            regionToNumpyArray(screenshot)

    def test_exist(self):
        exist = main._exist

        with self.assertRaises(TypeError):
            exist(image=None)
            exist(image=1)
            exist(image=[1, 2])
            exist(image=(1, 2))

        self.assertIsInstance(exist(image=np.array(self.test_img)), main.match)

        exist(
            image=self.test_img,
            region=self.test_reg,
            grayscale=True,
            precision=0.8,
        )

    def test_exist_compression_ratio(self):
        # TODO: test all variants with compression
        pass

    def test_imgDownsize(self):
        # TODO:
        pass

    def test_showImage(self):
        sik.keyDown(sik.Key.esc)
        self.test_match.showImage()
        sik.keyUp(sik.Key.esc)

    def test_showRegion(self):
        sik.keyDown(sik.Key.esc)
        ans = self.test_match.showRegion()
        self.assertIsNone(ans)
        sik.keyUp(sik.Key.esc)

    @unittest.skipUnless(UNIX, "linux specific")
    def test_linux(self):
        # TODO:
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
