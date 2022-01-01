import time
import os

from logger import Logger
from template_finder import TemplateFinder
from screen import Screen
from char import IChar
from config import Config


class Chest:
    def __init__(self, char: IChar, template_finder: TemplateFinder, template: str = None):
        self._config = Config()
        self._screen = Screen(self._config.general["monitor"])
        self._char = char
        self._template_finder = template_finder
        self._folder_name = "chests"
        # load all templates
        self._templates = []
        for filename in os.listdir(f'assets/{self._folder_name}/{template}'):
            filename = filename.lower()
            if filename.endswith('.png'):
                chest = filename[:-4].upper()
                self._templates.append(chest)

    def open_up_chests(self, time_out: float = 8.0, threshold: float = 0.79) -> bool:
        Logger.debug("Open chests")
        templates = self._templates
        found_chest = True
        start = time.time()
        while time.time() - start < time_out:
            template_match = self._template_finder.search(templates, self._screen.grab(), roi=self._config.ui_roi["reduce_to_center"], threshold=threshold, use_grayscale=True, best_match=True)
            if not template_match.valid:
                break
            found_chest = True
            Logger.debug(f"Opening {template_match.name} ({template_match.score*100:.1f}% confidence)")
            x_m, y_m = self._screen.convert_screen_to_monitor(template_match.position)
            # TODO: Act as picking up a potion to support telekinesis. This workaround needs a proper solution.
            self._char.pick_up_item([x_m, y_m], 'potion')
            time.sleep(0.3)
            locked_chest = self._template_finder.search("LOCKED", self._screen.grab(), threshold=0.85)
            if locked_chest.valid:
                templates.remove(template_match.name)
                Logger.debug("No more keys, removing locked chest template")
                continue
        Logger.debug("No chests left")
        return found_chest


if __name__ == "__main__":
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")
    from char.hammerdin import Hammerdin
    from screen import Screen
    from pather import Pather
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    pather = Pather(screen, template_finder)
    ui_manager = UiManager(screen, template_finder)
    char = Hammerdin(config.hammerdin, config.char, screen, template_finder, ui_manager, pather)
    chest = Chest(char, template_finder, 'arcane')
    chest.open_up_chests(threshold=0.8)
