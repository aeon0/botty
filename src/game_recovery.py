from screen import Screen
from template_finder import TemplateFinder
from config import Config
from death_manager import DeathManager
from ui import UiManager
import time
import keyboard
from ui_components.ingame_menu import SaveAndExit
from ui_components.loading import check_for_black_screen, Loading
from ui_components.main_menu import MainMenu

from utils.misc import set_d2r_always_on_top
from utils.custom_mouse import mouse


class GameRecovery:
    def __init__(self, death_manager: DeathManager, template_finder: TemplateFinder):
        self._death_manager = death_manager
        self._template_finder = template_finder
        self._ui_manager = UiManager(self._template_finder)

    def go_to_hero_selection(self):
        set_d2r_always_on_top()
        time.sleep(1)
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(Config().char["stand_still"])
        time.sleep(0.1)
        keyboard.release(Config().char["show_items"])
        start = time.time()
        while (time.time() - start) < 30:
            # make sure we are not on loading screen
            is_loading = check_for_black_screen()
            while is_loading:
                _, m = Loading.detect(self._template_finder)
                is_loading = m.valid
                time.sleep(0.5)
            # lets just see if you might already be at hero selection
            _, m = MainMenu.detect(self._template_finder)
            if m.valid:
                return True
            # would have been too easy, maybe we have died?
            if self._death_manager.handle_death_screen():
                time.sleep(1)
                continue
            # we must be ingame, but maybe we are at vendor or on stash, press esc and look for save and exit btn
            res, m = SaveAndExit.detect(self._template_finder)
            if m.valid:
                res.save_and_exit(False)
            else:
                keyboard.send("esc")
            time.sleep(1)
        return False


if __name__ == "__main__":
    from death_manager import DeathManager
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    template_finder = TemplateFinder()
    death_manager = DeathManager(template_finder)
    game_recovery = GameRecovery(death_manager, template_finder)
    print(game_recovery.go_to_hero_selection())
