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
from typing import Dict, Tuple
from config import Config


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

    def select_by_template(self, template_type: str) -> bool:
        if template_type == "A5_STASH":
            # sometimes waypoint is opened and stash not found because of that, check for that
            if self._template_finder.search("WAYPOINT_MENU", self._screen.grab())[0]:
                keyboard.send("esc")
        Logger.debug(f"Select {template_type}")
        success, screen_loc = self._template_finder.search_and_wait(template_type, time_out=10)
        if success:
            x_m, y_m = self._screen.convert_screen_to_monitor(screen_loc)
            mouse.move(x_m, y_m)
            wait(0.3, 0.4)
            mouse.click(button="left")
            return True
        return False

    def move(self, pos_monitor: Tuple[float, float], force_tp: bool = False):
        if force_tp or not self._ui_manager.is_teleport_selected():
            keyboard.send(self._skill_hotkeys["teleport"])
            wait(0.15, 0.25)
        factor = self._config.advanced_options["pathing_delay_factor"]
        if force_tp or self._ui_manager.can_teleport():
            mouse.move(pos_monitor[0], pos_monitor[1], randomize=3, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.03)
        else:
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
            pos_screen = self._screen.convert_monitor_to_screen(pos_monitor)
            pos_abs = self._screen.convert_screen_to_abs(pos_screen)
            dist = math.dist(pos_abs, (0, 0))
            adjust_factor = (dist - 50) / dist
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
            x, y = self._screen.convert_abs_to_monitor(pos_abs)
            mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            mouse.click(button="left")
            if self._config.char["slow_walk"]:
                wait(0.8)

    def tp_town(self):
        skill_before = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        keyboard.send(self._char_config["tp"])
        wait(0.1, 0.1)
        skill_after = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
        if max_val > 0.96:
            # found same skill again, thus no more tps available
            Logger.warning("Out of tps")
            return False
        mouse.click(button="right")
        # TODO: Add hardcoded coordinates to ini file
        pos_away = self._screen.convert_abs_to_monitor((int(-250 * self._config.scale), -30))
        mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        wait(0.8, 1.3) # takes quite a while for tp to be visible
        roi = self._config.ui_roi["tp_search"]
        start = time.time()
        while (time.time() - start)  < 8:
            img = self._screen.grab()
            success1, pos1 = self._template_finder.search(
                "BLUE_PORTAL", 
                img, 
                threshold=0.66, 
                roi=roi, 
                normalize_monitor=True
            )
            success2, pos2 = self._template_finder.search(
                "BLUE_PORTAL_2", 
                img, 
                threshold=0.7, 
                roi=roi, 
                normalize_monitor=True
            )
            if success1 or success2:
                pos = pos1 if success1 else pos2
                pos = (pos[0], pos[1] + (45 * self._config.scale))
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                wait(0.08, 0.15)
                mouse.click(button="left")
                if self._ui_manager.wait_for_loading_screen(2.0):
                    return True
                else:
                    mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        return False

    def _pre_buff_cta(self):
        # save current skill img
        skill_before = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.28, 0.35)
        keyboard.send(self._char_config["battle_command"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.25, 0.3)
        # Make sure that we are back at the previous skill
        skill_after = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
        if max_val < 0.96:
            Logger.warning("Failed to switch weapon, try again")
            wait(1.0)
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.4)

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
