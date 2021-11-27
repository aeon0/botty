from screen import Screen
from template_finder import TemplateFinder
from typing import Tuple
from utils.custom_mouse import mouse
import keyboard
import time
import cv2
import itertools
import os
import numpy as np
from logger import Logger
from utils.misc import wait, cut_roi, color_filter, send_discord
from config import Config
from item_finder import ItemFinder


class UiManager():
    """Everything that is clicking on some static 2D UI or is checking anything in regard to it should be placed here."""

    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._template_finder = template_finder
        self._screen = screen
        self._curr_stash = 0 # 0: personal, 1: shared1, 2: shared2, 3: shared3

    def use_wp(self, act: int, idx: int):
        """
        Use Waypoint. The menu must be opened when calling the function.
        :param act: Index of the act from left. Note that it start at 0. e.g. Act5 -> act=4
        :param idx: Index of the waypoint from top. Note that it start at 0.
        """
        # Note: We are currently only in act 5, thus no need to click here.
        # pos_act_btn = (self._config.ui_pos["wp_act_i_btn_x"] + self._config.ui_pos["wp_act_btn_width"] * act, self._config.ui_pos["wp_act_i_btn_y"])
        # x, y = self._screen.convert_screen_to_monitor(pos_act_btn)
        # mouse.move(x, y, randomize=8)
        # mouse.click(button="left")
        # wait(0.3, 0.4)
        pos_wp_btn = (self._config.ui_pos["wp_first_btn_x"], self._config.ui_pos["wp_first_btn_y"] + self._config.ui_pos["wp_btn_height"] * idx)
        x, y = self._screen.convert_screen_to_monitor(pos_wp_btn)
        mouse.move(x, y, randomize=[110, 20], delay_factor=[0.9, 1.4])
        wait(0.4, 0.5)
        mouse.click(button="left")

    def can_teleport(self) -> bool:
        """
        :return: Bool if teleport is red/available or not. Teleport skill must be selected on right skill slot when calling the function.
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

    def is_teleport_selected(self) -> bool:
        """
        :return: Bool if teleport is currently the selected skill on the right skill slot.
        """
        roi = [
            self._config.ui_pos["skill_right_x"] - (self._config.ui_pos["skill_width"] // 2),
            self._config.ui_pos["skill_y"] - (self._config.ui_pos["skill_height"] // 2),
            self._config.ui_pos["skill_width"],
            self._config.ui_pos["skill_height"]
        ]
        if self._template_finder.search("TELE_ACTIVE", self._screen.grab(), threshold=0.94, roi=roi)[0]:
            return True
        if self._template_finder.search("TELE_INACTIVE", self._screen.grab(), threshold=0.94, roi=roi)[0]:
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

    def wait_for_loading_screen(self, time_out):
        start = time.time()
        while time.time() - start < time_out:
            img = self._screen.grab()
            is_loading_black_roi = np.average(img[:700, 0:250]) < 3.5
            if is_loading_black_roi:
                return True
        return False

    def save_and_exit(self, does_chicken: bool = False) -> bool:
        """
        Performes save and exit action from within game
        :return: Bool if action was successful
        """
        start = time.time()
        while (time.time() - start) < 15:
            keyboard.send("esc")
            wait(0.3)
            exit_btn_pos = (self._config.ui_pos["save_and_exit_x"], self._config.ui_pos["save_and_exit_y"])
            x_m, y_m = self._screen.convert_screen_to_monitor(exit_btn_pos)
            # TODO: Add hardcoded coordinates to ini file
            away_x_m, away_y_m = self._screen.convert_abs_to_monitor((int(-250 * self._config.scale), 0))
            templates = ["SAVE_AND_EXIT_NO_HIGHLIGHT","SAVE_AND_EXIT_HIGHLIGHT"]
            while self._template_finder.search_and_wait(templates, roi=self._config.ui_roi["save_and_exit"], time_out=1.5, take_ss=False)[0]:
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
        while 1:
            img = self._screen.grab()
            # search offline btn
            found_btn, _ = self._template_finder.search("PLAY_BTN", img, roi=self._config.ui_roi["go_btn"], threshold=0.8)
            score_enabled = self._template_finder.last_score
            self._template_finder.search("PLAY_BTN_GRAY", img, roi=self._config.ui_roi["go_btn"], threshold=0.8)
            score_disabled = self._template_finder.last_score
            found_btn = found_btn and score_enabled > score_disabled
            if found_btn:
                x_s = self._config.ui_pos["go_x"]
                pos = [x_s, self._config.ui_pos["go_y"]]
                x, y = self._screen.convert_screen_to_monitor(pos)
                Logger.debug(f"Found Play Btn")
                mouse.move(x, y, randomize=[50, 9], delay_factor=[1.0, 1.8])
                wait(0.1, 0.15)
                mouse.click(button="left")
                break
            else:
                # Might be in online mode?
                found_btn, _ = self._template_finder.search("PLAY_BTN", img, roi=self._config.ui_roi["play_btn"], threshold=0.8)
                if found_btn:
                    Logger.error("Botty only works for single player. Please switch to offline mode and restart botty!")
                    return False
            time.sleep(3.0)

        difficulty=self._config.general["difficulty"].lower()
        Logger.debug(f"Searching for {difficulty} Btn...")
        while 1:
            # edge case: if a player hasn't unlocked nightmare difficulty, there won't be an option to select difficulty after clicking play button
            wait(0.75,1.25)
            if self._template_finder.search("LOADING", self._screen.grab())[0]:
                Logger.debug("On loading screen, nightmare not unlocked")
                return True

            found, pos = self._template_finder.search_and_wait("NORMAL_BTN", roi=self._config.ui_roi["normal_btn"], time_out=8)

            if not found:
                Logger.debug("Could not find btn, try from start again")
                return self.start_game()

            x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos[f"{difficulty}_x"], self._config.ui_pos[f"{difficulty}_y"]))
            Logger.debug(f"Found {difficulty} Btn -> clicking it")
            mouse.move(x, y, randomize=[50, 9], delay_factor=[1.0, 1.8])
            wait(0.15, 0.2)
            mouse.click(button="left")
            break

        # check for server issue
        wait(2.0)
        server_issue, _ = self._template_finder.search("SERVER_ISSUES", self._screen.grab())
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
    def get_slot_pos_and_img(config: Config, img: np.ndarray, column: int, row: int) -> Tuple[Tuple[int, int],  np.ndarray]:
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

    def _inventory_has_items(self, img, num_loot_columns: int) -> bool:
        """
        Check if Inventory has any items
        :param img: Img from screen.grab() with inventory open
        :param num_loot_columns: Number of columns to check from left
        :return: Bool if inventory still has items or not
        """
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            _, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                return True
        return False

    def _keep_item(self, item_finder: ItemFinder) -> bool:
        """
        Check if an item should be kept, the item should be hovered and in own inventory when function is called
        :param item_finder: ItemFinder to check if item is in pickit
        :return: Bool if item should be kept
        """
        wait(0.2, 0.3)
        img = self._screen.grab()
        _, w, _ = img.shape
        img = img[:, (w//2):,:]
        item_list = item_finder.search(img)
        item_list = [x for x in item_list if "potion" not in x.name]
        return len(item_list) > 0

    def stash_all_items(self, num_loot_columns: int, item_finder: ItemFinder):
        """
        Stashing all items in inventory. Stash UI must be open when calling the function.
        :param num_loot_columns: Number of columns used for loot from left
        """
        # TODO: Do not stash portal scrolls and potions but throw them out of inventory on the ground!
        #       then the pickit check for potions and belt free can also be removed
        Logger.debug("Searching for inventory gold btn...")
        found, pos_gold_btn = self._template_finder.search_and_wait("INVENTORY_GOLD_BTN", roi=self._config.ui_roi["gold_btn"], time_out=20)
        if not found:
            Logger.error("Could not determine to be in stash menu. Continue...")
            return
        Logger.debug("Found inventory gold btn")
        # select the start stash
        personal_stash_pos = (self._config.ui_pos["stash_personal_btn_x"], self._config.ui_pos["stash_personal_btn_y"])
        stash_btn_width = self._config.ui_pos["stash_btn_width"]
        next_stash_pos = (personal_stash_pos[0] + stash_btn_width * self._curr_stash, personal_stash_pos[1])
        x_m, y_m = self._screen.convert_screen_to_monitor(next_stash_pos)
        mouse.move(x_m, y_m, randomize=[30, 7], delay_factor=[1.0, 1.5])
        wait(0.2, 0.3)
        mouse.click(button="left")
        wait(0.3, 0.4)
        # stash gold
        if self._config.char["stash_gold"]:
            x, y = self._screen.convert_screen_to_monitor(pos_gold_btn)
            mouse.move(x, y, randomize=4)
            wait(0.1, 0.15)
            mouse.press(button="left")
            wait(0.25, 0.35)
            mouse.release(button="left")
            wait(0.4, 0.6)
            keyboard.send("enter") #if stash already full of gold just nothing happens -> gold stays on char -> no popup window
        # stash stuff
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            img = self._screen.grab()
            slot_pos, slot_img = self.get_slot_pos_and_img(self._config, img, column, row)
            if self._slot_has_item(slot_img):
                x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                mouse.move(x_m, y_m, randomize=10, delay_factor=[1.0, 1.3])
                # check item again and discard it or stash it
                if self._keep_item(item_finder):
                    keyboard.send('ctrl', do_release=False)
                    wait(0.2, 0.25)
                    mouse.press(button="left")
                    wait(0.2, 0.25)
                    mouse.release(button="left")
                    wait(0.2, 0.25)
                    keyboard.send('ctrl', do_press=False)
                else:
                    # make sure there is actually an item
                    time.sleep(0.3)
                    hovered_item = self._screen.grab()
                    slot_pos, slot_img = self.get_slot_pos_and_img(self._config, hovered_item, column, row)
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
        top_left_slot = (self._config.ui_pos["inventory_top_left_slot_x"], self._config.ui_pos["inventory_top_left_slot_y"])
        move_to = (top_left_slot[0] - 300, top_left_slot[1] - 200)
        x, y = self._screen.convert_screen_to_monitor(move_to)
        mouse.move(x, y, randomize=40, delay_factor=[1.0, 1.5])
        img = self._screen.grab()
        if self._inventory_has_items(img, num_loot_columns):
            Logger.info("Stash page is full, selecting next stash")
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/debug_info_inventory_not_empty_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
            self._curr_stash += 1
            if self._curr_stash > 3:
                Logger.error("All stash is full, quitting")
                if self._config.general["custom_discord_hook"]:
                    send_discord(f"{self._config.general['name']} all stash is full, quitting", self._config.general["custom_discord_hook"])
                os._exit(1)
            else:
                # move to next stash
                wait(0.5, 0.6)
                return self.stash_all_items(num_loot_columns, item_finder)

        Logger.debug("Done stashing")
        wait(0.4, 0.5)
        keyboard.send("esc")

    def close_vendor_screen(self):
        keyboard.send("esc")
        # just in case also bring cursor to center and click
        x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["center_x"], self._config.ui_pos["center_y"]))
        mouse.move(x, y, randomize=25, delay_factor=[1.0, 1.5])
        mouse.click(button="left")

    def repair_and_fill_up_tp(self) -> bool:
        """
        Repair and fills up TP buy selling tomb and buying. Vendor inventory needs to be open!
        :return: Bool if success
        """
        found, pos_repair_abs = self._template_finder.search_and_wait("REPAIR_BTN", roi=self._config.ui_roi["repair_btn"], time_out=4)
        if not found:
            return False
        x, y = self._screen.convert_screen_to_monitor(pos_repair_abs)
        mouse.move(x, y, randomize=12, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.1, 0.15)
        x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["vendor_misc_x"], self._config.ui_pos["vendor_misc_y"]))
        mouse.move(x, y, randomize=[20, 6], delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.5, 0.6)
        found, pos_tp_inventory = self._template_finder.search_and_wait("TP_TOMB", roi=self._config.ui_roi["inventory"], time_out=3)
        if not found:
            return False
        x, y = self._screen.convert_screen_to_monitor(pos_tp_inventory)
        keyboard.send('ctrl', do_release=False)
        mouse.move(x, y, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.press(button="left")
        wait(0.25, 0.35)
        mouse.release(button="left")
        wait(0.5, 0.6)
        keyboard.send('ctrl', do_press=False)
        found, pos_tp_inventory = self._template_finder.search_and_wait("TP_TOMB", roi=self._config.ui_roi["vendor_stash"], time_out=3)
        if not found:
            return False
        x, y = self._screen.convert_screen_to_monitor(pos_tp_inventory)
        keyboard.send('ctrl', do_release=False)
        mouse.move(x, y, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="right")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        return True


# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    print("Start")
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    item_finder = ItemFinder()
    ui_manager = UiManager(screen, template_finder)
    ui_manager.start_game()
