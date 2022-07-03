import cv2
import time
import os
import json
from utils.misc import wait
from requests import JSONDecodeError
from screen import grab, convert_monitor_to_screen
from logger import Logger
from utils.custom_mouse import mouse
from ui_manager import center_mouse


def label_vendor(npc_name: str):
    Logger.debug(f"Label NPC: {npc_name}")
    center_pos_monitor = mouse.get_position()
    center_pos_screen = convert_monitor_to_screen(center_pos_monitor)
    center_mouse()

    # create folders
    base_path = "log/labels/vendors"
    ground_truth_path = f"{base_path}/ground_truth.json"
    for dir_name in ["log", "log/labels", base_path, f"{base_path}/imgs"]:
        os.makedirs(dir_name, exist_ok=True)
    if not os.path.exists(ground_truth_path):
        with open(ground_truth_path, "w+") as f:
            pass # just to create file if it does not yet exist

    # label it
    img_name = "vendor_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
    cv2.imwrite(f"{base_path}/imgs/" + img_name, grab())
    label = {
        "objects":  [{"name": npc_name, "center": center_pos_screen}],
        "img": img_name
    }
    data = None
    with open(ground_truth_path, "r") as f:
        try:
            data = json.load(f)
        except ValueError as e:
            print(e)
            Logger.debug("Creating vendor ground_truth json file")
            data = []
        data.append(label)
    if data is not None:
        with open(ground_truth_path, "w") as f:
            json.dump(data, f)
    
    # move back mouse
    mouse.move(*center_pos_monitor)
    wait(0.2, 0.3)
