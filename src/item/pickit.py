import time
import keyboard
import cv2

from utils.custom_mouse import mouse
from config import Config
from logger import Logger
from screen import Screen
from item import ItemFinder, Item
from ui import UiManager
from ui import BeltManager
from char import IChar

class PickIt:
    def __init__(self, screen: Screen, item_finder: ItemFinder, ui_manager: UiManager, belt_manager: BeltManager):
        self._item_finder = item_finder
        self._screen = screen
        self._belt_manager = belt_manager
        self._ui_manager = ui_manager
        self._config = Config()
        self._last_closest_item: Item = None

    def pick_up_items(self, char: IChar, is_at_trav: bool = False) -> bool:
        """
        Pick up all items with specified char
        :param char: The character used to pick up the item
        :param is_at_trav: Dirty hack to reduce gold pickup only to trav area, should be removed once we can determine the amount of gold reliably
        :return: Bool if any items were picked up or not. (Does not account for picking up scrolls and pots)
        """
        found_nothing = 0
        found_items = False
        keyboard.send(self._config.char["show_items"])
        time.sleep(1.0) # sleep needed here to give d2r time to display items on screen on keypress
        #Creating a screenshot of the current loot
        start = prev_cast_start = time.time()
        time_out = False
        picked_up_items = []
        skip_items = []
        curr_item_to_pick: Item = None
        same_item_timer = None
        did_force_move = False
        done_ocr=False

        while not time_out:
            if (time.time() - start) > 28:
                time_out = True
                Logger.warning("Got stuck during pickit, skipping it this time...")
                break
            img = self._screen.grab()
            item_list = self._item_finder.search(img)

            # Check if we need to pick up certain pots more pots
            need_pots = self._belt_manager.get_pot_needs()
            if need_pots["mana"] <= 0:
                item_list = [x for x in item_list if "mana_potion" not in x.name]
            if need_pots["health"] <= 0:
                item_list = [x for x in item_list if "healing_potion" not in x.name]
            if need_pots["rejuv"] <= 0:
                item_list = [x for x in item_list if "rejuvenation_potion" not in x.name]

            # TODO: Hacky solution for trav only gold pickup, hope we can soon read gold ammount and filter by that...
            if self._config.char["gold_trav_only"] and not is_at_trav:
                item_list = [x for x in item_list if "misc_gold" not in x.name]

            if len(item_list) == 0:
                # if twice no item was found, break
                found_nothing += 1
                if found_nothing > 1:
                    break
                else:
                    # Maybe we need to move cursor to another position to avoid highlighting items
                    pos_m = self._screen.convert_abs_to_monitor((0, 0))
                    mouse.move(*pos_m, randomize=[90, 160])
                    time.sleep(0.2)
            else:
                if done_ocr == False:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    # timestamp = str(round(time.time_ns() // 1_000_000 ))
                    for item in item_list:
                        Logger.debug(f"OCR DROP: Name: {item.ocr_result['text']}, Conf: {item.ocr_result['word_confidences']}")
                        if self._config.general["loot_screenshots"]:
                            cv2.imwrite("./loot_screenshots/ocr_drop_" + timestamp + "_o.png", item.ocr_result['original_img'])
                            cv2.imwrite("./loot_screenshots/ocr_drop_" + timestamp + "_n.png", item.ocr_result['processed_img'])
                    done_ocr = True

                found_nothing = 0
                closest_item = item_list[0]
                for item in item_list[1:]:
                    if closest_item.dist > item.dist:
                        closest_item = item

                # check if we trying to pickup the same item for a longer period of time
                force_move = False
                if curr_item_to_pick is not None:
                    is_same_item = (curr_item_to_pick.name == closest_item.name and \
                        abs(curr_item_to_pick.dist - closest_item.dist) < 20)
                    if same_item_timer is None or not is_same_item:
                        same_item_timer = time.time()
                        did_force_move = False
                    elif time.time() - same_item_timer > 1 and not did_force_move:
                        force_move = True
                        did_force_move = True
                    elif time.time() - same_item_timer > 3:
                        # backlist this item type for this pickit round
                        Logger.warning(f"Could not pick up: {closest_item.name}. Continue with other items")
                        skip_items.append(closest_item.name)
                curr_item_to_pick = closest_item

                # To avoid endless teleport or telekinesis loop
                force_pick_up = char.can_teleport() and \
                                self._last_closest_item is not None and \
                                self._last_closest_item.name == closest_item.name and \
                                abs(self._last_closest_item.dist - closest_item.dist) < 20

                x_m, y_m = self._screen.convert_screen_to_monitor(closest_item.center)
                if not force_move and (closest_item.dist < self._config.ui_pos["item_dist"] or force_pick_up):
                    self._last_closest_item = None
                    # if potion is picked up, record it in the belt manager
                    if "potion" in closest_item.name:
                        self._belt_manager.picked_up_pot(closest_item.name)
                    # no need to stash potions, scrolls, or gold
                    if "potion" not in closest_item.name and "tp_scroll" != closest_item.name and "misc_gold" not in closest_item.name:
                        found_items = True

                    prev_cast_start = char.pick_up_item((x_m, y_m), item_name=closest_item.name, prev_cast_start=prev_cast_start)
                    if not char.can_teleport():
                        time.sleep(0.2)

                    if self._ui_manager.is_overburdened():
                        found_items = True
                        Logger.warning("Inventory full, skipping pickit!")
                        # TODO: Could think about sth like: Go back to town, stash, come back picking up stuff
                        break
                    else:
                        # send log to discord
                        if found_items and closest_item.name not in picked_up_items:
                            Logger.info(f"Picking up: {closest_item.name} ({closest_item.score*100:.1f}% confidence)")
                        picked_up_items.append(closest_item.name)
                else:
                    char.pre_move()
                    char.move((x_m, y_m), force_move=True)
                    if not char.can_teleport():
                        time.sleep(0.3)
                    time.sleep(0.1)
                    # save closeset item for next time to check potential endless loops of not reaching it or of telekinsis/teleport
                    self._last_closest_item = closest_item

        keyboard.send(self._config.char["show_items"])
        return found_items


if __name__ == "__main__":
    import os
    from config import Config
    from char.sorceress import LightSorc
    from char.hammerdin import Hammerdin
    from ui import UiManager
    from template_finder import TemplateFinder
    from pather import Pather
    import keyboard

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, t_finder)
    belt_manager = BeltManager(screen, t_finder)
    belt_manager._pot_needs = {"rejuv": 0, "health": 2, "mana": 2}
    pather = Pather(screen, t_finder)
    item_finder = ItemFinder()
    char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather)
    pickit = PickIt(screen, item_finder, ui_manager, belt_manager)
    print(pickit.pick_up_items(char))
