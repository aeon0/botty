from typing import List
import keyboard
import time
import cv2
import os
import numpy as np

from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, color_filter

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder


class UiManager():
    """Everything that is clicking on some static 2D UI or is checking anything in regard to it should be placed here."""

    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._template_finder = template_finder
        self._screen = screen

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
            found_btn_off = self._template_finder.search(["PLAY_BTN", "PLAY_BTN_GRAY"], img, roi=self._config.ui_roi["offline_btn"], threshold=0.8, best_match=True)
            found_btn_on = self._template_finder.search(["PLAY_BTN", "PLAY_BTN_GRAY"], img, roi=self._config.ui_roi["online_btn"], threshold=0.8, best_match=True)
            found_btn = found_btn_off if found_btn_off.valid else found_btn_on
            if found_btn.name == "PLAY_BTN":
                x, y = self._screen.convert_screen_to_monitor(found_btn.position)
                Logger.debug(f"Found Play Btn")
                mouse.move(x, y, randomize=[35, 7], delay_factor=[1.0, 1.8])
                wait(0.1, 0.15)
                mouse.click(button="left")
                break
            wait(2.0, 3.0)

        difficulty=self._config.general["difficulty"].upper()
        while 1:
            template_match = self._template_finder.search_and_wait(["LOADING", f"{difficulty}_BTN"], time_out=8, roi=self._config.ui_roi["difficulty_select"], threshold=0.9)
            if not template_match.valid:
                Logger.debug(f"Could not find {difficulty}_BTN, try from start again")
                return self.start_game()
            if template_match.name == "LOADING":
                Logger.debug(f"Found {template_match.name} screen")
                return True
            x, y = self._screen.convert_screen_to_monitor(template_match.position)
            mouse.move(x, y, randomize=[50, 9], delay_factor=[1.0, 1.8])
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

    def repair_needed(self) -> bool:
        template_match = self._template_finder.search(
            "REPAIR_NEEDED",
            self._screen.grab(),
            roi=self._config.ui_roi["repair_needed"],
            use_grayscale=True)
        return template_match.valid

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

    def center_mouse(self):
        center_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*center_m, randomize=20)


# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")
    print("Start")
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder)
    #ui_manager.stash_all_items(5, item_finder)
