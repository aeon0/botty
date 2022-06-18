import keyboard
from typing import Callable
from utils.custom_mouse import mouse
from char import IChar
import template_finder
from pather import Pather
from screen import grab
from utils.misc import wait
import time
from pather import Pather
from config import Config
from ui_manager import ScreenObjects, is_visible
from screen import convert_screen_to_abs

class Sorceress(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        super().__init__(skill_hotkeys)
        self._pather = pather

    def pick_up_item(self, pos: tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
        if any(x in item_name for x in ['potion', 'misc_gold', 'tp_scroll']) and self._set_active_skill(mouse_click_type="right", skill="telekinesis"):
            self._cast_telekinesis(*pos)
            # need about 0.4s delay before next capture for the item not to persist on screen
            cast_start = time.time()
            interval = (cast_start - prev_cast_start)
            cast_duration_wait = (self._cast_duration - interval)
            delay = 0.35 if cast_duration_wait <0 else (0.35+cast_duration_wait)
            wait(delay,delay+0.1)
            return cast_start
        else:
            return super().pick_up_item(pos, item_name, prev_cast_start)

    def select_by_template(
        self,
        template_type:  str | list[str],
        success_func: Callable = None,
        timeout: float = 8,
        threshold: float = 0.68,
        telekinesis: bool = False
    ) -> bool:
        # In case telekinesis is False or hotkey is not set, just call the base implementation
        if not (telekinesis and self._get_hotkey("telekinesis")):
            return super().select_by_template(template_type, success_func, timeout, threshold)
        if type(template_type) == list and "A5_STASH" in template_type:
            # sometimes waypoint is opened and stash not found because of that, check for that
            if is_visible(ScreenObjects.WaypointLabel):
                keyboard.send("esc")
        start = time.time()
        while timeout is None or (time.time() - start) < timeout:
            template_match = template_finder.search(template_type, grab(), threshold=threshold)
            if template_match.valid:
                pos_abs = convert_screen_to_abs(template_match.center)
                self._cast_telekinesis(*pos_abs)
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        # In case telekinesis fails, try again with the base implementation
        return super().select_by_template(template_type, success_func, timeout, threshold)

    def pre_buff(self):
        if self._pre_buff_cta():
            wait(self._cast_duration + 0.1)
        if self._cast_energy_shield():
            wait(self._cast_duration + 0.1)
        if self._cast_thunder_storm():
            wait(self._cast_duration + 0.1)
        if self._cast_frozen_armor():
            wait(self._cast_duration + 0.1)

    def _cast_static(self, duration: float = 1.4) -> bool:
        return self._cast_simple(skill_name="static_field", mouse_click_type = "right", duration=duration)

    def _cast_telekinesis(self, cast_pos_abs: tuple[float, float]) -> bool:
        return self._cast_at_position(skill_name="telekinesis", cast_pos_abs = cast_pos_abs, spray = 0, mouse_click_type = "right")

    def _cast_thunder_storm(self) -> bool:
        return self._cast_simple(skill_name="thunder_storm", mouse_click_type="right")

    def _cast_energy_shield(self) -> bool:
        return self._cast_simple(skill_name="energy_shield", mouse_click_type="right")

    def _cast_frozen_armor(self) -> bool:
        return self._cast_simple(skill_name="frozen_armor", mouse_click_type="right")