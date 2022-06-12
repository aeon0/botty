from enum import Enum
from math import dist
from numpy import ndarray
from typing import Tuple
import cv2
import json
import keyboard
import os
import time
import uuid

from char import IChar
from config import Config
from d2r_image import processing as d2r_image
from d2r_image.data_models import HoveredItem, EnhancedJSONEncoder
from inventory import personal
from item import consumables
from item.consumables import ITEM_CONSUMABLES_MAP
from logger import Logger
from nip.actions import should_pickup
from nip.NTIPAliasType import NTIPAliasType as NTIP_TYPES
from screen import grab, convert_abs_to_monitor, convert_screen_to_monitor
from ui_manager import ScreenObjects, is_visible
from utils.custom_mouse import mouse


class PickedUpResults(Enum):
    TeleportedTo   = 0
    PickedUp       = 1
    PickedUpFailed = 3
    InventoryFull  = 4

class PickIt:
    def __init__(self):
        self._cached_pickit_items = {} # * Cache the result of whether or not we should pick up the item. this should save some time
        self._last_action = None
        self._prev_item_pickup_attempt = ''
        self._fail_pickup_count = 0
        self._picked_up_items = []
        self._picked_up_item = False
        self.timeout = 30


    def _log_data(self, items: list, img, counter, _uuid):
        if Config().general["pickit_screenshots"]:
            cv2.imwrite(f"log/screenshots/pickit/{_uuid }_{counter}.png", img)
            with open(f"log/screenshots/pickit/{_uuid }_{counter}.json", 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, sort_keys=False, cls=EnhancedJSONEncoder, indent=2)

    def _move_cursor_to_hud(self): # * Avoid highlighting the items
        pos_m = convert_abs_to_monitor((0, (Config().ui_pos["screen_height"] / 2)))
        mouse.move(*pos_m, delay_factor=(0.1, 0.2))

    def _locate_items(self) -> Tuple[list, ndarray]:
        def _sort_by_distance(item): # * sets some extra item data since we already looping
            item.ScreenX, item.ScreenY = (item.BoundingBox["x"] + item.BoundingBox["w"] // 2, item.BoundingBox["y"] + item.BoundingBox["h"] // 2)
            item.MonitorX, item.MonitorY = convert_screen_to_monitor((item.ScreenX, item.ScreenY))
            item.Dist = dist((item.ScreenX, item.ScreenY), (Config().ui_pos["screen_width"] / 2, Config().ui_pos["screen_height"] / 2))
            item.ID = f"{item.Name}_" + "_".join([str(value) for _, value in item.as_dict().items()])
            item.UID = f"{item.ID}_{item.ScreenX}_{item.ScreenY}"
            return item.Dist

        img = grab()
        start = time.time()
        items = d2r_image.get_ground_loot(img).items.copy()
        Logger.debug(f"Read {len(items)} ground items in {round(time.time() - start, 3)} seconds")

        items.sort(key=_sort_by_distance)
        return items, img

    def _reset_state(self):
        """Reset the pickit state"""
        self._last_action = None
        self._prev_item_pickup_attempt = ''
        self._fail_pickup_count = 0
        self._picked_up_items = []
        self._picked_up_item = False


    def _ignore_consumable(self, item: HoveredItem):
        # ignore item if it's a consumable AND there's no need for that consumable

        for consumable_type in ITEM_CONSUMABLES_MAP.keys():
            if not item.Name.lower() == consumable_type:
                continue
            need_exists = consumables.get_needs(consumable_type) > 0
            if need_exists:
                consumables.increment_need(consumable_type, -1)
                return False
            else:
                self._picked_up_item = False
                return True

        return False

    def _yoink_item(self, item: HoveredItem, char: IChar, force_tp=False):
        if item.Dist > Config().ui_pos["item_dist"] or force_tp:
            char.pre_move()
            char.move((item.MonitorX, item.MonitorY), force_move=force_tp)
            time.sleep(0.1)
            # * Move mouse to the middle of the screen and click on the item you teleported to
            pos_m = convert_abs_to_monitor((0,-45))
            mouse.move(*pos_m)
            mouse.click(button="left")
        else:
            char.pick_up_item((item.MonitorX, item.MonitorY), item_name=item.Name, prev_cast_start=0.1)
        return PickedUpResults.PickedUp

    def _pick_up_item(self, char: IChar, item: HoveredItem) -> bool:
        if item.UID == self._prev_item_pickup_attempt:
            self._fail_pickup_count += 1
            time.sleep(0.2)
            if is_visible(ScreenObjects.Overburdened):
                if item.BaseItem["DisplayName"] == "Gold":
                    personal.set_inventory_gold_full(True)
                    Logger.warning("Detected gold full")
                else:
                    Logger.warning("Inventory is full") #TODO Create logic to handle inventory full
                return PickedUpResults.InventoryFull
            elif self._fail_pickup_count >= 1:
                # * +1 because we failed at picking it up once already, we just can't detect the first failure (unless it is due to full inventory)
                if char.capabilities.can_teleport_natively or char.capabilities.can_teleport_with_charges:
                    Logger.warning(f"Failed to pick up '{item.Name}' {self._fail_pickup_count + 1} times in a row, trying to teleport")
                    return self._yoink_item(item, char, force_tp=True)
                else:
                    Logger.warning(f"Failed to pick up '{item.Name}' {self._fail_pickup_count + 1} times in a row, moving on to the next item.")
                    return PickedUpResults.PickedUpFailed # * Since the pickup failed, the pickit loop will move on to another item. (but wont forget this item exists)

        self._prev_item_pickup_attempt = item.UID
        return self._yoink_item(item, char)

    def pick_up_items(self, char: IChar) -> bool:
        """
            To be called everytime the bot wants to pick up items
            Pick up items that with a specified char
            :param char: The character used to pick up the item
            TODO :return: return a list of the items that were picked up
        """
        self._reset_state()
        #self._move_cursor_to_hud()
        keyboard.send(Config().char["show_items"])
        time.sleep(0.2)
        pickit_phase_start = time.time()

        items, img = self._locate_items()
        counter = 1
        _uuid = uuid.uuid4()
        self._log_data(items, img, counter, _uuid)
        i = 0
        while i < len(items) and time.time() - pickit_phase_start < self.timeout:
            if self._picked_up_item: # * Picked up an item, get dropped item data again and reset the loop
                #self._move_cursor_to_hud()
                time.sleep(0.5)
                items, img = self._locate_items()
                counter += 1
                self._log_data(items, img, counter, _uuid)
                i=0

            item = items[i]

            pick_up_res=None
            if item.ID in self._cached_pickit_items: # * Check if we cached the result of whether or not we should pick up the item
                if self._cached_pickit_items[item.ID]:
                    if self._ignore_consumable(item):
                        i+=1
                        continue
                    else:
                        pick_up_res = self._pick_up_item(char, item)
            else:
                item_dict = item.as_dict()
                if personal.get_inventory_gold_full() and item.BaseItem["DisplayName"] == "Gold":
                    Logger.debug("Gold is full, skip gold")
                    i+=1
                    continue
                pickup, raw_expression = should_pickup(item_dict)
                self._cached_pickit_items[item.ID] = pickup
                if pickup:
                    if self._ignore_consumable(item):
                        i+=1
                        continue
                    else:
                        pick_up_res = self._pick_up_item(char, item)
                        Logger.debug(f"Pick up expression: {raw_expression}")
            if pick_up_res == PickedUpResults.InventoryFull:
                break
            else:
                self._picked_up_item = pick_up_res == PickedUpResults.PickedUp
                self._picked_up_item and self._picked_up_items.append(item)
                self._picked_up_item and Logger.info(f"Attempting to pick up {item.Name}")
            self._last_action = pick_up_res
            i+=1

        keyboard.send(Config().char["show_items"])
        return len(self._picked_up_items) >= 1


if __name__ == "__main__":
    import os
    from config import Config
    from char.sorceress import LightSorc
    from char.paladin import Hammerdin
    from pather import Pather
    import keyboard

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    pather = Pather()
    char = Hammerdin(Config().hammerdin, Config().char, pather)
    pickit = PickIt()
    print(pickit.pick_up_items(char))
