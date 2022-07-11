from ui_manager import detect_screen_object, select_screen_object_match, ScreenObjects
from logger import Logger
from utils import hotkeys
from utils.misc import wait
import keyboard

def handle_error() -> bool:
    Logger.warning("Server connection issue. waiting 20s")
    if (match := detect_screen_object(ScreenObjects.ServerError)).valid:
        select_screen_object_match(match)
        wait(1, 2)
        keyboard.send(hotkeys.d2r_keymap[hotkeys.HotkeyName.OpenMenu])
        wait(18, 22)