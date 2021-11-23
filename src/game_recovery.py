from death_manager import DeathManager
from screen import Screen
from template_finder import TemplateFinder
from config import Config
from death_manager import DeathManager
from ui_manager import UiManager
import keyboard
import time


class GameRecovery:
    def __init__(self):
        self._config = Config()
        self._screen = Screen(self._config.general["monitor"])
        self._template_finder = TemplateFinder(self._screen)
        self._death_manager = DeathManager(self._screen, self._template_finder)
        self._ui_manager = UiManager(self._screen, self._template_finder)

    def go_to_hero_selection(self):
        # make sure we are not on loading screen
        is_loading = True
        while is_loading:
            is_loading = self._template_finder.search("LOADING", self._screen.grab())[0]
            time.sleep(0.5)
        # first lets just see if you might already be at hero selection
        found, _ = self._template_finder.search_and_wait("D2_LOGO_HS", time_out=1, take_ss=False, roi=self._config.ui_roi["hero_selection_logo"])
        if found:
            return True
        # would have been too easy, maybe we have died?
        died = self._death_manager.handle_death_screen()
        if died:
            return self._ui_manager.save_and_exit()
        # we must be ingame, but maybe we are at vendor or on stash, press "esc" until we find a save and exit btn (max 5 times)
        for _ in range(5):
            keyboard.send("esc")
            time.sleep(1)
            templates = ["SAVE_AND_EXIT_NO_HIGHLIGHT","SAVE_AND_EXIT_HIGHLIGHT"]
            found, _ = self._template_finder.search_and_wait(templates, roi=self._config.ui_roi["save_and_exit"], time_out=1.5, take_ss=False)
            if found:
                keyboard.send("esc")
                time.sleep(1)
                return self._ui_manager.save_and_exit()
        return False


if __name__ == "__main__":
    game_recovery = GameRecovery()
    game_recovery.go_to_hero_selection()
