import src.pysikuli as sik
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
