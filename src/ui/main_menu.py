import time
import keyboard
from config import Config
from utils.misc import wait
from logger import Logger
from ui import error_screens
from ui_manager import detect_screen_object, is_visible, select_screen_object_match, ScreenObjects

MAIN_MENU_MARKERS = ["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"]

def _play_active(match) -> bool:
    return match.name == "PLAY_BTN"

def start_game() -> bool:
    """
    Starting a game. Will wait and retry on server connection issue.
    :return: Bool if action was successful
    """
    Logger.debug("Wait for Play button")
    start = time.time()
    difficulty=Config().general["difficulty"].lower()
    difficulty_key="r" if difficulty == "normal" else "n" if difficulty == "nightmare" else "h"
    while True:
        if (m := detect_screen_object(ScreenObjects.PlayBtn)).valid:
            if _play_active(m):
                # found active play button
                Logger.debug(f"Found Play Btn, select and press key: {difficulty_key}")
                select_screen_object_match(m)
                keyboard.press(difficulty_key)
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
    start = time.time()
    while True:
        #check for loading screen
        if is_visible(ScreenObjects.Loading):
            Logger.debug("Found loading screen / creating game")
            keyboard.release(difficulty_key)
            break
        else:
            wait(0.2)
        # check for server issue
        if is_visible(ScreenObjects.ServerError):
            error_screens.handle_error()
            keyboard.release(difficulty_key)
            return start_game()

        if time.time() - start > 15:
            Logger.error(f"Could not find {difficulty}_BTN or LOADING, start over")
            keyboard.release(difficulty_key)
            return start_game()
    return True
