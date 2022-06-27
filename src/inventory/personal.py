import itertools
from game_stats import GameStats
import keyboard
import cv2
import time
import numpy as np
from dataclasses import dataclass
import parse

from logger import Logger
from config import Config
import template_finder
from utils.misc import wait, is_in_roi, mask_by_roi
from utils.custom_mouse import mouse
from inventory import stash, common, vendor
from ui import view
from ui_manager import detect_screen_object, is_visible, select_screen_object_match, wait_until_visible, ScreenObjects, center_mouse, wait_for_update
from messages import Messenger
from d2r_image import processing as d2r_image
from d2r_image.data_models import HoveredItem, ItemText
from screen import grab, convert_screen_to_monitor
from item import consumables
from bnip.NTIPAliasStat import NTIPAliasStat as NTIP_STATS
from bnip.actions import should_id, should_keep

inv_gold_full = False
messenger = Messenger()

nontradable_items = ["key of ", "essense of", "wirt's", "jade figurine"]

@dataclass
class BoxInfo:
    img: np.ndarray = None
    pos: tuple = None
    column: int = None
    row: int = None
    need_id: bool = False
    sell: bool = False
    keep: bool = False
    def __getitem__(self, key):
        return super().__getattribute__(key)
    def __setitem__(self, key, value):
        setattr(self, key, value)

def get_inventory_gold_full():
    return inv_gold_full

def set_inventory_gold_full(new_value: bool):
    global inv_gold_full
    if get_inventory_gold_full() != new_value:
        Logger.info(f"Set inventory gold full: {new_value}")
        inv_gold_full = new_value

def inventory_has_items(img: np.ndarray = None, close_window = False) -> bool:
    """
    Check if Inventory has any items
    :param img: Img from screen.grab() with inventory open
    :return: Bool if inventory still has items or not
    """
    img = open(img)
    items=False
    for column, row in itertools.product(range(0, Config().char["num_loot_columns"]), range(4)):
        _, slot_img = common.get_slot_pos_and_img(img, column, row)
        if common.slot_has_item(slot_img):
            items=True
            break
    if close_window:
        common.close()
    if items:
        return True
    return False


