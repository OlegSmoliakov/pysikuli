try:
    import win32gui as w32
except:
    raise ImportError("Please install win32gui")


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
