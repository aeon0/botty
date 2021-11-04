import numpy as np
from mss import mss
from PIL import Image
import cv2
import time
from logger import Logger
from typing import Tuple
import os


class Screen:
    def __init__(self, monitor: int = 0):
        self._sct = mss()
        monitor_idx = monitor + 1 # sct saves the whole screen (including both monitors if available at index 0, then monitor 1 at 1 and 2 at 2)
        if len(self._sct.monitors) == 1:
            Logger.error("How do you not have a monitor connected?!")
            os._exit(1)
        if monitor_idx >= len(self._sct.monitors):
            Logger.warning("Monitor index not available! Choose a smaller number for 'monitor' in the param.ini. Forcing value to 0 for now.")
            monitor_idx = 1
        self._monitor_roi = self._sct.monitors[monitor_idx]

    def convert_monitor_to_screen(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] - self._monitor_roi["left"], screen_coord[1] - self._monitor_roi["top"])

    def convert_screen_to_monitor(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] + self._monitor_roi["left"], screen_coord[1] + self._monitor_roi["top"])

    def convert_abs_to_screen(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
        # abs has it's center on char which is the center of the screen
        return ((self._monitor_roi["width"] // 2) + abs_coord[0], (self._monitor_roi["height"] // 2) + abs_coord[1])

    def convert_screen_to_abs(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] - (self._monitor_roi["width"] // 2), screen_coord[1] - (self._monitor_roi["height"] // 2))

    def convert_abs_to_monitor(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
        screen_coord = self.convert_abs_to_screen(abs_coord)
        monitor_coord = self.convert_screen_to_monitor(screen_coord)
        return monitor_coord

    def grab(self) -> np.ndarray:
        img_raw = Image.frombytes('RGB', (self._monitor_roi["width"], self._monitor_roi["height"]), self._sct.grab(self._monitor_roi).rgb)
        img = cv2.cvtColor(np.array(img_raw), cv2.COLOR_RGB2BGR)
        return img


if __name__ == "__main__":
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    while 1:
        start = time.time()
        test_img = screen.grab()
        print(time.time() - start)
        cv2.imshow("test", test_img)
        cv2.waitKey(1)
