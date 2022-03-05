import keyboard
from template_finder import TemplateFinder
from config import Config
from utils.misc import wait
from screen import convert_screen_to_monitor, grab
from item import ItemFinder
import itertools
from logger import Logger
from utils.custom_mouse import mouse
from ui_manager import wait_for_screen_object, ScreenObjects
from inventory import common, personal

def close_vendor_screen():
    keyboard.send("esc")

def repair_and_fill_up_tp() -> bool:
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
            if (personal.inventory_has_items(grab(), Config().char["num_loot_columns"], ignore_columns) and personal.inventory_has_items(grab(),2)):
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
                    slot_pos, slot_img = common.get_slot_pos_and_img(img, column, row)
                    if common.slot_has_item(slot_img):
                        x_m, y_m = convert_screen_to_monitor(slot_pos)
                        mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                        # check item again and discard it or stash it
                        wait(1.2, 1.4)
                        hovered_item = grab()
                        if not personal.keep_item(item_finder, hovered_item):
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
