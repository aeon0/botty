import cv2
from typing import Tuple, List
import numpy as np
import time
import os
from dataclasses import dataclass
import math
from config import Config
from utils.misc import color_filter, cut_roi


@dataclass
class Template:
    data: np.ndarray = None
    hist = None
    blacklist: bool = False

@dataclass
class Item:
    center: Tuple[float, float] = None # (x, y) in screen coordinates
    name: str = None
    score: float = -1.0
    dist: float = -1.0
    roi: List[int] = None

class ItemFinder:
    def __init__(self):
        config = Config()
        # color range for each type of item
        # hsv ranges in opencv h: [0-180], s: [0-255], v: [0, 255]
        self._template_color_ranges = {
            "white": [np.array([0, 0, 150]), np.array([0, 0, 245])],
            "gray": [np.array([0, 0, 90]), np.array([0, 0, 126])],
            "magic": [np.array([120, 120, 190]), np.array([120, 126, 255])],
            "set": [np.array([60, 250, 190]), np.array([60, 255, 255])],
            "rare": [np.array([30, 128, 190]), np.array([30, 137, 255])],
            "unique": [np.array([23, 80, 140]), np.array([23, 89, 216])],
            "runes": [np.array([21, 251, 190]), np.array([22, 255, 255])]
        }
        self._game_color_ranges = {
            "white": config.colors["white"],
            "gray": config.colors["gray"],
            "magic": config.colors["blue"],
            "set": config.colors["green"],
            "rare": config.colors["yellow"],
            "unique": config.colors["gold"],
            "runes": config.colors["orange"]
        }
        self._gaus_filter = (17, 5)
        self._folder_name = "items"
        self._min_score = 0.86
        # load all templates
        self._config = config
        self._templates = {}
        for filename in os.listdir(f'assets/{self._folder_name}'):
            filename = filename.lower()
            if filename.endswith('.png'):
                item_name = filename[:-4]
                # assets with bl__ are black listed items and will not be picke up
                blacklist_item = item_name.startswith("bl__")
                # these items will be searched for regardless of pickit setting (e.g. for runes to avoid mixup)
                force_search = item_name.startswith("rune_")
                if blacklist_item or ((item_name in config.items and self._config.items[item_name]) or force_search):
                    data = cv2.imread(f"assets/{self._folder_name}/" + filename)
                    filtered_template = np.zeros(data.shape, np.uint8)
                    for key in self._template_color_ranges:
                        _, extracted_template = color_filter(data, self._template_color_ranges[key])
                        filtered_template = cv2.bitwise_or(filtered_template, extracted_template)
                    grayscale = cv2.cvtColor(filtered_template, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(grayscale, 0, 255, cv2.THRESH_BINARY)
                    hist = cv2.calcHist([filtered_template], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    template = Template()
                    template.data = filtered_template
                    template.hist = hist
                    if blacklist_item:
                        template.blacklist = True
                    self._templates[item_name] = template

    def search(self, inp_img: np.ndarray) -> List[Item]:
        img = inp_img[:,:,:]
        start = time.time()
        # Pre filter black and highlight
        mask1, _ = color_filter(img, self._config.colors["black"])
        mask2, _ = color_filter(img, self._config.colors["item_highlight"])
        filtered_img = cv2.bitwise_or(mask1, mask2)
        contours = cv2.findContours(filtered_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        new_img = np.zeros(img.shape, np.uint8)
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            new_img[y:y+h, x:x+w] = img[y:y+h, x:x+w]
        img = new_img
        # Filter by item colors
        filtered_img = np.zeros(img.shape, np.uint8)
        for key in self._game_color_ranges:
            _, extracted_img = color_filter(img, self._game_color_ranges[key])
            filtered_img = cv2.bitwise_or(filtered_img, extracted_img)
        filtered_img_gray = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)
        # Cluster item names
        cluster_img = np.clip(cv2.GaussianBlur(filtered_img_gray, self._gaus_filter, cv2.BORDER_DEFAULT), 0, 255)
        contours = cv2.findContours(cluster_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        item_list = []
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            x -= 5
            y -= 5
            w += 10
            h += 10
            # cv2.rectangle(inp_img, (x, y), (x+w, y+h), (0, 255, 0), 1)

            cropped_input = filtered_img[y:y+h, x:x+w]
            best_score = None
            item = None
            for key in self._templates:
                template: Template = self._templates[key]
                if cropped_input.shape[1] > template.data.shape[1] and cropped_input.shape[0] > template.data.shape[0]:
                    # sanity check if there is any color overlap of template and cropped_input
                    grayscale = cv2.cvtColor(cropped_input, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(grayscale, 0, 255, cv2.THRESH_BINARY)
                    hist = cv2.calcHist([cropped_input], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                    hist_result = cv2.compareHist(template.hist, hist, cv2.HISTCMP_CORREL)
                    same_type = hist_result > 0.0 and hist_result is not np.inf
                    if same_type:
                        result = cv2.matchTemplate(cropped_input, template.data, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(result)
                        if max_val > self._min_score:
                            if template.blacklist:
                                max_val += 0.02
                            if (best_score is None or max_val > best_score):
                                best_score = max_val
                                if template.blacklist:
                                    item = None
                                else:
                                    max_loc = [max_loc[0] + x, max_loc[1] + y]
                                    # Do another color hist check with the actuall found item template
                                    cropped_roi = [*max_loc, template.data.shape[1], template.data.shape[0]]
                                    cropped_item = cut_roi(filtered_img, cropped_roi)
                                    grayscale = cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY)
                                    _, mask = cv2.threshold(grayscale, 0, 255, cv2.THRESH_BINARY)
                                    hist = cv2.calcHist([cropped_item], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
                                    hist_result = cv2.compareHist(template.hist, hist, cv2.HISTCMP_CORREL)
                                    same_type = hist_result > 0.65 and hist_result is not np.inf
                                    if same_type:
                                        item = Item()
                                        item.center = (int(max_loc[0] + int(template.data.shape[1] * 0.5)), int(max_loc[1] + int(template.data.shape[0] * 0.5)))
                                        item.name = key
                                        item.score = max_val
                                        item.roi = [*max_loc, template.data.shape[1], template.data.shape[0]]
                                        center_abs = (item.center[0] - (inp_img.shape[1] // 2), item.center[1] - (inp_img.shape[0] // 2))
                                        item.dist = math.dist(center_abs, (0, 0))
            if item is not None and self._config.items[item.name]:
                item_list.append(item)
        elapsed = time.time() - start
        # print(f"Item Search: {elapsed}")
        return item_list


# Testing: Throw some stuff on the ground see if it is found
if __name__ == "__main__":
    from screen import Screen
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    item_finder = ItemFinder()
    while 1:
        # img = cv2.imread("")
        img = screen.grab().copy()
        item_list = item_finder.search(img)
        for item in item_list:
            print(item.name + " " + str(item.score))
            cv2.circle(img, item.center, 5, (255, 0, 255), thickness=3)
            cv2.rectangle(img, item.roi[:2], (item.roi[0] + item.roi[2], item.roi[1] + item.roi[3]), (0, 0, 255), 1)
            cv2.putText(img, item.name, item.center, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        # img = cv2.resize(img, None, fx=0.5, fy=0.5)
        cv2.imshow('test', img)
        cv2.waitKey(1)
