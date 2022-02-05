from typing import Dict, Tuple, Union, List, Callable
import random
import time
import cv2
import math
import keyboard
import numpy as np
from char.capabilities import CharacterCapabilities

from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, is_in_roi, color_filter

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager


class IChar:
    _CrossGameCapabilities: Union[None, CharacterCapabilities] = None

    def __init__(self, skill_hotkeys: Dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager):
        self._skill_hotkeys = skill_hotkeys
        self._char_config = Config().char
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._screen = screen
        self._config = Config()
        self._last_tp = time.time()
        # Add a bit to be on the save side
        self._cast_duration = self._char_config["casting_frames"] * 0.04 + 0.01
        self.capabilities = None

    def _discover_capabilities(self) -> CharacterCapabilities:
        if self._skill_hotkeys["teleport"]:
            if self.select_tp():
                img = self._screen.grab()
                skill_img = cut_roi(img, self._config.ui_roi["skill_right"])
                charge_mask, _ = color_filter(skill_img, self._config.colors["blue"])
                if np.sum(charge_mask) > 0:
                    return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=True)
                else:
                    return CharacterCapabilities(can_teleport_natively=True, can_teleport_with_charges=False)
            return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=True)
        else:
            return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=False)

    def discover_capabilities(self, force = False):
        if IChar._CrossGameCapabilities is None or force:
            capabilities = self._discover_capabilities()
            self.capabilities = capabilities
        Logger.info(f"Capabilities: {self.capabilities}")
        self.on_capabilities_discovered(self.capabilities)

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        pass

    def pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
        mouse.move(pos[0], pos[1])
        time.sleep(0.1)
        mouse.click(button="left")
        wait(0.45, 0.5)
        return prev_cast_start

    def select_by_template(
        self,
        template_type:  Union[str, List[str]],
        success_func: Callable = None,
        time_out: float = 8,
        threshold: float = 0.68,
        telekinesis: bool = False
    ) -> bool:
        """
        Finds any template from the template finder and interacts with it
        :param template_type: Strings or list of strings of the templates that should be searched for
        :param success_func: Function that will return True if the interaction is successful e.g. return True when loading screen is reached, defaults to None
        :param time_out: Timeout for the whole template selection, defaults to None
        :param threshold: Threshold which determines if a template is found or not. None will use default form .ini files
        :return: True if success. False otherwise
        """
        if type(template_type) == list and "A5_STASH" in template_type:
            # sometimes waypoint is opened and stash not found because of that, check for that
            if self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid:
                keyboard.send("esc")
        start = time.time()
        while time_out is None or (time.time() - start) < time_out:
            template_match = self._template_finder.search(template_type, self._screen.grab(), threshold=threshold, normalize_monitor=True)
            if template_match.valid:
                Logger.debug(f"Select {template_match.name} ({template_match.score*100:.1f}% confidence)")
                mouse.move(*template_match.center)
                wait(0.2, 0.3)
                mouse.click(button="left")
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        Logger.error(f"Wanted to select {template_type}, but could not find it")
        return False



    def is_low_on_teleport_charges(self):
        return self._template_finder.search(["TELE_3_CHARGES", "TELE_3_CHARGES_INACTIVE", "TELE_2_CHARGES", "TELE_2_CHARGES_INACTIVE", "TELE_1_CHARGES", "TELE_1_CHARGES_INACTIVE"], self._screen.grab(), threshold=0.95, roi=self._config.ui_roi["skill_right"]).valid

    def _remap_skill_hotkey(self, skill_asset, hotkey, skill_roi, expanded_skill_roi):
        x, y, w, h = skill_roi
        x, y = self._screen.convert_screen_to_monitor((x, y))
        mouse.move(x + w/2, y + h / 2)
        mouse.click("left")
        wait(0.3)
        match = self._template_finder.search(skill_asset, self._screen.grab(), threshold=0.84, roi=expanded_skill_roi)
        if match.valid:
            x, y = self._screen.convert_screen_to_monitor(match.position)
            mouse.move(x, y)
            wait(0.3)
            keyboard.send(hotkey)
            wait(0.3)
            mouse.click("left")
            wait(0.3)

    def remap_right_skill_hotkey(self, skill_asset, hotkey):
        return self._remap_skill_hotkey(skill_asset, hotkey, self._config.ui_roi["skill_right"], self._config.ui_roi["skill_right_expanded"])

    def select_tp(self):
       if self._skill_hotkeys["teleport"] and not self._ui_manager.is_right_skill_selected(["TELE_ACTIVE", "TELE_INACTIVE"]):
            keyboard.send(self._skill_hotkeys["teleport"])
            wait(0.1, 0.2)
       return self._ui_manager.is_right_skill_selected(["TELE_ACTIVE", "TELE_INACTIVE"])

    def pre_move(self):
        # if teleport hotkey is set and if teleport is not already selected
        if self.capabilities.can_teleport_natively:
            self.select_tp()

    def move(self, pos_monitor: Tuple[float, float], force_tp: bool = False, force_move: bool = False):
        factor = self._config.advanced_options["pathing_delay_factor"]
        if self._skill_hotkeys["teleport"] and (force_tp or (self._ui_manager.is_right_skill_selected(["TELE_ACTIVE"]) and self._ui_manager.is_right_skill_active())):
            mouse.move(pos_monitor[0], pos_monitor[1], randomize=3, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.02)
        else:
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
            pos_screen = self._screen.convert_monitor_to_screen(pos_monitor)
            pos_abs = self._screen.convert_screen_to_abs(pos_screen)
            dist = math.dist(pos_abs, (0, 0))
            min_wd = max(10, self._config.ui_pos["min_walk_dist"])
            max_wd = random.randint(int(self._config.ui_pos["max_walk_dist"] * 0.65), self._config.ui_pos["max_walk_dist"])
            adjust_factor = max(max_wd, min(min_wd, dist - 50)) / max(min_wd, dist)
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
            x, y = self._screen.convert_abs_to_monitor(pos_abs)
            mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            if force_move:
                keyboard.send(self._config.char["force_move"])
            else:
                mouse.click(button="left")

    def tp_town(self):
        # will check if tp is available and select the skill
        if not self._ui_manager.has_tps():
            return False
        mouse.click(button="right")
        roi_mouse_move = [
            int(self._config.ui_pos["screen_width"] * 0.3),
            0,
            int(self._config.ui_pos["screen_width"] * 0.4),
            int(self._config.ui_pos["screen_height"] * 0.7)
        ]
        pos_away = self._screen.convert_abs_to_monitor((-167, -30))
        wait(0.8, 1.3) # takes quite a while for tp to be visible
        roi = self._config.ui_roi["tp_search"]
        start = time.time()
        retry_count = 0
        while (time.time() - start) < 8:
            if time.time() - start > 3.7 and retry_count == 0:
                retry_count += 1
                Logger.debug("Move to another position and try to open tp again")
                pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
                self.pre_move()
                self.move(pos_m)
                if self._ui_manager.has_tps():
                    mouse.click(button="right")
                wait(0.8, 1.3) # takes quite a while for tp to be visible
            img = self._screen.grab()
            template_match = self._template_finder.search(
                ["BLUE_PORTAL","BLUE_PORTAL_2"],
                img,
                threshold=0.66,
                roi=roi,
                normalize_monitor=True
            )
            if template_match.valid:
                pos = template_match.center
                pos = (pos[0], pos[1] + 30)
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                wait(0.08, 0.15)
                mouse.click(button="left")
                if self._ui_manager.wait_for_loading_screen(2.0):
                    return True
            # move mouse away to not overlay with the town portal if mouse is in center
            pos_screen = self._screen.convert_monitor_to_screen(mouse.get_position())
            if is_in_roi(roi_mouse_move, pos_screen):
                mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        return False

    def _pre_buff_cta(self):
        # Save current skill img
        skill_before = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
        # Try to switch weapons and select bo until we find the skill on the right skill slot
        start = time.time()
        switch_sucess = False
        while time.time() - start < 4:
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.3, 0.35)
            keyboard.send(self._char_config["battle_command"])
            wait(0.1, 0.19)
            if self._ui_manager.is_right_skill_selected(["BC", "BO"]):
                switch_sucess = True
                break

        if not switch_sucess:
            Logger.warning("You dont have Battle Command bound, or you do not have CTA. ending CTA buff")
            self._char_config["cta_available"] = 0
        else:
            # We switched succesfully, let's pre buff
            mouse.click(button="right")
            wait(self._cast_duration + 0.16, self._cast_duration + 0.18)
            keyboard.send(self._char_config["battle_orders"])
            wait(0.1, 0.19)
            mouse.click(button="right")
            wait(self._cast_duration + 0.16, self._cast_duration + 0.18)

        # Make sure the switch back to the original weapon is good
        start = time.time()
        while time.time() - start < 4:
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.3, 0.35)
            skill_after = cut_roi(self._screen.grab(), self._config.ui_roi["skill_right"])
            _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
            if max_val > 0.9:
                break
            else:
                Logger.warning("Failed to switch weapon, try again")
                wait(0.5)

    def pre_buff(self):
        pass

    def kill_pindle(self) -> bool:
        raise ValueError("Pindle is not implemented!")

    def kill_shenk(self) -> bool:
        raise ValueError("Shenk is not implemented!")

    def kill_eldritch(self) -> bool:
        raise ValueError("Eldritch is not implemented!")

    def kill_council(self) -> bool:
        raise ValueError("Council is not implemented!")

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        raise ValueError("Nihlathak is not implemented!")

    def kill_summoner(self) -> bool:
        raise ValueError("Arcane is not implemented!")

    def kill_diablo(self) -> bool:
        raise ValueError("Diablo is not implemented!")

    def kill_deseis(self, nodes1: list[int], nodes2: list[int], nodes3: list[int]) -> bool:
        raise ValueError("Diablo De Seis is not implemented!")

    def kill_infector(self) -> bool:
        raise ValueError("Diablo Infector is not implemented!")

    def kill_vizier(self, nodes1: list[int], nodes2: list[int]) -> bool:
        raise ValueError("Diablo Vizier is not implemented!")

    def kill_cs_trash(self) -> bool:
        raise ValueError("Diablo CS Trash is not implemented!")
