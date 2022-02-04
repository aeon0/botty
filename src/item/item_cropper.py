import cv2
import numpy as np
from config import Config
from utils.misc import color_filter, erode_to_black
from dataclasses import dataclass
import time


# TODO: With OCR we can then add a "text" field to this class
@dataclass
class ItemText:
    color_key: str = None
    roi: list[int] = None
    data: np.ndarray = None

class ItemCropper:
    def __init__(self):
        self._config = Config()

        self._gaus_filter = (19, 1)
        self._expected_height_range = [int(round(num, 0)) for num in [x / 1.5 for x in [14, 40]]]
        self._expected_width_range = [int(round(num, 0)) for num in [x / 1.5 for x in [60, 1280]]]

        self._hud_mask = cv2.imread(f"assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
        self._hud_mask = cv2.threshold(self._hud_mask, 1, 255, cv2.THRESH_BINARY)[1]

        self._item_colors = ['white', 'gray', 'blue', 'green', 'yellow', 'gold', 'orange']

    def clean_img(self, inp_img: np.ndarray) -> np.ndarray:
        img = inp_img[:, :, :]
        if img.shape[0] == self._hud_mask.shape[0] and img.shape[1] == self._hud_mask.shape[1]:
            img = cv2.bitwise_and(img, img, mask=self._hud_mask)
        # In order to not filter out highlighted items, change their color to black
        highlight_mask = color_filter(img, self._config.colors["item_highlight"])[0]
        img[highlight_mask > 0] = (0, 0, 0)
        img = erode_to_black(img)
        return img

    def crop(self, inp_img: np.ndarray, padding_y: int = 5) -> list[ItemText]:
        start = time.time()
        cleaned_img = self.clean_img(inp_img)
        debug_str = f" | clean: {time.time() - start}"

        # Cluster item names
        start = time.time()
        item_clusters = []
        for key in self._item_colors:
            _, filtered_img = color_filter(cleaned_img, self._config.colors[key])
            filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
            blured_img = np.clip(cv2.GaussianBlur(filtered_img_gray, self._gaus_filter, cv2.BORDER_DEFAULT), 0, 255)
            contours = cv2.findContours(blured_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = contours[0] if len(contours) == 2 else contours[1]
            for count, cntr in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cntr)
                expected_height = 1 if (self._expected_height_range[0] < h < self._expected_height_range[1]) else 0
                # increase height a bit to make sure we have the full item name in the cluster
                y = y - padding_y if y > padding_y else 0
                h += padding_y * 2
                cropped_item = filtered_img[y:y+h, x:x+w]
                # save most likely item drop contours
                avg = int(np.average(filtered_img_gray[y:y+h, x:x+w]))
                contains_black = True if np.min(cropped_item) < 14 else False
                expected_width = True if (self._expected_width_range[0] < w < self._expected_width_range[1]) else False
                mostly_dark = True if 4 < avg < 25 else False
                if contains_black and mostly_dark and expected_height and expected_width:
                    # double-check item color
                    color_averages=[]
                    for key2 in self._item_colors:
                        _, extracted_img = color_filter(cropped_item, self._config.colors[key2])
                        extr_avg = np.average(cv2.cvtColor(extracted_img, cv2.COLOR_BGR2GRAY))
                        color_averages.append(extr_avg)
                    max_idx = color_averages.index(max(color_averages))
                    if key == self._item_colors[max_idx]:
                        item_clusters.append(ItemText(
                            color_key=self._item_colors[max_idx],
                            roi=[x, y, w, h],
                            data=cropped_item
                        ))
        debug_str += f" | cluster: {time.time() - start}"
        # print(debug_str)
        return item_clusters


if __name__ == "__main__":
    import keyboard
    import os
    from screen import Screen

    keyboard.add_hotkey('f12', lambda: os._exit(1))
    cropper = ItemCropper()
    screen = Screen()

    while 1:
        img = screen.grab().copy()
        res = cropper.crop(img)
        for cluster in res:
            x, y, w, h = cluster.roi
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
        cv2.imshow("res", img)
        cv2.waitKey(1)
