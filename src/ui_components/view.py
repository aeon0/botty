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

def save_and_exit() -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    start=time.time()
    while not (exit_button := detect_screen_object(ScreenObjects.SaveAndExit)).valid:
        keyboard.send("esc")
        wait(0.1)
        if time.time() - start > 5:
            return False
    select_screen_object_match(exit_button, delay_factor=(0.1, 0.3))
    return True

def pickup_corpse():
    Logger.info("Pickup corpse")
    move_to_corpse()
    wait(0.4,0.6)
    mouse.click(button="left")
    #TODO: handle "Overburdened"

def move_to_corpse():
    pos = convert_screen_to_monitor((Config().ui_pos["corpse_x"], Config().ui_pos["corpse_y"]))
    mouse.move(*pos)
