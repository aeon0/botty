from enum import Enum
import time
import keyboard
import cv2
from ui_manager import ScreenObjects, is_visible
from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import grab, convert_abs_to_monitor, convert_screen_to_monitor
from char import IChar
from inventory import consumables
from math import dist
from inventory import personal

from d2r_image import processing as d2r_image
from nip.transpile import should_pickup


class PickedUpResults(Enum):
    TeleportedTo   = 0
    PickedUp       = 1
    PickedUpFailed = 3
    InventoryFull  = 4

class PickIt:
    def __init__(self):
        self.cached_pickit_items = {} # * Cache the result of whether or not we should pick up the item. this should save some time

        self.last_action = None

        self.prev_item_pickup_attempt = ''
        self.fail_pickup_count = 0

        self.picked_up_items = []
        self.picked_up_item = False

        self.timeout = 30 # * The we should be in the pickit phase


    def move_cursor_to_hud(self): # * Avoid highlighting the items
        pos_m = convert_abs_to_monitor((0, (Config().ui_pos["screen_height"] / 2)))
        mouse.move(*pos_m, delay_factor=(0.1, 0.2))

    def grab_items(self) -> list:
        def sort_by_distance(item): # * sets some extra item data since we already looping
            item.ScreenX, item.ScreenY = (item.BoundingBox["x"] + item.BoundingBox["w"] // 2, item.BoundingBox["y"] + item.BoundingBox["h"] // 2)
            item.MonitorX, item.MonitorY = convert_screen_to_monitor((item.ScreenX, item.ScreenY))
            item.Dist = dist((item.ScreenX, item.ScreenY), (Config().ui_pos["screen_width"] / 2, Config().ui_pos["screen_height"] / 2))
            item.ID = f"{item.Name}_" + "_".join([str(value) for _, value in item.as_dict().items()])
            item.UID = f"{item.ID}_{item.ScreenX}_{item.ScreenY}"
            return item.Dist

        img = grab()
        items = d2r_image.get_ground_loot(img).items.copy()
        items.sort(key=sort_by_distance)
        return items

    def reset_state(self):
        """Reset the pickit state"""
        self.last_action = None
        self.prev_item_pickup_attempt = ''
        self.fail_pickup_count = 0
        self.picked_up_items = []
        self.picked_up_item = False

    def needs_pot420(self, item): # TODO implement proper [itemquality] filter
        needs = consumables.get_needs()
        if "Healing Potion" in item.Name:
            if needs["health"] == 0:
                return True
            else:
                consumables.increment_need("health", -1)
        elif "Mana Potion" in item.Name:
            if needs["mana"] == 0:
                return True
            else:
                consumables.increment_need("mana", -1)
        elif "Rejuvenation" in item.Name:
            if needs["rejuv"] == 0:
                return True
            else:
                consumables.increment_need("rejuv", -1)

    def yoink_item(self, item: object, char: IChar, force_tp=False):
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

    def pick_up_item(self, char: IChar, item: object) -> bool:
        if item.UID == self.prev_item_pickup_attempt:
            self.fail_pickup_count += 1
            time.sleep(0.2)
            if is_visible(ScreenObjects.Overburdened):
                Logger.warning("Inventory is full, creating creating next game.") #TODO Create logic that will go to the next game, sense you can possible have other runs the bot wants to do
                return PickedUpResults.InventoryFull
            elif self.fail_pickup_count >= 1:
                # * +1 because we failed at picking it up once already, we just can't detect the first failure (unless it is due to full inventory)
                if char.capabilities.can_teleport_natively or char.capabilities.can_teleport_with_charges:
                    Logger.warning(f"Failed to pick up '{item.Name}' {self.fail_pickup_count + 1} times in a row, trying to teleport")
                    return self.yoink_item(item, char, force_tp=True)
                else:
                    Logger.warning(f"Failed to pick up '{item.Name}' {self.fail_pickup_count + 1} times in a row, moving on to the next item.")
                    return PickedUpResults.PickedUpFailed # * Since the pickup failed, the pickit loop will move on to another item. (but wont forget this item exists)

        self.prev_item_pickup_attempt = item.UID
        return self.yoink_item(item, char)

    def pick_up_items(self, char: IChar) -> bool:
        """
            To be called everytime the bot wants to pick up items
            Pick up items that with a specified char
            :param char: The character used to pick up the item
            TODO :return: return a list of the items that were picked up
        """
        self.reset_state()
        #self.move_cursor_to_hud()
        keyboard.send(Config().char["show_items"])
        time.sleep(0.2)
        pickit_phase_start = time.time()

        items = self.grab_items()
        i = 0
        while i < len(items) and time.time() - pickit_phase_start < self.timeout:
            if self.picked_up_item: # * Picked up an item, get dropped item data again and reset the loop
                #self.move_cursor_to_hud()
                time.sleep(0.5)
                items = self.grab_items()
                i=0


            item = items[i]

            if self.needs_pot420(item): # * If item is potion & we need a potion of any kind, we should pick it up and move on
                self.picked_up_item = False
                i+=1
                continue


            pick_up_res=None
            if item.ID in self.cached_pickit_items: # * Check if we cached the result of whether or not we should pick up the item
                if self.cached_pickit_items[item.ID]:
                    pick_up_res = self.pick_up_item(char, item)
            else:
                item_dict = item.as_dict()
                if item.BaseItem["DisplayName"] == "Gold": # ? This seems pretty ghetto maybe somehow get this into d2r_image
                    if personal.get_inventory_gold_full():
                        Logger.debug("Gold is full, skip gold")
                        i+=1
                        continue
                    """
                    TODO FIX THE ERROR WITH GOLD PADDING OR SOMETHING! BELOW TRY EXCEPT STATEMENT WILL DO FOR NOW.
                        item_dict["NTIPAliasStat"] = {'14': int(item.Name.replace(" GOLD", ""))}
                            ValueError: invalid literal for int() with base 10: '12801 3897'

                    """
                    try:
                        item_dict["NTIPAliasStat"] = {'14': int(item.Name.replace(" GOLD", ""))}
                    except ValueError:
                        item_dict["NTIPAliasStat"] = {'14': 0}
                pickup, raw_expression = should_pickup(item_dict)
                self.cached_pickit_items[item.ID] = pickup
                if pickup:
                    pick_up_res = self.pick_up_item(char, item)
                    Logger.debug(f"Pick up expression: {raw_expression}")
            if pick_up_res == PickedUpResults.InventoryFull:
                break
            else:
                self.picked_up_item = pick_up_res == PickedUpResults.PickedUp
                self.picked_up_item and self.picked_up_items.append(item)
                self.picked_up_item and Logger.info(f"Attempting to pick up {item.Name}")
            self.last_action = pick_up_res
            i+=1

        keyboard.send(Config().char["show_items"])
        return len(self.picked_up_items) >= 1


if __name__ == "__main__":
    import os
    from config import Config
    from char.sorceress import LightSorc
    from char.hammerdin import Hammerdin
    from template_finder import TemplateFinder
    from pather import Pather
    import keyboard

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    pather = Pather()
    char = Hammerdin(Config().hammerdin, Config().char, pather)
    pickit = PickIt()
    print(pickit.pick_up_items(char))
