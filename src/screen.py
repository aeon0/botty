import numpy as np
from mss import mss
import cv2
import time
from logger import Logger
from typing import Tuple
from config import Config
from utils import misc
from utils.misc import load_template
import os


class Screen:
    """Grabs images from screen and converts different coordinate systems to each other"""

    def __init__(self, monitor: int = 0, wait: int = 20):
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
        self.found_offsets = False
        position = None
        if self._config.general["find_window_via_win32_api"] :
            Logger.debug("Using WinAPI to search for window under D2R.exe process")
            position = self.find_window_via_winapi()
            if position is None:
                Logger.debug("Can't find any window owned by D2R.exe falling back to matching via assets. Make sure D2R is in focus and you are on the hero selection screen")

        if position is None:
            position = self.find_window_via_assets(wait)

        if position is not None:
            self._set_window_position(*position)
        else:
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/error_d2r_window_not_found_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.grab())
            Logger.error("Could not find hero selection or template for ingame, shutting down")
            Logger.error("Could not determine window offset. Please make sure you have the D2R window " +
                                    f"focused and that you are on the hero selection screen when pressing {self._config.general['resume_key']}")

    def _set_window_position(self, offset_x: int, offset_y: int):
        Logger.debug(f"Set offsets: left {offset_x}px, top {offset_y}px")
        self._monitor_roi["top"] += offset_y
        self._monitor_roi["left"] += offset_x
        self._monitor_x_range = (self._monitor_roi["left"] + 10, self._monitor_roi["left"] + self._monitor_roi["width"] - 10)
        self._monitor_y_range = (self._monitor_roi["top"] + 10, self._monitor_roi["top"] + self._monitor_roi["height"] - 10)
        self._monitor_roi["width"] = self._config.ui_pos["screen_width"]
        self._monitor_roi["height"] = self._config.ui_pos["screen_height"]
        self.found_offsets = True


    def find_window_via_assets(self, wait: int) -> Tuple[int, int]:
        template = load_template(f"assets/templates/main_menu_top_left.png", 1.0)
        template_ingame = load_template(f"assets/templates/window_ingame_offset_reference.png", 1.0)
        debug_max_val = 0
        start = time.time()
        while time.time() - start < wait:
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
            # Save max found scores for debug in case it fails
            if max_val > debug_max_val:
                debug_max_val = max_val
            if max_val > 0.84:
                if max_val < 0.93:
                    Logger.warning(f"Your template match score to calc corner was lower then usual ({max_val*100:.1f}% confidence). " +
                        "You might run into template matching issues along the way!")
                return max_pos
        Logger.error(f"The max score that could be found was: ({debug_max_val*100:.1f}% confidence)")
        return None

    def find_window_via_winapi(self) -> Tuple[int, int]:
        position = misc.find_d2r_window()
        if position is None:
            return None

        offset_x, offset_y, _, _ = position
        return offset_x, offset_y

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
        # cv2.imwrite("./info_screenshots/screenshot_" + time.strftime("%Y%m%d_%H%M%S") + ".png", test_img)
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
                cv2.putText(test_img, roi_key, (p1[0], p1[1]+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

        if show_pt:
            pass

        cv2.imshow("test", test_img)
        cv2.waitKey(1)
