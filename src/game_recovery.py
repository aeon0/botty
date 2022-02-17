from screen import grab
from template_finder import TemplateFinder
from config import Config
from death_manager import DeathManager
from ui import UiManager
import time
import keyboard
from ui.ui_manager import detect_screen_object
from ui.screen_objects import ScreenObjects
from ui_components.ingame_menu import save_and_exit
from ui_components.loading import check_for_black_screen
from ui_components.view import handle_death_screen
from utils.misc import set_d2r_always_on_top

class GameRecovery:
    def __init__(self, death_manager: DeathManager):
        self._death_manager = death_manager
        self._ui_manager = UiManager()

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
                is_loading = TemplateFinder().search("LOADING", grab()).valid
                time.sleep(0.5)
            # lets just see if you might already be at hero selection
            found = TemplateFinder().search(["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"], grab(), roi=Config().ui_roi["main_menu_top_left"]).valid
            if found:
                return True
            # would have been too easy, maybe we have died?
            if handle_death_screen():
                time.sleep(1)
                continue
            # we must be ingame, but maybe we are at vendor or on stash, press esc and look for save and exit btn
            match = detect_screen_object(ScreenObjects.SaveAndExit)
            if match.valid:
                save_and_exit(False)
            time.sleep(1)
        return False


if __name__ == "__main__":
    from death_manager import DeathManager
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    death_manager = DeathManager()
    game_recovery = GameRecovery(death_manager)
    print(game_recovery.go_to_hero_selection())
