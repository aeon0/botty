from config import Config
import cv2
import numpy as np
import time
import parse
from utils.custom_mouse import mouse
from template_finder import TemplateFinder
from inventory import personal
from utils.misc import wait
from screen import grab
from dataclasses import dataclass
from logger import Logger
from item import ItemCropper

@dataclass
class Consumables:
    tp: int = 0
    id: int = 0
    rejuv: int = 0
    health: int = 0
    mana: int = 0
    key: int = 0
    def __getitem__(self, key):
        return super().__getattribute__(key)
    def __setitem__(self, key, value):
        setattr(self, key, value)

consumable_needs = Consumables()
item_consumables_map = {
    "misc_rejuvenation_potion": "rejuv",
    "misc_full_rejuvenation_potion": "rejuv",
    "misc_super_healing_potion": "health",
    "misc_greater_healing_potion": "health",
    "misc_super_mana_potion": "mana",
    "misc_greater_mana_potion": "mana",
    "misc_scroll_tp": "tp",
    "misc_scroll_id": "id",
    "misc_key": "key"
}
pot_cols = {
    "rejuv": Config().char["belt_rejuv_columns"],
    "health": Config().char["belt_hp_columns"],
    "mana": Config().char["belt_mp_columns"],
}

def get_needs(consumable_type: str = None):
    global consumable_needs
    if consumable_type:
        consumable = reduce_name(consumable_type)
        return consumable_needs[consumable]
    return consumable_needs

def set_needs(consumable_type: str, quantity: int):
    global consumable_needs
    consumable = reduce_name(consumable_type)
    consumable_needs[consumable] = quantity

def increment_need(consumable_type: str = None, quantity: int = 1):
    """
    Adjust the consumable_needs of a specific consumable
    :param consumable_type: Name of item in pickit or in consumable_map
    :param quantity: Increase the need (+int) or decrease the need (-int)
    """
    global consumable_needs
    consumable = reduce_name(consumable_type)
    consumable_needs[consumable] = max(0, consumable_needs[reduce_name(consumable)] + quantity)

def reduce_name(consumable_type: str):
    global item_consumables_map
    if consumable_type in item_consumables_map:
        consumable_type = item_consumables_map[consumable_type]
    elif consumable_type in item_consumables_map.values():
        pass
    else:
        Logger.warning(f"adjust_consumable_need: unknown item: {consumable_type}")
    return consumable_type

def get_remaining(item_name: str = None) -> int:
    global consumable_needs, pot_cols
    if item_name is None:
        Logger.error("get_remaining: param item_name is required")
        return -1
    if item_name.lower() in ["health", "mana", "rejuv"]:
        return pot_cols[item_name] * Config().char["belt_rows"] - consumable_needs[item_name]
    elif item_name.lower() in ['tp', 'id']:
        return 20 - consumable_needs[item_name]
    elif item_name.lower() == "key":
        return 12 - consumable_needs[item_name]
    else:
        Logger.error(f"get_remaining: error with item_name={item_name}")
        return -1

def should_buy(item_name: str = None, min_remaining: int = None, min_needed: int = None) -> bool:
    global consumable_needs
    if item_name is None:
        Logger.error("should_buy: param item_name is required")
        return False
    if min_needed:
        return consumable_needs[item_name] >= min_needed
    elif min_remaining:
        return get_remaining(item_name) <= min_remaining
    else:
        Logger.error("should_buy: need to specify min_remaining or min_needed")
    return False

def update_tome_key_needs(img: np.ndarray = None, item_type: str = "tp") -> bool:
    img = personal.open(img)
    if item_type.lower() in ["tp", "id"]:
        match = TemplateFinder().search(
            [f"{item_type.upper()}_TOME", f"{item_type.upper()}_TOME_RED"],
            img,
            roi = Config().ui_roi["restricted_inventory_area"],
            best_match = True,
            normalize_monitor=True
            )
        if match.valid:
            if match.name == f"{item_type.upper()}_TOME_RED":
                set_needs(item_type, 20)
                return True
            # else the tome exists and is not empty, continue
        else:
            Logger.debug(f"update_tome_key_needs: could not find {item_type}")
            return False
    elif item_type.lower() in ["key"]:
        match = TemplateFinder().search("INV_KEY", img, roi = Config().ui_roi["restricted_inventory_area"], normalize_monitor = True)
        if not match.valid:
            return False
    else:
        Logger.error(f"update_tome_key_needs failed, item_type: {item_type} not supported")
        return False
    mouse.move(*match.center, randomize=4, delay_factor=[0.5, 0.7])
    wait(0.2, 0.2)
    hovered_item = grab()
    # get the item description box
    item_box = ItemCropper().crop_item_descr(hovered_item, model="engd2r_inv_th_fast")
    if item_box.valid:
        try:
            result = parse.search("Quantity: {:d}", item_box.ocr_result.text).fixed[0]
            if item_type.lower() in ["tp", "id"]:
                set_needs(item_type, 20 - result)
            if item_type.lower() == "key":
                set_needs(item_type, 12 - result)
        except Exception as e:
            Logger.error(f"update_tome_key_needs: unable to parse quantity for {item_type}. Exception: {e}")
    else:
        Logger.error(f"update_tome_key_needs: Failed to capture item description box for {item_type}")
        if Config().general["info_screenshots"]:
            cv2.imwrite("./info_screenshots/failed_capture_item_description_box" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
        return False
    return True