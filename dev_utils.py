import cv2
import src.pysikuli as sik
import numpy as np
import toml


def pyproject_version_update():
    filename = "pyproject.toml"
    version = sik.__version__

    with open(filename, "r") as f:
        data = toml.load(f)

    if data["tool"]["poetry"]["version"] != version:
        data["tool"]["poetry"]["version"] = version
    else:
        return None

    with open(filename, "w") as f:
        toml.dump(data, f)

    print(f"Version updated to: {version}")


def getAllFuncs(module):
    ans = dir(module)
    for x in ans:
        if "__" not in x:
            print(x)


def getUncommonFuncs(first_module, second_module):
    ans = dir(first_module)
    ans2 = dir(second_module)

    common = []
    for x in ans2:
        for y in ans:
            if x in y:
                common.append(x)
                ans.remove(y)
    return ans


def test_getColor():
    # tmp_reg = sik._main._grab((0, 0, 1920, 1080))
    # tmp_reg = np.array(tmp_reg)
    tmp_reg = "pics/monitor.png"
    tmp_reg = cv2.imread(tmp_reg, cv2.IMREAD_COLOR)
    # tmp_reg2 = sik._main._grab(sik._main.mss().monitors[0])
    tmp_reg2 = sik._main.grab((0, 0, 300, 500))
    tmp_reg2 = np.array(tmp_reg2)

    # y, x, color with custom
    # np.array: height, width color

    sum = 0

    for loc_x in range(tmp_reg2.shape[1]):
        for loc_y in range(tmp_reg2.shape[0]):
            r = tmp_reg[loc_y][loc_x][2]
            g = tmp_reg[loc_y][loc_x][1]
            b = tmp_reg[loc_y][loc_x][0]

            grab_rgb = (r, g, b)

            r = tmp_reg2[loc_y][loc_x][2]
            g = tmp_reg2[loc_y][loc_x][1]
            b = tmp_reg2[loc_y][loc_x][0]

            monitor_rgb = (r, g, b)

            assert grab_rgb == monitor_rgb
            sum += 1
    return sum


def test_run():
    sik.config.MOUSE_SPEED = 2

    pic_1 = "pics/1.png"
    pic_8 = "pics/8.png"
    pic_plus = "pics/plus.png"
    pic_equal = "pics/equal.png"

    if sik.windowExist("calculator"):
        sik.closeWindow("calculator")
    sik.tap(sik.Key.win)
    sik.sleep(0.1)
    sik.write("calc")
    sik.tap(sik.Key.enter)
    sik.click(pic_8)
    sik.click(pic_plus)
    sik.click(pic_1)
    sik.click(pic_equal)

    sik.click((200, 200)), sik.sleep(0.5)
    sik.activateWindow("Calculator"), sik.sleep(0.5)

    sik.click((200, 200)), sik.sleep(0.5)
    loc_equal = sik.find(pic_equal).center_loc
    sik.activateWindowAt(loc_equal), sik.sleep(0.5)

    sik.click((200, 200)), sik.sleep(0.5)
    sik.mouseMove(loc_equal)
    sik.activateWindowUnderMouse(), sik.sleep(0.5)
