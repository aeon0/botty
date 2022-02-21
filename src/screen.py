import numpy as np
from mss import mss
import cv2
import time
from logger import Logger
from typing import Tuple
from utils.misc import WindowSpec, find_d2r_window, wait
import os
from config import Config
import threading

sct = mss()
monitor_roi = sct.monitors[0]
found_offsets = False
monitor_x_range = None
monitor_y_range = None
detect_window = True

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
    global monitor_roi, monitor_x_range, monitor_y_range, found_offsets
    if found_offsets and monitor_roi["top"] == offset_y and monitor_roi["left"] == offset_x:
        return
    Logger.debug(f"Set offsets: left {offset_x}px, top {offset_y}px")
    monitor_roi["top"] = offset_y
    monitor_roi["left"] = offset_x
    monitor_roi["width"] = Config().ui_pos["screen_width"]
    monitor_roi["height"] = Config().ui_pos["screen_height"]
    monitor_x_range = (
        monitor_roi["left"] + 10, monitor_roi["left"] + monitor_roi["width"] - 10)
    monitor_y_range = (
        monitor_roi["top"] + 10, monitor_roi["top"] + monitor_roi["height"] - 10)
    found_offsets = True


def grab() -> np.ndarray:
    global monitor_roi
    img = np.array(sct.grab(monitor_roi))
    return img[:, :, :3]


def detect_window_position():
    global detect_window
    Logger.debug('Detect window thread started')
    while detect_window:
        position = find_d2r_window(find_window, offset=Config(
        ).advanced_options["window_client_area_offset"])
        if position is not None:
            set_window_position(*position)
        wait(0.5)
    Logger.debug('Detect window thread stopped')


detect_window_thread = None


def start_detecting_window():
    global detect_window, detect_window_thread
    detect_window = True
    if detect_window_thread is None:
        detect_window_thread = threading.Thread(target=detect_window_position)
        detect_window_thread.start()


def stop_detecting_window():
    global detect_window, detect_window_thread
    detect_window = False
    detect_window_thread.join()


find_window = WindowSpec(
    title_regex=Config().advanced_options["hwnd_window_title"],
    process_name_regex=Config().advanced_options["hwnd_window_process"],
)

Logger.debug(f"Using WinAPI to search for window: {find_window}")
