import unittest
import os

import src.pysikuli as sik

# scriptFolder = os.path.dirname(os.path.realpath(__file__))
# os.chdir(scriptFolder)


# modify Key class test
# sik.Key.test = sik.Key.space

# class ownKey(sik.Key):
#     test2 = sik.Key.left

# sik.tap(ownKey.left)


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
        sik.checkRegion
        sik.wait
        sik.sleep

        # tools-related API
        sik.getLocation
        sik.getRegion

    def test_imShow(self):
        self.test_match.showImage()


if __name__ == "__main__":
    unittest.main()
