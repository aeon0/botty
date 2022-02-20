import numpy as np
from mss import mss
import cv2
import time
from logger import Logger
from typing import Tuple
from utils.misc import WindowSpec, find_d2r_window
import os
from config import Config

sct = mss()
monitor_roi = sct.monitors[0]
found_offsets = False
monitor_x_range = None
monitor_y_range = None

def convert_monitor_to_screen(screen_coord: Tuple[float, float]) -> Tuple[float, float]:
    global monitor_roi
    return (screen_coord[0] - monitor_roi["left"], screen_coord[1] - monitor_roi["top"])

def convert_screen_to_monitor(screen_coord: Tuple[float, float]) -> Tuple[float, float]:
    global monitor_roi
    x = screen_coord[0] + monitor_roi["left"]
    y = screen_coord[1] + monitor_roi["top"]
    return (np.clip(x, *monitor_x_range), np.clip(y, *monitor_y_range))

def convert_abs_to_screen(abs_coord: Tuple[float, float]) -> Tuple[float, float]:
    global monitor_roi
    # abs has it's center on char which is the center of the screen
    return ((monitor_roi["width"] // 2) + abs_coord[0], (monitor_roi["height"] // 2) + abs_coord[1])

def convert_screen_to_abs(screen_coord: Tuple[float, float]) -> Tuple[float, float]:
    global monitor_roi
    return (screen_coord[0] - (monitor_roi["width"] // 2), screen_coord[1] - (monitor_roi["height"] // 2))

def convert_abs_to_monitor(abs_coord: Tuple[float, float]) -> Tuple[float, float]:
    screen_coord = convert_abs_to_screen(abs_coord)
    monitor_coord = convert_screen_to_monitor(screen_coord)
    return monitor_coord

def set_window_position(offset_x: int, offset_y: int):
    Logger.debug(f"Set offsets: left {offset_x}px, top {offset_y}px")
    global monitor_roi, monitor_x_range, monitor_y_range, found_offsets
    monitor_roi["top"] = offset_y
    monitor_roi["left"] = offset_x
    monitor_roi["width"] = Config().ui_pos["screen_width"]
    monitor_roi["height"] = Config().ui_pos["screen_height"]
    monitor_x_range = (monitor_roi["left"] + 10, monitor_roi["left"] + monitor_roi["width"] - 10)
    monitor_y_range = (monitor_roi["top"] + 10, monitor_roi["top"] + monitor_roi["height"] - 10)
    found_offsets = True

def grab() -> np.ndarray:
    global monitor_roi
    img = np.array(sct.grab(monitor_roi))
    return img[:, :, :3]

find_window = WindowSpec(
    title_regex=Config().advanced_options["hwnd_window_title"],
    process_name_regex=Config().advanced_options["hwnd_window_process"],
)
Logger.debug(f"Using WinAPI to search for window: {find_window}")
position = find_d2r_window(find_window, offset=Config().advanced_options["window_client_area_offset"])
if position is not None:
    set_window_position(*position)

# class Screen:
#     """Grabs images from screen and converts different coordinate systems to each other"""

#     _instance = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(Screen, cls).__new__(cls)
#             cls._instance._sct = mss()
#             if len(cls._instance._sct.monitors) == 1:
#                 Logger.error("How do you not have a monitor connected?!")
#                 os._exit(1)
#             cls._instance._monitor_roi = cls._instance._sct.monitors[0]
#             # Find d2r screen offsets and monitor idx
#             cls._instance.found_offsets = False
#             position = None
#             Logger.debug("Using WinAPI to search for window under D2R.exe process")
#             position = find_d2r_window()
#             if position is not None:
#                 cls._instance._set_window_position(*position)
#             else:
#                 if Config().general["info_screenshots"]:
#                     cv2.imwrite("./info_screenshots/error_d2r_window_not_found_" + time.strftime("%Y%m%d_%H%M%S") + ".png", cls._instance.grab())
#                 Logger.error("Could not determine window offset. Please make sure you have the D2R window open.")
#         return cls._instance

#     def _set_window_position(self, offset_x: int, offset_y: int):
#         Logger.debug(f"Set offsets: left {offset_x}px, top {offset_y}px")
#         self._monitor_roi["top"] = offset_y
#         self._monitor_roi["left"] = offset_x
#         self._monitor_roi["width"] = Config().ui_pos["screen_width"]
#         self._monitor_roi["height"] = Config().ui_pos["screen_height"]
#         self._monitor_x_range = (self._monitor_roi["left"] + 10, self._monitor_roi["left"] + self._monitor_roi["width"] - 10)
#         self._monitor_y_range = (self._monitor_roi["top"] + 10, self._monitor_roi["top"] + self._monitor_roi["height"] - 10)
#         self.found_offsets = True

#     def convert_monitor_to_screen(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
#         return (screen_coord[0] - self._monitor_roi["left"], screen_coord[1] - self._monitor_roi["top"])

#     def convert_screen_to_monitor(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
#         x = screen_coord[0] + self._monitor_roi["left"]
#         y = screen_coord[1] + self._monitor_roi["top"]
#         return (np.clip(x, *self._monitor_x_range), np.clip(y, *self._monitor_y_range))

#     def convert_abs_to_screen(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
#         # abs has it's center on char which is the center of the screen
#         return ((self._monitor_roi["width"] // 2) + abs_coord[0], (self._monitor_roi["height"] // 2) + abs_coord[1])

#     def convert_screen_to_abs(self, screen_coord: Tuple[float, float]) -> Tuple[float, float]:
#         return (screen_coord[0] - (self._monitor_roi["width"] // 2), screen_coord[1] - (self._monitor_roi["height"] // 2))

#     def convert_abs_to_monitor(self, abs_coord: Tuple[float, float]) -> Tuple[float, float]:
#         screen_coord = self.convert_abs_to_screen(abs_coord)
#         monitor_coord = self.convert_screen_to_monitor(screen_coord)
#         return monitor_coord

#     def grab(self) -> np.ndarray:
#         img = np.array(self._sct.grab(self._monitor_roi))
#         return img[:, :, :3]


if __name__ == "__main__":
    while 1:
        start = time.time()
        test_img = grab().copy()
        # print(time.time() - start)

        show_roi = True
        show_pt = True

        if show_roi:
            for roi_key in Config().ui_roi:
                x, y, w, h = Config().ui_roi[roi_key]
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
