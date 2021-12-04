import numpy as np
from mss import mss
import cv2
import time
from logger import Logger
from typing import Tuple
from config import Config
from utils.misc import load_template
import os


class Screen:
    """Grabs images from screen and converts different coordinate systems to each other"""

    def __init__(self, monitor: int = 0):
        self._sct = mss()
        monitor_idx = monitor + 1 # sct saves the whole screen (including both monitors if available at index 0, then monitor 1 at 1 and 2 at 2)
        if len(self._sct.monitors) == 1:
            Logger.error("How do you not have a monitor connected?!")
            os._exit(1)
        if monitor_idx >= len(self._sct.monitors):
            Logger.warning("Monitor index not available! Choose a smaller number for 'monitor' in the param.ini. Forcing value to 0 for now.")
            monitor_idx = 1
        self._config = Config()
        self._monitor_roi = self._sct.monitors[monitor_idx]
        # auto find offests
        template = load_template(f"assets/templates/main_menu_top_left.png", 1.0)
        template_ingame = load_template(f"assets/templates/window_ingame_offset_reference.png", 1.0)
        start = time.time()
        found_offsets = False
        Logger.info("Searching for window offsets. Make sure D2R is in focus and you are on the hero selection screen")
        while time.time() - start < 20:
            img = self.grab()
            self._sct = mss()
            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            res_ingame = cv2.matchTemplate(img, template_ingame, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_pos = cv2.minMaxLoc(res)
            _, max_val_ingame, _, max_pos_ingame = cv2.minMaxLoc(res_ingame)

            # We are in game
            if max_val_ingame > max_val:
                max_val = max_val_ingame
                offset_x, offset_y = max_pos_ingame
                max_pos = (
                    offset_x - self._config.ui_pos["ingame_ref_x"],
                    offset_y - self._config.ui_pos["ingame_ref_y"],
                )

            if max_val > 0.9:
                offset_left, offset_top = max_pos
                Logger.debug(f"Set offsets: left {offset_left}px, top {offset_top}px")
                self._monitor_roi["top"] += offset_top
                self._monitor_roi["left"] += offset_left
                self._monitor_x_range = (self._monitor_roi["left"] + 10, self._monitor_roi["left"] + self._monitor_roi["width"] - 10)
                self._monitor_y_range = (self._monitor_roi["top"] + 10, self._monitor_roi["top"] + self._monitor_roi["height"] - 10)
                self._monitor_roi["width"] = self._config.ui_pos["screen_width"]
                self._monitor_roi["height"] = self._config.ui_pos["screen_height"]
                found_offsets = True
                break
        if not found_offsets:
            Logger.error("Could not find top left corner of D2R window to set offset, shutting down")
            raise RuntimeError("Could not determine window offset. Please make sure you have the D2R window " +
                                f"focused and that you are on the hero selection screen when pressing {self._config.general['resume_key']}")

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

    def grab(self) -> np.ndarray:
        img = np.array(self._sct.grab(self._monitor_roi))
        return img[:, :, :3]


if __name__ == "__main__":
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    while 1:
        start = time.time()
        test_img = screen.grab().copy()
        # print(time.time() - start)

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
