# f: repair_needed(self) -> bool:
# f: wait_for_town_spawn
# f: pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
# - repair_needed
# - ammo_low
# - chat_box (might be same roi as is_overburdened? diablo walks? item pickup?)
# - enemy_name / enemy_health
# - enemy_info / enemy_resistances
# - death message
# - death button
# - red portal
# - blue portal
import time
import cv2
from screen import grab
from config import Config
import keyboard
import mouse
from logger import Logger
from template_finder import TemplateFinder
from utils.misc import wait
from ui.ui_manager import wait_for_screen_object, detect_screen_object, select_screen_object_match, ScreenObjects


def enable_no_pickup() -> bool:
    """
    Checks the best match between enabled and disabled an retrys if already set.
    :return: Returns True if we succesfully set the nopickup option
    """
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.write('/nopickup',delay=.20)
    keyboard.send('enter')
    wait(0.1, 0.25)
    item_pickup_text = wait_for_screen_object(ScreenObjects.ItemPickupText, time_out=3)
    if not item_pickup_text.valid:
        return False
    if item_pickup_text.name == "ITEM_PICKUP_DISABLED":
        return True
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.send('up')
    wait(0.1, 0.25)
    keyboard.send('enter')
    wait(0.1, 0.25)
    return True

def save_and_exit(does_chicken: bool = False) -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    start = time.time()
    keyboard.send("esc")
    while (time.time() - start) < 15:
        match = detect_screen_object(ScreenObjects.SaveAndExit)
        if match.valid:
            wait(0.05)
            select_screen_object_match(match)
            wait(0.05)
            select_screen_object_match(match)
            wait(0.1, 0.5)
            return True
    return False