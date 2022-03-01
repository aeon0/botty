import keyboard
from template_finder import TemplateFinder
from config import Config
import numpy as np
from utils.misc import wait
from screen import convert_screen_to_monitor, grab
from logger import Logger
from utils.custom_mouse import mouse
from ui_manager import wait_for_screen_object, ScreenObjects
from inventory import common, personal

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
    gold = True
    gamble_on = True
    if Config().char["num_loot_columns"] % 2 == 0:
        ignore_columns = Config().char["num_loot_columns"]-1
    else:
        ignore_columns = Config().char["num_loot_columns"]-2
    template_match = TemplateFinder().search_and_wait("REFRESH", threshold=0.79, time_out=4)
    if template_match.valid:
        #Gambling window is open. Starting to spent some coins
        while (gamble_on and gold):
            img=grab()
            if (personal.inventory_has_items(img, ignore_columns) and personal.inventory_has_items(img, 2)):
                gamble_on = False
                common.close()
                break
            for item in Config().char["gamble_items"]:
                template_match_item = TemplateFinder().search (item.upper(), grab(), roi=Config().ui_roi["left_inventory"], normalize_monitor=True)
                while not template_match_item.valid:
                    #Refresh gambling screen
                    template_match = TemplateFinder().search ("REFRESH", grab(), normalize_monitor=True)
                    if (template_match.valid):
                        mouse.move(*template_match.center, randomize=12, delay_factor=[1.0, 1.5])
                        wait(0.1, 0.15)
                        mouse.click(button="left")
                        wait(0.1, 0.15)
                    template_match_item = TemplateFinder().search (item.upper(), grab(), roi=Config().ui_roi["left_inventory"], normalize_monitor=True)
                #item found in gambling menu
                mouse.move(*template_match_item.center, randomize=12, delay_factor=[1.0, 1.5])
                wait(0.1, 0.15)
                mouse.click(button="right")
                wait(0.1, 0.15)
                img=grab()
                template_match = TemplateFinder().search ("no_gold".upper(), inp_img=img, threshold= 0.90)
                #check if gold is av
                if template_match.valid:
                    gold = False
                    common.close()
                    break
                if personal.inventory_has_items(img):
                    personal.inspect_items(img)
        #Stashing needed
    else:
        Logger.warning("gambling failed")

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