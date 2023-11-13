import platform

OSX, WIN, UNIX = 0, 0, 0

system = platform.system()
if system == "Darwin":
    OSX = 1
    from AppKit import NSScreen
elif system == "Windows":
    WIN = 1
elif system == "Linux":
    UNIX = 1
else:
    raise OSError("Can't recognize system os")

def getRefreshRate():
    #https://stackoverflow.com/questions/1225057/how-can-i-determine-the-monitor-refresh-rate
    # answer how to do it in other OS
    maxRefreshRate = 0
    if OSX:
        for each in NSScreen.screens():
            if each.maximumFramesPerSecond() > maxRefreshRate:
                maxRefreshRate = each.maximumFramesPerSecond()
                # print(f"{each.localizedName()}: {each.maximumFramesPerSecond()}Hz")
    if not maxRefreshRate:
        raise OSError("Can't detect refresh rate of the monitors, please insert it manully")
    else:
        return maxRefreshRate