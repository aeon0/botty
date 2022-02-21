import itertools
from item import ItemFinder
from logger import Logger
from screen import convert_abs_to_monitor, grab, convert_screen_to_monitor
import mouse
from template_finder import TemplateFinder
from config import Config
from utils.misc import wait
import keyboard
import cv2
import time
import numpy as np
from utils.custom_mouse import mouse
import os
from ui_components import stash
from ui_components.stash import gold_full
from ui.ui_manager import detect_screen_object, messenger, game_stats, wait_for_screen_object, ScreenObjects
from messages import Messenger

messanger = Messenger()

def inventory_has_items(img, num_loot_columns: int, num_ignore_columns=0) -> bool:
    """
    Check if Inventory has any items
    :param img: Img from screen.grab() with inventory open
    :param num_loot_columns: Number of columns to check from left
    :return: Bool if inventory still has items or not
    """
    for column, row in itertools.product(range(num_ignore_columns, num_loot_columns), range(4)):
        _, slot_img = get_slot_pos_and_img(img, column, row)
        if slot_has_item(slot_img):
            return True
    return False

def stash_all_items(num_loot_columns: int, item_finder: ItemFinder, gamble = False):
    """
    Stashing all items in inventory. Stash UI must be open when calling the function.
    :param num_loot_columns: Number of columns used for loot from left
    """
    global gold_full, messenger, game_stats
    Logger.debug("Searching for inventory gold btn...")
    # Move cursor to center
    x, y = convert_abs_to_monitor((0, 0))
    mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
    # Wait till gold btn is found
    gold_btn = wait_for_screen_object(ScreenObjects.GoldBtnInventory, time_out = 20)
    if not gold_btn.valid:
        Logger.error("Could not determine to be in stash menu. Continue...")
        return
    Logger.debug("Found inventory gold btn")
    if not gamble:
        # stash gold
        if Config().char["stash_gold"]:
            inventory_no_gold = detect_screen_object(ScreenObjects.GoldNone)
            if inventory_no_gold.valid:
                Logger.debug("Skipping gold stashing")
            else:
                Logger.debug("Stashing gold")
                stash.move_to_stash_tab(min(3, stash.curr_stash["gold"]))
                mouse.move(*gold_btn.center, randomize=4)
                wait(0.1, 0.15)
                mouse.press(button="left")
                wait(0.25, 0.35)
                mouse.release(button="left")
                wait(0.4, 0.6)
                keyboard.send("enter") #if stash already full of gold just nothing happens -> gold stays on char -> no popup window
                wait(1.0, 1.2)
                # move cursor away from button to interfere with screen grab
                mouse.move(-120, 0, absolute=False, randomize=15)
                inventory_no_gold = detect_screen_object(ScreenObjects.GoldNone)
                if not inventory_no_gold.valid:
                    Logger.info("Stash tab is full of gold, selecting next stash tab.")
                    stash.curr_stash["gold"] += 1
                    if Config().general["info_screenshots"]:
                        cv2.imwrite("./info_screenshots/info_gold_stash_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                    if stash.curr_stash["gold"] > 3:
                        #decide if gold pickup should be disabled or gambling is active
                        if Config().char["gamble_items"]:
                            gold_full = True
                        else:
                            # turn off gold pickup
                            Config().turn_off_goldpickup()
                            # inform user about it
                            msg = "All stash tabs and character are full of gold, turn of gold pickup"
                            Logger.info(msg)
                            if Config().general["custom_message_hook"]:
                                messenger.send_message(msg=f"{Config().general['name']}: {msg}")
                    else:
                        # move to next stash
                        wait(0.5, 0.6)
                        return stash_all_items(num_loot_columns, item_finder)
    else:
        stash.transfer_shared_to_private_gold(stash.gambling_round)
    # stash stuff
    stash.move_to_stash_tab(stash.curr_stash["items"])
    center_m = convert_abs_to_monitor((0, 0))
    for column, row in itertools.product(range(num_loot_columns), range(4)):
        img = grab()
        slot_pos, slot_img = get_slot_pos_and_img(img, column, row)
        if slot_has_item(slot_img):
            x_m, y_m = convert_screen_to_monitor(slot_pos)
            mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
            # check item again and discard it or stash it
            wait(1.2, 1.4)
            hovered_item = grab()
            found_items = keep_item(item_finder, hovered_item)
            if len(found_items) > 0:
                keyboard.send('ctrl', do_release=False)
                wait(0.2, 0.25)
                mouse.press(button="left")
                wait(0.2, 0.25)
                mouse.release(button="left")
                wait(0.2, 0.25)
                keyboard.send('ctrl', do_press=False)
                # To avoid logging multiple times the same item when stash tab is full
                # check the _keep_item again. In case stash is full we will still find the same item
                wait(0.3)
                did_stash_test_img = grab()
                if len(keep_item(item_finder, did_stash_test_img, False)) > 0:
                    Logger.debug("Wanted to stash item, but its still in inventory. Assumes full stash. Move to next.")
                    break
                else:
                    game_stats.log_item_keep(found_items[0].name, Config().items[found_items[0].name].pickit_type == 2, hovered_item)
            else:
                # make sure there is actually an item
                time.sleep(0.3)
                curr_pos = mouse.get_position()
                # move mouse away from inventory, for some reason it was sometimes included in the grabed img
                x, y = convert_abs_to_monitor((0, 0))
                mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
                item_check_img = grab()
                mouse.move(*curr_pos, randomize=2)
                wait(0.4, 0.6)
                slot_pos, slot_img = get_slot_pos_and_img(item_check_img, column, row)
                if slot_has_item(slot_img):
                    if Config().general["info_screenshots"]:
                        cv2.imwrite("./info_screenshots/info_discard_item_" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
                    mouse.press(button="left")
                    wait(0.2, 0.4)
                    mouse.release(button="left")
                    mouse.move(*center_m, randomize=20)
                    wait(0.2, 0.3)
                    mouse.press(button="left")
                    wait(0.2, 0.3)
                    mouse.release(button="left")
                    wait(0.5, 0.5)
    Logger.debug("Check if stash is full")
    time.sleep(0.6)
    # move mouse away from inventory, for some reason it was sometimes included in the grabed img
    x, y = convert_abs_to_monitor((0, 0))
    mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
    img = grab()
    if inventory_has_items(img, num_loot_columns):
        Logger.info("Stash page is full, selecting next stash")
        if Config().general["info_screenshots"]:
            cv2.imwrite("./info_screenshots/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)

        # if filling shared stash first, we decrement from 3, otherwise increment
        stash.curr_stash["items"] += -1 if Config().char["fill_shared_stash_first"] else 1
        if (Config().char["fill_shared_stash_first"] and stash.curr_stash["items"] < 0) or stash.curr_stash["items"] > 3:
            Logger.error("All stash is full, quitting")
            if Config().general["custom_message_hook"]:
                messenger.send_stash()
            os._exit(1)
        else:
            # move to next stash
            wait(0.5, 0.6)
            return stash_all_items(num_loot_columns, item_finder)

    Logger.debug("Done stashing")
    wait(0.4, 0.5)

def keep_item(item_finder: ItemFinder, img: np.ndarray, do_logging: bool = True) -> bool:
    """
    Check if an item should be kept, the item should be hovered and in own inventory when function is called
    :param item_finder: ItemFinder to check if item is in pickit
    :param img: Image in which the item is searched (item details should be visible)
    :param do_logging: Bool value to turn on/off logging for items that are found and should be kept
    :return: Bool if item should be kept
    """
    wait(0.2, 0.3)
    _, w, _ = img.shape
    img = img[:, (w//2):,:]
    original_list = item_finder.search(img)
    filtered_list = []
    for x in original_list:
        if ("potion" in x.name) or (Config().items[x.name].pickit_type == 0): continue
        include_props = Config().items[x.name].include
        exclude_props = Config().items[x.name].exclude
        #Disable include params for uniq, rare, magical if ident is disabled in params.ini
        #if (not Config().char["id_items"]) and ("uniq" in x.name or "magic" in x.name or "rare" in x.name or "set" in x.name):
        if (not Config().char["id_items"]) and any(item_type in x.name for item_type in ["uniq", "magic", "rare", "set"]):
            include_props = False
            exclude_props = False
        if not (include_props or exclude_props):
            if do_logging:
                Logger.debug(f"{x.name}: Stashing")
            filtered_list.append(x)
            continue
        include = True
        include_logic_type = Config().items[x.name].include_type
        if include_props:
            include = False
            found_props=[]
            for prop in include_props:
                if len(prop)>1:
                    found_subprops=[]
                    for subprop in prop:
                        try:
                            template_match = TemplateFinder().search(subprop, img, threshold=0.95)
                        except:
                            Logger.error(f"{x.name}: can't find template file for required {prop}, ignore just in case")
                            template_match = lambda: None; template_match.valid = True
                        if template_match.valid:
                            if include_logic_type == "OR":
                                found_subprops.append(True)
                            else:
                                found_props.append (True)
                                break
                        else:
                            found_subprops.append(False)
                            break
                    if (len(found_subprops) > 0 and all(found_subprops)):
                        include = True
                        break
                else:
                    try:
                        template_match = TemplateFinder().search(prop, img, threshold=0.95)
                    except:
                        Logger.error(f"{x.name}: can't find template file for required {prop}, ignore just in case")
                        template_match = lambda: None; template_match.valid = True
                    if template_match.valid:
                        if include_logic_type == "AND":
                            found_props.append(True)
                        else:
                            include = True
                            break
                    else:
                        found_props.append(False)
            if include_logic_type == "AND" and len(found_props) > 0 and all(found_props):
                include = True
        if not include:
            if do_logging:
                Logger.debug(f"{x.name}: Discarding. Required {include_logic_type}({include_props})={include}")
            continue
        exclude = False
        exclude_logic_type = Config().items[x.name].exclude_type
        if exclude_props:
            found_props=[]
            for prop in exclude_props:
                try:
                    template_match = TemplateFinder().search(prop, img, threshold=0.97)
                except:
                    Logger.error(f"{x.name}: can't find template file for exclusion {prop}, ignore just in case")
                    template_match = lambda: None; template_match.valid = False
                if template_match.valid:
                    if exclude_logic_type == "AND":
                        found_props.append(True)
                    else:
                        exclude = True
                        break
                else:
                    found_props.append(False)
            if exclude_logic_type == "AND" and len(exclude_props) > 0 and all(found_props):
                exclude = True
                break
        if include and not exclude:
            if do_logging:
                Logger.debug(f"{x.name}: Stashing. Required {include_logic_type}({include_props})={include}, exclude {exclude_logic_type}({exclude_props})={exclude}")
            filtered_list.append(x)
    return filtered_list

def should_stash(num_loot_columns: int):
    """
    Check if there are items that need to be stashed in the inventory
    :param num_loot_columns: Number of columns used for loot from left
    """
    wait(0.2, 0.3)
    keyboard.send(Config().char["inventory_screen"])
    wait(0.7, 1.0)
    should_stash = inventory_has_items(grab(), num_loot_columns)
    keyboard.send(Config().char["inventory_screen"])
    wait(0.4, 0.6)
    return should_stash

def get_slot_pos_and_img(img: np.ndarray, column: int, row: int) -> tuple[tuple[int, int],  np.ndarray]:
    """
    Get the pos and img of a specific slot position in Inventory. Inventory must be open in the image.
    :param config: The config which should be used
    :param img: Image from screen.grab() not cut
    :param column: Column in the Inventory
    :param row: Row in the Inventory
    :return: Returns position and image of the cut area as such: [[x, y], img]
    """
    top_left_slot = (Config().ui_pos["inventory_top_left_slot_x"], Config().ui_pos["inventory_top_left_slot_y"])
    slot_width = Config().ui_pos["slot_width"]
    slot_height= Config().ui_pos["slot_height"]
    slot = (top_left_slot[0] + slot_width * column, top_left_slot[1] + slot_height * row)
    # decrease size to make sure not to have any borders of the slot in the image
    offset_w = int(slot_width * 0.12)
    offset_h = int(slot_height * 0.12)
    min_x = slot[0] + offset_w
    max_x = slot[0] + slot_width - offset_w
    min_y = slot[1] + offset_h
    max_y = slot[1] + slot_height - offset_h
    slot_img = img[min_y:max_y, min_x:max_x]
    center_pos = (int(slot[0] + (slot_width // 2)), int(slot[1] + (slot_height // 2)))
    return center_pos, slot_img

def slot_has_item(slot_img: np.ndarray) -> bool:
    """
    Check if a specific slot in the inventory has an item or not based on color
    :param slot_img: Image of the slot
    :return: Bool if there is an item or not
    """
    slot_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
    avg_brightness = np.average(slot_img[:, :, 2])
    return avg_brightness > 16.0