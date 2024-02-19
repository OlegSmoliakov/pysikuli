import random
import string
import shutil
import subprocess
import os
import functools
import time
import multiprocessing

import cv2
import pytest
import pymonctl as pmc
import numpy as np
import pywinctl as pwc

from copy import copy
from mss.screenshot import ScreenShot

import src.pysikuli as sik

from src.pysikuli import _main as main, config
from src.pysikuli._main import Region, Match


config.PERCENT_IMAGE_DOWNSIZING = 100


@pytest.fixture()
def test_setup():
    sik.config.MOUSE_SPEED = 1000


@pytest.fixture()
def half_width():
    random.seed(time.time())
    return random.randrange(50, 100)


@pytest.fixture()
def test_reg_for_img(half_width):
    half_reg_monitor = [
        config.MONITOR_RESOLUTION[0] // 2,
        config.MONITOR_RESOLUTION[1] // 2,
    ]
    test_reg_for_img = (
        half_reg_monitor[0] - half_width,
        half_reg_monitor[1] - half_width,
        half_reg_monitor[0] + half_width,
        half_reg_monitor[1] + half_width,
    )
    return test_reg_for_img


@pytest.fixture()
def test_reg_for_reg(test_reg_for_img, half_width):
    random.seed(time.time())
    mult = 1 + random.random() * 0.2
    test_reg_for_reg = (
        test_reg_for_img[0] - int(half_width * mult),
        test_reg_for_img[1] - int(half_width * mult),
        test_reg_for_img[2] + int(half_width * mult),
        test_reg_for_img[3] + int(half_width * mult),
    )
    return test_reg_for_reg


@pytest.fixture()
def test_img_ScreenShot(test_reg_for_img):
    return main.grab(test_reg_for_img)


@pytest.fixture()
def test_reg_ScreenShot(test_reg_for_reg):
    return main.grab(test_reg_for_reg)


@pytest.fixture()
def test_class_region(test_reg_for_reg):
    return sik.Region(*test_reg_for_reg)


@pytest.fixture()
def test_img_ndarray(test_img_ScreenShot):
    return np.array(test_img_ScreenShot)


@pytest.fixture()
def test_reg_ndarray(test_reg_for_reg):
    return np.array(main.grab(test_reg_for_reg))


@pytest.fixture()
def random_str():
    random.seed(time.time())
    letters = string.ascii_letters
    return "".join(random.choice(letters) for _ in range(random.randint(10, 15)))


@pytest.fixture()
def open_textEditor():
    window_name = ""

    if config.UNIX:
        subprocess.Popen(["xed"])
        window_name = "Unsaved Document 1"
        sik.sleep(0.5)

    yield window_name

    if window_name in main.getAllWindowsTitle():
        main.closeWindow(window_name)
        sik.sleep(0.2)
        assert main.windowExist(window_name) is None


@pytest.fixture()
def title_exist_window_name_1():
    if config.UNIX:
        return "xfce4-panel"


@pytest.fixture()
def title_exist_window_name_2():
    if config.UNIX:
        return "Desktop"


@pytest.fixture()
def cleanup_clipboard(open_textEditor):
    sik.tap(sik.Key.space)
    sik.hotkey(sik.Key.shift, sik.Key.left)
    sik.hotkey(sik.Key.ctrl, "c", interval=0.05)
    sik.tap(sik.Key.backspace)

    yield


@pytest.fixture()
def random_np_img():
    return np.random.randint(0, 256, size=(100, 100, 3), dtype=np.uint8)


@pytest.fixture()
def saved_img(test_img_ndarray):
    path = main.saveNumpyImg(test_img_ndarray, "test_image")
    assert os.path.isfile(path)

    yield path

    os.remove(path)


@pytest.fixture()
def saved_random_img(random_np_img):
    path = main.saveNumpyImg(random_np_img, "random_image")
    assert os.path.isfile(path)

    yield path

    os.remove(path)


