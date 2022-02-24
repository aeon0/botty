import itertools
from item import ItemFinder
from logger import Logger
from screen import convert_abs_to_monitor, grab, convert_screen_to_monitor
import keyboard
import cv2
import time
import numpy as np
import os

from template_finder import TemplateFinder
from config import Config
from utils.misc import wait, is_in_roi, mask_by_roi
from utils.custom_mouse import mouse
from inventory import stash, common
from ui import view
from ui_manager import detect_screen_object, wait_for_screen_object, ScreenObjects, center_mouse
from game_stats import game_stats
from item import ItemCropper
from messages import Messenger

messenger = Messenger()

def inventory_has_items(img: np.ndarray = None, num_ignore_columns: int = 0) -> bool:
    """
    Check if Inventory has any items
    :param img: Img from screen.grab() with inventory open
    :return: Bool if inventory still has items or not
    """
    img = open(img)
    for column, row in itertools.product(range(num_ignore_columns, Config().char["num_loot_columns"]), range(4)):
        _, slot_img = common.get_slot_pos_and_img(img, column, row)
        if common.slot_has_item(slot_img):
            return True
    return False

def stash_all_items(num_loot_columns: int, item_finder: ItemFinder, gamble = False):
    """
    Stashing all items in inventory. Stash UI must be open when calling the function.
    :param num_loot_columns: Number of columns used for loot from left
    """
    global messenger, game_stats
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
                            stash.set_gold_full(True)
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
        slot_pos, slot_img = common.get_slot_pos_and_img(img, column, row)
        if common.slot_has_item(slot_img):
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
                slot_pos, slot_img = common.get_slot_pos_and_img(item_check_img, column, row)
                if common.slot_has_item(slot_img):
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
    if inventory_has_items(img):
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

    if Config().advanced_options["use_ocr"]:
        item_box = ItemCropper().crop_item_descr(inp_img=img)
        if item_box.valid:
            Logger.debug(f"OCR ITEM DESCR: Mean conf: {item_box.ocr_result.mean_confidence}")
            for i, line in enumerate(list(filter(None, item_box.ocr_result.text.splitlines()))):
                Logger.debug(f"OCR LINE{i}: {line}")
            if Config().general["loot_screenshots"]:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                found_low_confidence = False
                for cnt, x in enumerate(item_box.ocr_result['word_confidences']):
                    if x <= 88:
                        try:
                            Logger.debug(f"Low confidence word #{cnt}: {item_box.ocr_result['original_text'].split()[cnt]} -> {item_box.ocr_result['text'].split()[cnt]}, Conf: {x}, save screenshot")
                            found_low_confidence = True
                        except: pass
                if found_low_confidence:
                    cv2.imwrite(f"./loot_screenshots/ocr_box_{timestamp}_o.png", item_box.ocr_result['original_img'])
                    cv2.imwrite(f"./loot_screenshots/ocr_box_{timestamp}_n.png", item_box.ocr_result['processed_img'])


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

def should_stash() -> bool:
    """
    Check if there are items that need to be stashed in the inventory
    """
    wait(0.2, 0.3)
    keyboard.send(Config().char["inventory_screen"])
    wait(0.7, 1.0)
    should_stash = inventory_has_items()
    keyboard.send(Config().char["inventory_screen"])
    wait(0.4, 0.6)
    return should_stash

def specific_inventory_roi(desired: str = "reserved"):
    #roi spec: left, top, W, H
    roi = Config().ui_roi["inventory"].copy()
    open_width = Config().ui_pos["slot_width"] * Config().char["num_loot_columns"]
    if desired == "reserved":
        roi[0]=roi[0] + open_width
        roi[2]=roi[2] - open_width
    elif desired == "open":
        roi[2]=open_width
    else:
        Logger.error(f"set_inventory_rois: unsupported desired={desired}")
        return None
    return roi

def open(img: np.ndarray = None) -> np.ndarray:
    img = grab() if img is None else img
    if not detect_screen_object(ScreenObjects.RightPanel, img).valid:
        keyboard.send(Config().char["inventory_screen"])
        if not wait_for_screen_object(ScreenObjects.RightPanel, 1).valid:
            if not view.return_to_play():
                return None
            keyboard.send(Config().char["inventory_screen"])
            if not wait_for_screen_object(ScreenObjects.RightPanel, 1).valid:
                return None
        img = grab()
    return img

