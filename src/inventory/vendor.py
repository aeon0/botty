from math import floor
import keyboard
from template_finder import TemplateFinder
from config import Config
import numpy as np
from utils.misc import wait
from screen import grab
from logger import Logger
from utils.custom_mouse import mouse
from ui_manager import is_visible, select_screen_object_match, wait_until_visible, ScreenObjects
from inventory import personal, common, stash

gamble_count = 0
gamble_status = False

def get_gamble_count() -> int:
    global gamble_count
    return gamble_count

def set_gamble_count(count: int = 0):
    global gamble_count
    gamble_count = count

def get_gamble_status() -> bool:
    global gamble_status
    return gamble_status

def set_gamble_status (bool: bool):
    global gamble_status, gold_in_stash
    gamble_status = bool
    if gamble_status:
        set_gamble_count(0)
        Config().turn_off_goldpickup()
    else:
        Config().turn_on_goldpickup()

def repair() -> bool:
    """
    Repair and fills up TP buy selling tome and buying. Vendor inventory needs to be open!
    :return: Bool if success
    """
    if not (repair_btn := wait_until_visible(ScreenObjects.RepairBtn, timeout=4)).valid:
        return False
    select_screen_object_match(repair_btn)
    if wait_until_visible(ScreenObjects.NotEnoughGold, 1).valid:
        Logger.warning("Couldn't repair--out of gold. Continue.")
        keyboard.send("esc")
        return False
    return True

def gamble():
    if (refresh_btn := TemplateFinder().search_and_wait("REFRESH", threshold=0.79, timeout=4, normalize_monitor=True)).valid:
        #Gambling window is open. Starting to spent some coins
        max_gamble_count = floor(2000000/188000) # leave about 500k gold and assume buying coronets at ~188k
        while get_gamble_status() and get_gamble_count() < max_gamble_count:
            img=grab()
            for item in Config().char["gamble_items"]:
                # while desired gamble item is not on screen, refresh
                while not (desired_item := TemplateFinder().search (item.upper(), grab(), roi=Config().ui_roi["left_inventory"], normalize_monitor=True)).valid:
                    mouse.move(*refresh_btn.center, randomize=12, delay_factor=[1.0, 1.5])
                    wait(0.1, 0.15)
                    mouse.click(button="left")
                    wait(0.1, 0.15)
                # desired item found, purchase it
                mouse.move(*desired_item.center, randomize=12, delay_factor=[1.0, 1.5])
                wait(0.1, 0.15)
                mouse.click(button="right")
                wait(0.4, 0.6)
                img=grab()
                # make sure the "not enough gold" message doesn't exist
                if is_visible(ScreenObjects.NotEnoughGold, img):
                    Logger.warning(f"Out of gold, stop gambling")
                    keyboard.send("esc")
                    set_gamble_status(False)
                    break
                new_count = get_gamble_count()+1
                Logger.debug(f"Gamble purchase {new_count}/{max_gamble_count}")
                set_gamble_count(new_count)
                # inspect purchased item
                if personal.inventory_has_items(img):
                    items = personal.inspect_items(img, close_window=False)
                    if items:
                        # specifically in gambling scenario, all items returned from inspect_items, which sells/drops unwanted items, are to be kept
                        # if there is a desired item, end function and go to stash
                        Logger.debug("Found desired item, go to stash")
                        common.close()
                        return items
                if new_count >= max_gamble_count:
                    break
        Logger.debug(f"Finish gambling")
        stash.set_curr_stash(gold = 0)
        personal.set_inventory_gold_full(False)
        if get_gamble_status():
            set_gamble_status(False)
        common.close()
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
            if is_visible(ScreenObjects.NotEnoughGold):
                Logger.warning(f"Out of gold, could not purchase {template_name}")
                keyboard.send('shift', do_release=True)
                keyboard.send("esc")
                return False
            keyboard.send('shift', do_release=True)
            personal.set_inventory_gold_full(False)
            return True
        if quantity:
            for _ in range(quantity):
                mouse.click(button="right")
                wait(0.9, 1.1)
                if is_visible(ScreenObjects.NotEnoughGold):
                    Logger.warning(f"Out of gold, could not purchase {template_name}")
                    keyboard.send("esc")
                    return False
            personal.set_inventory_gold_full(False)
            return True
        else:
            Logger.error("buy_item: Quantity not specified")
            return False

    Logger.error(f"buy_item: Desired item {template_name} not found")
    return False
