from typing import List
import keyboard
import time
import cv2
import itertools
import os
import numpy as np

from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, color_filter

from logger import Logger
from config import Config, ItemProps
from screen import Screen
from item import ItemFinder
from template_finder import TemplateFinder

from messages import Messenger
from game_stats import GameStats


class UiManager():
    """Everything that is clicking on some static 2D UI or is checking anything in regard to it should be placed here."""

    def __init__(self, screen: Screen, template_finder: TemplateFinder, game_stats: GameStats = None):
        self._config = Config()
        self._template_finder = template_finder
        self._messenger = Messenger()
        self._game_stats = game_stats
        self._screen = screen
        self._gold_full = False
        self._gambling_round = 1
        self._curr_stash = {
            "items": 3 if self._config.char["fill_shared_stash_first"] else 0,
            "gold": 0
        } #0: personal, 1: shared1, 2: shared2, 3: shared3

    def use_wp(self, act: int, idx: int):
        """
        Use Waypoint. The menu must be opened when calling the function.
        :param act: Index of the desired act starting at 1 [A1 = 1, A2 = 2, A3 = 3, ...]
        :param idx: Index of the waypoint from top. Note that it start at 0!
        """
        str_to_idx_map = {"WP_A1_ACTIVE": 1, "WP_A2_ACTIVE": 2, "WP_A3_ACTIVE": 3, "WP_A4_ACTIVE": 4, "WP_A5_ACTIVE": 5}
        template_match = self._template_finder.search([*str_to_idx_map], self._screen.grab(), threshold=0.7, best_match=True, roi=self._config.ui_roi["wp_act_roi"])
        curr_active_act = str_to_idx_map[template_match.name] if template_match.valid else -1
        if curr_active_act != act:
            pos_act_btn = (self._config.ui_pos["wp_act_i_btn_x"] + self._config.ui_pos["wp_act_btn_width"] * (act - 1), self._config.ui_pos["wp_act_i_btn_y"])
            x, y = self._screen.convert_screen_to_monitor(pos_act_btn)
            mouse.move(x, y, randomize=8)
            mouse.click(button="left")
            wait(0.3, 0.4)
        pos_wp_btn = (self._config.ui_pos["wp_first_btn_x"], self._config.ui_pos["wp_first_btn_y"] + self._config.ui_pos["wp_btn_height"] * idx)
        x, y = self._screen.convert_screen_to_monitor(pos_wp_btn)
        mouse.move(x, y, randomize=[60, 9], delay_factor=[0.9, 1.4])
        wait(0.4, 0.5)
        mouse.click(button="left")
        # wait till loading screen is over
        if self.wait_for_loading_screen(5):
            while 1:
                if not self.wait_for_loading_screen(0.2):
                    return True
        return False

    def is_right_skill_active(self) -> bool:
        """
        :return: Bool if skill is red/available or not. Skill must be selected on right skill slot when calling the function.
        """
        roi = [
            self._config.ui_pos["skill_right_x"] - (self._config.ui_pos["skill_width"] // 2),
            self._config.ui_pos["skill_y"] - (self._config.ui_pos["skill_height"] // 2),
            self._config.ui_pos["skill_width"],
            self._config.ui_pos["skill_height"]
        ]
        img = cut_roi(self._screen.grab(), roi)
        avg = np.average(img)
        return avg > 75.0

    def is_right_skill_selected(self, template_list: List[str]) -> bool:
        """
        :return: Bool if skill is currently the selected skill on the right skill slot.
        """
        for template in template_list:
            if self._template_finder.search(template, self._screen.grab(), threshold=0.84, roi=self._config.ui_roi["skill_right"]).valid:
                return True
        return False

    def is_left_skill_selected(self, template_list: List[str]) -> bool:
        """
        :return: Bool if skill is currently the selected skill on the left skill slot.
        """
        for template in template_list:
            if self._template_finder.search(template, self._screen.grab(), threshold=0.84, roi=self._config.ui_roi["skill_left"]).valid:
                return True
        return False

    def is_overburdened(self) -> bool:
        """
        :return: Bool if the last pick up overburdened your char. Must be called right after picking up an item.
        """
        img = cut_roi(self._screen.grab(), self._config.ui_roi["is_overburdened"])
        _, filtered_img = color_filter(img, self._config.colors["gold"])
        templates = [cv2.imread("assets/templates/inventory_full_msg_0.png"), cv2.imread("assets/templates/inventory_full_msg_1.png")]
        for template in templates:
            _, filtered_template = color_filter(template, self._config.colors["gold"])
            res = cv2.matchTemplate(filtered_img, filtered_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.8:
                return True
        return False

    def wait_for_loading_screen(self, time_out: float = None) -> bool:
        """
        Waits until loading screen apears
        :param time_out: Maximum time to search for a loading screen
        :return: True if loading screen was found within the timeout. False otherwise
        """
        start = time.time()
        while True:
            img = self._screen.grab()
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 1.5
            if is_loading_black_roi:
                return True
            if time_out is not None and time.time() - start > time_out:
                return False

    def save_and_exit(self, does_chicken: bool = False) -> bool:
        """
        Performes save and exit action from within game
        :return: Bool if action was successful
        """
        start = time.time()
        while (time.time() - start) < 15:
            templates = ["SAVE_AND_EXIT_NO_HIGHLIGHT","SAVE_AND_EXIT_HIGHLIGHT"]
            if not self._template_finder.search(templates, self._screen.grab(), roi=self._config.ui_roi["save_and_exit"], threshold=0.85).valid:
                keyboard.send("esc")
            wait(0.3)
            exit_btn_pos = (self._config.ui_pos["save_and_exit_x"], self._config.ui_pos["save_and_exit_y"])
            x_m, y_m = self._screen.convert_screen_to_monitor(exit_btn_pos)
            # TODO: Add hardcoded coordinates to ini file
            away_x_m, away_y_m = self._screen.convert_abs_to_monitor((-167, 0))
            while self._template_finder.search_and_wait(templates, roi=self._config.ui_roi["save_and_exit"], time_out=1.5, take_ss=False).valid:
                delay = [0.9, 1.1]
                if does_chicken:
                    delay = [0.3, 0.4]
                mouse.move(x_m, y_m, randomize=[38, 7], delay_factor=delay)
                wait(0.03, 0.06)
                mouse.press(button="left")
                wait(0.06, 0.1)
                mouse.release(button="left")
                if does_chicken:
                    # lets just try again just in case
                    wait(0.05, 0.08)
                    # mouse.click(button="left")
                wait(1.5, 2.0)
                mouse.move(away_x_m, away_y_m, randomize=40, delay_factor=[0.6, 0.9])
                wait(0.1, 0.5)
            return True
        return False

    def start_game(self) -> bool:
        """
        Starting a game. Will wait and retry on server connection issue.
        :return: Bool if action was successful
        """
        Logger.debug("Wait for Play button")
        while 1:
            img = self._screen.grab()
            found_btn_off = self._template_finder.search(["PLAY_BTN", "PLAY_BTN_GRAY"], img, roi=self._config.ui_roi["offline_btn"], threshold=0.8, best_match=True, normalize_monitor=True)
            found_btn_on = self._template_finder.search(["PLAY_BTN", "PLAY_BTN_GRAY"], img, roi=self._config.ui_roi["online_btn"], threshold=0.8, best_match=True, normalize_monitor=True)
            found_btn = found_btn_off if found_btn_off.valid else found_btn_on
            if found_btn.name == "PLAY_BTN":
                Logger.debug(f"Found Play Btn")
                mouse.move(*found_btn.center, randomize=[35, 7], delay_factor=[1.0, 1.8])
                wait(0.1, 0.15)
                mouse.click(button="left")
                break
            wait(2.0, 3.0)

        difficulty=self._config.general["difficulty"].upper()
        while 1:
            template_match = self._template_finder.search_and_wait(["LOADING", f"{difficulty}_BTN"], time_out=8, roi=self._config.ui_roi["difficulty_select"], threshold=0.9, normalize_monitor=True)
            if not template_match.valid:
                Logger.debug(f"Could not find {difficulty}_BTN, try from start again")
                return self.start_game()
            if template_match.name == "LOADING":
                Logger.debug(f"Found {template_match.name} screen")
                return True
            mouse.move(*template_match.center, randomize=[50, 9], delay_factor=[1.0, 1.8])
            wait(0.15, 0.2)
            mouse.click(button="left")
            break

        # check for server issue
        wait(2.0)
        server_issue = self._template_finder.search("SERVER_ISSUES", self._screen.grab()).valid
        if server_issue:
            Logger.warning("Server connection issue. waiting 20s")
            x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["issue_occured_ok_x"], self._config.ui_pos["issue_occured_ok_y"]))
            mouse.move(x, y, randomize=10, delay_factor=[2.0, 4.0])
            mouse.click(button="left")
            wait(1, 2)
            keyboard.send("esc")
            wait(18, 22)
            return self.start_game()
        else:
            return True

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

    def _inventory_has_items(self, img, num_loot_columns: int, num_ignore_columns=0) -> bool:
        """
        Check if Inventory has any items
        :param img: Img from screen.grab() with inventory open
        :param num_loot_columns: Number of columns to check from left
        :return: Bool if inventory still has items or not
        """
        for column, row in itertools.product(range(num_ignore_columns, num_loot_columns), range(4)):
            _, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                return True
        return False

    def _keep_item(self, item_finder: ItemFinder, img: np.ndarray, do_logging: bool = True) -> bool:
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
            if ("potion" in x.name) or (self._config.items[x.name].pickit_type == 0): continue
            include_props = self._config.items[x.name].include
            exclude_props = self._config.items[x.name].exclude
            #Disable include params for uniq, rare, magical if ident is disabled in params.ini
            #if (not self._config.char["id_items"]) and ("uniq" in x.name or "magic" in x.name or "rare" in x.name or "set" in x.name):
            if (not self._config.char["id_items"]) and any(item_type in x.name for item_type in ["uniq", "magic", "rare", "set"]):
                include_props = False
                exclude_props = False
            if not (include_props or exclude_props):
                if do_logging:
                    Logger.debug(f"{x.name}: Stashing")
                filtered_list.append(x)
                continue
            include = True
            include_logic_type = self._config.items[x.name].include_type
            if include_props:
                include = False
                found_props=[]
                for prop in include_props:
                    if len(prop)>1:
                        found_subprops=[]
                        for subprop in prop:
                            try:
                                template_match = self._template_finder.search(subprop, img, threshold=0.95)
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
                            template_match = self._template_finder.search(prop, img, threshold=0.95)
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
            exclude_logic_type = self._config.items[x.name].exclude_type
            if exclude_props:
                found_props=[]
                for prop in exclude_props:
                    try:
                        template_match = self._template_finder.search(prop, img, threshold=0.97)
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

    def stash_all_items(self, num_loot_columns: int, item_finder: ItemFinder, gamble = False):
        """
        Stashing all items in inventory. Stash UI must be open when calling the function.
        :param num_loot_columns: Number of columns used for loot from left
        """
        Logger.debug("Searching for inventory gold btn...")
        # Move cursor to center
        x, y = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
        # Wait till gold btn is found
        gold_btn = self._template_finder.search_and_wait("INVENTORY_GOLD_BTN", roi=self._config.ui_roi["gold_btn"], time_out=20, normalize_monitor=True)
        if not gold_btn.valid:
            Logger.error("Could not determine to be in stash menu. Continue...")
            return
        Logger.debug("Found inventory gold btn")
        if not gamble:
            # stash gold
            if self._config.char["stash_gold"]:
                inventory_no_gold = self._template_finder.search("INVENTORY_NO_GOLD", self._screen.grab(), roi=self._config.ui_roi["inventory_gold"], threshold=0.83)
                if inventory_no_gold.valid:
                    Logger.debug("Skipping gold stashing")
                else:
                    Logger.debug("Stashing gold")
                    self._move_to_stash_tab(min(3, self._curr_stash["gold"]))
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
                    inventory_no_gold = self._template_finder.search("INVENTORY_NO_GOLD", self._screen.grab(), roi=self._config.ui_roi["inventory_gold"], threshold=0.83)
                    if not inventory_no_gold.valid:
                        Logger.info("Stash tab is full of gold, selecting next stash tab.")
                        self._curr_stash["gold"] += 1
                        if self._config.general["info_screenshots"]:
                            cv2.imwrite("./info_screenshots/info_gold_stash_full_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                        if self._curr_stash["gold"] > 3:
                            #decide if gold pickup should be disabled or gambling is active
                            if self._config.char["gamble_items"]:
                                self._gold_full = True
                            else:
                                # turn off gold pickup
                                self._config.turn_off_goldpickup()
                                # inform user about it
                                msg = "All stash tabs and character are full of gold, turn of gold pickup"
                                Logger.info(msg)
                                if self._config.general["custom_message_hook"]:
                                    self._messenger.send_message(msg=f"{self._config.general['name']}: {msg}")
                        else:
                            # move to next stash
                            wait(0.5, 0.6)
                            return self.stash_all_items(num_loot_columns, item_finder)
        else:
            self.transfer_shared_to_private_gold (self._gambling_round)
        # stash stuff
        self._move_to_stash_tab(self._curr_stash["items"])
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            img = self._screen.grab()
            slot_pos, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                # check item again and discard it or stash it
                wait(1.2, 1.4)
                hovered_item = self._screen.grab()
                found_items = self._keep_item(item_finder, hovered_item)
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
                    did_stash_test_img = self._screen.grab()
                    if len(self._keep_item(item_finder, did_stash_test_img, False)) > 0:
                        Logger.debug("Wanted to stash item, but its still in inventory. Assumes full stash. Move to next.")
                        break
                    else:
                        self._game_stats.log_item_keep(found_items[0].name, self._config.items[found_items[0].name].pickit_type == 2, hovered_item)
                else:
                    # make sure there is actually an item
                    time.sleep(0.3)
                    curr_pos = mouse.get_position()
                    # move mouse away from inventory, for some reason it was sometimes included in the grabed img
                    x, y = self._screen.convert_abs_to_monitor((0, 0))
                    mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
                    item_check_img = self._screen.grab()
                    mouse.move(*curr_pos, randomize=2)
                    wait(0.4, 0.6)
                    slot_pos, slot_img = self.get_slot_pos_and_img(self._config, item_check_img, column, row)
                    if self._slot_has_item(slot_img):
                        if self._config.general["info_screenshots"]:
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
        x, y = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(x, y, randomize=[40, 200], delay_factor=[1.0, 1.5])
        img = self._screen.grab()
        if self._inventory_has_items(img, num_loot_columns):
            Logger.info("Stash page is full, selecting next stash")
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)

            # if filling shared stash first, we decrement from 3, otherwise increment
            self._curr_stash["items"] += -1 if self._config.char["fill_shared_stash_first"] else 1
            if (self._config.char["fill_shared_stash_first"] and self._curr_stash["items"] < 0) or self._curr_stash["items"] > 3:
                Logger.error("All stash is full, quitting")
                if self._config.general["custom_message_hook"]:
                    self._messenger.send_stash()
                os._exit(1)
            else:
                # move to next stash
                wait(0.5, 0.6)
                return self.stash_all_items(num_loot_columns, item_finder)

        Logger.debug("Done stashing")
        wait(0.4, 0.5)

    def transfer_shared_to_private_gold (self, count: int):
        for x in range (3):
            self._move_to_stash_tab (count)
            stash_gold_btn = self._template_finder.search("INVENTORY_GOLD_BTN", self._screen.grab(), roi=self._config.ui_roi["gold_btn_stash"], threshold=0.83)
            if stash_gold_btn.valid:
                x,y = self._screen.convert_screen_to_monitor(stash_gold_btn.center)
                mouse.move(x, y, randomize=4)
                wait (0.4, 0.5)
                mouse.press(button="left")
                wait (0.1, 0.15)
                mouse.release(button="left")
                wait (0.1, 0.15)
                keyboard.send ("Enter")
                wait (0.1, 0.15)
                self._move_to_stash_tab (0)
                inventory_gold_btn = self._template_finder.search("INVENTORY_GOLD_BTN", self._screen.grab(), roi=self._config.ui_roi["gold_btn"], threshold=0.83)
                if inventory_gold_btn.valid:
                    x,y = self._screen.convert_screen_to_monitor(inventory_gold_btn.center)
                    mouse.move(x, y, randomize=4)
                    wait (0.4, 0.5)
                    mouse.press(button="left")
                    wait (0.1, 0.15)
                    mouse.release(button="left")
                    wait (0.1, 0.15)
                    keyboard.send ("Enter")
                    wait (0.1, 0.15)
        self._gambling_round += 1

    def should_stash(self, num_loot_columns: int):
        """
        Check if there are items that need to be stashed in the inventory
        :param num_loot_columns: Number of columns used for loot from left
        """
        wait(0.2, 0.3)
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.7, 1.0)
        should_stash = self._inventory_has_items(self._screen.grab(), num_loot_columns)
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.4, 0.6)
        return should_stash

    def close_vendor_screen(self):
        keyboard.send("esc")
        # just in case also bring cursor to center and click
        # x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["center_x"], self._config.ui_pos["center_y"]))
        # mouse.move(x, y, randomize=25, delay_factor=[1.0, 1.5])
        # mouse.click(button="left")

    def repair_and_fill_up_tp(self) -> bool:
        """
        Repair and fills up TP buy selling tome and buying. Vendor inventory needs to be open!
        :return: Bool if success
        """
        repair_btn = self._template_finder.search_and_wait("REPAIR_BTN", roi=self._config.ui_roi["repair_btn"], time_out=4, normalize_monitor=True)
        if not repair_btn.valid:
            return False
        mouse.move(*repair_btn.center, randomize=12, delay_factor=[1.0, 1.5])
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
        tp_tome = self._template_finder.search_and_wait(["TP_TOME", "TP_TOME_RED"], roi=self._config.ui_roi["right_inventory"], time_out=3, normalize_monitor=True)
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
        tp_tome = self._template_finder.search_and_wait("TP_TOME", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if not tp_tome.valid:
            return False
        keyboard.send('ctrl', do_release=False)
        mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="right")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        # delay to make sure the tome has time to transfer to other inventory before closing window
        tp_tome = self._template_finder.search_and_wait("TP_TOME", roi=self._config.ui_roi["right_inventory"], time_out=3)
        if not tp_tome.valid:
            return False
        return True

    def has_tps(self) -> bool:
        """
        :return: Returns True if botty has town portals available. False otherwise
        """
        if self._config.char["tp"]:
            keyboard.send(self._config.char["tp"])
            template_match = self._template_finder.search_and_wait(
                ["TP_ACTIVE", "TP_INACTIVE"],
                roi=self._config.ui_roi["skill_right"],
                best_match=True,
                threshold=0.79,
                time_out=4)
            if not template_match.valid:
                Logger.warning("You are out of tps")
                if self._config.general["info_screenshots"]:
                    cv2.imwrite("./info_screenshots/debug_out_of_tps_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return template_match.valid
        else:
            return False

    def repair_needed(self) -> bool:
        template_match = self._template_finder.search(
            "REPAIR_NEEDED",
            self._screen.grab(),
            roi=self._config.ui_roi["repair_needed"],
            use_grayscale=True)
        return template_match.valid

    def gambling_needed(self) -> bool:
        return self._gold_full

    def set__gold_full (self, bool: bool):
        self._gold_full = bool
        self._gambling_round = 1

    def gamble(self, item_finder: ItemFinder):
        gold = True
        gamble_on = True
        if self._config.char["num_loot_columns"]%2==0:
            ignore_columns = self._config.char["num_loot_columns"]-1
        else:
            ignore_columns = self._config.char["num_loot_columns"]-2
        template_match = self._template_finder.search_and_wait("REFRESH", threshold=0.79, time_out=4)
        if template_match.valid:
            #Gambling window is open. Starting to spent some coins
            while (gamble_on and gold):
                if (self._inventory_has_items (self._screen.grab(),self._config.char["num_loot_columns"], ignore_columns) and self._inventory_has_items (self._screen.grab(),2)):
                    gamble_on = False
                    self.close_vendor_screen ()
                    break
                for item in self._config.char["gamble_items"]:
                    template_match_item = self._template_finder.search (item.upper(), self._screen.grab(), roi=self._config.ui_roi["left_inventory"], normalize_monitor=True)
                    while not template_match_item.valid:
                        #Refresh gambling screen
                        template_match = self._template_finder.search ("REFRESH", self._screen.grab(), normalize_monitor=True)
                        if (template_match.valid):
                            mouse.move(*template_match.center, randomize=12, delay_factor=[1.0, 1.5])
                            wait(0.1, 0.15)
                            mouse.click(button="left")
                            wait(0.1, 0.15)
                        template_match_item = self._template_finder.search (item.upper(), self._screen.grab(), roi=self._config.ui_roi["left_inventory"], normalize_monitor=True)
                    #item found in gambling menu
                    mouse.move(*template_match_item.center, randomize=12, delay_factor=[1.0, 1.5])
                    wait(0.1, 0.15)
                    mouse.click(button="right")
                    wait(0.1, 0.15)
                    template_match = self._template_finder.search ("no_gold".upper(), self._screen.grab(), threshold= 0.90)
                    #check if gold is av
                    if template_match.valid:
                        gold = False
                        self.close_vendor_screen ()
                        break
                    for column, row in itertools.product(range(self._config.char["num_loot_columns"]), range(4)):
                        img = self._screen.grab()
                        slot_pos, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
                        if self._slot_has_item(slot_img):
                            x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                            mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                            # check item again and discard it or stash it
                            wait(1.2, 1.4)
                            hovered_item = self._screen.grab()
                            if not self._keep_item(item_finder, hovered_item):
                                keyboard.send('ctrl', do_release=False)
                                wait(0.1, 0.15)
                                mouse.click (button="left")
                                wait(0.1, 0.15)
                                keyboard.send('ctrl', do_press=False)
            #Stashing needed
        else:
            Logger.warning("gambling failed")

    def enable_no_pickup(self) -> bool:
        """
        Checks the best match between enabled and disabled an retrys if already set.
        :return: Returns True if we succesfully set the nopickup option
        """
        keyboard.send('enter')
        wait(0.1, 0.25)
        keyboard.write('/nopickup',delay=.20)
        keyboard.send('enter')
        wait(0.1, 0.25)
        no_pickup = self._template_finder.search_and_wait(["ITEM_PICKUP_ENABLED","ITEM_PICKUP_DISABLED"], roi=self._config.ui_roi["no_pickup"], best_match=True, time_out=3)
        if not no_pickup.valid:
            return False
        if no_pickup.name == "ITEM_PICKUP_DISABLED":
            return True
        keyboard.send('enter')
        wait(0.1, 0.25)
        keyboard.send('up')
        wait(0.1, 0.25)
        keyboard.send('enter')
        wait(0.1, 0.25)
        return True

    def buy_pots(self, healing_pots: int = 0, mana_pots: int = 0):
        """
        Buy pots from vendors. Vendor inventory needs to be open!
        :param healing_pots: Number of healing pots to buy
        :param mana_pots: Number of mana pots to buy
        """
        h_pot = self._template_finder.search_and_wait("SUPER_HEALING_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if h_pot.valid is False:  # If not available in shop, try to shop next best potion.
            h_pot = self._template_finder.search_and_wait("GREATER_HEALING_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True)
        if h_pot.valid:
            mouse.move(*h_pot.center, randomize=8, delay_factor=[1.0, 1.5])
            for _ in range(healing_pots):
                mouse.click(button="right")
                wait(0.9, 1.1)

        m_pot = self._template_finder.search_and_wait("SUPER_MANA_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3,normalize_monitor=True)
        if m_pot.valid is False:  # If not available in shop, try to shop next best potion.
            m_pot = self._template_finder.search_and_wait("GREATER_MANA_POTION", roi=self._config.ui_roi["left_inventory"], time_out=3,normalize_monitor=True)
        if m_pot.valid:
            mouse.move(*m_pot.center, randomize=8, delay_factor=[1.0, 1.5])
            for _ in range(mana_pots):
                mouse.click(button="right")
                wait(0.9, 1.1)


# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")
    print("Start")
    from config import Config
    config = Config()
    game_stats = GameStats()
    screen = Screen()
    template_finder = TemplateFinder(screen)
    item_finder = ItemFinder()
    ui_manager = UiManager(screen, template_finder, game_stats)
    ui_manager.gamble (item_finder)
