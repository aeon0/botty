# f: close_vendor_screen(self):
# f: repair_and_fill_up_tp(self) -> bool:
# f: gamble(self, item_finder: ItemFinder):
# f: buy_pots(self, healing_pots: int = 0, mana_pots: int = 0):
# - label (Stash vs Jamella)
# - tabs (weapons, misc, etc.)
# - btn_repair (if repair vendor)
# - btn_refresh (if gamble vendor)
import keyboard
from template_finder import TemplateFinder
from config import Config
import mouse
from utils.misc import wait
from screen import convert_screen_to_monitor, grab
from item import ItemFinder
from ui_components.inventory import inventory_has_items, keep_item, get_slot_pos_and_img, slot_has_item
import itertools
from logger import Logger
from utils.custom_mouse import mouse
import cv2
import time

def close_vendor_screen():
    keyboard.send("esc")

def repair_and_fill_up_tp() -> bool:
    """
    Repair and fills up TP buy selling tome and buying. Vendor inventory needs to be open!
    :return: Bool if success
    """
    repair_btn = TemplateFinder().search_and_wait("REPAIR_BTN", roi=Config().ui_roi["repair_btn"], time_out=4, normalize_monitor=True)
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
    tp_tome = TemplateFinder().search_and_wait(["TP_TOME", "TP_TOME_RED"], roi=Config().ui_roi["right_inventory"], time_out=3, normalize_monitor=True)
    if not tp_tome.valid:
        return False
    keyboard.send('ctrl', do_release=False)
    mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
    wait(0.1, 0.15)
    mouse.press(button="left")
    wait(0.25, 0.35)
    mouse.release(button="left")
    wait(0.5, 0.6)
    keyboard.send('ctrl', do_press=False)
    tp_tome = TemplateFinder().search_and_wait("TP_TOME", roi=Config().ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
    if not tp_tome.valid:
        return False
    keyboard.send('ctrl', do_release=False)
    mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
    wait(0.1, 0.15)
    mouse.click(button="right")
    wait(0.1, 0.15)
    keyboard.send('ctrl', do_press=False)
    # delay to make sure the tome has time to transfer to other inventory before closing window
    tp_tome = TemplateFinder().search_and_wait("TP_TOME", roi=Config().ui_roi["right_inventory"], time_out=3)
    if not tp_tome.valid:
        return False
    return True

def gamble(item_finder: ItemFinder):
    gold = True
    gamble_on = True
    if Config().char["num_loot_columns"]%2==0:
        ignore_columns = Config().char["num_loot_columns"]-1
    else:
        ignore_columns = Config().char["num_loot_columns"]-2
    template_match = TemplateFinder().search_and_wait("REFRESH", threshold=0.79, time_out=4)
    if template_match.valid:
        #Gambling window is open. Starting to spent some coins
        while (gamble_on and gold):
            if (inventory_has_items(grab(), Config().char["num_loot_columns"], ignore_columns) and inventory_has_items(grab(),2)):
                gamble_on = False
                close_vendor_screen ()
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
                template_match = TemplateFinder().search ("no_gold".upper(), grab(), threshold= 0.90)
                #check if gold is av
                if template_match.valid:
                    gold = False
                    close_vendor_screen()
                    break
                for column, row in itertools.product(range(Config().char["num_loot_columns"]), range(4)):
                    img = grab()
                    slot_pos, slot_img = get_slot_pos_and_img(img, column, row)
                    if slot_has_item(slot_img):
                        x_m, y_m = convert_screen_to_monitor(slot_pos)
                        mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                        # check item again and discard it or stash it
                        wait(1.2, 1.4)
                        hovered_item = grab()
                        if not keep_item(item_finder, hovered_item):
                            keyboard.send('ctrl', do_release=False)
                            wait(0.1, 0.15)
                            mouse.click (button="left")
                            wait(0.1, 0.15)
                            keyboard.send('ctrl', do_press=False)
        #Stashing needed
    else:
        Logger.warning("gambling failed")

def buy_pots(healing_pots: int = 0, mana_pots: int = 0):
    """
    Buy pots from vendors. Vendor inventory needs to be open!
    :param healing_pots: Number of healing pots to buy
    :param mana_pots: Number of mana pots to buy
    """
    h_pot = TemplateFinder().search_and_wait("SUPER_HEALING_POTION", roi=Config().ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
    if h_pot.valid is False:  # If not available in shop, try to shop next best potion.
        h_pot = TemplateFinder().search_and_wait("GREATER_HEALING_POTION", roi=Config().ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
    if h_pot.valid:
        mouse.move(*h_pot.center, randomize=8, delay_factor=[1.0, 1.5])
        for _ in range(healing_pots):
            mouse.click(button="right")
            wait(0.9, 1.1)
    m_pot = TemplateFinder().search_and_wait("SUPER_MANA_POTION", roi=Config().ui_roi["left_inventory"], time_out=3,normalize_monitor=True)
    if m_pot.valid is False:  # If not available in shop, try to shop next best potion.
        m_pot = TemplateFinder().search_and_wait("GREATER_MANA_POTION", roi=Config().ui_roi["left_inventory"], time_out=3,normalize_monitor=True)
    if m_pot.valid:
        mouse.move(*m_pot.center, randomize=8, delay_factor=[1.0, 1.5])
        for _ in range(mana_pots):
            mouse.click(button="right")
            wait(0.9, 1.1)

def sell_junk(num_loot_columns: int, item_finder: ItemFinder):
    for column, row in itertools.product(range(num_loot_columns), range(4)):
            img = grab()
            slot_pos, slot_img = get_slot_pos_and_img(img, column, row)
            if slot_has_item(slot_img):
                x_m, y_m = convert_screen_to_monitor(slot_pos)
                mouse.move(x_m, y_m)
                wait(0.2)
                hovered_item = grab()
                should_keep_item = keep_item(item_finder, hovered_item)
                if not should_keep_item:
                    if Config().general["info_screenshots"]:
                        cv2.imwrite("./info_screenshots/info_sold_item_" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
                    keyboard.press("ctrl")
                    wait(0.2, 0.4)
                    mouse.press(button="left")
                    wait(0.2, 0.4)
                    keyboard.release("ctrl")
    close_vendor_screen()
    wait(0.2, 0.4)