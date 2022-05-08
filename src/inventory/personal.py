import itertools
from game_stats import GameStats
from item import ItemFinder, Item
from item.item_cropper import ItemText
from logger import Logger
from screen import grab, convert_screen_to_monitor
import keyboard
import cv2
import time
import numpy as np
from dataclasses import dataclass

from template_finder import TemplateFinder
from config import Config
from utils.misc import wait, is_in_roi, mask_by_roi
from utils.custom_mouse import mouse
from inventory import stash, common, vendor
from ui import view
from ui_manager import detect_screen_object, is_visible, select_screen_object_match, wait_until_visible, ScreenObjects, center_mouse, wait_for_update
from item import ItemCropper
from messages import Messenger

inv_gold_full = False
messenger = Messenger()
item_finder = ItemFinder()
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
    global inv_gold_full
    return inv_gold_full

def set_inventory_gold_full(bool):
    global inv_gold_full
    inv_gold_full = bool

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
    if items is None:
        Logger.debug("No items to stash, skip")
        return None
    center_mouse()
    # Wait for stash to fully load
    if not common.wait_for_left_inventory():
        Logger.error("stash_all_items(): Could not determine to be in stash menu. Continue...")
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
                if wait_until_visible(ScreenObjects.DepositBtn, 3).valid:
                    keyboard.send("enter") #if stash already full of gold just nothing happens -> gold stays on char -> no popup window
                else:
                    Logger.error("stash_all_items(): deposit button not detected, failed to stash gold")
                # move cursor away from button to interfere with screen grab
                mouse.move(-120, 0, absolute=False, randomize=15, delay_factor=[0.3, 0.5])
                # if 0 gold becomes visible in personal inventory then the stash tab still has room for gold
                stash_full_of_gold = not wait_until_visible(ScreenObjects.GoldNone, 1.5).valid
            if stash_full_of_gold:
                Logger.debug("Stash tab is full of gold, selecting next stash tab.")
                stash.set_curr_stash(gold = (stash.get_curr_stash()["gold"] + 1))
                if Config().general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/info_gold_stash_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                if stash.get_curr_stash()["gold"] > 3:
                    #decide if gold pickup should be disabled or gambling is active
                    vendor.set_gamble_status(True)
                else:
                    # move to next stash tab
                    return stash_all_items(items=items)
            else:
                set_inventory_gold_full(False)
    # check if stash tab is completely full (no empty slots)
    common.select_tab(stash.get_curr_stash()["items"])
    while stash.get_curr_stash()["items"] <= 3:
        img = grab()
        if is_visible(ScreenObjects.EmptyStashSlot, img):
            break
        else:
            Logger.debug(f"Stash tab completely full, advance to next")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/stash_tab_completely_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
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
                cv2.imwrite("./info_screenshots/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
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

def keep_item(item_box: ItemText = None, found_item: Item = None, do_logging: bool = True) -> bool:
    """
    Check if an item should be kept, the item should be hovered and in own inventory when function is called
    :param img: Image in which the item is searched (item details should be visible)
    :param do_logging: Bool value to turn on/off logging for items that are found and should be kept
    :return: Bool if item should be kept
    """
    ymax = 50 if item_box.data.shape[0] < 50 else item_box.data.shape[0]
    img = item_box.data[0:ymax,:]

    if any(x in found_item.name for x in ["potion", "misc_scroll"]) or found_item.name == "misc_key" or (Config().items[found_item.name].pickit_type == 0):
        return False
    setattr(found_item, "ocr_result", item_box["ocr_result"])

    include_props = Config().items[found_item.name].include
    exclude_props = Config().items[found_item.name].exclude

    if (
        #Disable include/exclude params for uniq, rare, magical if ident is disabled in params.ini
        (
            not Config().char["id_items"]
            and any(item_type in found_item.name for item_type in ["uniq", "magic", "rare", "set"])
        )
        # items that are checked to be kept should all be identified unless an error occurred or user preferred unidentified
        or is_visible(ScreenObjects.Unidentified, item_box.data)
    ):
        include_props = False
        exclude_props = False

    if not (include_props or exclude_props):
        if do_logging:
            Logger.debug(f"{found_item.name}: Stashing")
        return True
    include = True
    include_logic_type = Config().items[found_item.name].include_type
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
                        Logger.error(f"{found_item.name}: can't find template file for required {prop}, ignore just in case")
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
                    Logger.error(f"{found_item.name}: can't find template file for required {prop}, ignore just in case")
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
            Logger.debug(f"{found_item.name}: Discarding. Required {include_logic_type}({include_props})={include}")
        return False
    exclude = False
    exclude_logic_type = Config().items[found_item.name].exclude_type
    if exclude_props:
        found_props = []
        for prop in exclude_props:
            try:
                template_match = TemplateFinder().search(prop, img, threshold=0.97)
            except:
                Logger.error(f"{found_item.name}: can't find template file for exclusion {prop}, ignore just in case")
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
    if include and not exclude:
        if do_logging:
            Logger.debug(f"{found_item.name}: Stashing. Required {include_logic_type}({include_props})={include}, exclude {exclude_logic_type}({exclude_props})={exclude}")
        return True
    return False

def open(img: np.ndarray = None) -> np.ndarray:
    img = grab() if img is None else img
    if not is_visible(ScreenObjects.RightPanel, img):
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

def inspect_items(inp_img: np.ndarray = None, close_window: bool = True, game_stats: GameStats = None) -> list[BoxInfo]:
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
    for count, slot in enumerate(slots):
        failed = False
        # ignore this slot if it lies within in a previous item's ROI
        if any(is_in_roi(item_roi, slot[0]) for item_roi in item_rois): continue
        img = grab()
        x_m, y_m = convert_screen_to_monitor(slot[0])
        delay = [0.2, 0.3] if count else [1, 1.3]
        mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
        wait(0.1, 0.2)
        hovered_item = grab()
        # get the item description box
        item_box = ItemCropper().crop_item_descr(hovered_item)
        if item_box.valid:
            # determine the item's ROI in inventory
            cnt=0
            while True:
                pre = mask_by_roi(img, Config().ui_roi["open_inventory_area"])
                post = mask_by_roi(hovered_item, Config().ui_roi["open_inventory_area"])
                # will sometimes have equivalent diff if mouse ends up in an inconvenient place.
                if not np.array_equal(pre, post):
                    break
                Logger.debug(f"inspect_items: pre=post, try again. slot {slot[0]}")
                center_mouse()
                img = grab()
                mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
                wait(0.3, 0.5)
                hovered_item = grab()
                cnt += 1
                if cnt >= 2:
                    Logger.error(f"inspect_items: Unable to get item's inventory ROI, slot {slot[0]}")
                    break
            item_name = item_box.ocr_result.text.splitlines()[0] if not vendor_open else item_box.ocr_result.text.splitlines()[1]
            extend_roi = item_box.roi[:]
            extend_roi[3] = extend_roi[3] + 30
            item_roi = common.calc_item_roi(mask_by_roi(pre, extend_roi, type = "inverse"), mask_by_roi(post, extend_roi, type = "inverse"))
            if item_roi:
                item_rois.append(item_roi)
            # determine whether the item can be sold
            item_can_be_traded = not any(substring in item_name for substring in nontradable_items)
            sell = Config().char["sell_junk"] and item_can_be_traded
            # check and see if item exists in pickit
            try:
                found_item = item_finder.search(item_box.data)[0]
            except:
                Logger.debug(f"inspect_items: item_finder returned None or error for {item_name}, likely an accidental pick")
                Logger.debug(f"Dropping {item_name}")
                found_item = False
            # attempt to identify item
            need_id = False
            if Config().char["id_items"] and found_item:
                # if this item has no include or exclude properties, leave it unidentified
                implied_no_id = not (Config().items[found_item.name].include or Config().items[found_item.name].exclude)
                implied_no_id |= not any(item_type in found_item.name for item_type in ["uniq", "magic", "rare", "set"])
                if not implied_no_id:
                    if (is_unidentified := is_visible(ScreenObjects.Unidentified, item_box.data)):
                        need_id = True
                        center_mouse()
                        tome_state, tome_pos = common.tome_state(grab(), tome_type = "id", roi = Config().ui_roi["restricted_inventory_area"])
                    if is_unidentified and tome_state is not None and tome_state == "ok":
                        common.id_item_with_tome([x_m, y_m], tome_pos)
                        need_id = False
                        # recapture box after ID
                        mouse.move(x_m, y_m, randomize = 4, delay_factor = delay)
                        wait(0.2, 0.3)
                        hovered_item = grab()
                        item_box = ItemCropper().crop_item_descr(hovered_item)

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

                # decide whether to keep item
                keep = False
                if not need_id:
                    keep = keep_item(item_box, found_item) if found_item else False
                if keep:
                    sell = need_id = False

                box = BoxInfo(
                    img = item_box.data,
                    pos = (x_m, y_m),
                    column = slot[2],
                    row = slot[1],
                    need_id = need_id,
                    sell = sell,
                    keep = keep
                )
                # sell if not keeping item, vendor is open, and item type can be traded
                if not (keep or need_id) and vendor_open and item_can_be_traded:
                    Logger.debug(f"Selling {item_name}")
                    box.sell = True
                    transfer_items([box], action = "sell")
                    continue
                # if item is to be kept and is already ID'd or doesn't need ID, log and stash
                if game_stats is not None and (keep and not need_id):
                    game_stats.log_item_keep(found_item.name, Config().items[found_item.name].pickit_type == 2, item_box.data, item_box.ocr_result.text)
                # if item is to be kept or still needs to be sold or identified, append to list
                if keep or sell or need_id:
                    # save item info
                    boxes.append(box)
                else:
                    # if item isn't going to be kept (or sold if vendor window not open), trash it
                    Logger.debug(f"Dropping {item_name}")
                    transfer_items([box], action = "drop")
                wait(0.3, 0.5)
            else:
                failed = True
        else:
            failed = True
        if failed:
            Logger.error(f"item_cropper failed for slot_pos: {slot[0]}")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/failed_item_box_" + time.strftime("%Y%m%d_%H%M%S") + ".png", hovered_item)
    if close_window:
        if not is_visible(ScreenObjects.RightPanel, img):
            center_mouse()
        common.close()
    return boxes

def transfer_items(items: list, action: str = "drop", img: np.ndarray = None) -> list:
    #requires open inventory / stash / vendor
    img = img if img is not None else grab()
    filtered = []
    left_panel_open = is_visible(ScreenObjects.LeftPanel, img)
    if action == "drop":
        filtered = [ item for item in items if item.keep == False and item.sell == False ]
    elif action == "sell":
        filtered = [ item for item in items if item.keep == False and item.sell == True ]
        if not left_panel_open:
            Logger.error(f"transfer_items: Can't perform, vendor is not open")
    elif action == "stash":
        if is_visible(ScreenObjects.GoldBtnStash, img):
            filtered = [ item for item in items if item.keep == True ]
        else:
            Logger.error(f"transfer_items: Can't perform, stash is not open")
    else:
        Logger.error(f"transfer_items: incorrect action param={action}")
    if filtered:
        # if dropping, control+click to drop unless left panel is open, then drag to middle
        # if stashing, control+click to stash
        # if selling, control+click to sell
        if (action == "drop" and not left_panel_open) or action in ["sell", "stash"]:
            keyboard.send('ctrl', do_release=False)
            wait(0.1, 0.2)
        for item in filtered:
            pre_hover_img = grab()
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
            pre_transfer_img = grab()
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