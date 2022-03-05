import keyboard
from template_finder import TemplateFinder
from config import Config
import numpy as np
from utils.misc import wait
from screen import convert_screen_to_monitor, grab
from logger import Logger
from utils.custom_mouse import mouse
from ui_manager import detect_screen_object, wait_for_screen_object, ScreenObjects
from inventory import personal, stash, common


gamble_status = False

def get_gamble_status() -> bool:
    global gamble_status
    return gamble_status

def set_gamble_status (bool: bool):
    global gamble_status, gold_in_stash
    gamble_status = bool
    if gamble_status:
        stash.set_gold_in_stash(2500000)
        Config().turn_off_goldpickup()
    else:
        Config().turn_on_goldpickup()

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
    if detect_screen_object(ScreenObjects.NotEnoughGold):
        Logger.warning("Couldn't repair--out of gold. Continue.")
        return False
    return True

def gamble():
    if (refresh_btn := TemplateFinder().search_and_wait("REFRESH", threshold=0.79, time_out=4, normalize_monitor=True)).valid:
        #Gambling window is open. Starting to spent some coins
        reserve_stash_gold = 500000
        while get_gamble_status() and stash.get_gold_in_stash() > reserve_stash_gold:
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
                wait(0.3, 0.5)
                img=grab()
                # make sure the "not enough gold" message doesn't exist
                if detect_screen_object(ScreenObjects.NotEnoughGold, img).valid:
                    Logger.warning(f"Out of gold, stop gambling")
                    set_gamble_status(False)
                    break
                # if there's was no gold left in player inventory, check how much gold is in stash in vendor window
                if detect_screen_object(ScreenObjects.GoldNone, img).valid:
                    last_gold = stash.get_gold_in_stash()
                    # attempt to read stash gold with OCR
                    try: read_gold = common.read_gold(img, "vendor")
                    except: read_gold = 0
                    # make sure read_gold is within ballpark...
                    if read_gold and read_gold < 2500000 and (last_gold - read_gold) < 1000000:
                        stash.set_gold_in_stash(read_gold)
                    else:
                        # if OCR failed or result is out of expected range, assume 188000 drop (~max cost of coronet)
                        Logger.debug("OCR failed to read stash/vendor gold")
                        stash.set_gold_in_stash(last_gold - 188000)
                # inspect purchased item
                if personal.inventory_has_items(img):
                    items = personal.inspect_items(img, close_window=False)
                    if items:
                        # specifically in gambling scenario, all items returned from inspect_items, which sells/drops unwanted items, are to be kept
                        # if there is a desired item, end function and go to stash
                        Logger.debug("Found desired item, go to stash")
                        common.close()
                        return items
                if stash.get_gold_in_stash() < reserve_stash_gold:
                    break
        Logger.debug(f"Finish gambling")
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
            if detect_screen_object(ScreenObjects.NotEnoughGold):
                Logger.warning(f"Out of gold, could not purchase {template_name}")
                return False
            keyboard.send('shift', do_release=True)
            return True
        if quantity:
            for _ in range(quantity):
                mouse.click(button="right")
                wait(0.9, 1.1)
                if detect_screen_object(ScreenObjects.NotEnoughGold):
                    Logger.warning(f"Out of gold, could not purchase {template_name}")
                    return False
            return True
        else:
            Logger.error("buy_item: Quantity not specified")
            return False

    Logger.error(f"buy_item: Desired item {template_name} not found")
    return False