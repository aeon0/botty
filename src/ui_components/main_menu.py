# f: has_char_template_saved(self):
# f: save_char_template(self):
# f: save_char_online_status(self):
# f: select_online_tab(self, region: tuple[int, int, int, int] = None, center: tuple[int, int] = None):
# f: select_char(self):
# DONE - f:  start_game(self) -> bool:
# - btn_play (online vs. offline)
# - characters
# - tabs (online vs offline)
import keyboard
import time

from config import Config
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger

from ui_components import ScreenObject, Locator
from ui_components.difficulty import Normal, Nightmare, Hell
from ui_components.loading import Loading
from ui_components.error_screens import ServerError

@Locator(ref=["PLAY_BTN", "PLAY_BTN_GRAY"], roi="play_btn", best_match=True)
class PlayBtn(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)

@Locator(ref=["MAIN_MENU_TOP_LEFT", "MAIN_MENU_TOP_LEFT_DARK"])
class MainMenu(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)
        self._screen = screen
        self._template_finder = template_finder
        self._config = Config()

    def start_game(self) -> bool:
        """
        Starting a game. Will wait and retry on server connection issue.
        :return: Bool if action was successful
        """
        Logger.debug("Wait for Play button")
        start = time.time()
        while True:
            res, m = PlayBtn.detect(self._screen, self._template_finder)
            if m.valid:
                if m.name == "PLAY_BTN":
                    # found active play button
                    Logger.debug(f"Found Play Btn")
                    res.select_self()
                    break
                # else found inactive play button, continue loop
            else:
                # did not find either active or inactive play button
                Logger.error("start_game: No play button found, not on main menu screen")
                return False
            wait(1,2)
            if time.time() - start > 90:
                Logger.error("start_game: Active play button never appeared")
                return False

        difficulty=self._config.general["difficulty"].upper()
        if difficulty == "NORMAL": Difficulty = Normal
        elif difficulty == "NIGHTMARE": Difficulty = Nightmare
        elif difficulty == "HELL": Difficulty = Hell
        else: Logger.error(f"Invalid difficulty: {self._config.general['difficulty']}")
        start = time.time()
        while True:
            #look for difficulty select
            res, m = Difficulty.detect(self._screen, self._template_finder)
            if m.valid:
                res.select_self()
                break
            #check for loading screen
            _, m = Loading.detect(self._screen, self._template_finder)
            if m.valid:
                Logger.debug("Found loading screen rather than difficulty select, normal difficulty")
                break
            else:
                wait(1,2)
            # check for server issue
            res, m = ServerError.detect(self._screen, self._template_finder)
            if m.valid:
                Logger.warning("Server connection issue. waiting 20s")
                res.select_self()
                wait(1, 2)
                keyboard.send("esc")
                wait(18, 22)
                return self.start_game()

            if time.time() - start > 15:
                Logger.error(f"Could not find {difficulty}_BTN or LOADING, start over")
                return self.start_game()
        return True
