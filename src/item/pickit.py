from enum import Enum
import time
import keyboard
import cv2
from ui_manager import ScreenObjects, is_visible
from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import grab, convert_abs_to_monitor, convert_screen_to_monitor
from item import ItemFinder
from char import IChar
from inventory import consumables
from math import dist
from ui import view

from d2r_image import processing as d2r_image
from nip.transpile import should_pickup


class PickedUpResults(Enum):
    TeleportedTo   = 0
    PickedUp       = 1
    PickedUpFailed = 3
    InventoryFull  = 4

class PickIt:
    def __init__(self, item_finder: ItemFinder): # TODO remove ItemFinder from here
        self.cached_pickit_items = {} # * Cache the result of weather or not we should pick up the item. this should save some time
        
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
                view.save_and_exit()
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
        self.move_cursor_to_hud()
        keyboard.send(Config().char["show_items"])
        time.sleep(0.2)
        pickit_phase_start = time.time()

        items = self.grab_items()
        i = 0
        while i < len(items) and time.time() - pickit_phase_start < self.timeout:
            if self.picked_up_item: # * Picked up an item, get dropped item data again and reset the loop
                self.move_cursor_to_hud()
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
                    """
                    TODO FIX THE ERROR WITH GOLD PADDING OR SOMETHING! BELOW TRY EXCEPT STATEMENT WILL DO FOR NOW.
                        item_dict["NTIPAliasStat"] = {'14': int(item.Name.replace(" GOLD", ""))}
                            ValueError: invalid literal for int() with base 10: '12801 3897'

                    """
                    try: 
                        item_dict["NTIPAliasStat"] = {'14': int(item.Name.replace(" GOLD", ""))}
                    except ValueError:
                        item_dict["NTIPAliasStat"] = {'14': 0}
                pickup = should_pickup(item_dict)
                self.cached_pickit_items[item.ID] = pickup
                if pickup:
                    pick_up_res = self.pick_up_item(char, item, )             
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


# class PickIt:
#     def __init__(self, item_finder: ItemFinder):
#         self._item_finder = item_finder
#         self._last_closest_item: Item = None

#     def pick_up_items(self, char: IChar) -> bool:
#         """
#         Pick up all items with specified char
#         :param char: The character used to pick up the item
#         :return: Bool if any items were picked up or not. (Does not account for picking up scrolls and pots)
#         """
#         found_nothing = 0
#         found_items = False
#         keyboard.send(Config().char["show_items"])
#         time.sleep(1.0) # sleep needed here to give d2r time to display items on screen on keypress
#         #Creating a screenshot of the current loot
#         if Config().general["loot_screenshots"]:
#             img = grab()
#             cv2.imwrite("./loot_screenshots/info_debug_drop_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
#             Logger.debug("Took a screenshot of current loot")
#         start = prev_cast_start = time.time()
#         timeout = False
#         picked_up_items = []
#         skip_items = []
#         curr_item_to_pick: Item = None
#         same_item_timer = None
#         did_force_move = False
#         done_ocr=False

#         while not timeout:
#             if (time.time() - start) > 28:
#                 timeout = True
#                 Logger.warning("Got stuck during pickit, skipping it this time...")
#                 break
#             img = grab()
#             item_list = self._item_finder.search(img) # ! gets the items

#             if Config().advanced_options["ocr_during_pickit"] and not done_ocr:
#                 timestamp = time.strftime("%Y%m%d_%H%M%S")
#                 for cnt, item in enumerate(item_list):
#                     for cnt2, x in enumerate(item.ocr_result['word_confidences']):
#                         found_low_confidence = False
#                         if x <= 88:
#                             try:
#                                 Logger.debug(f"Low confidence word #{cnt2}: {item.ocr_result['original_text'].split()[cnt2]} -> {item.ocr_result['text'].split()[cnt2]}, Conf: {x}, save screenshot")
#                                 found_low_confidence = True
#                             except: pass
#                         if found_low_confidence and Config().general["loot_screenshots"]:
#                             cv2.imwrite(f"./loot_screenshots/ocr_drop_{timestamp}_{cnt}_o.png", item.ocr_result['original_img'])
#                             cv2.imwrite(f"./loot_screenshots/ocr_drop_{timestamp}_{cnt}_n.png", item.ocr_result['processed_img'])
#                             with open(f"./loot_screenshots/ocr_drop_{timestamp}_{cnt}_o.gt.txt", 'w') as f:
#                                 f.write(item.ocr_result['text'])
#                 done_ocr = True

#             # Check if we need to pick up any consumables
#             needs = consumables.get_needs()
#             if needs["mana"] <= 0:
#                 item_list = [x for x in item_list if "mana_potion" not in x.name]
#             if needs["health"] <= 0:
#                 item_list = [x for x in item_list if "healing_potion" not in x.name]
#             if needs["rejuv"] <= 0:
#                 item_list = [x for x in item_list if "rejuvenation_potion" not in x.name]
#             if needs["tp"] <= 0:
#                 item_list = [x for x in item_list if "scroll_tp" not in x.name]
#             if needs["id"] <= 0:
#                 item_list = [x for x in item_list if "scroll_id" not in x.name]
#             if needs["key"] <= 0:
#                 item_list = [x for x in item_list if "misc_key" != x.name]

