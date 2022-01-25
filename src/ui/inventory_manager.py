from dataclasses import dataclass
import numpy as np
from typing import List
import keyboard
import itertools
import cv2
import os
import time
import parse

from utils.misc import wait, trim_black, color_filter, is_in_roi, mask_by_roi
from utils.custom_mouse import mouse

from game_stats import GameStats
from messenger import Messenger
from logger import Logger
from config import Config
from screen import Screen
from item import ItemFinder
from item import ItemCropper
from template_finder import TemplateFinder

@dataclass
class BoxInfo:
    img: np.ndarray = None
    pos: list = None
    column: int = None
    row: int = None
    need_id: bool = False
    sell: bool = False
    keep: bool = False

class InventoryManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder, game_stats: GameStats = None):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._game_stats = game_stats
        self._messenger = Messenger()
        self._item_cropper = ItemCropper(self._template_finder)
        self._curr_stash = {
            "items": 3 if self._config.char["fill_shared_stash_first"] else 0,
            "gold": 0
        }

    @staticmethod
    def _slot_has_item(slot_img: np.ndarray) -> bool:
        """
        Check if a specific slot in the inventory has an item or not based on color
        :param slot_img: Image of the slot
        :return: Bool if there is an item or not
        """
        slot_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
        avg_brightness = np.average(slot_img[:, :, 2])
        return avg_brightness > 16.0

    @staticmethod
    def get_slot_pos_and_img(config: Config, img: np.ndarray, column: int, row: int) -> tuple[tuple[int, int],  np.ndarray]:
        """
        Get the pos and img of a specific slot position in Inventory. Inventory must be open in the image.
        :param config: The config which should be used
        :param img: Image from screen.grab() not cut
        :param column: Column in the Inventory
        :param row: Row in the Inventory
        :return: Returns position and image of the cut area as such: [[x, y], img]
        """
        top_left_slot = (config.ui_pos["inventory_top_left_slot_x"], config.ui_pos["inventory_top_left_slot_y"])
        slot_width = config.ui_pos["slot_width"]
        slot_height= config.ui_pos["slot_height"]
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

    def _inventory_has_items(self) -> bool:
        """
        Check if Inventory has any items
        :param img: Img from screen.grab() with inventory open
        :param num_loot_columns: Number of columns to check from left
        :return: Bool if inventory still has items or not
        """
        self.toggle_inventory("open")
        img = self._screen.grab()
        for column, row in itertools.product(range(self._config.char["num_loot_columns"]), range(4)):
            _, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                return True
        return False

    def _find_color_diff_roi(self, img_pre, img_post):
        try:
            diff = cv2.absdiff(img_pre, img_post)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            diff_thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)[1]

            blue_mask, _ = color_filter(img_pre, self._config.colors["blue_slot"])
            red_mask, _ = color_filter(img_pre, self._config.colors["red_slot"])
            green_mask, _ = color_filter(img_post, self._config.colors["green_slot"])

            blue_red_mask = np.bitwise_or(blue_mask, red_mask)
            final = np.bitwise_and.reduce([blue_red_mask, green_mask, diff_thresh])
            #cv2.imwrite("./info_screenshots/diff_roi_final_" + time.strftime("%Y%m%d_%H%M%S") + ".png", final)
            _, roi = trim_black(final)
            return roi
        except:
            Logger.error("_find_color_diff_roi failed")
            return None

    def _inspect_items(self, item_finder: ItemFinder) -> bool:
        """
        Iterate over all picked items in inventory--ID items and decide which to stash
        :param img: Image in which the item is searched (item details should be visible)
        """
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        img = self._screen.grab()
        # check if inventory open
        inventory_open = self._template_finder.search("CLOSE_PANEL", img, roi = self._config.ui_roi["right_panel_header"], threshold = 0.9).valid
        if not inventory_open:
            self.toggle_inventory("open")
            img = self._screen.grab()
        slots = []
        # check which slots have items
        for column, row in itertools.product(range(self._config.char["num_loot_columns"]), range(4)):
            slot_pos, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                slots.append([slot_pos, row, column])
        boxes = []
        # iterate over slots with items
        item_rois = []
        for count, slot in enumerate(slots):
            img = self._screen.grab()
            x_m, y_m = self._screen.convert_screen_to_monitor(slot[0])
            # ignore this slot if it lies within in a previous item's ROI
            skip = False
            for item_roi in item_rois:
                if is_in_roi(item_roi, slot[0]):
                    skip = True
                    break
            if skip: continue
            delay = [0.2, 0.3] if count else [1, 1.3]
            mouse.move(x_m, y_m, randomize = 10, delay_factor = delay)
            wait(0.3, 0.5)
            hovered_item = self._screen.grab()
            # get the item description box
            try:
                item_box = self._item_cropper.crop_item_descr(hovered_item)[0]
            except:
                Logger.error(f"item_cropper failed for slot_pos: {slot[0]}")
                if self._config.general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/failed_item_box_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                continue
            if item_box.color:
                # determine the item's ROI in inventory
                pre = mask_by_roi(img, self._config.ui_roi["inventory"])
                post = mask_by_roi(hovered_item, self._config.ui_roi["inventory"])
                extend_roi = item_box.roi[:]
                extend_roi[3] = extend_roi[3] + 30
                item_roi = self._find_color_diff_roi(mask_by_roi(pre, extend_roi, type = "inverse"), mask_by_roi(post, extend_roi, type = "inverse"))
                if item_roi:
                    item_rois.append(item_roi)
                # determine whether the item can be sold
                sell = False
                if self._config.char["sell_items"] and not (item_box.ocr_result.text.lower() in ["key of ", "essense of", "wirt's", "jade figurine"]):
                    sell = True
                # attempt to identify item
                need_id = False
                if self._config.char["id_items"]:
                    is_unidentified = self._template_finder.search("UNIDENTIFIED", item_box.data, threshold = 0.9).valid
                    if is_unidentified:
                        need_id = True
                        mouse.move(*center_m, randomize=20)
                        tome_state, tome_pos = self._tome_state(self._screen.grab(), tome_type="id")
                    if is_unidentified and tome_state is not None and tome_state == "ok":
                        self._id_item_with_tome([x_m, y_m], tome_pos)
                        need_id = False
                        # recapture box after ID
                        mouse.move(x_m, y_m, randomize = 4, delay_factor = delay)
                        wait(0.3, 0.5)
                        hovered_item = self._screen.grab()
                        item_box = self._item_cropper.crop_item_descr(hovered_item)[0]
                Logger.debug(f"OCR ITEM DESCR: Mean conf: {item_box.ocr_result.mean_confidence}")
                for i, line in enumerate(list(filter(None, item_box.ocr_result.text.splitlines()))):
                    Logger.debug(f"OCR LINE{i}: {line}")
                if self._config.general["loot_screenshots"]:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite("./loot_screenshots/ocr_box_" + timestamp + "_o.png", item_box.ocr_result.original_img)
                    cv2.imwrite("./loot_screenshots/ocr_box_" + timestamp + "_n.png", item_box.ocr_result.processed_img)

                # decide whether to keep item
                result = self._keep_item(item_finder, item_box)
                keep = False if result is None else True
                if keep: sell = False

                box = BoxInfo(
                    img = item_box.data,
                    pos = [x_m, y_m],
                    column = slot[2],
                    row = slot[1],
                    need_id = need_id,
                    sell = sell,
                    keep = keep
                )
                if keep:
                    self._game_stats.log_item_keep(result.name, self._config.items[result.name].pickit_type == 2, item_box.data, result.ocr_result.text)
                if keep or sell or need_id:
                    # save item info
                    boxes.append(box)
                else:
                    # if item isn't going to be sold or kept, drop it
                    Logger.debug(f"Dropping {item_box.ocr_result.text.splitlines()[0]}")
                    self._transfer_items([box], action = "drop", close = False)
                wait(0.3, 0.5)
        self.toggle_inventory("close")
        return boxes

    def _transfer_items(self, items: list, action: str = "drop", close: bool = True) -> list:
        img = self._screen.grab()
        left_panel_open = stash_open = False
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        if action == "drop":
            inventory_open = self._template_finder.search("CLOSE_PANEL", img, roi = self._config.ui_roi["right_panel_header"], threshold = 0.9).valid
            if not inventory_open:
                self.toggle_inventory()
            else:
                left_panel_open = self._template_finder.search("CLOSE_PANEL", img, roi = self._config.ui_roi["left_panel_header"], threshold = 0.9).valid
            filtered = [ item for item in items if item.keep == False and item.sell == False ]
        elif action == "sell":
            left_panel_open = self._template_finder.search("CLOSE_PANEL", img, roi = self._config.ui_roi["left_panel_header"], threshold = 0.9).valid
            if left_panel_open:
                filtered = [ item for item in items if item.keep == False and item.sell == True ]
            else:
                Logger.error(f"_handle_items: Can't perform, vendor is not open")
                filtered = []
        elif action == "stash":
            stash_open = self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn"], threshold = 0.9).valid
            if stash_open:
                left_panel_open = True
                filtered = [ item for item in items if item.keep == True ]
            else:
                Logger.error(f"_handle_items: Can't perform, stash is not open")
                filtered = []
        else:
            Logger.error(f"_handle_items: incorrect action param={action}")
            filtered = []
        if filtered:
            # if dropping, control+click to drop unless left panel is open, then drag to middle
            # if stashing, control+click to stash
            # if selling, control+click to sell
            if (action == "drop" and not left_panel_open) or action in ["sell", "stash"]:
                keyboard.send('ctrl', do_release=False)
                wait(0.2, 0.4)
            for item in filtered:
                attempts = 0
                while True:
                    mouse.move(item.pos[0], item.pos[1], randomize=4, delay_factor=[0.2, 0.4])
                    wait(0.2, 0.4)
                    if self._config.general["info_screenshots"]:
                        cv2.imwrite("./info_screenshots/info" + action + "_item_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                    mouse.press(button="left")
                    wait(0.2, 0.4)
                    mouse.release(button="left")
                    wait(0.2, 0.4)
                    if action == "drop" and left_panel_open:
                        mouse.move(*center_m, randomize=20)
                        wait(0.2, 0.3)
                        mouse.press(button="left")
                        wait(0.2, 0.3)
                        mouse.release(button="left")
                        wait(0.2, 0.3)
                    # check if item is still there
                    slot_img = self.get_slot_pos_and_img(self._config, self._screen.grab(), item.column, item.row)[1]
                    if self._slot_has_item(slot_img):
                        attempts += 1
                    else:
                        # items.remove(item) # causes ValueError sometimes
                        for cnt, o_item in enumerate(items):
                            if o_item.pos == item.pos:
                                items.pop(cnt)
                                break
                        break
                    if attempts > 1:
                        return items
            if (action == "drop" and not left_panel_open) or action in ["sell", "stash"]:
                keyboard.send('ctrl', do_press=False)
            wait(0.2, 0.3)
            if close:
                self.toggle_inventory("close")
        return items

    def _id_item_with_tome(self, item_location: list, id_tome_location: list):
        mouse.move(id_tome_location[0], id_tome_location[1], randomize=4, delay_factor=[0.4, 0.8])
        wait(0.2, 0.4)
        mouse.click(button="right")
        wait(0.2, 0.4)
        mouse.move(item_location[0], item_location[1], randomize=4, delay_factor=[0.4, 0.8])
        wait(0.2, 0.4)
        mouse.click(button="left")
        wait(0.2, 0.4)

    def _keep_item(self, item_finder: ItemFinder, item_box, do_logging: bool = True) -> bool:
        """
        Check if an item should be kept, the item should be hovered and in own inventory when function is called
        :param item_finder: ItemFinder to check if item is in pickit
        :param item_box: result object from item_cropper.crop_item_descr()
        :param do_logging: Bool value to turn on/off logging for items that are found and should be kept
        :return: Bool if item should be kept
        """
        wait(0.2, 0.3)
        # as long as we are using template matching to decide whether to keep item the base name template will be near top
        ymax = 50 if item_box.data.shape[0] < 50 else item_box.data.shape[0]
        img = item_box.data[0:ymax,:]
        try:
            found_item = item_finder.search(img)[0]
        except:
            Logger.debug(f"item_finder returned None or error for {item_box.ocr_result.text.split()[0]}")
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/failed_found_item_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
            return None
        if ("potion".casefold() in found_item.name.casefold()) or (self._config.items[found_item.name].pickit_type == 0):
            return None
        setattr(found_item, "ocr_result", item_box["ocr_result"])
        include_props = self._config.items[found_item.name].include
        exclude_props = self._config.items[found_item.name].exclude
        if not (include_props or exclude_props):
            if do_logging:
                Logger.debug(f"{found_item.name}: Stashing")
            return found_item
        include = True
        include_logic_type = self._config.items[found_item.name].include_type
        if include_props:
            include = False
            found_props=[]
            for prop in include_props:
                try:
                    template_match = self._template_finder.search(prop, img, threshold=0.95)
                except:
                    Logger.error(f"{found_item.name}: can't find template file for required {prop}, assume prop is present just in case")
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
            return None
        exclude = False
        exclude_logic_type = self._config.items[found_item.name].exclude_type
        if exclude_props:
            found_props=[]
            for prop in exclude_props:
                try:
                    template_match = self._template_finder.search(prop, img, threshold=0.97)
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
            return found_item
        return None

    def _move_to_stash_tab(self, stash_idx: int):
        """Move to a specifc tab in the stash
        :param stash_idx: idx of the stash starting at 0 (personal stash)
        """
        str_to_idx_map = {"STASH_0_ACTIVE": 0, "STASH_1_ACTIVE": 1, "STASH_2_ACTIVE": 2, "STASH_3_ACTIVE": 3}
        template_match = self._template_finder.search([*str_to_idx_map], self._screen.grab(), threshold=0.7, best_match=True, roi=self._config.ui_roi["stash_btn_roi"])
        curr_active_stash = str_to_idx_map[template_match.name] if template_match.valid else -1
        if curr_active_stash != stash_idx:
            # select the start stash
            personal_stash_pos = (self._config.ui_pos["stash_personal_btn_x"], self._config.ui_pos["stash_personal_btn_y"])
            stash_btn_width = self._config.ui_pos["stash_btn_width"]
            next_stash_pos = (personal_stash_pos[0] + stash_btn_width * stash_idx, personal_stash_pos[1])
            x_m, y_m = self._screen.convert_screen_to_monitor(next_stash_pos)
            mouse.move(x_m, y_m, randomize=[30, 7], delay_factor=[1.0, 1.5])
            wait(0.2, 0.3)
            mouse.click(button="left")
            wait(0.3, 0.4)

    def stash_all_items(self, item_finder: ItemFinder, items: list):
        """
        Stashing all items in inventory. Stash UI must be open when calling the function.
        """
        Logger.debug("Searching for inventory gold btn...")
        # Move cursor to center
        x, y = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
        # Wait till gold btn is found
        gold_btn = self._template_finder.search_and_wait("INVENTORY_GOLD_BTN", roi=self._config.ui_roi["gold_btn"], time_out=20)
        if not gold_btn.valid:
            Logger.error("Could not determine to be in stash menu. Continue...")
            return None
        Logger.debug("Found inventory gold btn")
        # stash gold
        if self._config.char["stash_gold"]:
            inventory_no_gold = self._template_finder.search("INVENTORY_NO_GOLD", self._screen.grab(), roi=self._config.ui_roi["inventory_gold"], threshold=0.83)
            if inventory_no_gold.valid:
                Logger.debug("Skipping gold stashing")
            else:
                Logger.debug("Stashing gold")
                self._move_to_stash_tab(min(3, self._curr_stash["gold"]))
                x, y = self._screen.convert_screen_to_monitor(gold_btn.position)
                mouse.move(x, y, randomize=4)
                wait(0.1, 0.15)
                mouse.press(button="left")
                wait(0.25, 0.35)
                mouse.release(button="left")
                wait(0.4, 0.6)
                keyboard.send("enter") #if stash already full of gold just nothing happens -> gold stays on char -> no popup window
                wait(1.0, 1.2)
                # move cursor away from button to interfere with screen grab
                mouse.move(-120, 0, absolute=False, randomize=15)
                inventory_no_gold = self._template_finder.search("INVENTORY_NO_GOLD", self._screen.grab(), roi=self._config.ui_roi["inventory_gold"], threshold=0.83)
                if not inventory_no_gold.valid:
                    Logger.info("Stash tab is full of gold, selecting next stash tab.")
                    self._curr_stash["gold"] += 1
                    if self._config.general["info_screenshots"]:
                        cv2.imwrite("./info_screenshots/info_gold_stash_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                    if self._curr_stash["gold"] > 3:
                        # turn off gold pickup
                        self._config.turn_off_goldpickup()
                        # inform user about it
                        Logger.info("All stash tabs and character are full of gold, turn of gold pickup")
                        if self._config.general["custom_message_hook"]:
                            self._messenger.send_gold()
                    else:
                        # move to next stash
                        wait(0.5, 0.6)
                        return self.stash_all_items(item_finder, items)
        self._move_to_stash_tab(self._curr_stash["items"])
        # check if stash tab is completely full (no empty slots)
        # while self._curr_stash["items"] <= 3:
        #     img = self._screen.grab()
        #     found_empty_slot = self._template_finder.search("STASH_EMPTY_SLOT", img, roi = self._config.ui_roi["vendor_stash"], threshold = 0.85)
        #     if found_empty_slot.valid:
        #         break
        #     else:
        #         Logger.info(f"Stash tab completely full, advance to next")
        #         if self._config.general["info_screenshots"]:
        #                 cv2.imwrite("./info_screenshots/stash_tab_completely_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        #         self._curr_stash["items"] += -1 if self._config.char["fill_shared_stash_first"] else 1
        #         if (self._config.char["fill_shared_stash_first"] and self._curr_stash["items"] < 0) or self._curr_stash["items"] > 3:
        #             self.stash_full()
        #         self._move_to_stash_tab(self._curr_stash["items"])
        # stash stuff
        while True:
            items = self._transfer_items(items, action = "stash", close = False)
            if items and any([item.keep for item in items]):
                # could not stash all items, stash tab is likely full
                Logger.debug("Wanted to stash item, but it's still in inventory. Assumes full stash. Move to next.")
                if self._config.general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                self._curr_stash["items"] += -1 if self._config.char["fill_shared_stash_first"] else 1
                if (self._config.char["fill_shared_stash_first"] and self._curr_stash["items"] < 0) or self._curr_stash["items"] > 3:
                    self.stash_full()
                self._move_to_stash_tab(self._curr_stash["items"])
            else:
                break
        Logger.debug("Done stashing")
        wait(0.4, 0.5)
        self.toggle_inventory("close")
        return items

    def stash_full(self):
        Logger.error("All stash is full, quitting")
        if self._config.general["custom_message_hook"]:
            self._messenger.send_stash()
        os._exit(1)

    def toggle_inventory(self, action: str = None):
        """
        Open/close inventory panel
        """
        wait(0.7, 1.0)
        if action == "open":
            inventory_open = self._template_finder.search("CLOSE_PANEL", self._screen.grab(), roi = self._config.ui_roi["right_panel_header"], threshold = 0.9).valid
            if not inventory_open:
                keyboard.send(self._config.char["inventory_screen"])
                wait(0.4, 0.6)
                inventory_open = self._template_finder.search_and_wait("CLOSE_PANEL", roi = self._config.ui_roi["right_panel_header"], threshold = 0.9, time_out = 2).valid
                if not inventory_open:
                    # might need to close a dialogue box or something
                    keyboard.send("esc")
                    wait(0.7, 1)
                    keyboard.send(self._config.char["inventory_screen"])
                    wait(0.4, 0.6)
                    inventory_open = self._template_finder.search_and_wait("CLOSE_PANEL", roi = self._config.ui_roi["right_panel_header"], threshold = 0.9, time_out = 2).valid
                    if not inventory_open:
                        Logger.error("could not open inventory")
        elif action == "close":
            inventory_open = self._template_finder.search("CLOSE_PANEL", self._screen.grab(), roi = self._config.ui_roi["right_panel_header"], threshold = 0.9).valid
            if inventory_open:
                keyboard.send("esc")
        else:
            inventory_open = self._template_finder.search("CLOSE_PANEL", self._screen.grab(), roi = self._config.ui_roi["right_panel_header"], threshold = 0.9).valid
            if inventory_open:
                keyboard.send("esc")
            else:
                keyboard.send(self._config.char["inventory_screen"])
        wait(0.4, 0.6)

    def _tome_state(self, in_img: np.ndarray, tome_type: str = "tp"):
        tome_found = self._template_finder.search([f"{tome_type.upper()}_TOME", f"{tome_type.upper()}_TOME_RED"], in_img, roi = self._config.ui_roi["inventory"], threshold = 0.9, best_match = True)
        if tome_found.valid:
            if tome_found.name == f"{tome_type.upper()}_TOME":
                state = "ok"
            else:
                state = "empty"
            position = self._screen.convert_screen_to_monitor(tome_found.position)
        else:
            state = position = None
        return state, position

    def exchange_tomes(self) -> bool:
        """
        Sells and buys back tomes from vendor
        :return: Bool for success/failure
        """
        repair_btn = self._template_finder.search("REPAIR_BTN", self._screen.grab(), roi=self._config.ui_roi["repair_btn"]).valid
        if not repair_btn:
            return False
        # sell
        sold_tomes = []
        start = time.time()
        while True:
            tome = self._template_finder.search(["ID_TOME", "ID_TOME_RED", "TP_TOME", "TP_TOME_RED"], self._screen.grab(), roi=self._config.ui_roi["inventory"], threshold=0.8)
            if not tome.valid:
                break
            if "ID" in tome.name:
                sold_tomes.append("ID_TOME")
            if "TP" in tome.name:
                sold_tomes.append("TP_TOME")
            x, y = self._screen.convert_screen_to_monitor(tome.position)
            keyboard.send('ctrl', do_release=False)
            mouse.move(x, y, randomize=8, delay_factor=[0.7, 1])
            wait(0.1, 0.15)
            mouse.press(button="left")
            wait(0.25, 0.35)
            mouse.release(button="left")
            wait(0.3, 0.5)
            keyboard.send('ctrl', do_press=False)
            if time.time() - start > 5:
                Logger.error("Couldn't sell tomes")
                return False
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*center_m, randomize=20)
        # buy back
        for sold_tome in sold_tomes:
            tome = self._template_finder.search_and_wait(sold_tome, roi=self._config.ui_roi["vendor_stash"], time_out=2)
            if not tome.valid:
                Logger.error(f"Couldn't buy back {sold_tome}")
                return False
            x, y = self._screen.convert_screen_to_monitor(tome.position)
            keyboard.send('ctrl', do_release=False)
            mouse.move(x, y, randomize=8, delay_factor=[0.7, 1])
            wait(0.1, 0.15)
            mouse.click(button="right")
            wait(0.3, 0.5)
            keyboard.send('ctrl', do_press=False)
            start = time.time()
            # check buy back
            while True:
                tome = self._template_finder.search_and_wait(sold_tome, roi=self._config.ui_roi["inventory"], time_out=2)
                if tome.valid:
                    break
                if time.time() - start > 5:
                    Logger.error(f"Couldn't verify {sold_tome} buyback")
                    return False
        return True

    def repair(self) -> bool:
        """
        Repair items. Vendor inventory needs to be open!
        :return: Bool if success
        """
        repair_btn = self._template_finder.search_and_wait("REPAIR_BTN", roi=self._config.ui_roi["repair_btn"], time_out=4)
        if not repair_btn.valid:
            return False
        x, y = self._screen.convert_screen_to_monitor(repair_btn.position)
        mouse.move(x, y, randomize=12, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.1, 0.15)
        x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["vendor_misc_x"], self._config.ui_pos["vendor_misc_y"]))
        mouse.move(x, y, randomize=[20, 6], delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        # another click to dismiss popup message in case you have not enough gold to repair, preventing tome not being bought back
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.5, 0.6)
        return True

    def buy_pots(self, healing_pots: int = 0, mana_pots: int = 0):
        """
        Buy pots from vendors. Vendor inventory needs to be open!
        :param healing_pots: Number of healing pots to buy
        :param mana_pots: Number of mana pots to buy
        """
        h_pot = self._template_finder.search_and_wait("SUPER_HEALING_POTION", roi=self._config.ui_roi["vendor_stash"], time_out=3)
        if h_pot.valid is False:  # If not available in shop, try to shop next best potion.
            h_pot = self._template_finder.search_and_wait("GREATER_HEALING_POTION", roi=self._config.ui_roi["vendor_stash"], time_out=3)
        if h_pot.valid:
            x, y = self._screen.convert_screen_to_monitor(h_pot.position)
            mouse.move(x, y, randomize=8, delay_factor=[1.0, 1.5])
            for _ in range(healing_pots):
                mouse.click(button="right")
                wait(0.9, 1.1)

        m_pot = self._template_finder.search_and_wait("SUPER_MANA_POTION", roi=self._config.ui_roi["vendor_stash"], time_out=3)
        if m_pot.valid is False:  # If not available in shop, try to shop next best potion.
            m_pot = self._template_finder.search_and_wait("GREATER_MANA_POTION", roi=self._config.ui_roi["vendor_stash"], time_out=3)
        if m_pot.valid:
            x, y = self._screen.convert_screen_to_monitor(m_pot.position)
            mouse.move(x, y, randomize=8, delay_factor=[1.0, 1.5])
            for _ in range(mana_pots):
                mouse.click(button="right")
                wait(0.9, 1.1)

    def get_consumible_quantity(self, img: np.ndarray = None, item_type: str = "tp"):
        self.toggle_inventory("open")
        if img is None:
            img = self._screen.grab()
        if item_type.lower() in ["tp", "id"]:
            state, pos = self._tome_state(img, item_type)
            if not state:
                return None
            if state == "empty":
                return 0
            # else the tome exists and is not empty, continue
        elif item_type.lower() in ["key", "keys"]:
            result = self._template_finder.search("INV_KEY", img, roi=self._config.ui_roi["inventory"], threshold=0.9)
            if not result.valid:
                return None
            pos = self._screen.convert_screen_to_monitor(result.position)
        else:
            Logger.error(f"get_quantity failed, item_type:{item_type} not supported")
            return None
        mouse.move(pos[0], pos[1], randomize=4, delay_factor=[0.5, 0.7])
        wait(0.2, 0.4)
        hovered_item = self._screen.grab()
        # get the item description box
        try:
            item_box = self._item_cropper.crop_item_descr(hovered_item, ocr_language="engd2r_inv_th_fast")[0]
            result = parse.search("Quantity: {:d}", item_box.ocr_result.text).fixed[0]
            return result
        except:
            Logger.error(f"get_consumible_quantity: Failed to capture item description box for {item_type}")
            return None

if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")
    print("Start")
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    template_finder = TemplateFinder(screen)
    item_finder = ItemFinder()
    inventory_manager = InventoryManager(screen, template_finder, game_stats)
    inventory_manager._inspect_items(item_finder)