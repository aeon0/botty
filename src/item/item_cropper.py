import cv2
import numpy as np
from dataclasses import dataclass
import time

from utils.misc import color_filter, erode_to_black
from template_finder import TemplateFinder
from ocr import Ocr, OcrResult
from config import Config
from logger import Logger

# TODO: With OCR we can then add a "text" field to this class
@dataclass
class ItemText:
    color: str = None
    roi: list[int] = None
    data: np.ndarray = None
    ocr_result: OcrResult = None
    clean_img: np.ndarray = None
    valid: bool = False
    def __getitem__(self, key):
        return super().__getattribute__(key)

class ItemCropper:
    def __init__(self):
        self._ocr = Ocr()

        self._gaus_filter = (19, 1)
        self._expected_height_range = [round(num) for num in [x / 1.5 for x in [14, 40]]]
        self._expected_width_range = [round(num) for num in [x / 1.5 for x in [60, 1280]]]
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
        highlight_mask = color_filter(img, Config().colors["item_highlight"])[0]
        img[highlight_mask > 0] = (0, 0, 0)
        img = erode_to_black(img, black_thresh)
        return img

    def crop(self, inp_img: np.ndarray, padding_y: int = 5) -> list[ItemText]:
        start = time.time()
        cleaned_img = self.clean_img(inp_img)
        debug_str = f" | clean: {time.time() - start}"

        # Cluster item names
        start = time.time()
        item_clusters = []
        for key in self._item_colors:
            _, filtered_img = color_filter(cleaned_img, Config().colors[key])
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
                        _, extracted_img = color_filter(cropped_item, Config().colors[key2])
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
        if Config().advanced_options["ocr_during_pickit"]:
            cluster_images = [ key["clean_img"] for key in item_clusters ]
            results = self._ocr.image_to_text(cluster_images, model = "engd2r_inv_th_fast", psm = 7)
            for count, cluster in enumerate(item_clusters):
                setattr(cluster, "ocr_result", results[count])
        return item_clusters

    def crop_item_descr(self, inp_img: np.ndarray, inventory_side: str = "right", model = "engd2r_inv_th") -> ItemText:
        """
        Crops visible item description boxes / tooltips
        :inp_img: image from hover over item of interest.
        :inventory_side: enter either "left" for stash/vendor region or "right" for user inventory region
        :model: which ocr model to use
        returns cropped item tooltip box
        """
        result = ItemText()
        black_mask, _ = color_filter(inp_img, Config().colors["black"])
        contours = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        for cntr in contours:
            x, y, w, h = cv2.boundingRect(cntr)
            cropped_item = inp_img[y:y+h, x:x+w]
            avg = np.average(cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY))
            mostly_dark = True if 0 < avg < 25 else False
            contains_black = True if np.min(cropped_item) < 14 else False
            contains_white = True if np.max(cropped_item) > 250 else False
            contains_orange = False
            if not contains_white:
                #check for orange (like key of destruction, etc.)
                orange_mask, _ = color_filter(cropped_item, Config().colors["orange"])
                contains_orange = np.min(orange_mask) > 0
            expected_height = True if (self._box_expected_height_range[0] < h < self._box_expected_height_range[1]) else False
            expected_width = True if (self._box_expected_width_range[0] < w < self._box_expected_width_range[1]) else False
            box2 = Config().ui_roi[f"{inventory_side}_inventory"]
            overlaps_inventory = False if (x+w<box2[0] or box2[0]+box2[2]<x or y+h+50+10<box2[1] or box2[1]+box2[3]<y) else True # padded height because footer isn't included in contour
            if contains_black and (contains_white or contains_orange) and mostly_dark and expected_height and expected_width and overlaps_inventory:
                footer_height_max = (720 - (y + h)) if (y + h + 35) > 720 else 35
                found_footer = TemplateFinder().search(["TO_TOOLTIP"], inp_img, threshold=0.8, roi=[x, y+h, w, footer_height_max]).valid
                if found_footer:
                    ocr_result = self._ocr.image_to_text(cropped_item, psm=6, model=model)[0]
                    result.color = "black"
                    result.roi = [x, y, w, h]
                    result.data = cropped_item
                    result.ocr_result = ocr_result
                    result.valid = True
                    break
        return result

if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, grab
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")

    keyboard.add_hotkey('f12', lambda: os._exit(1))
    cropper = ItemCropper()

    while 1:
        img = grab().copy()
        res = cropper.crop_item_descr(img, model="engd2r_inv_th_fast")
        if res.valid:
            x, y, w, h = res.roi
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
            #Logger.debug(f"{res.ocr_result['text']}")

            Logger.debug(f"OCR ITEM DESCR: Mean conf: {res.ocr_result.mean_confidence}")
            for i, line in enumerate(list(filter(None, res.ocr_result.text.splitlines()))):
                Logger.debug(f"OCR LINE{i}: {line}")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            found_low_confidence = False
            for cnt, x in enumerate(res.ocr_result['word_confidences']):
                if x <= 88:
                    try:
                        Logger.debug(f"Low confidence word #{cnt}: {res.ocr_result['original_text'].split()[cnt]} -> {res.ocr_result['text'].split()[cnt]}, Conf: {x}")
                        found_low_confidence = True
                    except: pass


        cv2.imshow("res", img)
        cv2.waitKey(5000)
