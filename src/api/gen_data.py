import time
import numpy as np
from api.mapassist import MapAssistApi
from screen import Screen
import cv2
import time
import cv2
import numpy as np
import keyboard
import json
from json.decoder import JSONDecodeError
import os


_idx = 0
_file = "generated/gt.json"
_name = "vendors"

def save_frame(api: MapAssistApi, screen: Screen):
    global _idx
    img = screen.grab().copy()
    data = api.get_data()

    delta_x = [64, -64]
    delta_y = [10, -54]
    scale = 0.5

    if data is not None:
        if not os.path.exists("generated"):
            os.system(f"mkdir generated")
            with open(_file, 'w+') as f:
                f.write("")
        curr_file_name = f"{_name}_{_idx}"
        gt = []
        with open(_file, "r") as json_file:
            try:
                gt = json.load(json_file)
            except JSONDecodeError as e:
                print(e)
            for monster in data["monsters"]:
                p = monster["abs_screen_position"]
                gt.append({
                    "pos": [
                        int((p[0] - delta_x[0]) / scale),
                        int((p[1] - delta_y[0]) / scale),
                    ],
                    "name": str(monster["name"]),
                    "id": int(monster["id"]),
                    "file": curr_file_name
                })
        if len(gt) > 0:
            with open(_file, "w") as json_file:
                json.dump(gt, json_file)

        img = cv2.resize(img, None, fx=scale, fy=scale)
        img = img[delta_y[0]:delta_y[1], delta_x[0]:delta_x[1], :]
        cv2.imwrite(f"generated/{curr_file_name}.png", img)
        print(f"Saved {_idx}")
        _idx += 1
    time.sleep(0.5)
    return True


if __name__ == "__main__":
    os.system(f"rm -rf generated")
    screen = Screen(1)
    api = MapAssistApi()
    while True:
        if keyboard.is_pressed("j"):
            done = save_frame(api, screen)
