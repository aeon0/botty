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
import threading
from utils.misc import send_discord


class PickIt:
    def __init__(self, screen: Screen, item_finder: ItemFinder, ui_manager: UiManager):
        self._item_finder = item_finder
        self._screen = screen
        self._ui_manager = ui_manager
        self._config = Config()

    def pick_up_items(self, char: IChar) -> bool:
        """
        Pick up all items with specified char
        :param char: The character used to pick up the item
        :return: Bool if any items were picked up or not. (Does not account for picking up scrolls and pots)
        """
        found_items = False
        keyboard.send(self._config.char["show_items"], do_press=True, do_release=False)
        time.sleep(1.0) # sleep needed here to give d2r time to display items on screen on keypress
        #Creating a screenshot of the current loot
        if self._config.general["loot_screenshots"]:
            img = self._screen.grab()
            cv2.imwrite("./loot_screenshots/info_debug_drop_" + str(time.time()) + ".png", img)
            Logger.debug("Took a screenshot of current loot")
        start = time.time()
        time_out = False
        while not time_out:
            if (time.time() - start) > 20:
                time_out = True
                Logger.warning("Got stuck during pickit, skipping it this time...")
            img = self._screen.grab()
            item_list = self._item_finder.search(img)
            if not self._ui_manager.check_free_belt_spots():
                # no free slots in belt, do not pick up health or mana potions
                item_list = [x for x in item_list if "potion" not in x.name]
            if len(item_list) == 0:
                break
            else:
                closest_item = item_list[0]
                for item in item_list[1:]:
                    if closest_item.dist > item.dist:
                        closest_item = item
                x_m, y_m = self._screen.convert_screen_to_monitor(closest_item.center)
                if closest_item.dist < self._config.ui_pos["item_dist"]:
                    # no need to stash potions, scrolls, or gold 
                    if (("potion" not in closest_item.name) and ("tp_scroll" != closest_item.name) and ("misc_gold" not in closest_item.name)):
                        found_items = True
                    Logger.info(f"Picking up {closest_item.name}")
                    mouse.move(x_m, y_m)
                    time.sleep(0.1)
                    mouse.click(button="left")
                    time.sleep(0.5)
                    
                    if found_items:
                        try:
                            runeLvl = int(closest_item.name.split('_')[1])
                        except:
                            runeLvl=0

                    if found_items and ((runeLvl >= 23) or ("tt_" in closest_item.name)):
                        
                        if self._config.general["send_drops_to_discord"]:
                            send_discord_thread = threading.Thread(target=send_discord, args=(closest_item.name,))
                            send_discord_thread.daemon = True
                            send_discord_thread.start()
    
                        if self._config.general["custom_discord_hook"] != "":
                            send_discord_thread = threading.Thread(target=send_discord, args=(closest_item.name, self._config.general["custom_discord_hook"]))
                            send_discord_thread.daemon = True
                            send_discord_thread.start()

                    if self._ui_manager.is_overburdened():
                        Logger.warning("Inventory full, skipping pickit!")
                        # TODO: should go back to town and stash stuff then go back to picking up more stuff
                        #       but sm states are not fine enough for such a routine right now...
                        break
                else:
                    char.move((x_m, y_m))
                    time.sleep(0.1)
        keyboard.send(self._config.char["show_items"], do_press=False, do_release=True)
        return found_items


if __name__ == "__main__":
    import os
    from config import Config
    from char.sorceress import Sorceress
    from ui_manager import UiManager
    from template_finder import TemplateFinder
    import keyboard

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, t_finder)
    item_finder = ItemFinder()
    char = Sorceress(config.sorceress, config.char, screen, t_finder, item_finder, ui_manager)
    pickit = PickIt(screen, item_finder, ui_manager)
    pickit.pick_up_items(char)
