import numpy as np
from mss import mss
import cv2
import time
from logger import Logger
from typing import Tuple
from config import Config
from utils.custom_mouse import mouse
import os


class Screen:
    """Grabs images from screen and converts differnt coordinate systems to each other"""

    def __init__(self, monitor: int = 0):
        self._sct = mss()
        monitor_idx = monitor + 1 # sct saves the whole screen (including both monitors if available at index 0, then monitor 1 at 1 and 2 at 2)
        if len(self._sct.monitors) == 1:
            Logger.error("How do you not have a monitor connected?!")
            os._exit(1)
        if monitor_idx >= len(self._sct.monitors):
            Logger.warning("Monitor index not available! Choose a smaller number for 'monitor' in the param.ini. Forcing value to 0 for now.")
            monitor_idx = 1
        config = Config()
        self._monitor_roi = self._sct.monitors[monitor_idx]
        # For windowed screens it is expected to always have them at the top left edge and adjust offset_top then
        self._monitor_roi["top"] += config.general["offset_top"]
        self._monitor_roi["left"] += config.general["offset_left"]
        self._monitor_roi["width"] = config.ui_pos["screen_width"]
        self._monitor_roi["height"] = config.ui_pos["screen_height"]
        self._monitor_x_range = (self._monitor_roi["left"] + 10, self._monitor_roi["left"] + self._monitor_roi["width"] - 10)
        self._monitor_y_range = (self._monitor_roi["top"] + 10, self._monitor_roi["top"] + self._monitor_roi["height"] - 10)

    def convert_monitor_to_screen(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] - self._monitor_roi["left"], screen_coord[1] - self._monitor_roi["top"])

    def convert_screen_to_monitor(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        x = screen_coord[0] + self._monitor_roi["left"]
        y = screen_coord[1] + self._monitor_roi["top"]
        return (np.clip(x, *self._monitor_x_range), np.clip(y, *self._monitor_y_range))

    def convert_abs_to_screen(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
        # abs has it's center on char which is the center of the screen
        return ((self._monitor_roi["width"] // 2) + abs_coord[0], (self._monitor_roi["height"] // 2) + abs_coord[1])

    def convert_screen_to_abs(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
        return (screen_coord[0] - (self._monitor_roi["width"] // 2), screen_coord[1] - (self._monitor_roi["height"] // 2))

    def convert_abs_to_monitor(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
        screen_coord = self.convert_abs_to_screen(abs_coord)
        monitor_coord = self.convert_screen_to_monitor(screen_coord)
        return monitor_coord

    def grab(self, hide_mouse=False) -> np.ndarray:
        if hide_mouse:
            mouse.move(0, 0)  # Moving the mouse to the edge of the screen to not cover any loot.
            time.sleep(0.1)
        img = np.array(self._sct.grab(self._monitor_roi))
        return img[:, :, :3]


if __name__ == "__main__":
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    while 1:
        start = time.time()
        test_img = screen.grab().copy()
        print(time.time() - start)

        show_roi = True
        show_pt = True

        if show_roi:
            for roi_key in config.ui_roi:
                x, y, w, h = config.ui_roi[roi_key]
                # t = screen.convert_screen_to_monitor((0, 0))
                # p1 = screen.convert_screen_to_monitor((x, y))
                # p2 = screen.convert_screen_to_monitor((x+w, y+h))
                p1 = (x, y)
                p2 = (x+w, y+h)
                cv2.rectangle(test_img, p1, p2, (0, 255, 0), 2)
                cv2.putText(test_img, roi_key, (p1[0], p1[1]+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)

        if show_pt:
            pass

        cv2.imshow("test", test_img)
        cv2.waitKey(1)