def stash_all_items(items: list = None):
    """
    Stashing all items in inventory. Stash UI must be open when calling the function.
    """
    global messenger
    if not get_inventory_gold_full() and items is None:
        Logger.debug("No items to stash, skip")
        return None
    center_mouse()
    # Wait for stash to fully load
    if not common.wait_for_left_inventory():
        Logger.error("stash_all_items(): Failed to find stash menu. Continue...")
        return items
    # stash gold
    if Config().char["stash_gold"]:
        if not is_visible(ScreenObjects.GoldNone):
            Logger.debug("Stashing gold")
            common.select_tab(min(3, stash.get_curr_stash()["gold"]))
            wait(0.7, 1)
            stash_full_of_gold = False
            # Try to read gold count with OCR
            try: stash_full_of_gold = common.read_gold(grab(), "stash") == 2500000
            except: pass
            if not stash_full_of_gold:
                # If gold read by OCR fails, fallback to old method
                gold_btn = detect_screen_object(ScreenObjects.GoldBtnInventory)
                select_screen_object_match(gold_btn)
                # move cursor away from button to interfere with screen grab
                mouse.move(-60, 0, absolute=False, randomize=15, delay_factor=[0.1, 0.3])
                if wait_until_visible(ScreenObjects.DepositBtn, 3).valid:
                    keyboard.send("enter") #if stash already full of gold just nothing happens -> gold stays on char -> no popup window
                else:
                    Logger.error("stash_all_items(): deposit button not detected, failed to stash gold")
                # if 0 gold becomes visible in personal inventory then the stash tab still has room for gold
                stash_full_of_gold = not wait_until_visible(ScreenObjects.GoldNone, 2).valid
            if stash_full_of_gold:
                Logger.debug("Stash tab is full of gold, selecting next stash tab.")
                stash.set_curr_stash(gold = (stash.get_curr_stash()["gold"] + 1))
                if Config().general["info_screenshots"]:
                    cv2.imwrite("./log/screenshots/info/info_gold_stash_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                if stash.get_curr_stash()["gold"] > 3:
                    #decide if gold pickup should be disabled or gambling is active
                    vendor.set_gamble_status(True)
                else:
                    # move to next stash tab
                    return stash_all_items(items=items)
            else:
                set_inventory_gold_full(False)
    if not items:
        return []
    # check if stash tab is completely full (no empty slots)
    common.select_tab(stash.get_curr_stash()["items"])
    while stash.get_curr_stash()["items"] <= 3:
        img = grab()
        if is_visible(ScreenObjects.EmptyStashSlot, img):
            break
        else:
            Logger.debug(f"Stash tab completely full, advance to next")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./log/screenshots/info/stash_tab_completely_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
            if Config().char["fill_shared_stash_first"]:
                stash.set_curr_stash(items = (stash.get_curr_stash()["items"] - 1))
            else:
                stash.set_curr_stash(items = (stash.get_curr_stash()["items"] + 1))
            if (Config().char["fill_shared_stash_first"] and stash.get_curr_stash()["items"] < 0) or stash.get_curr_stash()["items"] > 3:
                stash.stash_full()
            common.select_tab(stash.get_curr_stash()["items"])
    # stash stuff
    while True:
        items = transfer_items(items, "stash")
        if items and any([item.keep for item in items]):
            # could not stash all items, stash tab is likely full
            Logger.debug("Wanted to stash item, but it's still in inventory. Assumes full stash. Move to next.")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./log/screenshots/info/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            if Config().char["fill_shared_stash_first"]:
                stash.set_curr_stash(items = (stash.get_curr_stash()["items"] - 1))
            else:
                stash.set_curr_stash(items = (stash.get_curr_stash()["items"] + 1))
            if (Config().char["fill_shared_stash_first"] and stash.get_curr_stash()["items"] < 0) or stash.get_curr_stash()["items"] > 3:
                stash.stash_full()
            common.select_tab(stash.get_curr_stash()["items"])
        else:
            break
    Logger.debug("Done stashing")
    return items

def open(img: np.ndarray = None) -> np.ndarray:
    img = grab() if img is None else img
    if not common.inventory_is_open():
        keyboard.send(Config().char["inventory_screen"])
        if not wait_until_visible(ScreenObjects.RightPanel, 1).valid:
            if not view.return_to_play():
                return None
            keyboard.send(Config().char["inventory_screen"])
            if not wait_until_visible(ScreenObjects.RightPanel, 1).valid:
                Logger.error(f"personal.open(): Failed to open inventory")
                return None
        img = grab()
    return img


def log_item(item_box: ItemText, item_properties: HoveredItem):
    if item_box is not None and item_box.ocr_result:
        Logger.debug(f"OCR mean confidence: {item_box.ocr_result.mean_confidence}")
        Logger.debug(item_properties.Text)
        if Config().general["info_screenshots"]:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            found_low_confidence = False
            for cnt, x in enumerate(item_box.ocr_result.word_confidences):
                if x <= 88:
                    try:
                        Logger.debug(f"Low confidence word #{cnt}: {item_box.ocr_result.original_text.split()[cnt]} -> {item_box.ocr_result.text.split()[cnt]}, Conf: {x}, save screenshot")
                        found_low_confidence = True
                    except: pass
            if found_low_confidence:
                cv2.imwrite(f"./log/screenshots/info/ocr_low_confidence_box_{timestamp}.png", item_box.img)

def log_item_fail(hovered_item, slot):
    Logger.error(f"item segmentation failed for slot_pos: {slot[0]}")
    if Config().general["info_screenshots"]:
        cv2.imwrite("./log/screenshots/info/failed_item_box_" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)

def inspect_items(inp_img: np.ndarray = None, close_window: bool = True, game_stats: GameStats = None, ignore_sell: bool = False) -> list[BoxInfo]:
    """
    Iterate over all picked items in inventory--ID items and decide which to stash
    :param img: Image in which the item is searched (item details should be visible)
    """
    center_mouse()
    img = open(inp_img)
    vendor_open = is_visible(ScreenObjects.GoldBtnVendor, inp_img)
    slots = []
    # check which slots have items
    for column, row in itertools.product(range(Config().char["num_loot_columns"]), range(4)):
        slot_pos, slot_img = common.get_slot_pos_and_img(img, column, row)
        if common.slot_has_item(slot_img):
            slots.append([slot_pos, row, column])
    boxes = []
    # iterate over slots with items
    item_rois = []
    already_detected_slots = set()
    for count, slot in enumerate(slots):
        failed = False
        # ignore this slot if it lies within the range of a previous item's dimension property
        if (slot[1], slot[2]) in already_detected_slots: continue
        # ignore this slot if it lies within in a previous item's ROI (no dimension property)
        if any(is_in_roi(item_roi, slot[0]) for item_roi in item_rois): continue
        img = grab(True)
        x_m, y_m = convert_screen_to_monitor(slot[0])
        delay = [0.2, 0.3] if count else [1, 1.3]
        mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
        wait(0.1, 0.2)
        hovered_item = grab(True)
        # get the item description box
        item_properties, item_box = (None, None)
        try: # ! This happens because we don't know the items slot count. To get more context remove the try and catch and see what happens
            item_properties, item_box = d2r_image.get_hovered_item(hovered_item)
        except Exception as e:
            Logger.error(f"personal.inspect_items(): Failed to get item properties for slot {slot}")
            failed = True
        if item_box is None:
            failed = True
        else:
            if item_box.ocr_result:
                if item_properties is not None and hasattr(item_properties, 'BaseItem') and "dimensions" in item_properties.BaseItem:
                    positions = common.dimensions_to_slots(item_properties.BaseItem["dimensions"], (slot[1], slot[2]))
                    already_detected_slots.update(positions)
                else:
                    Logger.error(f"personal.inspect_items(): unable to determine dimensions for slot {slot}")
                    # determine the item's ROI in inventory
                    cnt=0
                    while True:
                        pre = mask_by_roi(img, Config().ui_roi["open_inventory_area"])
                        post = mask_by_roi(hovered_item, Config().ui_roi["open_inventory_area"])
                        # will sometimes have equivalent diff if mouse ends up in an inconvenient place.
                        if not np.array_equal(pre, post):
                            break
                        Logger.debug(f"inspect_items: pre=post, try again. slot {slot[0]}")
                        center_mouse(delay_factor=[0.05, 0.1])
                        img = grab(True)
                        mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
                        wait(0.05, 0.1)
                        hovered_item = grab(True)
                        cnt += 1
                        if cnt >= 2:
                            Logger.error(f"inspect_items: Unable to get item's inventory ROI, slot {slot[0]}")
                            break
                    extend_roi = item_box.roi[:]
                    extend_roi[3] = extend_roi[3] + 30
                    item_roi = common.calc_item_roi(mask_by_roi(pre, extend_roi, type = "inverse"), mask_by_roi(post, extend_roi, type = "inverse"))
                    if item_roi:
                        item_rois.append(item_roi)

                # determine whether the item can be sold
                ocr_result_split = item_box.ocr_result.text.splitlines()

                item_name = vendor_open and ocr_result_split[1] or ocr_result_split[0]
                item_can_be_traded = not any(substring in item_name for substring in nontradable_items)
                sell = Config().char["sell_junk"] and item_can_be_traded and not ignore_sell
                is_unidentified = is_visible(ScreenObjects.Unidentified, item_box.img)

                box = BoxInfo(
                    img = item_box.img,
                    pos = (x_m, y_m),
                    column = slot[2],
                    row = slot[1],
                    sell = sell,
                    need_id = False,
                    keep = False
                )

                tome_state = None
                try:
                    if (is_unidentified and should_id(item_properties.as_dict())):
                        box.need_id = True
                        center_mouse()
                        tome_state, tome_pos = common.tome_state(grab(True), tome_type = "id", roi = Config().ui_roi["restricted_inventory_area"])
                    if is_unidentified and tome_state is not None and tome_state == "ok":
                        common.id_item_with_tome([x_m, y_m], tome_pos)
                        box.need_id = False
                        is_unidentified = True
                        # recapture box after ID
                        mouse.move(x_m, y_m, randomize = 4, delay_factor = delay)
                        wait(0.05, 0.1)
                        hovered_item = grab(True)
                        item_properties, item_box = d2r_image.get_hovered_item(hovered_item)

                    if item_box is not None:
                        log_item(item_box, item_properties)
                        # decide whether to keep item
                        box.keep, expression = should_keep(item_properties.as_dict())

                        # make sure it's not a consumable
                        # TODO: logic for trying to add potion to belt if there are needs
                        box.keep &= not bool(consumables.is_consumable(item_properties))

                        if box.keep:
                            Logger.info(f"Keep {item_name}. Expression: {expression}")
                            sell = False
                        elif box.need_id:
                            Logger.debug(f"Need to ID {item_name}.")
                        else:
                            #Logger.debug(f"Discarding {json.dumps(item_properties.as_dict(), indent = 4)}")
                            Logger.debug(f"Discarding {item_name}.")

                        # sell if not keeping item, vendor is open, and item type can be traded
                        if vendor_open and item_can_be_traded and not (box.keep or box.need_id):
                            box.sell = True
                            transfer_items([box], action = "sell")
                            continue

                        # if item is to be kept and is already ID'd or doesn't need ID, log and stash
                        if (box.keep and not box.need_id):
                            if game_stats is not None:
                                game_stats.log_item_keep(item_name, True, item_box.img, item_box.ocr_result.text, expression, item_properties.as_dict())
                        # if item is to be kept or still needs to be sold or identified, append to list
                        if box.keep or sell or box.need_id:
                            # save item info
                            boxes.append(box)
                        else:
                            # if item isn't going to be kept (or sold if vendor window not open), trash it
                            transfer_items([box], action = "drop")
                        wait(0.05, 0.2)
                    else:
                        failed = True
                except AttributeError as e:
                    failed = True
                    # * Drop item.
                    Logger.info(f"Dropping {item_name}. Failed with AttributeError {e}")
                    transfer_items([box], action = "drop")


        if failed:
            log_item_fail(hovered_item, slot)

    if close_window:
        common.close()
    return boxes

def transfer_items(items: list, action: str = "drop", img: np.ndarray = None) -> list:
    #requires open inventory / stash / vendor
    if not items:
        return []
    img = img if img is not None else grab(True)
    filtered = []
    left_panel_open = is_visible(ScreenObjects.LeftPanel, img)
    match action:
        case "drop":
            filtered = [ item for item in items if item.keep == False and item.sell == False ]
        case "sell":
            filtered = [ item for item in items if item.keep == False and item.sell == True ]
            if not left_panel_open:
                Logger.error(f"transfer_items: Can't perform, vendor is not open")
        case "stash":
            if is_visible(ScreenObjects.GoldBtnStash, img):
                filtered = [ item for item in items if item.keep == True ]
            else:
                Logger.error(f"transfer_items: Can't perform, stash is not open")
        case _:
            Logger.error(f"transfer_items: incorrect action param={action}")
    if filtered:
        # if dropping, control+click to drop unless left panel is open, then drag to middle
        # if stashing, control+click to stash
        # if selling, control+click to sell
        if (action == "drop" and not left_panel_open) or action in ["sell", "stash"]:
            keyboard.send('ctrl', do_release=False)
            wait(0.1, 0.2)
        for item in filtered:
            pre_hover_img = grab(True)
            _, slot_img = common.get_slot_pos_and_img(pre_hover_img, item.column, item.row)
            if not common.slot_has_item(slot_img):
                # item no longer exists in that position...
                Logger.debug(f"Item at {item.pos} doesn't exist, skip and remove from list")
                for cnt, o_item in enumerate(items):
                    if o_item.pos == item.pos:
                        items.pop(cnt)
                        break
                continue
            # move to item position and left click
            mouse.move(*item.pos, randomize=4, delay_factor=[0.2, 0.4])
            wait(0.2, 0.4)
            pre_transfer_img = grab(True)
            mouse.press(button="left")
            # wait for inventory image to update indicating successful transfer / item select
            success = wait_for_update(pre_transfer_img, Config().ui_roi["open_inventory_area"], 3)
            mouse.release(button="left")
            if not success:
                Logger.warning(f"transfer_items: inventory unchanged after attempting to {action} item at position {item.pos}")
                break
            else:
                # if dropping, drag item to middle if vendor/stash is open
                if action == "drop" and left_panel_open:
                    center_mouse()
                    wait(0.04, 0.08)
                    mouse.press(button="left")
                    wait(0.2, 0.3)
                    mouse.release(button="left")
                # item successfully transferred, delete from list
                Logger.debug(f"Confirmed {action} at position {item.pos}")
                for cnt, o_item in enumerate(items):
                    if o_item.pos == item.pos:
                        items.pop(cnt)
                        break
                if action == "sell":
                    # check and see if inventory gold count changed
                    if (gold_unchanged := not wait_for_update(pre_transfer_img, Config().ui_roi["inventory_gold_digits"], 3)):
                        Logger.info("Inventory gold is full, force stash")
                    set_inventory_gold_full(gold_unchanged)
    keyboard.send('ctrl', do_press=False)
    return items

def update_tome_key_needs(img: np.ndarray = None, item_type: str = "tp") -> bool:
    img = open(img)
    if item_type.lower() in ["tp", "id"]:
        match = template_finder.search(
            [f"{item_type.upper()}_TOME", f"{item_type.upper()}_TOME_RED"],
            img,
            roi = Config().ui_roi["restricted_inventory_area"],
            best_match = True,
            )
        if match.valid:
            if match.name == f"{item_type.upper()}_TOME_RED":
                consumables.set_needs(item_type, 20)
                return True
            # else the tome exists and is not empty, continue
        else:
            Logger.debug(f"update_tome_key_needs: could not find {item_type}")
            return False
    elif item_type.lower() in ["key"]:
        match = template_finder.search("INV_KEY", img, roi = Config().ui_roi["restricted_inventory_area"])
        if not match.valid:
            return False
    else:
        Logger.error(f"update_tome_key_needs failed, item_type: {item_type} not supported")
        return False
    mouse.move(*match.center_monitor, randomize=4, delay_factor=[0.5, 0.7])
    wait(0.2, 0.2)
    hovered_item = grab(True)
    # get the item description box
    item_properties, item_box = d2r_image.get_hovered_item(hovered_item)
    if item_box is not None:
        try:
            quantity = int(item_properties.NTIPAliasStat[NTIP_STATS["quantity"]])
            max_quantity = int(item_properties.NTIPAliasStat[NTIP_STATS["quantitymax"]])
            consumables.set_needs(item_type, max_quantity - quantity)
        except Exception as e:
            Logger.error(f"update_tome_key_needs: unable to parse quantity for {item_type}. Exception: {e}")
    else:
        Logger.error(f"update_tome_key_needs: Failed to capture item description box for {item_type}")
        if Config().general["info_screenshots"]:
            cv2.imwrite("./log/screenshots/info/failed_capture_item_description_box" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
        return False
    return True