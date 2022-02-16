# DONE - f:  start_game(self) -> bool:

import time

from config import Config
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
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

    def play_active(self) -> bool:
        return self.match.name == "PLAY_BTN"

@Locator(ref=["MAIN_MENU_TOP_LEFT", "MAIN_MENU_TOP_LEFT_DARK"], roi="main_menu_top_left")
class MainMenu(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)
        self._screen = screen
        self._template_finder = template_finder

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
                if res.play_active:
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

        difficulty=Config.general["difficulty"].upper()
        # TODO: need to revise logic here
        if difficulty == "NORMAL": Difficulty = Normal
        elif difficulty == "NIGHTMARE": Difficulty = Nightmare
        elif difficulty == "HELL": Difficulty = Hell
        else: Logger.error(f"Invalid difficulty: {Config.general['difficulty']}")
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
                Logger.debug("Found loading screen / creating game screen rather than difficulty select, normal difficulty")
                break
            else:
                wait(1,2)
            # check for server issue
            res, m = ServerError.detect(self._screen, self._template_finder)
            if m.valid:
                res.handle_error()
                return self.start_game(self)

            if time.time() - start > 15:
                Logger.error(f"Could not find {difficulty}_BTN or LOADING, start over")
                return self.start_game(self)
        return True
