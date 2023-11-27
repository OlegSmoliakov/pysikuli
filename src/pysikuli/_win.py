try:
    import win32gui as w32
except:
    raise ImportError("Please install win32gui")

import logging


class ActiveWindow:
    final_hwnd = 0

    def winEnumHandler(self, hwnd, ctx):
        if w32.IsWindowVisible(hwnd) and self.name in w32.GetWindowText(hwnd).lower():
            self.final_hwnd = hwnd
            print(hwnd, w32.GetWindowText(hwnd))

    def set_foreground(self, name: str):
        self.name = name.lower()
        w32.EnumWindows(self.winEnumHandler, None)
        """put the window in the foreground"""
        print(self.final_hwnd, "selected")
        w32.SetForegroundWindow(self.final_hwnd)


def _getRefreshRate():
    # TODO: figure out how to finished and implement this function
    # https://stackoverflow.com/questions/1225057/how-can-i-determine-the-monitor-refresh-rate
    pass


def _activateWindow(app_name: str):
    ActiveWindow().set_foreground(app_name)
    logging.debug("{0} activated".format(app_name))


def _getWindowRegion(app_name: str):
    raise NotImplementedError()


def _minimizeWindow(app_name: str):
    raise NotImplementedError()


def _unminimizeWindow(app_name: str):
    raise NotImplementedError()