@pytest.fixture()
def test_match(test_class_region, test_reg_for_img):
    img = main.grab(test_reg_for_img)
    return test_class_region.find(img, 0.5)


@pytest.fixture()
def path_with_pics(test_img_ndarray):
    path = os.path.join(os.getcwd(), "test_saved_pics")
    os.mkdir(path)

    for n in range(1, 3):
        main.saveNumpyImg(test_img_ndarray, n, path)

    yield path

    shutil.rmtree(path)


def execution_time_test(wrappedFunction, max_time=0.1):
    start_time = time.time()
    ans = wrappedFunction()
    elapsed_time = time.time() - start_time

    assert elapsed_time <= max_time
    return ans


@pytest.mark.usefixtures("test_setup")
class TestMain:
    # utils section

    def test_deleteFile(self, mocker):
        file_name = "test.txt"
        os.mknod(file_name)
        assert os.path.isfile(file_name)

        path = os.path.join(os.getcwd(), file_name)
        sik.deleteFile(path)

        assert not os.path.isfile(file_name)

        os.mknod(file_name)

        assert os.path.isfile(file_name)

        mocker.patch("src.pysikuli._main.send2trash", side_effect=Exception("test"))

        sik.deleteFile(path)

        assert not os.path.isfile(file_name)

    def test_copyToClip_Unix(self, random_str, cleanup_clipboard):
        # insert text into clipboard
        sik.activateWindow("*Unsaved Document 1")
        sik.copyToClip(random_str)

        sik.hotkey(sik.Key.alt, "e")
        sik.tap(sik.Key.down)
        sik.tap(sik.Key.enter)

        # close and save
        sik.hotkey(sik.Key.ctrl, "q")
        sik.tap(sik.Key.enter), sik.sleep(0.3)
        path = os.path.join(os.getcwd(), "test.txt")
        sik.write(path)
        sik.tap(sik.Key.enter), sik.sleep(0.7)

        # get the result
        with open(path) as f:
            result = f.read()

        # cleaning
        os.remove(path)

        assert result == f"{random_str}\n"

    @pytest.mark.skipif(not config.UNIX, reason="OS specific test")
    def test_pasteFromClip_UNIX(self, random_str, cleanup_clipboard):
        # type text
        sik.activateWindow("*Unsaved Document 1")

        sik.write(random_str)
        sik.hotkey(sik.Key.ctrl, "a")
        sik.hotkey(sik.Key.ctrl, "c")

        result = sik.pasteFromClip()

        # close and save
        sik.hotkey(sik.Key.ctrl, "q"), sik.sleep(0.1)
        sik.tap(sik.Key.tab)
        sik.tap(sik.Key.enter)

        assert result == random_str

    # image searching section

    def test_grab(self, test_reg_for_img):
        screenshot = main.grab(test_reg_for_img)
        assert isinstance(screenshot, ScreenShot)
        assert screenshot.left == test_reg_for_img[0]
        assert screenshot.top == test_reg_for_img[1]
        assert screenshot.height == test_reg_for_img[3] - test_reg_for_img[1]
        assert screenshot.width == test_reg_for_img[2] - test_reg_for_img[0]

    def test_getPixelRGB(self, saved_img, test_img_ScreenShot):
        imread_img = cv2.imread(saved_img, cv2.IMREAD_COLOR)
        grab_img = np.array(test_img_ScreenShot)

        # ScreenShot: [height][width][color with custom]
        # np.array:   [height][width][color][mask]

        sum = 0

        for x in range(grab_img.shape[1]):
            for y in range(grab_img.shape[0]):
                r = imread_img[y][x][2]
                g = imread_img[y][x][1]
                b = imread_img[y][x][0]

                grab_rgb = (r, g, b)

                r = grab_img[y][x][2]
                g = grab_img[y][x][1]
                b = grab_img[y][x][0]

                monitor_rgb = (r, g, b)

                assert grab_rgb == monitor_rgb

    @pytest.mark.parametrize(
        "w, h, loc, expected",
        [
            (2, 2, (10, 10), (11, 11)),
            (3, 3, (10, 10), (11, 11)),
            (4, 4, (10, 10), (12, 12)),
            (5, 5, (10, 10), (12, 12)),
        ],
    )
    def test_getCenterLoc(self, w, h, loc, expected):
        assert main._getCenterLoc(w, h, loc) == expected

    @pytest.mark.skip("already tested in other functions")
    def test_imageToNumpyArray(self):
        pass

    @pytest.mark.skip("already tested in other functions")
    def test_imgDownsize(self):
        pass

    @pytest.mark.parametrize(
        "loc",
        [
            (500, 300),
            [1, 1],
            pytest.param((2000, 2000), marks=pytest.mark.xfail),
            pytest.param((-1, -10), marks=pytest.mark.xfail),
            pytest.param((1.0, 10.0), marks=pytest.mark.xfail),
        ],
    )
    def test_locationValidation(self, loc):
        main._locationValidation(loc)

    def test_regionNormalization(
        self,
        test_class_region,
        test_reg_for_reg,
        test_img_ScreenShot,
        test_reg_for_img,
        test_img_ndarray,
    ):
        regionNormalization = main._regionNormalization
        assert regionNormalization() == pmc.getPrimary().box
        assert regionNormalization(test_img_ScreenShot) == test_reg_for_img
        assert regionNormalization(test_class_region) == test_reg_for_reg

        assert regionNormalization([0, 5, 10, 15]) == (0, 5, 10, 15)
        assert regionNormalization(["0", "5", "10", "15"]) == (0, 5, 10, 15)
        assert regionNormalization((250, 500, 750, 1000)) == (250, 500, 750, 1000)

        assert regionNormalization(test_img_ndarray) == None

        with pytest.raises(TypeError):
            regionNormalization("fasdf")

        with pytest.raises(TypeError):
            regionNormalization(main.Key)

    def test_regionToNumpyArray(
        self,
        test_reg_for_reg,
        test_reg_ndarray,
        test_reg_ScreenShot,
    ):
        # list
        np_reg, tuple_reg = main._regionToNumpyArray(list(test_reg_for_reg))

        assert np.array_equal(np_reg, test_reg_ndarray)
        assert tuple_reg == test_reg_for_reg

        # tuple
        np_reg, tuple_reg = main._regionToNumpyArray(test_reg_for_reg)

        assert np.array_equal(np_reg, test_reg_ndarray)
        assert tuple_reg == test_reg_for_reg

        # np.ndarray
        np_reg, tuple_reg = main._regionToNumpyArray(test_reg_ndarray, test_reg_for_reg)

        assert np.array_equal(np_reg, test_reg_ndarray)
        assert tuple_reg == test_reg_for_reg

        # ScreenShot
        np_reg, tuple_reg = main._regionToNumpyArray(test_reg_ScreenShot)

        assert np.array_equal(np_reg, test_reg_ndarray)
        assert tuple_reg == test_reg_for_reg

        # Region
        np_reg, tuple_reg = main._regionToNumpyArray(test_reg_for_reg)

        assert np.array_equal(np_reg, test_reg_ndarray)
        assert tuple_reg == test_reg_for_reg

        # None
        reg = np.array(sik.grab(config.MONITOR_REGION))
        np_reg, tuple_reg = main._regionToNumpyArray()

        # assert np.array_equal(np_reg, reg)
        assert np.allclose(np_reg, reg, 10, 10)
        assert tuple_reg == config.MONITOR_REGION

    @pytest.mark.parametrize(
        "reg",
        [
            ([0, 4, 4, 2]),
            ((0, 4, 4, 2)),
            ((0, 1, 4)),
            (10),
        ],
    )
    def test_regionToNumpyArray_raises(self, reg):
        with pytest.raises(TypeError):
            main._regionToNumpyArray(reg)

    @pytest.mark.parametrize(
        "reg, expected",
        [
            ((0, 0, 2, 2), (0, 0, 2, 2)),
            ((50.0, 30.0, 60.0, 100.0), (50, 30, 60, 100)),
            ([100, 150, 120, 300], (100, 150, 120, 300)),
            (["200", "300", "220", "600"], (200, 300, 220, 600)),
        ],
    )
    def test_regionValidation(self, reg, expected):
        assert main._regionValidation(reg) == expected

    @pytest.mark.parametrize(
        "reg",
        [
            ((1, 3)),
            ((1, 3, 2)),
            ((1, 3, 2, 2)),
            ((3, 1, 2, 2)),
            ((-1, 1, 2, 2)),
            ((1, 3000, -2, 2)),
            ((1, 1, 2, 2000)),
        ],
    )
    def test_regionValidation_raises(self, reg):
        # incorrect values test
        with pytest.raises(TypeError):
            main._regionValidation(reg)

    def test_handleNpRegion(self, test_reg_ndarray, test_reg_for_reg):
        ans = main._handleNpRegion(test_reg_ndarray, test_reg_for_reg)
        assert ans == (test_reg_ndarray, test_reg_for_reg)

        with pytest.raises(TypeError):
            main._handleNpRegion(test_reg_ndarray, None)

    @pytest.mark.parametrize(
        "configSetAttribute",
        [
            pytest.param((["PERCENT_IMAGE_DOWNSIZING", 100],), id="100"),
            pytest.param((["PERCENT_IMAGE_DOWNSIZING", 50],), id="50"),
            pytest.param((["PERCENT_IMAGE_DOWNSIZING", 25],), id="25"),
            pytest.param((["PERCENT_IMAGE_DOWNSIZING", 5],), id="5"),
            pytest.param((["PERCENT_IMAGE_DOWNSIZING", 1],), id="1"),
        ],
        indirect=["configSetAttribute"],
    )
    def test_matchProcessing_PERCENT_IMAGE_DOWNSIZING(
        self, configSetAttribute, test_img_ndarray, test_reg_for_reg
    ):
        match = main._matchProcessing(test_img_ndarray, test_reg_for_reg)
        _, max_val, _, _ = cv2.minMaxLoc(match[2])
        assert max_val >= 0.5

    @pytest.mark.parametrize(
        "configSetAttribute, expected, grayscale",
        [
            pytest.param((["GRAYSCALE", True],), (100, 100), (True), id="True"),
            pytest.param((["GRAYSCALE", False],), (100, 100, 3), (False), id="False"),
        ],
        indirect=["configSetAttribute"],
    )
    def test_matchProcessing_GRAYSCALE(
        self, configSetAttribute, expected, grayscale, random_np_img
    ):
        assert random_np_img.shape == (100, 100, 3)

        resize_image = sik._main._matchProcessing(random_np_img, grayscale=grayscale)
        assert resize_image[0].shape == expected

    def test_matchProcessing_raises(self, test_img_ScreenShot):
        with pytest.raises(ValueError):
            main._matchProcessing(test_img_ScreenShot, [50, 50, 100, 100])

        config.PERCENT_IMAGE_DOWNSIZING = 110
        with pytest.raises(ValueError):
            main._matchProcessing(test_img_ScreenShot, [50, 50, 100, 100])
        config.PERCENT_IMAGE_DOWNSIZING = 100

    def test_exist(
        self,
        test_img_ndarray,
        test_img_ScreenShot: ScreenShot,
        test_reg_for_reg,
    ):
        assert isinstance(main.exist(image=test_img_ndarray), Match)
        match = main.exist(
            image=test_img_ScreenShot,
            region=test_reg_for_reg,
            grayscale=True,
            precision=0.8,
        )

        assert isinstance(match, Match)

        width = test_img_ScreenShot.width / 2
        pixel = main.getPixelRGB((width, width), test_img_ndarray)

        match = main.exist(
            test_img_ScreenShot,
            test_reg_for_reg,
            False,
            0.7,
            pixel,
        )

        assert isinstance(match, Match)

    @pytest.mark.parametrize("img", [None, 1, [1, 2], (1, 2)])
    def test_exist_raises(self, img):
        with pytest.raises(TypeError):
            main.exist(image=img)

    def test_existAny(self, test_img_ScreenShot, test_img_ndarray):
        matches = main.existAny([test_img_ScreenShot, test_img_ndarray])
        for match in matches:
            assert isinstance(match, Match)

    def test_existFromFolder(self, path_with_pics):
        ans = main.existFromFolder(path_with_pics)
        assert isinstance(ans, dict)

    def test_existCount(self, test_img_ScreenShot):
        ans = main.existCount(test_img_ScreenShot)
        assert isinstance(ans, dict)

    def test_getCoordinates(self):
        pass

    @pytest.mark.parametrize(
        "loc_or_pic, expected",
        [
            (None, (None, None)),
            ((10, 10, 100, 100), (10, 10, 100, 100)),
            ([10, 10, 100, 100], [10, 10, 100, 100]),
            (10, (None, None)),
        ],
    )
    def test_coordinateNormalization(self, loc_or_pic, expected):
        ans = main._coordinateNormalization(loc_or_pic)
        assert ans == expected

    def test_coordinateNormalization_2(
        self, saved_img, test_match: Match, saved_random_img
    ):
        ans = main._coordinateNormalization(saved_img)
        diff = vec_abs_diff(ans, test_match.center_loc)
        assert diff[0] <= 1
        assert diff[1] <= 1

        with pytest.raises(TimeoutError):
            main._coordinateNormalization(saved_random_img, max_search_time=0.05)

    def test_saveNumpyImg_raises(self, test_img_ndarray):
        with pytest.raises(FileExistsError):
            main.saveNumpyImg(test_img_ndarray, path="src")

        with pytest.raises(FileExistsError):
            main.saveNumpyImg(test_img_ndarray, path="/src")

    def test_saveScreenshot(self):
        path = sik.saveScreenshot()
        assert os.path.isfile(path)
        os.remove(path)

        path = sik.saveScreenshot([1, 2, 3, 4])
        assert os.path.isfile(path)
        os.remove(path)

        path = sik.saveScreenshot((1, 2, 3, 4))
        assert os.path.isfile(path)
        os.remove(path)

    def test_wait(self, test_img_ScreenShot, test_class_region: Region, random_np_img):
        ans = test_class_region.wait(test_img_ScreenShot)
        assert ans == True

        with pytest.raises(TimeoutError):
            test_class_region.wait(random_np_img, 0.05)

    def test_waitWhileExist(
        self, test_img_ScreenShot, test_class_region: Region, random_np_img
    ):
        ans = test_class_region.waitWhileExist(test_img_ScreenShot, 0.05)
        assert ans == False

        ans = test_class_region.waitWhileExist(random_np_img, 0.05)
        assert ans == True

    def test_find(self, test_class_region: Region, random_np_img):
        ans = test_class_region.find(random_np_img, 0.1)
        assert ans == None

    # keyboard section

    def test_pressedKeys(self):
        pass

    # def test_hotkey(self):
    #     pass

    # def test_hotkeyFailSafeCheck(self):
    #     pass

    # def test_paste(self):
    #     pass

    # def test_keyDown(self):
    #     pass

    # def test_keyUp(self):
    #     pass

    # def test_tap(self):
    #     pass

    # def test_write(self):
    #     pass

    # # mouse section

    # def test_click(self):
    #     pass

    # def test_rightClick(self):
    #     pass

    # def test_mouseDown(self):
    #     pass

    # def test_mouseFailSafeCheck(self):
    #     pass

    # def test_mouseMove(self):
    #     pass

    # def test_mouseMoveRelative(self):
    #     pass

    # def test_mouseSmoothMove(self):
    #     pass

    # def test_mouseUp(self):
    #     pass

    # def test_mousePosition(self):
    #     pass

    # def test_mousePress(self):
    #     pass

    # def test_mouseRelease(self):
    #     pass

    # def test_dragDrop(self):
    #     pass

    # def test_scroll(self):
    #     pass

    # def test_hscroll(self):
    #     pass

    # def test_vscroll(self):
    #     pass

    # windows management section

    @pytest.mark.parametrize(
        "window_title",
        [
            pytest.param(
                "Desktop",
                marks=pytest.mark.skipif(not config.UNIX, reason="OS specific"),
            ),
            pytest.param(
                "xfce4-panel",
                marks=pytest.mark.skipif(not config.UNIX, reason="OS specific"),
            ),
            pytest.param("test_title", marks=pytest.mark.xfail),
        ],
    )
    def test_titleCheck(self, window_title):
        # we check only decorator, so print func uses as stub
        foo = main.titleCheck(print)
        assert foo(window_title) == None

    @pytest.mark.parametrize(
        "window_title, expected",
        [
            ("test", None),
            (123, None),
            (["title"], None),
            pytest.param(
                "Desktop",
                "Desktop",
                marks=pytest.mark.skipif(not config.UNIX, reason="OS specific"),
            ),
            pytest.param(
                "xfce4-panel",
                "xfce4-panel",
                marks=pytest.mark.skipif(not config.UNIX, reason="OS specific"),
            ),
        ],
    )
    def test_windowExist(self, window_title, expected):
        assert sik.windowExist(window_title) == expected

    @pytest.mark.parametrize("win", [False, True])
    def test_getAllWindowsTitle(self, win):
        setattr(config, "_WIN", win)
        titles = main.getAllWindowsTitle()
        for title in titles:
            assert isinstance(title, str)
            assert len(title) > 0

    @pytest.mark.parametrize(
        "window_title",
        [
            pytest.param("test", marks=pytest.mark.xfail),
            pytest.param(123, marks=pytest.mark.xfail),
            pytest.param(["title"], marks=pytest.mark.xfail),
            pytest.param(
                "Desktop",
                marks=pytest.mark.skipif(not config.UNIX, reason="OS specific"),
            ),
            pytest.param(
                "xfce4-panel",
                marks=pytest.mark.skipif(not config.UNIX, reason="OS specific"),
            ),
        ],
    )
    def test_getWindowWithTitle(self, window_title):
        window = main.getWindowWithTitle(window_title)
        assert hasattr(window, "maximize")

    def test_getWindowRegion(self, open_textEditor):
        def foo():
            return main.getWindowRegion(open_textEditor)

        reg = execution_time_test(foo)
        assert isinstance(reg, Region)

    def test_activateWindow(self, open_textEditor):
        expected_window = main.getWindowWithTitle(open_textEditor)

        titles = main.getAllWindowsTitle()
        for title in titles:
            if "Visual Studio Code" in title:
                main.activateWindow(title)
                break

        def foo():
            return main.activateWindow(open_textEditor)

        assert execution_time_test(foo)
        assert expected_window.isActive

    def test_activateWindowAt(self, open_textEditor):
        expected_window = main.getWindowWithTitle(open_textEditor)

        reg = main.getWindowRegion(open_textEditor)
        x = random.randint(reg.x1, reg.x2)
        y = random.randint(reg.y1, reg.y2)

        def foo():
            return main.activateWindowAt((x, y))

        assert execution_time_test(foo)
        assert expected_window.isActive

    def test_activateWindowUnderMouse(self, open_textEditor):
        expected_window = main.getWindowWithTitle(open_textEditor)

        reg = main.getWindowRegion(open_textEditor)
        x = random.randint(reg.x1, reg.x2)
        y = random.randint(reg.y1, reg.y2)

        main.mouseMove((x, y))

        def foo():
            return main.activateWindowUnderMouse()

        assert execution_time_test(foo)
        assert expected_window.isActive

    def test_getWindowUnderMouse(self, open_textEditor):
        expected_window = main.getWindowWithTitle(open_textEditor)
        reg = main.getWindowRegion(open_textEditor)
        x = random.randint(reg.x1, reg.x2)
        y = random.randint(reg.y1, reg.y2)
        main.mouseMove((x, y))

        def foo():
            return main.getWindowUnderMouse()

        window = execution_time_test(foo)
        assert window == expected_window

    def test_minimizeWindow(self, open_textEditor):
        reg = main.getWindowRegion(open_textEditor)
        screenshot = main.grab(reg.reg)

        def foo():
            return main.minimizeWindow(open_textEditor)

        assert execution_time_test(foo)

        sik.sleep(0.02)
        assert main.exist(screenshot, grayscale=False) is None
        assert main.windowExist(open_textEditor) == open_textEditor

    def test_closeWindow(self, open_textEditor):
        main.activateWindow(open_textEditor)

        def foo():
            return main.closeWindow(open_textEditor)

        execution_time_test(foo), sik.sleep(0.2)

        assert main.windowExist(open_textEditor) is None

    def test_maximizeWindow(self, open_textEditor):
        assert main.maximizeWindow(open_textEditor)

    # popups section

    def test_popupAlert(self):
        ans = main.popupAlert("conf", "title", (500, 500), 0.05)
        assert ans == "Timeout"

    def test_popupPassword(self):
        ans = main.popupPassword("conf", "title", "default", "#", (500, 500), 0.05)
        assert ans == "Timeout"

    def test_popupPrompt(self):
        ans = main.popupPrompt("conf", "title", "default", (500, 500), 0.05)
        assert ans == "Timeout"

    def test_popupConfirm(self):
        ans = main.popupConfirm("conf", "title", root=(500, 500), timeout=0.05)
        assert ans == "Timeout"


