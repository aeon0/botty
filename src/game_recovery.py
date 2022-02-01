from screen import Screen
from template_finder import TemplateFinder
from config import Config
from death_manager import DeathManager
from ui import UiManager
import time
import keyboard

from utils.misc import set_d2r_always_on_top
from utils.custom_mouse import mouse


class GameRecovery:
    def __init__(self, screen: Screen, death_manager: DeathManager, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._death_manager = death_manager
        self._template_finder = template_finder
        self._ui_manager = UiManager(self._screen, self._template_finder)

    def go_to_hero_selection(self):
        set_d2r_always_on_top()
        time.sleep(1)
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(self._config.char["stand_still"])
        time.sleep(0.1)
        keyboard.release(self._config.char["show_items"])
        start = time.time()
        while (time.time() - start) < 30:
            # make sure we are not on loading screen
            is_loading = True
            while is_loading:
                is_loading = self._template_finder.search("LOADING", self._screen.grab()).valid
                time.sleep(0.5)
            # lets just see if you might already be at hero selection
            found = self._template_finder.search(["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"], self._screen.grab(), roi=self._config.ui_roi["main_menu_top_left"]).valid
            if found:
                offline_tab = self._template_finder.search(["OFFLINE_TAB","OFFLINE_TAB_DARK"], self._screen.grab(), roi=self._config.ui_roi["offline_tab"], threshold=0.8, best_match = True)
                if offline_tab.valid:
                    if offline_tab.name == "OFFLINE_TAB_DARK":
                        #We need to press escape before clicking the tab
                        keyboard.send("esc")
                        time.sleep(0.2)
                    # Right now it selects the tab to the left of offline
                    offline_width = self._config.ui_pos["offline_width"]
                    tab = (offline_tab.position[0] - offline_width , offline_tab.position[1])
                    x, y = self._screen.convert_screen_to_monitor(tab)
                    mouse.move(x, y, randomize=8)
                    time.sleep(0.5)
                    mouse.click(button="left")
                return True
            # would have been too easy, maybe we have died?
            if self._death_manager.handle_death_screen():
                time.sleep(1)
                continue
            # we must be ingame, but maybe we are at vendor or on stash, press esc and look for save and exit btn
            template_match = self._template_finder.search(["SAVE_AND_EXIT_NO_HIGHLIGHT", "SAVE_AND_EXIT_HIGHLIGHT"], self._screen.grab(), roi=self._config.ui_roi["save_and_exit"], threshold=0.85)
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
    screen = Screen()
    death_manager = DeathManager(screen)
    game_recovery = GameRecovery(screen, death_manager)
    game_recovery.go_to_hero_selection()