#             # filter out gold less than desired quantity
#             if (min_gold := Config().char['min_gold_to_pick']):
#                 for item in item_list[:]:
#                     if "misc_gold" == item.name:
#                         try:
#                             ocr_gold = int(parse.search("{:d} GOLD", item.ocr_result.text).fixed[0])
#                         except:
#                             ocr_gold = 0
#                         if ocr_gold < min_gold:
#                             item_list.remove(item)

#             if len(item_list) == 0:
#                 # if twice no item was found, break
#                 found_nothing += 1
#                 if found_nothing > 1:
#                     break
#                 else:
#                     # Maybe we need to move cursor to another position to avoid highlighting items
#                     pos_m = convert_abs_to_monitor((0, 0))
#                     mouse.move(*pos_m, randomize=[90, 160])
#                     time.sleep(0.2)
#             else:
#                 found_nothing = 0
#                 item_list.sort(key=itemgetter('dist'))
#                 closest_item = next((obj for obj in item_list if not any(map(obj["name"].__contains__, ["misc_gold", "misc_scroll", "misc_key"]))), None)
#                 if not closest_item:
#                     closest_item = item_list[0]

#                 # check if we trying to pickup the same item for a longer period of time
#                 force_move = False
#                 if curr_item_to_pick is not None:
#                     is_same_item = (curr_item_to_pick.name == closest_item.name and \
#                         abs(curr_item_to_pick.dist - closest_item.dist) < 20)
#                     if same_item_timer is None or not is_same_item:
#                         same_item_timer = time.time()
#                         did_force_move = False
#                     elif time.time() - same_item_timer > 1 and not did_force_move:
#                         force_move = True
#                         did_force_move = True
#                     elif time.time() - same_item_timer > 3:
#                         # backlist this item type for this pickit round
#                         Logger.warning(f"Could not pick up: {closest_item.name}. Continue with other items")
#                         skip_items.append(closest_item.name)
#                 curr_item_to_pick = closest_item

#                 # To avoid endless teleport or telekinesis loop
#                 force_pick_up = char.capabilities.can_teleport_natively and \
#                                 self._last_closest_item is not None and \
#                                 self._last_closest_item.name == closest_item.name and \
#                                 abs(self._last_closest_item.dist - closest_item.dist) < 20

#                 x_m, y_m = convert_screen_to_monitor(closest_item.center)
#                 if not force_move and (closest_item.dist < Config().ui_pos["item_dist"] or force_pick_up):
#                     self._last_closest_item = None
#                     # no need to stash potions, scrolls, gold, keys
#                     if ("potion" not in closest_item.name) and ("misc_scroll" not in closest_item.name) and ("misc_key" != closest_item.name):
#                         if ("misc_gold" != closest_item.name):
#                             found_items = True
#                             if Config().advanced_options["ocr_during_pickit"]:
#                                 for item in item_list:
#                                     Logger.debug(f"OCR DROP: Name: {item.ocr_result['text']}, Conf: {item.ocr_result['word_confidences']}")
#                     else:
#                         # note: key pickup appears to be random between 1 and 5, but set here at minimum of 1 for now
#                         consumables.increment_need(closest_item.name, -1)

#                     prev_cast_start = char.pick_up_item((x_m, y_m), item_name=closest_item.name, prev_cast_start=prev_cast_start)
#                     if not char.capabilities.can_teleport_natively:
#                         time.sleep(0.2)

#                     if is_visible(ScreenObjects.Overburdened):
#                         found_items = True
#                         Logger.warning("Inventory full, terminating pickit!")
#                         # TODO: Could think about sth like: Go back to town, stash, come back picking up stuff
#                         break
#                     else:
#                         # send log to discord
#                         if found_items and closest_item.name not in picked_up_items:
#                             Logger.info(f"Picking up: {closest_item.name} ({closest_item.score*100:.1f}% confidence)")
#                         picked_up_items.append(closest_item.name)
#                 else:
#                     char.pre_move()
#                     char.move((x_m, y_m), force_move=True)
#                     if not char.capabilities.can_teleport_natively:
#                         time.sleep(0.3)
#                     time.sleep(0.1)
#                     # save closeset item for next time to check potential endless loops of not reaching it or of telekinsis/teleport
#                     self._last_closest_item = closest_item

#         keyboard.send(Config().char["show_items"])
#         return found_items

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
    item_finder = ItemFinder()
    char = Hammerdin(Config().hammerdin, Config().char, pather)
    pickit = PickIt(item_finder)
    print(pickit.pick_up_items(char))