@pytest.fixture()
def configSetAttribute(request):
    attrs_to_modify = {item[0]: item[1] for item in request.param}
    original_values = {attr: getattr(config, attr) for attr in attrs_to_modify.keys()}

    for attr, value in attrs_to_modify.items():
        setattr(config, attr, value)

    yield

    for attr, value in original_values.items():
        setattr(config, attr, value)


class TestPauseBetweenAction:
    @pytest.mark.parametrize(
        "configSetAttribute",
        [(["PAUSE_BETWEEN_ACTION", 0.5],)],
        indirect=True,
    )
    def test_PAUSE_BETWEEN_ACTION_deleteFile(self, configSetAttribute):
        assert config.PAUSE_BETWEEN_ACTION == 0.5
        path = os.path.join(os.getcwd(), "test.test")
        os.mknod(path)
        start_time = time.time()
        sik.deleteFile(path)
        elapsed = time.time() - start_time

        assert 0.5 <= elapsed <= 0.51


@pytest.fixture()
def show_region(test_match: main.Match):
    process = multiprocessing.Process(target=test_match.showRegion)
    process.start()
    time.sleep(0.2)
    yield
    time.sleep(0.2)


@pytest.fixture()
def show_image(test_match: main.Match):
    process = multiprocessing.Process(target=test_match.showImage)
    process.start()
    time.sleep(0.2)
    yield
    time.sleep(0.2)


