import time
import random
import ctypes
from logger import Logger
import cv2
from typing import List, Tuple
import requests
import os


def send_discord(item_name, url:str = None):
    if url is None:
        url = "https://discord.com/api/webhooks/908071105372250213/puaS6gIYqYxTE-TBLAIs6_Qb6ZUwuygSeQfTQkpuXrSag5DPeV2gk0SctOjPy5qMHGeh"
    data = {"content": f"Botty just found: {item_name}"}
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

def resize_imgs():
    folders = ["items"]
    for folder in folders:
        new_path = f"assets\\{folder}_1280_720\\"
        for filename in os.listdir(f'assets/{folder}'):
            if filename.endswith('.png') and "sur" in filename:
                data = cv2.imread(f"assets/{folder}/" + filename)
                # cv2.imshow("x", data)
                datan = cv2.resize(data, None, fx=0.666666667, fy=0.66666667, interpolation=cv2.INTER_NEAREST)
                cv2.imwrite(new_path + "near_" + filename, datan)
                datan = cv2.resize(data, None, fx=0.666666667, fy=0.66666667, interpolation=cv2.INTER_AREA)
                cv2.imwrite(new_path + "area_" + filename, datan)
                datan = cv2.resize(data, None, fx=0.666666667, fy=0.66666667, interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(new_path + "cubic_" + filename, datan)
                datan = cv2.resize(data, None, fx=0.666666667, fy=0.66666667, interpolation=cv2.INTER_LANCZOS4)
                cv2.imwrite(new_path + "lanc_" + filename, datan)
                datan = cv2.resize(data, None, fx=0.666666667, fy=0.66666667, interpolation=cv2.INTER_BITS2)
                cv2.imwrite(new_path + "bits_" + filename, datan)
                datan = cv2.resize(data, None, fx=0.666666667, fy=0.66666667, interpolation=cv2.INTER_BITS)
                cv2.imwrite(new_path + "bits2_" + filename, datan)


if __name__ == "__main__":
    resize_imgs()
