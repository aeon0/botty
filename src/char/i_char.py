from typing import Callable
import random
import time
import cv2
import math
from item import consumables
import keyboard
import numpy as np
from char.capabilities import CharacterCapabilities
from ui_manager import is_visible, wait_until_visible
from ui import skills
from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, is_in_roi, color_filter, arc_spread
from logger import Logger
from config import Config
from screen import grab, convert_monitor_to_screen, convert_screen_to_abs, convert_abs_to_monitor, convert_screen_to_monitor
import template_finder
from ui_manager import detect_screen_object, ScreenObjects, get_closest_non_hud_pixel

class IChar:
    _CrossGameCapabilities: None | CharacterCapabilities = None

    def __init__(self, skill_hotkeys: dict):
        self._skill_hotkeys = skill_hotkeys
        self._last_tp = time.time()
        # Add a bit to be on the save side
        self._cast_duration = Config().char["casting_frames"] * 0.04 + 0.01
        self.damage_scaling = float(Config().char.get("damage_scaling", 1.0))
        self.capabilities = None
        self._active_skill = {
            "left": "",
            "right": ""
        }
        self._use_safer_routines = Config().char["safer_routines"]

    def _set_active_skill(self, mouse_click_type: str = "left", skill: str =""):
        self._active_skill[mouse_click_type] = skill

    def _select_skill(self, skill: str, mouse_click_type: str = "left", delay: float | list | tuple = None):
        if not (
            skill in self._skill_hotkeys and (hotkey := self._skill_hotkeys[skill])
            or (skill in Config().char and (hotkey := Config().char[skill]))
        ):
            Logger.warning(f"No hotkey for skill: {skill}")
            self._set_active_skill(mouse_click_type, "")
            return False

        if self._active_skill[mouse_click_type] != skill:
            keyboard.send(hotkey)
        self._set_active_skill(mouse_click_type, skill)
        if delay:
            try:
                wait(*delay)
            except:
                try:
                    wait(delay)
                except Exception as e:
                    Logger.warning(f"_select_skill: Failed to delay with delay: {delay}. Exception: {e}")
        return True

    def _discover_capabilities(self) -> CharacterCapabilities:
        override = Config().advanced_options["override_capabilities"]
        if override is None:
            if Config().char["teleport"]:
                if self.select_tp():
                    if self.skill_is_charged():
                        return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=True)
                    else:
                        return CharacterCapabilities(can_teleport_natively=True, can_teleport_with_charges=False)
                return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=True)
            else:
                return CharacterCapabilities(can_teleport_natively=False, can_teleport_with_charges=False)
        else:
            Logger.debug(f"override_capabilities is set to {override}")
            return CharacterCapabilities(
                can_teleport_natively="can_teleport_natively" in override,
                can_teleport_with_charges="can_teleport_with_charges" in override
            )

    def discover_capabilities(self, force = False):
        if IChar._CrossGameCapabilities is None or force:
            capabilities = self._discover_capabilities()
            self.capabilities = capabilities
        Logger.info(f"Capabilities: {self.capabilities}")
        self.on_capabilities_discovered(self.capabilities)

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        pass

    def pick_up_item(self, pos: tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
        mouse.move(pos[0], pos[1])
        time.sleep(0.1)
        mouse.click(button="left")
        wait(0.25, 0.3)
        return prev_cast_start

    def select_by_template(
        self,
        template_type:  str | list[str],
        success_func: Callable = None,
        timeout: float = 8,
        threshold: float = 0.68,
        telekinesis: bool = False
    ) -> bool:
        """
        Finds any template from the template finder and interacts with it
        :param template_type: Strings or list of strings of the templates that should be searched for
        :param success_func: Function that will return True if the interaction is successful e.g. return True when loading screen is reached, defaults to None
        :param timeout: Timeout for the whole template selection, defaults to None
        :param threshold: Threshold which determines if a template is found or not. None will use default form .ini files
        :return: True if success. False otherwise
        """
        if type(template_type) == list and "A5_STASH" in template_type:
            # sometimes waypoint is opened and stash not found because of that, check for that
            if is_visible(ScreenObjects.WaypointLabel):
                keyboard.send("esc")
        start = time.time()
        while timeout is None or (time.time() - start) < timeout:
            template_match = template_finder.search(template_type, grab(), threshold=threshold)
            if template_match.valid:
                Logger.debug(f"Select {template_match.name} ({template_match.score*100:.1f}% confidence)")
                mouse.move(*template_match.center_monitor)
                wait(0.2, 0.3)
                mouse.click(button="left")
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        Logger.error(f"Wanted to select {template_type}, but could not find it")
        return False

    def skill_is_charged(self, img: np.ndarray = None) -> bool:
        if img is None:
            img = grab()
        skill_img = cut_roi(img, Config().ui_roi["skill_right"])
        charge_mask, _ = color_filter(skill_img, Config().colors["blue"])
        if np.sum(charge_mask) > 0:
            return True
        return False

    def is_low_on_teleport_charges(self):
        img = grab()
        charges_remaining = skills.get_skill_charges(img)
        if charges_remaining:
            Logger.debug(f"{charges_remaining} teleport charges remain")
            return charges_remaining <= 3
        else:
            charges_present = self.skill_is_charged(img)
            if charges_present:
                Logger.error("is_low_on_teleport_charges: unable to determine skill charges, assume zero")
            return True

    def _remap_skill_hotkey(self, skill_asset, hotkey, skill_roi, expanded_skill_roi):
        x, y, w, h = skill_roi
        x, y = convert_screen_to_monitor((x, y))
        mouse.move(x + w/2, y + h / 2)
        mouse.click("left")
        wait(0.3)
        match = template_finder.search(skill_asset, grab(), threshold=0.84, roi=expanded_skill_roi)
        if match.valid:
            mouse.move(*match.center_monitor)
            wait(0.3)
            keyboard.send(hotkey)
            wait(0.3)
            mouse.click("left")
            wait(0.3)

    def remap_right_skill_hotkey(self, skill_asset, hotkey):
        return self._remap_skill_hotkey(skill_asset, hotkey, Config().ui_roi["skill_right"], Config().ui_roi["skill_right_expanded"])

    def select_tp(self):
        return skills.select_tp(Config().char["teleport"])

    def pre_move(self):
        # if teleport hotkey is set and if teleport is not already selected
        if self.capabilities.can_teleport_natively:
            self.select_tp()
            self._set_active_skill("right", "teleport")

    def move(self, pos_monitor: tuple[float, float], force_tp: bool = False, force_move: bool = False):
        factor = Config().advanced_options["pathing_delay_factor"]
        if "teleport" in Config().char and Config().char["teleport"] and (
            force_tp
            or (
                skills.is_right_skill_selected(["TELE_ACTIVE"])
                and skills.is_right_skill_active()
            )
        ):
            self._set_active_skill("right", "teleport")
            mouse.move(pos_monitor[0], pos_monitor[1], randomize=3, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.02)
        else:
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
            pos_screen = convert_monitor_to_screen(pos_monitor)
            pos_abs = convert_screen_to_abs(pos_screen)
            dist = math.dist(pos_abs, (0, 0))
            min_wd = max(10, Config().ui_pos["min_walk_dist"])
            max_wd = random.randint(int(Config().ui_pos["max_walk_dist"] * 0.65), Config().ui_pos["max_walk_dist"])
            adjust_factor = max(max_wd, min(min_wd, dist - 50)) / max(min_wd, dist)
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
            x, y = convert_abs_to_monitor(pos_abs)
            mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
            wait(0.012, 0.02)
            if force_move:
                keyboard.send(Config().char["force_move"])
            else:
                mouse.click(button="left")

    def walk(self, pos_monitor: tuple[float, float], force_tp: bool = False, force_move: bool = False):
        factor = Config().advanced_options["pathing_delay_factor"]
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
        pos_screen = convert_monitor_to_screen(pos_monitor)
        pos_abs = convert_screen_to_abs(pos_screen)
        dist = math.dist(pos_abs, (0, 0))
        min_wd = max(10, Config().ui_pos["min_walk_dist"])
        max_wd = random.randint(int(Config().ui_pos["max_walk_dist"] * 0.65), Config().ui_pos["max_walk_dist"])
        adjust_factor = max(max_wd, min(min_wd, dist - 50)) / max(min_wd, dist)
        pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
        x, y = convert_abs_to_monitor(pos_abs)
        mouse.move(x, y, randomize=5, delay_factor=[factor*0.1, factor*0.14])
        wait(0.012, 0.02)
        if force_move:
            keyboard.send(Config().char["force_move"])
        else:
            mouse.click(button="left")

    def tp_town(self):
        # will check if tp is available and select the skill
        if not skills.has_tps():
            return False
        mouse.click(button="right")
        consumables.increment_need("tp", 1)
        roi_mouse_move = [
            int(Config().ui_pos["screen_width"] * 0.3),
            0,
            int(Config().ui_pos["screen_width"] * 0.4),
            int(Config().ui_pos["screen_height"] * 0.7)
        ]
        pos_away = convert_abs_to_monitor((-167, -30))
        wait(0.8, 1.3) # takes quite a while for tp to be visible
        start = time.time()
        retry_count = 0
        while (time.time() - start) < 8:
            if time.time() - start > 3.7 and retry_count == 0:
                retry_count += 1
                Logger.debug("Move to another position and try to open tp again")
                pos_m = convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
                self.pre_move()
                self.move(pos_m)
                if skills.has_tps():
                    mouse.click(button="right")
                    consumables.increment_need("tp", 1)
                wait(0.8, 1.3) # takes quite a while for tp to be visible
            if (template_match := detect_screen_object(ScreenObjects.TownPortal)).valid:
                pos = template_match.center_monitor
                pos = (pos[0], pos[1] + 30)
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                wait(0.08, 0.15)
                mouse.click(button="left")
                if wait_until_visible(ScreenObjects.Loading, 2).valid:
                    return True
            # move mouse away to not overlay with the town portal if mouse is in center
            pos_screen = convert_monitor_to_screen(mouse.get_position())
            if is_in_roi(roi_mouse_move, pos_screen):
                mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        return False

    def _pre_buff_cta(self):
        # Save current skill img
        skill_before = cut_roi(grab(), Config().ui_roi["skill_right"])
        # Try to switch weapons and select bo until we find the skill on the right skill slot
        start = time.time()
        switch_sucess = False
        while time.time() - start < 4:
            keyboard.send(Config().char["weapon_switch"])
            wait(0.3, 0.35)
            self._select_skill(skill = "battle_command", mouse_click_type="right", delay=(0.1, 0.2))
            if skills.is_right_skill_selected(["BC", "BO"]):
                switch_sucess = True
                break

        if not switch_sucess:
            Logger.warning("You dont have Battle Command bound, or you do not have CTA. ending CTA buff")
            Config().char["cta_available"] = 0
        else:
            # We switched succesfully, let's pre buff
            mouse.click(button="right")
            wait(self._cast_duration + 0.16, self._cast_duration + 0.18)
            self._select_skill(skill = "battle_orders", mouse_click_type="right", delay=(0.1, 0.2))
            mouse.click(button="right")
            wait(self._cast_duration + 0.16, self._cast_duration + 0.18)

        # Make sure the switch back to the original weapon is good
        start = time.time()
        while time.time() - start < 4:
            keyboard.send(Config().char["weapon_switch"])
            wait(0.3, 0.35)
            skill_after = cut_roi(grab(), Config().ui_roi["skill_right"])
            _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
            if max_val > 0.9:
                break
            else:
                Logger.warning("Failed to switch weapon, try again")
                wait(0.5)


    def vec_to_monitor(self, target):
        circle_pos_abs = get_closest_non_hud_pixel(pos = target, pos_type="abs")
        return convert_abs_to_monitor(circle_pos_abs)

    def _lerp(self,a: float,b: float, f:float):
        return a + f * (b - a)

    def cast_in_arc(self, ability: str, cast_pos_abs: tuple[float, float] = [0,-100], time_in_s: float = 3, spread_deg: float = 10, hold=True):
        #scale cast time by damage_scaling
        time_in_s *= self.damage_scaling
        Logger.debug(f'Casting {ability} for {time_in_s:.02f}s at {cast_pos_abs} with {spread_deg}°')
        if not self._skill_hotkeys[ability]:
            raise ValueError(f"You did not set {ability} hotkey!")
        keyboard.send(Config().char["stand_still"], do_release=False)
        self._select_skill(skill = ability, mouse_click_type="right", delay=(0.02, 0.08))

        target = self.vec_to_monitor(arc_spread(cast_pos_abs, spread_deg=spread_deg))
        mouse.move(*target,delay_factor=[0.95, 1.05])
        if hold:
            mouse.press(button="right")
        start = time.time()
        while (time.time() - start) < time_in_s:
            target = self.vec_to_monitor(arc_spread(cast_pos_abs, spread_deg=spread_deg))
            if hold:
                mouse.move(*target,delay_factor=[3, 8])
            if not hold:
                mouse.move(*target,delay_factor=[.2, .4])
                wait(0.02, 0.04)
                mouse.press(button="right")
                wait(0.02, 0.06)
                mouse.release(button="right")
                wait(self._cast_duration, self._cast_duration)

        if hold:
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)


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

    def kill_deseis(self, seal_layout:str) -> bool:
        raise ValueError("Diablo De Seis is not implemented!")

    def kill_infector(self, seal_layout:str) -> bool:
        raise ValueError("Diablo Infector is not implemented!")

    def kill_vizier(self, seal_layout:str) -> bool:
        raise ValueError("Diablo Vizier is not implemented!")

    def kill_cs_trash(self, location:str) -> bool:
        raise ValueError("Diablo CS Trash is not implemented!")

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    print(f"Get on D2R screen and press F11 when ready")
    keyboard.wait("f11")
    from utils.misc import cut_roi
    from config import Config
    from ui import skills

    skill_hotkeys = {}

    i_char = IChar({})

    while True:
        print(skills.get_skill_charges(grab()))
        wait(1)
