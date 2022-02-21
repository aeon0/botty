import time
import cv2
from screen import grab
from config import Config
import keyboard
from utils.custom_mouse import mouse
import numpy as np
from logger import Logger
from template_finder import TemplateFinder
from utils.misc import wait
from ui.ui_manager import wait_for_screen_object, detect_screen_object, select_screen_object_match, ScreenObjects
from screen import convert_screen_to_monitor

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

def check_save_exit(img: np.ndarray = None):
    img = grab() if img is None else img
    return detect_screen_object(ScreenObjects.SaveAndExit, img)

def open_save_exit():
    keyboard.send("esc")
    wait(0.1)
    return check_save_exit()

def click_save_exit(match):
    select_screen_object_match(match, delay_factor=(0.1, 0.3))
    wait(0.1)
    return not check_save_exit()

def save_and_exit(img: np.ndarray = None) -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    # see if save/exit already on screen
    exit_button = check_save_exit(img)
    if not exit_button.valid:
        # if not on screen, open
        if not (exit_button := open_save_exit()):
            return False
    # if clicked and the save/exit screen is no longer visible
    if click_save_exit(exit_button):
        return True
    # try one more time
    else:
        wait(0.6, 1)
        if click_save_exit(exit_button):
            return True
    wait(1, 2)
    return not check_save_exit()

def pickup_corpse():
    Logger.info("Pickup corpse")
    move_to_corpse()
    wait(0.4,0.6)
    mouse.click(button="left")
    #TODO: handle "Overburdened"

def move_to_corpse():
    pos = convert_screen_to_monitor((Config().ui_pos["corpse_x"], Config().ui_pos["corpse_y"]))
    mouse.move(*pos)
