from ui_manager import detect_screen_object, select_screen_object_match, ScreenObjects
from logger import Logger
from utils.misc import wait
import keyboard

def handle_error() -> bool:
    Logger.warning("Server connection issue. waiting 20s")
    if (match := detect_screen_object(ScreenObjects.ServerError)).valid:
        select_screen_object_match(match)
        wait(1, 2)
        keyboard.send("esc")
        wait(18, 22)