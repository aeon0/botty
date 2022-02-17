# - server issues?
from ui.ui_manager import UiManager, detect_screen_object, select_screen_object_match, SCREEN_OBJECTS
from logger import Logger
from utils.misc import wait
import keyboard

def handle_error() -> bool:
    Logger.warning("Server connection issue. waiting 20s")
    match = detect_screen_object(SCREEN_OBJECTS['SERVER_ISSUES'])
    if match.valid:
        select_screen_object_match(match)
        wait(1, 2)
        keyboard.send("esc")
        wait(18, 22)