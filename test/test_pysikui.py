from ..src import pysikuli as sik
import unittest
import os

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
        sik.mouseMove(42, 42)  # make sure failsafe isn't triggered during this test
        sik.FAILSAFE = True

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


if __name__ == "__main__":
    unittest.main()