def inspect_items(img: np.ndarray = None) -> bool:
    """
    Iterate over all picked items in inventory--ID items and decide which to stash
    :param img: Image in which the item is searched (item details should be visible)
    """
    img = open(img)
    slots = []
    # check which slots have items
    for column, row in itertools.product(range(Config().char["num_loot_columns"]), range(4)):
        slot_pos, slot_img = common.get_slot_pos_and_img(Config(), img, column, row)
        if common.slot_has_item(slot_img):
            slots.append([slot_pos, row, column])
    boxes = []
    # iterate over slots with items
    item_rois = []
    for count, slot in enumerate(slots):
        failed = False
        # ignore this slot if it lies within in a previous item's ROI
        for item_roi in item_rois:
            if is_in_roi(item_roi, slot[0]):
                continue
        img = grab()
        x_m, y_m = convert_screen_to_monitor(slot[0])
        delay = [0.2, 0.3] if count else [1, 1.3]
        mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
        wait(0.3, 0.5)
        hovered_item = grab()
        # get the item description box
        item_box = ItemCropper().crop_item_descr(hovered_item)
        if item_box.valid:
            # determine the item's ROI in inventory
            cnt=0
            while True:
                pre = mask_by_roi(img, specific_inventory_roi("open"))
                post = mask_by_roi(hovered_item, specific_inventory_roi("open"))
                # will sometimes have equivalent diff if mouse ends up in an inconvenient place.
                if not np.array_equal(pre, post):
                    break
                Logger.debug(f"_inspect_items: pre=post, try again. slot {slot[0]}")
                center_mouse()
                img = grab()
                mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
                wait(0.3, 0.5)
                hovered_item = grab()
                cnt += 1
                if cnt >= 2:
                    Logger.error(f"_inspect_items: Unable to get item's inventory ROI, slot {slot[0]}")
                    break
            extend_roi = item_box.roi[:]
            extend_roi[3] = extend_roi[3] + 30
            item_roi = common.calc_item_roi(mask_by_roi(pre, extend_roi, type = "inverse"), mask_by_roi(post, extend_roi, type = "inverse"))
            if item_roi:
                item_rois.append(item_roi)
            # determine whether the item can be sold
            sell = Config().char["sell_junk"] and not (item_box.ocr_result.text.lower() in ["key of ", "essense of", "wirt's", "jade figurine"])
            # attempt to identify item
            need_id = False
            if Config().char["id_items"]:
                if (is_unidentified := detect_screen_object(ScreenObjects.Unidentified, item_box.data)).valid:
                    need_id = True
                    center_mouse()
                    tome_state, tome_pos = common.tome_state(img, tome_type = "id", roi = specific_inventory_roi("reserved"))
                if is_unidentified and tome_state is not None and tome_state == "ok":
                    common.id_item_with_tome([x_m, y_m], tome_pos)
                    need_id = False
                    # recapture box after ID
                    mouse.move(x_m, y_m, randomize = 4, delay_factor = delay)
                    wait(0.2, 0.3)
                    hovered_item = grab()
                    item_box = ItemCropper().crop_item_descr(hovered_item)
            if item_box.valid:
                if Config.advanced_options["use_ocr"]:
                    Logger.debug(f"OCR ITEM DESCR: Mean conf: {item_box.ocr_result.mean_confidence}")
                    for i, line in enumerate(list(filter(None, item_box.ocr_result.text.splitlines()))):
                        Logger.debug(f"OCR LINE{i}: {line}")
                    if Config().general["loot_screenshots"]:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        found_low_confidence = False
                        for cnt, x in enumerate(item_box.ocr_result['word_confidences']):
                            if x <= 88:
                                try:
                                    Logger.debug(f"Low confidence word #{cnt}: {item_box.ocr_result['original_text'].split()[cnt]} -> {item_box.ocr_result['text'].split()[cnt]}, Conf: {x}, save screenshot")
                                    found_low_confidence = True
                                except: pass
                        if found_low_confidence:
                            cv2.imwrite(f"./loot_screenshots/ocr_box_{timestamp}_o.png", item_box.ocr_result['original_img'])
                            cv2.imwrite(f"./loot_screenshots/ocr_box_{timestamp}_n.png", item_box.ocr_result['processed_img'])

                # decide whether to keep item
                keep = (result := keep_item(ItemFinder(), item_box)) is not None
                if keep: sell = False

                box = common.BoxInfo(
                    img = item_box.data,
                    pos = (x_m, y_m),
                    column = slot[2],
                    row = slot[1],
                    need_id = need_id,
                    sell = sell,
                    keep = keep
                )
                if keep and not need_id:
                    game_stats.log_item_keep(result.name, Config().items[result.name].pickit_type == 2, item_box.data, result.ocr_result.text)
                if keep or sell or need_id:
                    # save item info
                    boxes.append(box)
                else:
                    # if item isn't going to be sold or kept, drop it
                    Logger.debug(f"Dropping {item_box.ocr_result.text.splitlines()[0]}")
                    common.transfer_items([box], action = "drop")
                wait(0.3, 0.5)
            else:
                failed = True
        else:
            failed = True
        if failed:
            Logger.error(f"item_cropper failed for slot_pos: {slot[0]}")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/failed_item_box_" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
    common.close()
    return boxes