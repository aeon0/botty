import time
import random
import ctypes
from logger import Logger
import cv2
from typing import List, Tuple
import requests
import subprocess
from version import __version__


def send_discord(msg, url: str):
    if not url:
        return
    data = {"content": f"{msg} (v{__version__})"}
    requests.post(url, json=data)

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
    x, y, width, height = roi 
    return img[y:y+height, x:x+width]

def is_in_roi(roi: List[float], pos: Tuple[float, float]):
    x, y, w, h = roi
    is_in_x_range = x < pos[0] < x + w
    is_in_y_range = y < pos[1] < y + h
    return is_in_x_range and is_in_y_range

def color_filter(img, color_range):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsv_img, color_range[0], color_range[1])
    filtered_img = cv2.bitwise_and(img, img, mask=color_mask)
    return color_mask, filtered_img

def close_down_d2():
    subprocess.call(["taskkill","/F","/IM","D2R.exe"])
    subprocess.call(["taskkill","/F","/IM","Battle.net.exe"])
