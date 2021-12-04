from death_manager import DeathManager
from screen import Screen
from template_finder import TemplateFinder
from config import Config
from death_manager import DeathManager
from ui_manager import UiManager
import keyboard
import time


class GameRecovery:
    def __init__(self, screen: Screen, death_manager: DeathManager):
        self._config = Config()
        self._screen = screen
        self._death_manager = death_manager
        self._template_finder = TemplateFinder(self._screen)
        self._ui_manager = UiManager(self._screen, self._template_finder)

    def go_to_hero_selection(self):
        time.sleep(1)
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(self._config.char["stand_still"])
        time.sleep(0.1)
        keyboard.release(self._config.char["show_items"])
        start = time.time()
        while (time.time() - start) < 60:
            # make sure we are not on loading screen
            is_loading = True
            while is_loading:
                is_loading = self._template_finder.search("LOADING", self._screen.grab()).valid
                time.sleep(0.5)
            # lets just see if you might already be at hero selection
            found = self._template_finder.search_and_wait("D2_LOGO_HS", time_out=1, take_ss=False, roi=self._config.ui_roi["hero_selection_logo"]).valid
            if found:
                return True
            # would have been too easy, maybe we have died?
            if self._death_manager.handle_death_screen():
                time.sleep(1)
                continue
            # we must be ingame, but maybe we are at vendor or on stash, press esc and look for save and exit btn
            time.sleep(1)
            templates = ["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"]
            template_match = self._template_finder.search(templates, self._screen.grab(), roi=self._config.ui_roi["save_and_exit"], threshold=0.85)
            if template_match.valid:
                self._ui_manager.save_and_exit()
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
    config = Config()
    screen = Screen(config.general["monitor"])
    death_manager = DeathManager(screen)
    game_recovery = GameRecovery(screen, death_manager)
    game_recovery.go_to_hero_selection()
