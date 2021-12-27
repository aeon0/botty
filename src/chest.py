import time
import os

from logger import Logger
from template_finder import TemplateFinder
from screen import Screen
from char import IChar
from config import Config

class Chest:
    def __init__(self, char: IChar, template_finder: TemplateFinder, template: str = None):
        config = Config()
        self._screen = Screen(config.general["monitor"])
        self._char = char
        self._template_finder = template_finder
        self._folder_name = "chests"
        self._min_score = 0.75
        # load all templates
        self._templates = []
        for filename in os.listdir(f'assets/{self._folder_name}/{template}'):
            filename = filename.lower()
            if filename.endswith('.png'):
                chest = filename[:-4].upper()
                self._templates.append(chest)
                
    def open_up_chest(
        self,  
        time_out: float = 8,
        threshold: float = 0.75
    ) -> float:
        score = 100
        templates = self._templates
        while len(templates) > 0:
            template_match = self._template_finder.search(templates, self._screen.grab(), threshold=threshold)
            score = template_match.score
            if template_match.name is None:
                break
            if score <= threshold:
                templates.remove(template_match.name)
                continue
            if template_match.valid:
                Logger.debug(f"Opening {template_match.name} ({template_match.score*100:.1f}% confidence)")
                x_m, y_m = self._screen.convert_screen_to_monitor(template_match.position)
                # act as picking up a potion to support telekinesis
                self._char.pick_up_item([x_m, y_m], 'potion')
                if not self._char.can_teleport():
                    time.sleep(0.2)
                locked_chest = self._template_finder.search("LOCKED", self._screen.grab(), threshold=threshold)
                if locked_chest.valid:
                    templates.remove(template_match.name)
                    Logger.debug("No more keys")
                    continue
                return template_match.score
        Logger.debug("No chests left")
        return 0
        
    def open_up_chests(
        self,
        time_out: float = 8,
        threshold: float = 0.75
    ) -> bool:
        # keep opening chests till no matches nearby
        score = 100
        while score >= threshold:
            score = self.open_up_chest(time_out, threshold)
        score = 100
        while score >= threshold:
            score = self.open_up_chest(time_out, threshold)
        return True
        
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
    chest.open_up_chests()