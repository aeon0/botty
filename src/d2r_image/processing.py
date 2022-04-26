import copy
from typing import Union
import cv2
import numpy as np
from d2r_image.data_models import GroundItemList, HoveredItem, ItemQuality, ItemText
from d2r_image.nip_helpers import parse_item
from d2r_image.ocr import image_to_text
from utils.misc import color_filter, cut_roi
from d2r_image.processing_data import BOX_EXPECTED_HEIGHT_RANGE, BOX_EXPECTED_WIDTH_RANGE
from d2r_image.processing_helpers import build_d2_items, contains_color, crop_text_clusters, get_items_by_quality, consolidate_clusters, find_base_and_remove_items_without_a_base, set_set_and_unique_base_items
import numpy as np

from logger import Logger
from template_finder import TemplateFinder
from config import Config

def get_ground_loot(image: np.ndarray, consolidate: bool = False) -> Union[GroundItemList, None]:
    crop_result = crop_text_clusters(image)
    items_by_quality = get_items_by_quality(crop_result)
    if consolidate:
        consolidate_clusters(items_by_quality)
    find_base_and_remove_items_without_a_base(items_by_quality)
    set_set_and_unique_base_items(items_by_quality)
    return build_d2_items(items_by_quality)

import traceback #TODO REMOV THIS

def get_hovered_item(image: np.ndarray, inventory_side: str = "right", model = "engd2r_inv_th_fast") -> tuple[HoveredItem, ItemText]:
    """
    Crops visible item description boxes / tooltips
    :inp_img: image from hover over item of interest.
    :inventory_side: enter either "left" for stash/vendor region or "right" for user inventory region
    :model: which ocr model to use
    """
    res = ItemText()
    quality = None
    black_mask = color_filter(image, Config().colors["black"])[0]
    contours = cv2.findContours(
        black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        cropped_item = image[y:y+h, x:x+w]
        avg = np.average(cv2.cvtColor(cropped_item, cv2.COLOR_BGR2GRAY))
        mostly_dark = 0 < avg < 20
        contains_black = np.min(cropped_item) < 14
        contains_white = np.max(cropped_item) > 250
        contains_orange = False
        if not contains_white:
            # check for orange (like key of destruction, etc.)
            orange_mask, _ = color_filter(cropped_item, Config().colors["orange"])
            contains_orange = np.min(orange_mask) > 0
        expected_height = BOX_EXPECTED_HEIGHT_RANGE[0] < h < BOX_EXPECTED_HEIGHT_RANGE[1]
        expected_width = BOX_EXPECTED_WIDTH_RANGE[0] < w < BOX_EXPECTED_WIDTH_RANGE[1]
        box2 = Config().ui_roi[f"{inventory_side}_inventory"]
        # padded height because footer isn't included in contour
        overlaps_inventory = False if (
            x+w < box2[0] or box2[0]+box2[2] < x or y+h+50+10 < box2[1] or box2[1]+box2[3] < y) else True
        if contains_black and (contains_white or contains_orange) and mostly_dark and expected_height and expected_width and overlaps_inventory:
            footer_height_max = (720 - (y + h)) if (y + h + 35) > 720 else 35
            found_footer = TemplateFinder().search(["TO_TOOLTIP"], image, threshold=0.8, roi=[x, y+h, w, footer_height_max]).valid
            if found_footer:
                first_row = cut_roi(copy.deepcopy(cropped_item), (0, 0, w, 26))
                if contains_color(first_row, "green"):
                    quality = ItemQuality.Set.value
                elif contains_color(first_row, "gold"):
                    quality = ItemQuality.Unique.value
                elif contains_color(first_row, "yellow"):
                    quality = ItemQuality.Rare.value
                elif contains_color(first_row, "blue"):
                    quality = ItemQuality.Magic.value
                elif contains_color(first_row, "orange"):
                    quality = ItemQuality.Crafted.value
                elif contains_color(first_row, "white"):
                    quality = ItemQuality.Normal.value
                elif contains_color(first_row, "gray"):
                    quality = ItemQuality.Gray.value
                else:
                    quality = ItemQuality.Normal.value
                Logger.error("HITTTT")
                res.ocr_result = image_to_text(cropped_item, psm=6, model=model)[0]
                res.roi = [x, y, w, h]
                res.img = cropped_item
                break

    parsed_item = None
    if res.ocr_result:
        if "SUPERIOR" in res.ocr_result.text[:10]:
            quality = ItemQuality.Superior.value
        try:
            parsed_item = parse_item(quality, res.ocr_result.text)
        except Exception as e:
            Logger.warning(f"\nparsed_item ERROR {e}\n {traceback.format_exc()}")
    return parsed_item, res


if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, stop_detecting_window, grab
    from d2r_image import processing as d2r_image
    from d2r_image.demo import draw_items_on_image_data
    from nip.transpile import should_keep, should_pickup
    import json
    from logger import Logger
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    Logger.info("Move to d2r window and press f11")
    keyboard.wait("f11")

    while 1:
        img = grab().copy()
        # look for item tooltip
        item, res = d2r_image.get_hovered_item(img)
        if res.roi is not None:
            Logger.debug(f"Keep {item.Quality} {item.BaseItem['DisplayName']}?: {should_keep(item.as_dict())}")
            x, y, w, h = res.roi
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
            Logger.debug(f"{json.dumps(item.as_dict(), indent=4)}\n")
        else:
            # look for dropped items
            all_loot = d2r_image.get_ground_loot(img)
            if all_loot.items and len(all_loot.items) > 0:
                for item in all_loot.items:
                    if item:
                        Logger.debug(f"Pick {item.Quality} {item.BaseItem['DisplayName']}?: {should_pickup(item.as_dict())}")
                        Logger.debug(item)
                draw_items_on_image_data(all_loot.items, img)
        cv2.imshow("res", img)
        cv2.waitKey(3000)