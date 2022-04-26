from dataclasses import dataclass
from decimal import InvalidOperation
from re import RegexFlag
import time
import random
import ctypes
import numpy as np
from copy import deepcopy

from pyparsing import Regex

from logger import Logger
import cv2
from typing import List, Tuple, Union
import os
from math import cos, sin, dist
import subprocess
from win32con import HWND_TOPMOST, SWP_NOMOVE, SWP_NOSIZE, HWND_NOTOPMOST
from win32gui import GetWindowText, SetWindowPos, EnumWindows, GetClientRect, ClientToScreen
from win32api import GetMonitorInfo, MonitorFromWindow
from win32process import GetWindowThreadProcessId
import psutil

from rapidfuzz.process import extractOne
from rapidfuzz.string_metric import levenshtein

def close_down_d2():
    subprocess.call(["taskkill","/F","/IM","D2R.exe"], stderr=subprocess.DEVNULL)

def close_down_bnet_launcher():
    subprocess.call(["taskkill","/F","/IM","Battle.net.exe"], stderr=subprocess.DEVNULL)

@dataclass
class WindowSpec:
    title_regex: 'Union[str, None]' = None
    process_name_regex: 'Union[str, None]' = None

    def match(self, hwnd) -> bool:
        result = True
        if self.title_regex is not None:
            result = result and Regex(self.title_regex).matches(GetWindowText(hwnd))
        if self.process_name_regex is not None:
            _, process_id = GetWindowThreadProcessId(hwnd)
            if process_id > 0:
                result = result and Regex(self.process_name_regex).matches(psutil.Process(process_id).name())
        if self.title_regex is None and self.process_name_regex is None:
            result = False
        return result

def find_d2r_window(spec: WindowSpec, offset = (0, 0)) -> tuple[int, int]:
    offset_x, offset_y = offset
    if os.name == 'nt':
        window_list = []
        EnumWindows(lambda w, l: l.append(w), window_list)
        for hwnd in window_list:
            if spec.match(hwnd):
                left, top, right, bottom = GetClientRect(hwnd)
                (left, top), (right, bottom) = ClientToScreen(hwnd, (left, top)), ClientToScreen(hwnd, (right, bottom))
                return (left + offset_x, top + offset_y)
    return None

def set_d2r_always_on_top():
    if os.name == 'nt':
        windows_list = []
        EnumWindows(lambda w, l: l.append((w, GetWindowText(w))), windows_list)
        for w in windows_list:
            if w[1] == "Diablo II: Resurrected":
                SetWindowPos(w[0], HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                print("Set D2R to be always on top")
    else:
        print('OS not supported, unable to set D2R always on top')

def restore_d2r_window_visibility():
    if os.name == 'nt':
        windows_list = []
        EnumWindows(lambda w, l: l.append((w, GetWindowText(w))), windows_list)
        for w in windows_list:
            if w[1] == "Diablo II: Resurrected":
                SetWindowPos(w[0], HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
                print("Restored D2R window visibility")
    else:
        print('OS not supported, unable to set D2R always on top')

def wait(min_seconds, max_seconds = None):
    if max_seconds is None:
        max_seconds = min_seconds
    time.sleep(random.uniform(min_seconds, max_seconds))
    return

def kill_thread(thread):
    thread_id = thread.ident
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        Logger.error('Exception raise failure')

def cut_roi(img, roi):
    x, y, w, h = roi
    return img[y:y+h, x:x+w]

def mask_by_roi(img, roi, type: str = "regular"):
    x, y, w, h = roi
    if type == "regular":
        masked = np.zeros(img.shape, dtype=np.uint8)
        masked[y:y+h, x:x+w] = img[y:y+h, x:x+w]
    elif type == "inverse":
        masked = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), -1)
    else:
        return None
    return masked

def is_in_roi(roi: List[float], pos: Tuple[float, float]):
    x, y, w, h = roi
    is_in_x_range = x < pos[0] < x + w
    is_in_y_range = y < pos[1] < y + h
    return is_in_x_range and is_in_y_range

def trim_black(image):
    y_nonzero, x_nonzero = np.nonzero(image)
    roi = np.min(x_nonzero), np.min(y_nonzero), np.max(x_nonzero) - np.min(x_nonzero), np.max(y_nonzero) - np.min(y_nonzero)
    img = image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]
    return img, roi

