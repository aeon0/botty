from item_finder import ItemFinder
import time
from utils import custom_mouse
import keyboard
import mouse
from config import Config
from char.i_char import IChar
from logger import Logger
from screen import Screen
from ui_manager import UiManager
import random


class PickIt:
    def __init__(self, screen: Screen, item_finder: ItemFinder, ui_manager: UiManager):
        self._item_finder = item_finder
        self._screen = screen
        self._ui_manager = ui_manager
        self._config = Config()

    def pick_up_items(self, char: IChar) -> bool:
        found_items = False
        keyboard.send(self._config.char["show_items"], do_press=True, do_release=False)
        time.sleep(1.0) # sleep needed here to give d2r time to display items on screen on keypress
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
                # TODO: 1920x1080 specific param
                if closest_item.dist < 400:
                    # no need to stash poitions and scrolls
                    if "potion" not in closest_item.name and "tp_scroll" != closest_item.name:
                        found_items = True
                    Logger.info(f"Picking up {closest_item.name}")
                    custom_mouse.move(x_m, y_m, duration=(random.random() * 0.01 + 0.02))
                    time.sleep(0.1)
                    mouse.click(button="left")
                    time.sleep(0.6)
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
