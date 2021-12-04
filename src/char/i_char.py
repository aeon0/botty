from typing import Tuple
from utils.custom_mouse import mouse
from template_finder import TemplateFinder
from ui_manager import UiManager
from screen import Screen
from utils.misc import wait, cut_roi
import cv2
import math
import keyboard
from logger import Logger
import time
from typing import Dict, Tuple, Union, List, Callable
from config import Config
import random


def abstract(f):
    def _decorator(*_):
        raise NotImplementedError(f"Method '{f.__name__}' is abstract")
    return _decorator

class IChar:
    def __init__(self, skill_hotkeys: Dict, char_config: Dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager):
        self._skill_hotkeys = skill_hotkeys
        self._char_config = char_config
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._screen = screen
        self._config = Config()
        self._last_tp = time.time()
        # It actually is 0.04s per frame but many people have issues with it (because of lag?)
        self._cast_duration = self._char_config["casting_frames"] * 0.05 + 0.04

    def pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
        mouse.move(pos[0], pos[1])
        time.sleep(0.1)
        mouse.click(button="left")
        wait(0.45,0.5)
        return prev_cast_start

    def select_by_template(self, template_type:  Union[str, List[str]], success_func: Callable = None, time_out: float = 8) -> bool:
        """
        Finds any template from the template finder and interacts with it
        :param template_type: Strings or list of strings of the templates that should be searched for
        :param success_func: Function that will return True if the interaction is successful e.g. return True when loading screen is reached, defaults to None
        :param time_out: Timeout for the whole template selection, defaults to None
        :return: True if success. False otherwise
        """
        if template_type == "A5_STASH":
            # sometimes waypoint is opened and stash not found because of that, check for that
            if self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid:
                keyboard.send("esc")
        Logger.debug(f"Select {template_type}")
        start = time.time()
        while time_out is not None or (time.time() - start) < time_out:
            template_match = self._template_finder.search(template_type, self._screen.grab())
            if template_match.valid:
                x_m, y_m = self._screen.convert_screen_to_monitor(template_match.position)
                mouse.move(x_m, y_m)
                wait(0.2, 0.3)
                mouse.click(button="left")
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        return False

    def pre_move(self):
        # if teleport hotkey is set and if teleport is not already selected
        if self._skill_hotkeys["teleport"] and not self._ui_manager.is_right_skill_selected(["TELE_ACTIVE", "TELE_INACTIVE"]):
            keyboard.send(self._skill_hotkeys["teleport"])
            wait(0.15, 0.25)

    def move(self, pos_monitor: Tuple[float, float], force_tp: bool = False):
        factor = self._config.advanced_options["pathing_delay_factor"]
        if self._skill_hotkeys["teleport"] and (force_tp or self._ui_manager.is_right_skill_active()):
            mouse.move(pos_monitor[0], pos_monitor[1], randomize=3, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.03)
        else:
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
            pos_screen = self._screen.convert_monitor_to_screen(pos_monitor)
            pos_abs = self._screen.convert_screen_to_abs(pos_screen)
            dist = math.dist(pos_abs, (0, 0))
            min_wd = self._config.ui_pos["min_walk_dist"]
            max_wd = random.randint(int(self._config.ui_pos["max_walk_dist"] * 0.65), self._config.ui_pos["max_walk_dist"])
            adjust_factor = max(max_wd, min(min_wd, dist - 50)) / dist
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
            x, y = self._screen.convert_abs_to_monitor(pos_abs)
            mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            mouse.click(button="left")

    def tp_town(self):
        if not self._ui_manager.has_tps():
            Logger.error("Wanted to TP but no TPs are available! Make sure your keybinding is correct and you have a tomb in your inventory.")
            return False
        mouse.click(button="right")
        # TODO: Add hardcoded coordinates to ini file
        pos_away = self._screen.convert_abs_to_monitor((-167, -30))
        wait(0.8, 1.3) # takes quite a while for tp to be visible
        roi = self._config.ui_roi["tp_search"]
        start = time.time()
        while (time.time() - start)  < 8:
            img = self._screen.grab()
            template_match = self._template_finder.search(
                ["BLUE_PORTAL","BLUE_PORTAL_2"],
                img,
                threshold=0.66,
                roi=roi,
                normalize_monitor=True
            )
            if template_match.valid:
                pos = template_match.position
                pos = (pos[0], pos[1] + 30)
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                wait(0.08, 0.15)
                mouse.click(button="left")
                if self._ui_manager.wait_for_loading_screen(2.0):
                    return True
            # move mouse away to not overlay with the town portal
            mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        return False

    def _pre_buff_cta(self):
        # save current skill img
        wait(0.1)
        skill_before = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.3, 0.35)
        keyboard.send(self._char_config["battle_command"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.3, 0.35)
        # Make sure that we are back at the previous skill
        skill_after = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
        if max_val < 0.96:
            Logger.warning("Failed to switch weapon, try again")
            wait(1.2)
            skill_after = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
            _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
            if max_val < 0.96:
                keyboard.send(self._char_config["weapon_switch"])
                wait(0.4)
            else:
                Logger.warning("Turns out weapon switch just took a long time. You ever considered getting a new internet provider or to upgrade your pc?")

    @abstract
    def pre_buff(self):
        pass

    @abstract
    def kill_pindle(self) -> bool:
        pass

    @abstract
    def kill_shenk(self) -> bool:
        pass

    @abstract
    def kill_eldritch(self) -> bool:
        pass
