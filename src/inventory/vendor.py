import keyboard
from template_finder import TemplateFinder
from config import Config
import numpy as np
from utils.misc import cut_roi, wait, color_filter
from screen import convert_screen_to_monitor, grab
from logger import Logger
from utils.custom_mouse import mouse
from ui_manager import detect_screen_object, wait_for_screen_object, ScreenObjects
from inventory import personal, stash, common
from ocr import Ocr
import cv2
import time

def repair() -> bool:
    """
    Repair and fills up TP buy selling tome and buying. Vendor inventory needs to be open!
    :return: Bool if success
    """
    repair_btn = wait_for_screen_object(ScreenObjects.RepairBtn, time_out=4)
    if not repair_btn.valid:
        return False
    mouse.move(*repair_btn.center, randomize=12, delay_factor=[1.0, 1.5])
    wait(0.1, 0.15)
    mouse.click(button="left")
    wait(0.1, 0.15)
    x, y = convert_screen_to_monitor((Config().ui_pos["vendor_misc_x"], Config().ui_pos["vendor_misc_y"]))
    mouse.move(x, y, randomize=[20, 6], delay_factor=[1.0, 1.5])
    wait(0.1, 0.15)
    mouse.click(button="left")
    # another click to dismiss popup message in case you have not enough gold to repair, preventing tome not being bought back
    wait(0.1, 0.15)
    mouse.click(button="left")
    wait(0.5, 0.6)
    return True

def gamble():
    if (refresh_btn := TemplateFinder().search_and_wait("REFRESH", threshold=0.79, time_out=4, normalize_monitor=True)).valid:
        #Gambling window is open. Starting to spent some coins
        while stash.get_gold_full():
            img=grab()
            for item in Config().char["gamble_items"]:
                # while desired gamble item is not on screen, refresh
                while not (desired_item := TemplateFinder().search (item.upper(), grab(), roi=Config().ui_roi["left_inventory"], normalize_monitor=True)).valid:
                    mouse.move(*refresh_btn.center, randomize=12, delay_factor=[1.0, 1.5])
                    wait(0.1, 0.15)
                    mouse.click(button="left")
                    wait(0.1, 0.15)
                # desired item found
                mouse.move(*desired_item.center, randomize=12, delay_factor=[1.0, 1.5])
                wait(0.1, 0.15)
                mouse.click(button="right")
                wait(0.1, 0.15)
                # if the last digit or two is no longer visible in stash, assume lower stash gold and set last iteration
                img=grab()
                gold_cutout = cut_roi(img, Config().ui_roi["vendor_gold_digits"])
                gold_mask, _ = color_filter(gold_cutout, Config().colors["gold_numbers"])
                if not np.sum(gold_mask) > 0:
                    stash.set_gold_full(False)
                # if there is a desired item, end function and go to stash
                if personal.inventory_has_items(img):
                    # specifically in gambling scenario, all items returned from inspect_items, which sells/drops unwanted items, are to be kept
                    items = personal.inspect_items(img, close_window=False)
                    if items:
                        Logger.debug("Found desired item, go to stash")
                        common.close()
                        return items
        Logger.debug(f"Finish gambling")
        return None
    else:
        Logger.warning("gamble: gamble vendor window not detected")
        return False

def buy_item(template_name: str, quantity: int = 1, img: np.ndarray = None, shift_click: bool = False) -> bool:
    """
    Buy desired item from vendors. Vendor inventory needs to be open!
    :param template_name: Name of template for desired item to buy; e.g., SUPER_MANA_POTION
    :param quantity: How many of the item to buy
    :param img: Precaptured image of opened vendor inventory
    :param shift_click: whether to hold shift and right click to buy full stack
    returns bool for success/failure
    """
    if img is None:
        img = grab()
    if (desired_item := TemplateFinder().search(template_name, inp_img=img, roi=Config().ui_roi["left_inventory"], normalize_monitor=True)).valid:
        mouse.move(*desired_item.center, randomize=8, delay_factor=[1.0, 1.5])
        if shift_click:
            keyboard.send('shift', do_release=False)
            wait(0.5, 0.8)
            mouse.click(button="right")
            wait(0.4, 0.6)
            keyboard.send('shift', do_release=True)
            return True
        if quantity:
            for _ in range(quantity):
                mouse.click(button="right")
                wait(0.9, 1.1)
            return True
        else:
            Logger.error("buy_item: Quantity not specified")
            return False
    Logger.error(f"buy_item: Desired item {template_name} not found")
    return False