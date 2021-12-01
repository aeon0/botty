from belt_manager import BeltManager
from ui_manager import UiManager
from item_finder import ItemFinder
import time
from utils.custom_mouse import mouse
import keyboard
import cv2
from config import Config
from char.i_char import IChar
from logger import Logger
from screen import Screen
from ui_manager import UiManager
from game_stats import GameStats


class PickIt:
    def __init__(self, screen: Screen, item_finder: ItemFinder, ui_manager: UiManager, belt_manager: BeltManager, game_stats: GameStats = None):
        self._item_finder = item_finder
        self._screen = screen
        self._belt_manager = belt_manager
        self._ui_manager = ui_manager
        self._game_stats = game_stats
        self._config = Config()

    def pick_up_items(self, char: IChar) -> bool:
        """
        Pick up all items with specified char
        :param char: The character used to pick up the item
        :return: Bool if any items were picked up or not. (Does not account for picking up scrolls and pots)
        """
        found_nothing = 0
        found_items = False
        keyboard.send(self._config.char["show_items"])
        time.sleep(1.0) # sleep needed here to give d2r time to display items on screen on keypress
        #Creating a screenshot of the current loot
        if self._config.general["loot_screenshots"]:
            img = self._screen.grab()
            cv2.imwrite("./loot_screenshots/info_debug_drop_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
            Logger.debug("Took a screenshot of current loot")
        start = prev_cast_start = time.time()
        time_out = False
        picked_up_items = []
        while not time_out:
            if (time.time() - start) > 24:
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

            if len(item_list) == 0:
                # if two times no item was found, break
                found_nothing += 1
                if found_nothing > 1:
                    break
            else:
                found_nothing = 0
                closest_item = item_list[0]
                for item in item_list[1:]:
                    if closest_item.dist > item.dist:
                        closest_item = item
                x_m, y_m = self._screen.convert_screen_to_monitor(closest_item.center)
                if closest_item.dist < self._config.ui_pos["item_dist"]:
                    # if potion is picked up, record it in the belt manager
                    if "potion" in closest_item.name:
                        self._belt_manager.picked_up_pot(closest_item.name)
                    # no need to stash potions, scrolls, or gold
                    if "potion" not in closest_item.name and "tp_scroll" != closest_item.name and "misc_gold" not in closest_item.name:
                        found_items = True

                    Logger.info(f"Picking up: {closest_item.name} ({closest_item.score*100:.1f}% confidence)")
                    prev_cast_start = char.pick_up_item((x_m, y_m), item_name=closest_item.name, prev_cast_start=prev_cast_start)

                    if self._ui_manager.is_overburdened():
                        Logger.warning("Inventory full, skipping pickit!")
                        # TODO: should go back to town and stash stuff then go back to picking up more stuff
                        #       but sm states are not fine enough for such a routine right now...
                        break
                    else:
                        # send log to discord
                        if found_items and closest_item.name not in picked_up_items:
                            self._game_stats.log_item_pickup(closest_item.name, self._config.items[closest_item.name] == 2)
                        picked_up_items.append(closest_item.name)
                else:
                    char.pre_move()
                    char.move((x_m, y_m))
                    time.sleep(0.1)
        keyboard.send(self._config.char["show_items"])
        return found_items


if __name__ == "__main__":
    import os
    from config import Config
    from char.sorceress import Sorceress
    from ui_manager import UiManager
    from template_finder import TemplateFinder
    from pather import Pather
    from game_stats import GameStats
    import keyboard

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    config = Config()
    game_states = GameStats()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, t_finder)
    belt_manager = BeltManager(screen, t_finder)
    belt_manager._pot_needs = {"rejuv": 0, "health": 2, "mana": 2}
    pather = Pather(screen, t_finder)
    item_finder = ItemFinder()
    char = Sorceress(config.sorceress, config.char, screen, t_finder, ui_manager, pather)
    pickit = PickIt(screen, item_finder, ui_manager, belt_manager, game_states)
    pickit.pick_up_items(char)
