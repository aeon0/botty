import numpy as np
from mss import mss
from logger import Logger
from utils.misc import WindowSpec, find_d2r_window, wait
from config import Config
import threading
import time

sct = mss()
monitor_roi = sct.monitors[0]
found_offsets = False
monitor_x_range = None
monitor_y_range = None
detect_window = True
detect_window_thread = None
last_grab = None
cached_img = None
cached_img_lock = threading.Lock()

FIND_WINDOW = WindowSpec(
    title_regex=Config().advanced_options["hwnd_window_title"],
    process_name_regex=Config().advanced_options["hwnd_window_process"],
)

def get_offset_state():
    global found_offsets
    return found_offsets

def start_detecting_window():
    global detect_window, detect_window_thread
    detect_window = True
    if detect_window_thread is None:
        Logger.debug(f"Using WinAPI to search for window: {FIND_WINDOW}")
        detect_window_thread = threading.Thread(target=detect_window_position)
        detect_window_thread.start()

def detect_window_position():
    global detect_window
    while detect_window:
        find_and_set_window_position()
    Logger.debug('Detect window thread stopped')

def find_and_set_window_position():
    position = find_d2r_window(FIND_WINDOW, offset=Config(
    ).advanced_options["window_client_area_offset"])
    if position is not None:
        set_window_position(*position)
    wait(1)

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

def stop_detecting_window():
    global detect_window, detect_window_thread
    detect_window = False
    if detect_window_thread:
        detect_window_thread.join()

def grab(force_new: bool = False) -> np.ndarray:
    global monitor_roi
    global cached_img
    global last_grab
    # with 25fps we have 40ms per frame. If we check for 20ms range to make sure we can still get each frame if we want.
    if not force_new and cached_img is not None and last_grab is not None and time.perf_counter() - last_grab < 0.04:
        return cached_img
    else:
        with cached_img_lock:
            last_grab = time.perf_counter()
        img = np.array(sct.grab(monitor_roi))
        with cached_img_lock:
            cached_img = img[:, :, :3]
        return cached_img

# TODO: Move the below funcs to utils(?)

def convert_monitor_to_screen(screen_coord: tuple[float, float]) -> tuple[float, float]:
    global monitor_roi
    if screen_coord is None:
        Logger.error("convert_monitor_to_screen: empty coordinates passed")
        return None
    return (screen_coord[0] - monitor_roi["left"], screen_coord[1] - monitor_roi["top"])

def convert_screen_to_monitor(screen_coord: tuple[float, float]) -> tuple[float, float]:
    global monitor_roi
    if screen_coord is None:
        Logger.error("convert_screen_to_monitor: empty coordinates passed")
        return None
    x = screen_coord[0] + monitor_roi["left"]
    y = screen_coord[1] + monitor_roi["top"]
    return (np.clip(x, *monitor_x_range), np.clip(y, *monitor_y_range))

def convert_abs_to_screen(abs_coord: tuple[float, float]) -> tuple[float, float]:
    global monitor_roi
    if abs_coord is None:
        Logger.error("convert_screen_to_monitor: empty coordinates passed")
        return None
    # abs has it's center on char which is the center of the screen
    return ((monitor_roi["width"] // 2) + abs_coord[0], (monitor_roi["height"] // 2) + abs_coord[1])

def convert_screen_to_abs(screen_coord: tuple[float, float]) -> tuple[float, float]:
    global monitor_roi
    if screen_coord is None:
        Logger.error("convert_screen_to_abs: empty coordinates passed")
        return None
    return (screen_coord[0] - (monitor_roi["width"] // 2), screen_coord[1] - (monitor_roi["height"] // 2))

def convert_abs_to_monitor(abs_coord: tuple[float, float]) -> tuple[float, float]:
    if abs_coord is None:
        Logger.error("convert_abs_to_monitor: empty coordinates passed")
        return None
    screen_coord = convert_abs_to_screen(abs_coord)
    monitor_coord = convert_screen_to_monitor(screen_coord)
    return monitor_coord