def vec_abs_diff(vec1, vec2):
    diff = tuple(v1 - v2 for v1, v2 in zip(vec1, vec2))
    diff = tuple(abs(p) for p in diff)
    return diff


@pytest.mark.usefixtures("test_setup")
class TestMatch:
    def test_init(
        self,
        test_img_ndarray,
        test_reg_ndarray,
        test_reg_for_img,
        test_class_region: main.Region,
        test_img_ScreenShot,
        half_width,
    ):
        GRAYSCALE = False
        PRECISION = 0.6
        error = 1

        test_match = test_class_region.find(
            test_img_ScreenShot, grayscale=GRAYSCALE, precision=PRECISION
        )

        up_left_loc = (test_reg_for_img[0], test_reg_for_img[1])
        diff_up_left_loc = vec_abs_diff(up_left_loc, test_match.up_left_loc)

        assert diff_up_left_loc[0] <= error
        assert diff_up_left_loc[1] <= error

        center_loc = (up_left_loc[0] + half_width, up_left_loc[1] + half_width)
        diff_center_loc = vec_abs_diff(center_loc, test_match.center_loc)

        assert diff_center_loc[0] <= error
        assert diff_center_loc[1] <= error

        x, y = center_loc
        diff_x = abs(x - test_match.x)
        diff_y = abs(y - test_match.y)

        assert diff_x <= error
        assert diff_y <= error

        assert test_match.offset_loc == test_match.center_loc
        assert test_match.offset_x == test_match.x
        assert test_match.offset_y == test_match.y

        assert test_match.precision <= test_match.score <= 1
        assert test_match.precision == PRECISION

        assert half_width == (test_match.center_loc[0] - test_match.up_left_loc[0])
        assert half_width == (test_match.center_loc[1] - test_match.up_left_loc[1])

        assert test_match.exit_keys_cv2 == [113, 27, 32, 8]

        assert np.array_equal(test_match.np_image, test_img_ndarray)
        assert np.array_equal(test_match.np_region, test_reg_ndarray)

        center_pixel = main.getPixelRGB((half_width, half_width), test_img_ndarray)
        assert test_match.center_pixel == center_pixel

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
    def test_setTargetOffset(self, test_match: main.Match, offset):
        x, y = test_match.center_loc
        expected_loc = (x + offset, y + offset)
        assert expected_loc == test_match.setTargetOffset(offset, offset)

    @pytest.mark.parametrize(
        "offset_x,offset_y",
        [(50, 2000), (2000, 50), (-50, -2000), (-2000, -50)],
    )
    def test_setTargetOffset_ValueError(
        self, test_match: main.Match, offset_x, offset_y
    ):
        x, y = test_match.center_loc
        expected_loc = (x + offset_x, y + offset_y)
        with pytest.raises(ValueError):
            assert expected_loc == test_match.setTargetOffset(offset_x, offset_y)

    def test_eq(self, test_match):
        assert test_match == test_match

    def test_ne(self, test_match):
        local_test_match = copy(test_match)
        local_test_match.center_loc = (10, 10)
        assert test_match != local_test_match

    def test_repr(self, test_match):
        assert isinstance(str(test_match), str)


