import time
from config import Config
from utils.misc import wait
from logger import Logger
from ui import error_screens
from ui_manager import detect_screen_object, select_screen_object_match, ScreenObjects

def start_game() -> bool:
    """
    Starting a game. Will wait and retry on server connection issue.
    :return: Bool if action was successful
    """
    Logger.debug("Wait for Play button")
    start = time.time()
    while True:
        m = detect_screen_object(ScreenObjects.PlayBtn)
        if m.valid:
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
    if difficulty == "NORMAL": Difficulty = ScreenObjects.Normal
    elif difficulty == "NIGHTMARE": Difficulty = ScreenObjects.Nightmare
    elif difficulty == "HELL": Difficulty = ScreenObjects.Hell
    else: Logger.error(f"Invalid difficulty: {Config().general['difficulty']}")
    start = time.time()
    while True:
        #look for difficulty select
        m = detect_screen_object(Difficulty)
        if m.valid:
            select_screen_object_match(m)
            break
        #check for loading screen
        m = detect_screen_object(ScreenObjects.Loading)
        if m.valid:
            Logger.debug("Found loading screen / creating game screen rather than difficulty select, normal difficulty")
            break
        else:
            wait(1,2)
        # check for server issue
        m = detect_screen_object(ScreenObjects.ServerError)
        if m.valid:
            error_screens.handle_error()
            return start_game()

        if time.time() - start > 15:
            Logger.error(f"Could not find {difficulty}_BTN or LOADING, start over")
            return start_game()
    return True

def play_active(match) -> bool:
    return match.name == "PLAY_BTN"