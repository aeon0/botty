import time
import random
import ctypes
from logger import Logger
import cv2
from typing import List, Tuple
import requests


def send_discord(item_name, url:str = None):
    if url is None:
        url =  "https://discord.com/api/webhooks/908045354061160459/8-HQRLPTHxMlf5VpvScuvNEpLLIe8KHqxgRIk6p17u6LMPvzCCQotT_iGioQHQVU5u_P"
    data = {"content": f"Botty just found: {item_name}"}
    requests.post(url, json=data)

def wait(min_seconds, max_seconds = None):
    if max_seconds is None:
        max_seconds = min_seconds
    time.sleep(random.random() * (max_seconds - min_seconds) + min_seconds)
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
