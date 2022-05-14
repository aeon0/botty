import keyboard
from typing import Tuple, Union, List, Callable
from utils.custom_mouse import mouse
from char import IChar
import template_finder
from pather import Pather
from screen import grab
from utils.misc import wait
import time
from typing import Tuple
from pather import Pather
from config import Config
from ui_manager import ScreenObjects, is_visible

class Sorceress(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        super().__init__(skill_hotkeys)
        self._pather = pather

    def pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
        if self._skill_hotkeys["telekinesis"] and any(x in item_name for x in ['potion', 'misc_gold', 'tp_scroll']):
            keyboard.send(self._skill_hotkeys["telekinesis"])
            wait(0.1, 0.2)
            mouse.move(pos[0], pos[1])
            wait(0.1, 0.2)
            mouse.click(button="right")
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
        template_type:  Union[str, List[str]],
        success_func: Callable = None,
        timeout: float = 8,
        threshold: float = 0.68,
        telekinesis: bool = False
    ) -> bool:
        # In case telekinesis is False or hotkey is not set, just call the base implementation
        if not self._skill_hotkeys["telekinesis"] or not telekinesis:
            return super().select_by_template(template_type, success_func, timeout, threshold)
        if type(template_type) == list and "A5_STASH" in template_type:
            # sometimes waypoint is opened and stash not found because of that, check for that
            if is_visible(ScreenObjects.WaypointLabel):
                keyboard.send("esc")
        start = time.time()
        while timeout is None or (time.time() - start) < timeout:
            template_match = template_finder.search(template_type, grab(), threshold=threshold)
            if template_match.valid:
                keyboard.send(self._skill_hotkeys["telekinesis"])
                wait(0.1, 0.2)
                mouse.move(*template_match.center_monitor)
                wait(0.2, 0.3)
                mouse.click(button="right")
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        # In case telekinesis fails, try again with the base implementation
        return super().select_by_template(template_type, success_func, timeout, threshold)

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        if self._skill_hotkeys["energy_shield"]:
            keyboard.send(self._skill_hotkeys["energy_shield"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["thunder_storm"]:
            keyboard.send(self._skill_hotkeys["thunder_storm"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["frozen_armor"]:
            keyboard.send(self._skill_hotkeys["frozen_armor"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)

    def _cast_static(self, duration: float = 1.4):
        if self._skill_hotkeys["static_field"]:
            keyboard.send(self._skill_hotkeys["static_field"])
            wait(0.1, 0.13)
            start = time.time()
            while time.time() - start < duration:
                mouse.click(button="right")
                wait(self._cast_duration)
