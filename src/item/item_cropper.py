import cv2
import numpy as np
from config import Config
from utils.misc import color_filter
from ocr import Ocr, OcrResult
from dataclasses import dataclass
import time
from logger import Logger
from template_finder import TemplateFinder

@dataclass
class ItemText:
    color: str = None
    ocr_result: OcrResult = None
    roi: list[int] = None
    data: np.ndarray = None
    clean_img: np.ndarray = None
    def __getitem__(self, key):
        return super().__getattribute__(key)

class ItemCropper:
    def __init__(self, template_finder: TemplateFinder):
        self._config = Config()
        self._template_finder = template_finder
        self._ocr = Ocr()

        self._gaus_filter = (19, 1)
        self._expected_height_range = [int(round(num, 0)) for num in [x / 1.5 for x in [14, 40]]]
        self._expected_width_range = [int(round(num, 0)) for num in [x / 1.5 for x in [60, 1280]]]
        self._box_expected_width_range=[200, 900]
        self._box_expected_height_range=[24, 710]

        self._hud_mask = cv2.imread(f"assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
        self._hud_mask = cv2.threshold(self._hud_mask, 1, 255, cv2.THRESH_BINARY)[1]

        self._item_colors = ['white', 'gray', 'blue', 'green', 'yellow', 'gold', 'orange']

    def clean_img(self, inp_img: np.ndarray, black_thresh: int = 14) -> np.ndarray:
        img = inp_img[:, :, :]
        if img.shape[0] == self._hud_mask.shape[0] and img.shape[1] == self._hud_mask.shape[1]:
            img = cv2.bitwise_and(img, img, mask=self._hud_mask)
        # In order to not filter out highlighted items, change their color to black
        highlight_mask = color_filter(img, self._config.colors["item_highlight"])[0]
        img[highlight_mask > 0] = (0, 0, 0)
        # Cleanup image with erosion image as marker with morphological reconstruction
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, black_thresh, 255, cv2.THRESH_BINARY)[1]
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
        return img, mask_r

    def crop(self, inp_img: np.ndarray, padding_y: int = 5, ocr: bool = True, ocr_language: str = "engd2r_inv_th_fast") -> list[ItemText]:
        start = time.time()
        cleaned_img = self.clean_img(inp_img)[0]
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
            for cntr in contours:
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
                            color = key,
                            roi = [x, y, w, h],
                            data = cropped_item,
                            clean_img = cleaned_img[y:y+h, x:x+w]
                        ))
        debug_str += f" | cluster: {time.time() - start}"
        # print(debug_str)
        if ocr:
            cluster_images = [ key["clean_img"] for key in item_clusters ]
            results = self._ocr.images_to_text(cluster_images, ocr_language=ocr_language)
            for count, cluster in enumerate(item_clusters):
                setattr(cluster, "ocr_result", results[count])
        return item_clusters

    def crop_item_descr(self, inp_img: np.ndarray, ocr: bool = True, ocr_language: str = "engd2r_inv_th", all_results: bool = False) -> ItemText:
        results=[]
        black_mask, _ = color_filter(inp_img, self._config.colors["black"])
        contours = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            cropped_item = inp_img[y:y+h, x:x+w]
            avg = np.average(cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY))
            mostly_dark = True if 0 < avg < 20 else False
            contains_black = True if np.min(cropped_item) < 14 else False
            contains_white = True if np.max(cropped_item) > 250 else False
            contains_orange = False
            if not contains_white:
                #check for orange (like key of destruction, etc.)
                orange_mask, _ = color_filter(cropped_item, self._config.colors["orange"])
                contains_orange = np.min(orange_mask) > 0
            expected_height = True if (self._box_expected_height_range[0] < h < self._box_expected_height_range[1]) else False
            expected_width = True if (self._box_expected_width_range[0] < w < self._box_expected_width_range[1]) else False
            box2 = self._config.ui_roi["inventory"]
            overlaps_inventory = False if (x+w<box2[0] or box2[0]+box2[2]<x or y+h+28+10<box2[1] or box2[1]+box2[3]<y) else True # padded height because footer isn't included in contour
            if contains_black and (contains_white or contains_orange) and mostly_dark and expected_height and expected_width and overlaps_inventory:
                found_footer = self._template_finder.search(["INVENTORY_HOLD_SHIFT", "INVENTORY_CNTR_CLICK"], inp_img, threshold=0.8).valid
                if found_footer:
                    ocr_result = None
                    if ocr:
                        ocr_result = self._ocr.images_to_text(cropped_item, multiline=True, ocr_language=ocr_language)[0]
                    results.append(ItemText(
                        color = "black",
                        roi = [x, y, w, h],
                        data = cropped_item,
                        ocr_result = ocr_result
                    ))
                    if not all_results:
                        break
        return results

if __name__ == "__main__":
    import keyboard
    import os
    from config import Config
    from template_finder import TemplateFinder
    from screen import Screen

    keyboard.add_hotkey('f12', lambda: os._exit(1))
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    cropper = ItemCropper(template_finder)

    while 1:
        img = screen.grab().copy()
        results = cropper.crop_item_descr(img, all_results=True, ocr=False)
        for res in results:
            if res["color"]:
                x, y, w, h = res.roi
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                #Logger.debug(f"{res.ocr_result['text']}")
        cv2.imshow("res", img)
        cv2.waitKey(1)
