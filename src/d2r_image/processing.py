import cv2
import time

import cv2
import numpy as np
from d2r_image.data_models import GroundItemList, HoveredItem, ItemQuality, ItemText
from d2r_image.bnip_helpers import parse_item

from d2r_image.processing_helpers import build_d2_items, crop_text_clusters, crop_item_tooltip, get_items_by_quality, consolidate_clusters, find_base_and_remove_items_without_a_base, set_set_and_unique_base_items
import numpy as np

from logger import Logger

import os

os.makedirs("./log/screenshots/info", exist_ok=True)

def get_ground_loot(image: np.ndarray, consolidate: bool = False) -> GroundItemList | None:
    crop_result = crop_text_clusters(image)
    items_by_quality = get_items_by_quality(crop_result)
    if consolidate:
        consolidate_clusters(items_by_quality)
    find_base_and_remove_items_without_a_base(items_by_quality)
    set_set_and_unique_base_items(items_by_quality)
    return build_d2_items(items_by_quality)

import traceback #TODO REMOV THIS

def get_hovered_item(image: np.ndarray, model = "hover-eng_inconsolata_inv_th_fast") -> tuple[HoveredItem, ItemText]:
    res, quality = crop_item_tooltip(image, model)
    parsed_item = None
    if res.ocr_result:
        try:
            parsed_item = parse_item(quality, res.ocr_result.text)
        except Exception as e:
            Logger.warning(f"\nparsed_item ERROR {e}\n {traceback.format_exc()}")
            # * Log the screenshot to log/screenshots/info directory.
            t = time.time()
            cv2.imwrite(f"log/screenshots/info/02_{t}.png", res.img)
            with open("log/screenshots/info/02_error_log.txt", "a") as f:
                f.write(f"""--------------------------------------------------------------------------------
[{t}]
{res.ocr_result.text}

{traceback.format_exc()}
--------------------------------------------------------------------------------""")
    return parsed_item, res


if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, stop_detecting_window, grab
    from d2r_image import processing as d2r_image
    from d2r_image.demo import draw_items_on_image_data, gen_truth_from_ground_loot
    from bnip.actions import should_keep, should_pickup
    import json
    from logger import Logger
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    Logger.info("Move to d2r window and press f11")
    keyboard.wait("f11")

    gen_truth = False

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
                        Logger.debug(item.as_dict())
                draw_items_on_image_data(all_loot.items, img)
                if gen_truth:
                    gen_truth_from_ground_loot(all_loot.items, img)
        cv2.imshow("res", img)
        cv2.waitKey(3000)