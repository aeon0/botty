import time, keyboard
from config import Config
from utils.misc import wait
from logger import Logger
from ui import error_screens
from ui_manager import detect_screen_object, is_visible, select_screen_object_match, ScreenObjects

def start_game() -> bool:
    """
    Starting a game. Will wait and retry on server connection issue.
    :return: Bool if action was successful
    """
    Logger.debug("Wait for Play button")
    start = time.time()
    while True:
        if (m := detect_screen_object(ScreenObjects.PlayBtn)).valid:
            if play_active(m):
                # found active play button
                Logger.debug(f"Found Play Btn")
                select_screen_object_match(m)
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
    difficulty=Config().general["difficulty"].upper()
    # TODO: need to revise logic here
    if difficulty == "NORMAL": Difficulty = 'r'
    elif difficulty == "NIGHTMARE": Difficulty = 'n'
    elif difficulty == "HELL": Difficulty = 'h'
    else: Logger.error(f"Invalid difficulty: {Config().general['difficulty']}")
    start = time.time()
    keyboard.press(Difficulty)
    while True:
        #check for loading screen
        if is_visible(ScreenObjects.Loading):
            keyboard.release(Difficulty)
            Logger.debug("Found loading screen")
            break
        else:
            wait(1,2)
        # check for server issue
        if is_visible(ScreenObjects.ServerError):
            keyboard.release(Difficulty)
            error_screens.handle_error()
            return start_game()

        if time.time() - start > 15:
            keyboard.release(Difficulty)
            Logger.error(f"Could not find {difficulty}_BTN or LOADING, start over")
            return start_game()
    return True

def play_active(match) -> bool:
    return match.name == "PLAY_BTN"
