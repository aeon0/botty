from screen import Screen
from template_finder import TemplateFinder
import mouse
from utils import custom_mouse, custom_keyboard
import keyboard # currently needed for a workaround
import random
import time
import cv2
import itertools
import os
import numpy as np
from logger import Logger
from utils.misc import wait, cut_roi
from config import Config
from utils.misc import color_filter


class UiManager():
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._template_finder = template_finder
        self._screen = screen
        self._curr_stash = 0 # 0: personal, 1: shared1, 2: shared2, 3: shared3

    def use_wp(self, act, idx):
        pos_act_btn = (self._config.ui_pos["wp_act_i_btn_x"] + self._config.ui_pos["wp_act_btn_width"] * act, self._config.ui_pos["wp_act_i_btn_y"])
        x, y = self._screen.convert_screen_to_monitor(pos_act_btn)
        custom_mouse.move(x, y, duration=0.4, randomize=5)
        mouse.click(button="left")
        wait(0.35, 0.4)
        pos_wp_btn = (self._config.ui_pos["wp_first_btn_x"], self._config.ui_pos["wp_first_btn_y"] + self._config.ui_pos["wp_btn_height"] * idx)
        x, y = self._screen.convert_screen_to_monitor(pos_wp_btn)
        custom_mouse.move(x, y, duration=0.4, randomize=5)
        mouse.click(button="left")

    def can_teleport(self):
        img = self._screen.grab()
        roi = [
            self._config.ui_pos["skill_right_x"] - (self._config.ui_pos["skill_width"] // 2),
            self._config.ui_pos["skill_y"] - (self._config.ui_pos["skill_height"] // 2),
            self._config.ui_pos["skill_width"],
            self._config.ui_pos["skill_height"]
        ]
        img = cut_roi(img, roi)
        avg = np.average(img)
        return avg > 75.0

    def is_teleport_selected(self):
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

    def is_overburdened(self):
        #TODO: 1920x1080 specific roi
        roi = [17, 765, 470, 90]
        img = self._screen.grab()
        img = cut_roi(img, roi)
        _, filtered_img = color_filter(img, self._config.colors["gold"])
        templates = [cv2.imread("assets/templates/inventory_full_msg_0.png"), cv2.imread("assets/templates/inventory_full_msg_1.png")]
        for template in templates:
            _, filtered_template = color_filter(template, self._config.colors["gold"])
            res = cv2.matchTemplate(filtered_img, filtered_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.8:
                return True
        return False

    @staticmethod
    def potion_type(img):
        avg_brightness = np.average(img)
        if avg_brightness < 47:
            return "empty"
        red_channel = img[:,:,2]
        redness = np.average(red_channel)
        blue_channel = img[:,:,0]
        blueness = np.average(blue_channel)
        if redness > blueness and redness > 55:
            return "health"
        if blueness > redness and blueness > 55:
            return "mana"
        return "empty"

    def check_free_belt_spots(self) -> bool:
        # currently only checks if a whole row is free
        img = self._screen.grab()
        for i in range(4):
            roi = [
                self._config.ui_pos["potion1_x"] - (self._config.ui_pos["potion_width"] // 2) + i * self._config.ui_pos["potion_next"],
                self._config.ui_pos["potion1_y"] - (self._config.ui_pos["potion_height"] // 2),
                self._config.ui_pos["potion_width"],
                self._config.ui_pos["potion_height"]
            ]
            potion_img = cut_roi(img, roi)
            potion_type = self.potion_type(potion_img)
            if potion_type == "empty":
                return True
        return False

    def save_and_exit(self):
        start = time.time()
        while (time.time() - start) < 10:
            keyboard.send("esc")
            wait(0.05)
            exit_btn_pos = (self._config.ui_pos["save_and_exit_x"], self._config.ui_pos["save_and_exit_y"])
            found, _ = self._template_finder.search_and_wait("SAVE_AND_EXIT", roi=[750, 350, 410, 260], time_out=2)
            if found:
                x_m, y_m = self._screen.convert_screen_to_monitor(exit_btn_pos)
                custom_mouse.move(x_m, y_m, duration=random.random()*0.05 + 0.15, randomize=10)
                mouse.click(button="left")
                break


    def start_hell_game(self):
        # expects to be in hero selection screen
        Logger.debug(f"Searching for Play Btn...")
        # TODO: roi is with respect to 1920x1080
        roi = [390, 760, 1150, 300]
        while 1:
            _, pos = self._template_finder.search_and_wait("PLAY_BTN", roi=roi)
            x_range_offline = [self._config.ui_pos["play_x_offline"] - 50, self._config.ui_pos["play_x_offline"] + 50]
            x_range_online = [self._config.ui_pos["play_x_online"] - 50, self._config.ui_pos["play_x_online"] + 50]
            y_range = [self._config.ui_pos["play_y"] - 50, self._config.ui_pos["play_y"] + 50]
            in_offline_range = x_range_offline[0] < pos[0] < x_range_offline[1]
            in_online_range = x_range_online[0] < pos[0] < x_range_online[1]
            mode_info = "online mode" if in_online_range else "offline mode"
            if (in_offline_range or in_online_range) and y_range[0] < pos[1] < y_range[1]:
                pos = [pos[0], self._config.ui_pos["play_y"]]
                x, y = self._screen.convert_screen_to_monitor(pos)
                Logger.debug(f"Found Play Btn ({mode_info}) -> clicking it")
                if mode_info == "online mode":
                    Logger.warning("You are currently creating a game in online mode!")
                custom_mouse.move(x, y, duration=(random.random() * 0.2 + 0.5), randomize=5)
                mouse.click(button="left")
                break
        Logger.debug("Searching for Hell Btn...")
        # TODO: roi is with respect to 1920x1080
        roi = [550, 100, 1000, 800]
        while 1:
            _, pos = self._template_finder.search_and_wait("HELL_BTN", roi=roi)
            # sanity x y check based on 1920x1080
            # note: not checking y range as it often detects nightmare button as hell btn, not sure why
            x_range = [self._config.ui_pos["hell_x"] - 50, self._config.ui_pos["hell_x"] + 50]
            if x_range[0] < pos[0] < x_range[1]:
                x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["hell_x"], self._config.ui_pos["hell_y"]))
                Logger.debug("Found Hell Btn -> clicking it")
                custom_mouse.move(x, y, duration=(random.random() * 0.2 + 0.5), randomize=5)
                mouse.click(button="left")
                break
        # check for server issue
        time.sleep(1.0)
        server_issue, _ = self._template_finder.search("SERVER_ISSUES", self._screen.grab())
        if server_issue:
            Logger.warning("Server issue. waiting 20s")
            x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["issue_occured_ok_x"], self._config.ui_pos["issue_occured_ok_y"]))
            custom_mouse.move(x, y, duration=(random.random() * 0.4 + 0.5), randomize=5)
            mouse.click(button="left")
            wait(1, 2)
            keyboard.send("esc")
            wait(16, 18)
            self.start_hell_game()

    @staticmethod
    def _slot_has_item(slot_img: np.ndarray) -> bool:
        slot_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
        avg_brightness = np.average(slot_img[:, :, 2])
        # TODO: magic param, move to param file (Could go as low as 11.0, but better be save, otherwise bot will stop cause "stash is full" if fails)
        return avg_brightness > 16.0

    def _get_slot_pos_and_img(self, img: np.ndarray, column: int, row: int):
        top_left_slot = (self._config.ui_pos["inventory_top_left_slot_x"], self._config.ui_pos["inventory_top_left_slot_y"])
        slot_width = self._config.ui_pos["slot_width"]
        slot_height= self._config.ui_pos["slot_height"]
        slot = (top_left_slot[0] + slot_width * column, top_left_slot[1] + slot_height * row)
        min_x = slot[0] + 7
        max_x = slot[0] + slot_width - 7
        min_y = slot[1] + 7
        max_y = slot[1] + slot_height - 7
        slot_img = img[min_y:max_y, min_x:max_x]
        center_pos = (int(slot[0] + (slot_width // 2)), int(slot[1] + (slot_height // 2)))
        return center_pos, slot_img

    def _inventory_has_items(self, img, num_loot_columns) -> bool:
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            _, slot_img = self._get_slot_pos_and_img(img, column, row)
            if self._slot_has_item(slot_img):
                return True
        return False

    def stash_all_items(self, num_loot_columns):
        # TODO: Do not stash portal scrolls and potions but throw them out of inventory on the ground!
        #       then the pickit check for potions and belt free can also be removed
        Logger.debug("Searching for inventory gold btn...")
        #TODO: 1920x1080 specific params
        gold_btn_pos = [self._config.ui_pos["inventory_gold_btn_x"], self._config.ui_pos["inventory_gold_btn_y"]]
        inventory_roi = [gold_btn_pos[0] - 120, gold_btn_pos[1] - 60, 400, 150]
        self._template_finder.search_and_wait("INVENTORY_GOLD_BTN", roi=inventory_roi)
        Logger.debug("Found inventory gold btn")
        # select the start stash
        personal_stash_pos = (self._config.ui_pos["stash_personal_btn_x"], self._config.ui_pos["stash_personal_btn_y"])
        stash_btn_width = self._config.ui_pos["stash_btn_width"]
        next_stash_pos = (personal_stash_pos[0] + stash_btn_width * self._curr_stash, personal_stash_pos[1])
        x_m, y_m = self._screen.convert_screen_to_monitor(next_stash_pos)
        custom_mouse.move(x_m, y_m, duration=(random.random() * 0.2 + 0.6), randomize=15)
        mouse.click(button="left")
        wait(0.3, 0.4)
        # stash stuff
        keyboard.send('ctrl', do_release=False)
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            img = self._screen.grab()
            slot_pos, slot_img = self._get_slot_pos_and_img(img, column, row)
            if self._slot_has_item(slot_img):
                x_m, y_m = self._screen.convert_screen_to_monitor(slot_pos)
                custom_mouse.move(x_m, y_m, duration=(random.random() * 0.2 + 0.3), randomize=6)
                wait(0.1, 0.15)
                mouse.click(button="left")
                wait(0.4, 0.6)
        keyboard.send('ctrl', do_press=False)
        Logger.debug("Check if stash is full")
        time.sleep(0.6)
        # move mouse away from inventory, for some reason it was sometimes included in the grabed img
        top_left_slot = (self._config.ui_pos["inventory_top_left_slot_x"], self._config.ui_pos["inventory_top_left_slot_y"])
        move_to = (top_left_slot[0] - 250, top_left_slot[1] - 250)
        x, y = self._screen.convert_screen_to_monitor(move_to)
        custom_mouse.move(x, y, duration=0.5, randomize=3)
        img = self._screen.grab()
        if self._inventory_has_items(img, num_loot_columns):
            Logger.info("Stash page is full, selecting next stash")
            cv2.imwrite("debug_info_inventory_not_empty.png", img)
            self._curr_stash += 1
            if self._curr_stash > 3:
                Logger.error("All stash is full, quitting")
                os._exit(1)
            else:
                # move to next stash
                wait(0.5, 0.6)
                return self.stash_all_items(num_loot_columns)

        Logger.debug("Done stashing")
        wait(0.5, 0.6)
        keyboard.send("esc")

    def fill_up_belt_from_inventory(self, num_loot_columns):
        # Find all pots in the inventory
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.7, 1.0)
        img = self._screen.grab()
        pot_positions = []
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            center_pos, slot_img = self._get_slot_pos_and_img(img, column, row)
            found = self._template_finder.search("SUPER_HEALING_POTION", slot_img, threshold=0.9)[0]
            found |= self._template_finder.search("SUPER_MANA_POTION", slot_img, threshold=0.9)[0]
            if found:
                pot_positions.append(center_pos)
        keyboard.press("shift")
        for pos in pot_positions:
            x, y = self._screen.convert_screen_to_monitor(pos)
            custom_mouse.move(x, y, duration=0.15, randomize=3)
            wait(0.1)
            mouse.click(button="left")
            wait(0.3, 0.4)
        keyboard.release("shift")
        wait(0.2, 0.25)
        keyboard.send(self._config.char["inventory_screen"])


# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder)
    # ui_manager.stash_all_items(6)
    # ui_manager.use_wp(4, 1)
    ui_manager.fill_up_belt_from_inventory(10)
