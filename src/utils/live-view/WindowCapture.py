import numpy as np
import win32gui, win32api
import ctypes
import mss
sct = mss.mss()
class WindowCapture:
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self):
        window_handle = win32gui.FindWindow('OsWindow', 'Diablo II: Resurrected')
        if not window_handle:
            raise Exception('Window not found')
        monitor_handle = ctypes.windll.user32.MonitorFromWindow(window_handle)
        #self.monitor_left, self.monitor_top = win32api.GetMonitorInfo(monitor_handle)['Monitor'][:2]
        self.monitor_left, self.monitor_top = (0,0)
        self.hwnd = win32gui.GetDesktopWindow()
        self.client_left, self.client_top = win32gui.ClientToScreen(window_handle, (0, 0))
        self.client_height = 720
        self.client_width = 1280
        self.client_right, self.client_bottom = self.client_to_screen((self.client_width, self.client_height))

    def screen_to_client(self, xy: tuple[int, int]) -> tuple[int, int]:
        # for things like detecting mouse movements, which will give screen coordinates
        # returns client coords
        return xy[0] - self.client_left, xy[1] - self.client_top

    def client_to_screen(self, xy: tuple[int, int]) -> tuple[int, int]:
        # for things like mouse movements or bbox, which use full virtual desktop
        # this function can return negative values
        return xy[0] + self.client_left, xy[1] + self.client_top

    def get_screenshot(self):
        screenshot = sct.grab({'left':self.client_left, 'top':self.client_top, 'width':self.client_width, 'height':self.client_height})
        return np.array(screenshot)