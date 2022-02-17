import time
import keyboard
from utils.misc import wait
from ui.ui_manager import UiManager, detect_screen_object, select_screen_object_match, SCREEN_OBJECTS

def save_and_exit(does_chicken: bool = False) -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    start = time.time()
    keyboard.send("esc")
    while (time.time() - start) < 15:
        match = detect_screen_object(SCREEN_OBJECTS['SaveAndExit'])
        if match.valid:
            wait(0.05)
            select_screen_object_match(match)
            wait(0.05)
            select_screen_object_match(match)
            wait(0.1, 0.5)
            return True
    return False