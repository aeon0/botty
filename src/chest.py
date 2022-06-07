import time
import os

from logger import Logger
import template_finder
from screen import grab
from char import IChar
from config import Config
from utils.custom_mouse import mouse
from utils.misc import wait
from inventory import consumables


class Chest:
    def __init__(self, char: IChar, template: str = None):
        self._char = char
        self._folder_name = "chests"
        # load all templates
        self._templates = []
        for filename in os.listdir(f'assets/{self._folder_name}/{template}'):
            filename = filename.lower()
            if filename.endswith('.png'):
                chest = filename[:-4].upper()
                self._templates.append(chest)

    def open_up_chests(self, timeout: float = 8.0, threshold: float = 0.73) -> bool:
        Logger.debug("Open chests")
        templates = self._templates
        found_chest = True
        start = time.time()
        while time.time() - start < timeout:
            template_match = template_finder.search(templates, grab(), roi=Config().ui_roi["reduce_to_center"], threshold=threshold, use_grayscale=True, best_match=True)
            # search for at least 1.5 second, if no chest found, break
            if not template_match.valid:
                if time.time() - start > 1.5:
                    break
            else:
                found_chest = True
                # move mouse and check for label
                mouse.move(*template_match.center_monitor, delay_factor=[0.4, 0.6])
                wait(0.13, 0.16)
                chest_label_img = grab()
                chest_label = template_finder.search("CHEST_LABEL", chest_label_img, threshold=0.85)
                is_locked = template_finder.search("LOCKED", chest_label_img, threshold=0.85).valid
                if chest_label.valid:
                    if is_locked:
                        consumables.increment_need("key", 1)
                    Logger.debug(f"Opening {template_match.name} ({template_match.score*100:.1f}% confidence)")
                    # TODO: Act as picking up a potion to support telekinesis. This workaround needs a proper solution.
                    self._char.pick_up_item(template_match.center_monitor, 'potion')
                    wait(0.13, 0.16)
                    if template_finder.search("LOCKED", grab(), threshold=0.85).valid:
                        templates.remove(template_match.name)
                        Logger.debug("No more keys, removing locked chest template")
                        continue
                else:
                    templates.remove(template_match.name)
        Logger.debug("No chests left")
        return found_chest


if __name__ == "__main__":
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")
    from char.hammerdin import Hammerdin
    from pather import Pather
    from config import Config
    pather = Pather()
    char = Hammerdin(Config().hammerdin, Config().char, pather)
    chest = Chest(char, 'arcane')
    chest.open_up_chests(threshold=0.8)
