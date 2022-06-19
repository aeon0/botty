from typing import Callable, TypeVar
import cv2
import keyboard
import math
import numpy as np
import random
import time
from functools import cached_property

from char.utils.capabilities import CharacterCapabilities
from char.utils.skill_data import get_cast_wait_time
from config import Config
from item import consumables
from logger import Logger
from screen import grab, convert_monitor_to_screen, convert_screen_to_abs, convert_abs_to_monitor, convert_screen_to_monitor, convert_abs_to_screen, ensure_coordinates_in_screen
from ui import skills
from ui_manager import detect_screen_object, ScreenObjects, wait_for_update, is_visible, wait_until_visible
from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, is_in_roi, color_filter, arc_spread, random_point_in_circle
import template_finder

class IChar:
    def __init__(self, skill_hotkeys: dict):
        self._active_aura = ""
        # Add a bit to be on the save side
        self._last_tp = time.time()
        self._mouse_click_held = {
            "left": False,
            "right": False
        }
        self._key_held = dict.fromkeys([v[0] for v in keyboard._winkeyboard.official_virtual_keys.values()], False)
        self._skill_hotkeys = skill_hotkeys
        self._standing_still = False
        self.default_move_skill = ""
        self.damage_scaling = float(Config().char.get("damage_scaling", 1.0))
        self._use_safer_routines = Config().char["safer_routines"]
        self._base_class = ""
        self.can_teleport = ""
        self.capabilities = None

    """
    MOUSE AND KEYBOARD METHODS
    """

    @staticmethod
    def _handle_delay(delay: float | list | tuple | None = None):
        if delay is None:
            return
        if isinstance(delay, (list, tuple)):
            wait(*delay)
        else:
            try:
                wait(delay)
            except Exception as e:
                Logger.warning(f"Failed to delay with delay: {delay}. Exception: {e}")

    def _keypress(self, key: str, hold_time: float | list | tuple | None = None):
        if not hold_time:
            keyboard.send(key)
        else:
            self._key_held[key] = True
            keyboard.send(key, do_release=False)
            self._handle_delay(hold_time)
            keyboard.send(key, do_press=False)
            self._key_held[key] = False

    def _click(self, mouse_click_type: str = "left", hold_time: float | list | tuple | None = None):
        if not hold_time:
            mouse.click(button = mouse_click_type)
        else:
            mouse.press(button = mouse_click_type)
            self._handle_delay(hold_time)
            mouse.release(button = mouse_click_type)

    def _hold_click(self, mouse_click_type: str = "left", enable: bool = True):
        if enable:
            if not self._mouse_click_held[mouse_click_type]:
                self._mouse_click_held[mouse_click_type] = True
                mouse.press(button = mouse_click_type)
        else:
            if self._mouse_click_held[mouse_click_type]:
                self._mouse_click_held[mouse_click_type] = False
                mouse.release(button = mouse_click_type)

    def _click_left(self, hold_time: float | list | tuple | None = None):
        self._click("left", hold_time = hold_time)

    def _click_right(self, hold_time: float | list | tuple | None = None):
        self._click("right", hold_time = hold_time)

    @cached_property
    def _get_hotkey(self, skill: str) -> str | None:
        if not (
            (skill in self._skill_hotkeys and (hotkey := self._skill_hotkeys[skill]))
            or (skill in Config().char and (hotkey := Config().char[skill]))
        ):
            # Logger.warning(f"No hotkey for skill: {skill}")
            return None
        return hotkey

    """
    CAPABILITIES METHODS
    """

    def _get_teleport_type(self) -> str:
        """
        1. player can teleport natively
            a. and has teleport bound and is visible
            b. and does not have teleport hotkey bound
        2. player can teleport with charges
            a. and has teleport bound and is visible
            b. and does not have teleport hotkey bound
            c. and has run out of teleport charges
        3. player can't teleport
        """

        # 3. player can't teleport
        if Config().char["use_charged_teleport"] and not self._get_hotkey("teleport"):
            Logger.error("No hotkey for teleport even though param.ini 'use_charged_teleport' is set to True")
            return "walk"
        if not self._get_hotkey("teleport"):
            return "walk"
        # 2. player can teleport with charges
        if Config().char["use_charged_teleport"]:
            if not skills.is_skill_bound(["BAR_TP_ACTIVE", "BAR_TP_INACTIVE"]):
                # 2c.
                Logger.debug("can_teleport: player can teleport with charges, but has no teleport bound. Likely needs repair.")
            # 2a.
            return "charges"
        # 1. player can teleport natively
        if not Config().char["use_charged_teleport"] and skills.is_skill_bound(["BAR_TP_ACTIVE", "BAR_TP_INACTIVE"]):
            return "native"
        return "walk"

    @staticmethod
    def _teleport_active():
        return skills.is_teleport_active()

    def can_teleport(self):
        return (self.capabilities.can_teleport_natively or self.capabilities.can_teleport_with_charges) and self._teleport_active()

    def _discover_capabilities(self) -> CharacterCapabilities:
        type = self._get_teleport_type()
        return CharacterCapabilities(can_teleport_natively=(type == "native"), can_teleport_with_charges=(type == "charges"))

    def discover_capabilities(self):
        if IChar._CrossGameCapabilities is None:
            capabilities = self._discover_capabilities()
            self.capabilities = capabilities
        Logger.info(f"Capabilities: {self.capabilities}")
        self.on_capabilities_discovered(self.capabilities)

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        pass

    """
    SKILL / CASTING METHODS
    """

    @staticmethod
    def _log_cast(skill_name: str, cast_pos_abs: tuple[float, float], spray: int, min_duration: float, aura: str):
        msg = f"Casting skill {skill_name}"
        if cast_pos_abs:
            msg += f" at screen coordinate {convert_abs_to_screen(cast_pos_abs)}"
        if spray:
            msg += f" with spray of {spray}"
        if min_duration:
            msg += f" for {round(min_duration, 1)}s"
        if aura:
            msg += f" with {aura} active"
        Logger.debug(msg)

    def _send_skill_and_cooldown(self, skill_name: str):
        self._keypress(self._get_hotkey(skill_name))
        wait(get_cast_wait_time(skill_name))

    def _activate_aura(self, skill_name: str, delay: float | list | tuple | None = (0.04, 0.08)):
        if not self._get_hotkey(skill_name):
            return False
        if self._activate_aura != skill_name: # if aura is already active, don't activate it again
            self._keypress(self._get_hotkey(skill_name))
            self._active_aura = skill_name
            self._handle_delay(delay)
        return True

    def _cast_simple(self, skill_name: str, duration: float | list | tuple | None = None) -> bool:
        """
        Casts a skill
        """
        if not (hotkey := self._get_hotkey(skill_name)):
            return False
        if not self._key_held[hotkey]: # if skill is already active, don't activate it again
            if not duration:
                self._send_skill_and_cooldown(skill_name)
            else:
                self._stand_still(True)
                self._keypress(self._get_hotkey(skill_name), hold_time=duration)
                self._stand_still(False)
        return True

    def _cast_at_position(self, skill_name: str, cast_pos_abs: tuple[float, float], spray: float = 0, spread_deg: float = 0, duration: float | list | tuple | None = None) -> bool:
        """
        Casts a skill at a given position.
        """
        def _adjust_position(cast_pos_abs, spray, spread_deg):
            if spread_deg:
                pos = vec_to_monitor(arc_spread(cast_pos_abs, spread_deg=spread_deg))
            if spray:
                pos = random_point_in_circle(pos = cast_pos_abs, r = spray)
            return ensure_coordinates_in_screen(pos, "abs")


        if not self._get_hotkey(skill_name):
            return False

        if cast_pos_abs:
            x, y = cast_pos_abs
            if spray:
                x += (random.random() * 2 * spray - spray)
                y += (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.1, 0.2])
        self._cast_simple(skill_name, duration)
        return True

    def _cast_left_with_aura(self, skill_name: str, cast_pos_abs: tuple[float, float] = None, spray: int = 0, duration: float | list | tuple | None = None, aura: str = "") -> bool:
        """
        Casts a skill at given position with an aura active
        """
        #self._log_cast(skill_name, cast_pos_abs, spray, duration, aura)
        if aura:
            self._activate_aura(aura)
        return self._cast_at_position(skill_name=skill_name, cast_pos_abs=cast_pos_abs, spray=spray, mouse_click_type="left", duration=duration)

    def _cast_in_arc(self, skill_name: str, cast_pos_abs: tuple[float, float] = [0,-100], time_in_s: float = 3, spread_deg: float = 10, hold=True):
        #scale cast time by damage_scaling
        time_in_s *= self.damage_scaling
        Logger.debug(f'Casting {skill_name} for {time_in_s:.02f}s at {cast_pos_abs} with {spread_deg}°')
        if not self._skill_hotkeys[skill_name]:
            raise ValueError(f"You did not set {skill_name} hotkey!")
        self._stand_still(True)

        target = self.vec_to_monitor(arc_spread(cast_pos_abs, spread_deg=spread_deg))
        mouse.move(*target,delay_factor=[0.95, 1.05])
        if hold:
            self._hold_click("right", True)
        start = time.time()
        while (time.time() - start) < time_in_s:
            target = self.vec_to_monitor(arc_spread(cast_pos_abs, spread_deg=spread_deg))
            if hold:
                mouse.move(*target, delay_factor=[3, 8])
            if not hold:
                mouse.move(*target, delay_factor=[.2, .4])
                self._click_right(0.04)
                wait(self._cast_duration, self._cast_duration)

        if hold:
            self._hold_click("right", False)
        self._stand_still(False)

    """
    GLOBAL SKILLS
    """

    def _cast_teleport(self) -> bool:
        return self._cast_simple(skill_name="teleport")

    def _cast_battle_orders(self) -> bool:
        return self._cast_simple(skill_name="battle_orders")

    def _cast_battle_command(self) -> bool:
        return self._cast_simple(skill_name="battle_command")

    def _cast_town_portal(self) -> bool:
        if res := self._cast_simple(skill_name="town_portal"):
            consumables.increment_need("tp", 1)
        return res

    def _weapon_switch(self):
        return self._keypress(self._get_hotkey("weapon_switch"))

    """
    CHARACTER ACTIONS AND MOVEMENT METHODS
    """
    def _force_move(self):
        self._keypress(self._get_hotkey("force_move"))

    def _stand_still(self, enable: bool):
        if enable:
            if not self._standing_still:
                keyboard.send(self._get_hotkey("stand_still"), do_release=False)
                self._standing_still = True
        else:
            if self._standing_still:
                keyboard.send(self._get_hotkey("stand_still"), do_press=False)
                self._standing_still = False

    def pick_up_item(self, pos: tuple[float, float], item_name: str = None, prev_cast_start: float = 0) -> float:
        mouse.move(pos[0], pos[1])
        self._click_left()
        wait(0.25, 0.35)
        return prev_cast_start

    def pre_move(self):
        pass

    def _teleport_to_position(self, pos_monitor: tuple[float, float]):
        factor = Config().advanced_options["pathing_delay_factor"]
        mouse.move(pos_monitor[0], pos_monitor[1], randomize=3, delay_factor=[(2+factor)/25, (4+factor)/25])
        wait(0.012, 0.02)
        self._keypress(self._get_hotkey("teleport"))

    def _walk_to_position(self, pos_monitor: tuple[float, float], force_move: bool = False):
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
        mouse.move(x, y, randomize=3, delay_factor=[(2+factor)/25, (4+factor)/25])
        wait(0.012, 0.02)
        if force_move:
            self._force_move()
        else:
            self._click_left()

    def move(self, pos_monitor: tuple[float, float], use_tp: bool = False, force_move: bool = False, last_move_time: float = time.time()) -> float:
        factor = Config().advanced_options["pathing_delay_factor"]
        if use_tp and self.can_teleport(): # can_teleport() activates teleport hotkey if True
            # 7 frames is the fastest that teleport can be casted with 200 fcr on sorc
            self._teleport_to_position(pos_monitor)
            min_wait = get_cast_wait_time(self._base_class, "teleport", Config().char["fcr"]) + factor/25
            # if there's still time remaining in cooldown, wait
            while time.time() - last_move_time < min_wait:
                wait(0.02)
        else:
            self._walk_to_position(pos_monitor = pos_monitor, force_move=force_move)
        return time.time()

    def tp_town(self) -> bool:
        # will check if tp is available and select the skill
        if not skills.has_tps():
            return False
        self._cast_town_portal()

        roi_mouse_move = [
            int(Config().ui_pos["screen_width"] * 0.3),
            0,
            int(Config().ui_pos["screen_width"] * 0.4),
            int(Config().ui_pos["screen_height"] * 0.7)
        ]
        pos_away = convert_abs_to_monitor((-167, -30))
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
                    self._cast_town_portal()
                else:
                    return False
            if (template_match := wait_until_visible(ScreenObjects.TownPortal, timeout=3)).valid:
                pos = template_match.center_monitor
                pos = (pos[0], pos[1] + 30)
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                mouse.move(*pos, randomize=6, delay_factor=[0.4, 0.6])
                self._click_left()
                if wait_until_visible(ScreenObjects.Loading, 2).valid:
                    return True
            # move mouse away to not overlay with the town portal if mouse is in center
            pos_screen = convert_monitor_to_screen(mouse.get_position())
            if is_in_roi(roi_mouse_move, pos_screen):
                mouse.move(*pos_away, randomize=40, delay_factor=[0.8, 1.4])
        return False

    def _pre_buff_cta(self) -> bool:
        if not Config().char["cta_available"]:
            return False
        # Save current skill img
        skill_before = cut_roi(grab(), Config().ui_roi["skill_right"])
        # Try to switch weapons and select bo until we find the skill on the right skill slot
        start = time.time()
        switch_success = False
        while time.time() - start < 4:
            self._weapon_switch()
            wait(0.3, 0.35)
            self._select_skill(skill = "battle_command", delay=(0.1, 0.2))
            if skills.is_right_skill_selected(["BC", "BO"]):
                switch_success = True
                break

        if not switch_success:
            Logger.warning("You dont have Battle Command bound, or you do not have CTA. ending CTA buff")
            Config().char["cta_available"] = 0
        else:
            # We switched succesfully, let's pre buff
            self._cast_battle_command()
            wait(self._cast_duration + 0.16, self._cast_duration + 0.18)
            self._cast_battle_orders()
            wait(self._cast_duration + 0.16, self._cast_duration + 0.18)

        # Make sure the switch back to the original weapon is good
        start = time.time()
        while (elapsed := time.time() - start < 4):
            self._weapon_switch()
            wait(0.3, 0.35)
            skill_after = cut_roi(grab(), Config().ui_roi["skill_right"])
            _, max_val, _, _ = cv2.minMaxLoc(cv2.matchTemplate(skill_after, skill_before, cv2.TM_CCOEFF_NORMED))
            if max_val > 0.9:
                break
            else:
                Logger.warning("Failed to switch weapon, try again")
                wait(0.5)
        return elapsed

    def pre_buff(self):
        pass


    """
    OTHER METHODS
    """

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
                self._click_left()
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        Logger.error(f"Wanted to select {template_type}, but could not find it")
        return False


    def vec_to_monitor(self, target: tuple[float, float]) -> tuple[float, float]:
        circle_pos_screen = self._pather._adjust_abs_range_to_screen(target)
        return convert_abs_to_monitor(circle_pos_screen)

    def _lerp(self, a: float, b: float, f:float) -> float:
        return a + f * (b - a)

    """
    KILL ROUTINES
    """

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