def erode_to_black(img: np.ndarray, threshold: int = 14):
    # Cleanup image with erosion image as marker with morphological reconstruction
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)[1]
    kernel = np.ones((3, 3), np.uint8)
    marker = thresh.copy()
    marker[1:-1, 1:-1] = 0
    while True:
        tmp = marker.copy()
        marker = cv2.dilate(marker, kernel)
        marker = cv2.min(thresh, marker)
        difference = cv2.subtract(marker, tmp)
        if cv2.countNonZero(difference) <= 0:
            break
    mask_r = cv2.bitwise_not(marker)
    mask_color_r = cv2.cvtColor(mask_r, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, mask_color_r)
    return img

def roi_center(roi: list[float] = None):
    x, y, w, h = roi
    return round(x + w/2), round(y + h/2)

def color_filter(img, color_range):
    color_ranges=[]
    # ex: [array([ -9, 201,  25]), array([ 9, 237,  61])]
    if color_range[0][0] < 0:
        lower_range = deepcopy(color_range)
        lower_range[0][0] = 0
        color_ranges.append(lower_range)
        upper_range = deepcopy(color_range)
        upper_range[0][0] = 180 + color_range[0][0]
        upper_range[1][0] = 180
        color_ranges.append(upper_range)
    # ex: [array([ 170, 201,  25]), array([ 188, 237,  61])]
    elif color_range[1][0] > 180:
        upper_range = deepcopy(color_range)
        upper_range[1][0] = 180
        color_ranges.append(upper_range)
        lower_range = deepcopy(color_range)
        lower_range[0][0] = 0
        lower_range[1][0] = color_range[1][0] - 180
        color_ranges.append(lower_range)
    else:
        color_ranges.append(color_range)
    color_masks = []
    for color_range in color_ranges:
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, color_range[0], color_range[1])
        color_masks.append(mask)
    color_mask = np.bitwise_or.reduce(color_masks) if len(color_masks) > 0 else color_masks[0]
    filtered_img = cv2.bitwise_and(img, img, mask=color_mask)
    return color_mask, filtered_img

def hms(seconds: int):
    seconds = int(seconds)
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60
    return '{:02d}:{:02d}:{:02d}'.format(h, m, s)

def load_template(path, scale_factor: float = 1.0, alpha: bool = False):
    if os.path.isfile(path):
        try:
            template_img = cv2.imread(path, cv2.IMREAD_UNCHANGED) if alpha else cv2.imread(path)
            template_img = cv2.resize(template_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
            return template_img
        except Exception as e:
            print(e)
            raise ValueError(f"Could not load template: {path}")
    return None

def alpha_to_mask(img: np.ndarray):
    # create a mask from template where alpha == 0
    if img.shape[2] == 4:
        if np.min(img[:, :, 3]) == 0:
            _, mask = cv2.threshold(img[:,:,3], 1, 255, cv2.THRESH_BINARY)
            return mask
    return None

def list_files_in_folder(path: str):
    r = []
    for root, _, files in os.walk(path):
        for name in files:
            r.append(os.path.join(root, name))
    return r

def rotate_vec(vec: np.ndarray, deg: float) -> np.ndarray:
    theta = np.deg2rad(deg)
    rot_matrix = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    return np.dot(rot_matrix, vec)

def unit_vector(vec: np.ndarray) -> np.ndarray:
    return vec / dist(vec, (0, 0))

def image_is_equal(img1: np.ndarray, img2: np.ndarray) -> bool:
    shape_equal = img1.shape == img2.shape
    if not shape_equal:
        Logger.debug("image_is_equal: Image shape is not equal")
        return False
    return not(np.bitwise_xor(img1, img2).any())

@dataclass
class best_match_result:
    match: str
    score: float

def find_best_match(in_str: str, str_list: list[str], normalize: bool = False) -> best_match_result:
    best_match, best_lev, _ = extractOne(in_str, str_list, scorer=levenshtein)
    if normalize:
        best_lev = 1 - best_lev / len(in_str)
    return best_match_result(best_match, best_lev)

# if __name__ == "__main__":
    # print(find_d2r_window())
    # print(find_d2r_window())