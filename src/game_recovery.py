from screen import Screen
from template_finder import TemplateFinder
from config import Config
from death_manager import DeathManager
from ui import UiManager
import time
import keyboard
from ui_components.ingame_menu import save_and_exit

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
            is_loading = True
            while is_loading:
                is_loading = self._template_finder.search("LOADING", Screen().grab()).valid
                time.sleep(0.5)
            # lets just see if you might already be at hero selection
            found = self._template_finder.search(["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"], Screen().grab(), roi=Config().ui_roi["main_menu_top_left"]).valid
            if found:
                return True
            # would have been too easy, maybe we have died?
            if self._death_manager.handle_death_screen():
                time.sleep(1)
                continue
            # we must be ingame, but maybe we are at vendor or on stash, press esc and look for save and exit btn
            template_match = self._template_finder.search(["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"], Screen().grab(), roi=Config().ui_roi["save_and_exit"], threshold=0.85)
            if template_match.valid:
                save_and_exit(self._template_finder, False)
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