@pytest.mark.usefixtures("test_setup")
class TestRegion:
    def test_init(self, test_reg_for_reg):
        reg = Region(*test_reg_for_reg)
        reg.time_step = 1
        assert reg.reg == test_reg_for_reg
        assert reg.x1 == test_reg_for_reg[0]
        assert reg.y1 == test_reg_for_reg[1]
        assert reg.x2 == test_reg_for_reg[2]
        assert reg.y2 == test_reg_for_reg[3]
        assert reg.time_step == 1

    def test_repr_str(self, test_class_region):
        assert str(test_class_region) == repr(test_class_region)

    def test_eq(self, test_class_region):
        assert test_class_region == test_class_region

    def test_ne(self, test_class_region):
        local_reg = Region(10, 10, 12, 12)
        assert test_class_region != local_reg

    def test_lt_le(self, test_class_region):
        local_reg = Region(10, 10, 12, 12)
        assert local_reg < test_class_region
        assert local_reg <= test_class_region

    def test_gt_ge(self, test_class_region):
        local_reg = Region(0, 0, 1000, 1000)
        assert local_reg > test_class_region
        assert local_reg >= test_class_region

    # def test_click(self):
    #     pass

    # def test_rightClick(self):
    #     pass

    # def test_exist(self):
    #     pass

    # def test_reg_find(self):
    #     pass

    # def test_existAny(self):
    #     pass

    # def test_has(self):
    #     pass

    # def test_wait(self):
    #     pass

    # def test_waitWhileExist(self):
    #     pass
