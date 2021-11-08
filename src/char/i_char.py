from typing import Tuple
from utils.custom_mouse import mouse
from template_finder import TemplateFinder
from ui_manager import UiManager
from screen import Screen
from utils.misc import wait
import random
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
        self._cast_duration = self._char_config["casting_frames"] * 0.04 + 0.04

    def select_by_template(self, template_type: str) -> bool:
        Logger.debug(f"Select {template_type}")
        success, screen_loc = self._template_finder.search_and_wait(template_type, time_out=10)
        if success:
            x_m, y_m = self._screen.convert_screen_to_monitor(screen_loc)
            mouse.move(x_m, y_m)
            wait(0.3, 0.4)
            mouse.click(button="left")
            return True
        return False

    def move(self, pos_monitor: Tuple[float, float]):
        if not self._ui_manager.is_teleport_selected():
            keyboard.send(self._skill_hotkeys["teleport"])
            wait(0.1, 0.2)
        if self._ui_manager.can_teleport():
            mouse.move(pos_monitor[0], pos_monitor[1])
            mouse.click(button="right")
            time.sleep(self._cast_duration)
        else:
            # in case we want to walk we actually want to move a bit before the point cause d2r will always "overwalk"
            pos_screen = self._screen.convert_monitor_to_screen(pos_monitor)
            pos_abs = self._screen.convert_screen_to_abs(pos_screen)
            dist = math.dist(pos_abs, (0, 0))
            adjust_factor = (dist - 50) / dist
            pos_abs = [int(pos_abs[0] * adjust_factor), int(pos_abs[1] * adjust_factor)]
            x, y = self._screen.convert_abs_to_monitor(pos_abs)
            mouse.move(x, y)
            mouse.click(button="left")
            wait(0.02, 0.03)
            if self._config.char["slow_walk"]:
                wait(1.2, 1.4)

    def tp_town(self):
        keyboard.send(self._char_config["tp"])
        wait(0.05, 0.1)
        mouse.click(button="right")
        mouse.move(1400 + random.randrange(0, 60), 300 + random.randrange(0, 60))
        time.sleep(1.4) # takes quite a while for tp to be visible
        roi = self._config.ui_roi["tp_search"]
        start = time.time()
        while (time.time() - start)  < 7:
            img = self._screen.grab()
            success1, pos1 = self._template_finder.search("BLUE_PORTAL", img, threshold=0.66, roi=roi)
            success2, pos2 = self._template_finder.search("BLUE_PORTAL_2", img, threshold=0.7, roi=roi)
            if success1 or success2:
                pos = pos1 if success1 else pos2
                pos = (pos[0], pos[1] + 48)
                x, y = self._screen.convert_screen_to_monitor(pos)
                # Note: Template is top of portal, thus move the y-position a bit to the bottom
                #       Also move a bit left and right to get rid of possibly highlight other things such as items
                mouse.move(x - 20, y, randomize=5)
                mouse.move(x + 20, y, randomize=5)
                mouse.move(x, y, randomize=5)
                wait(0.1, 0.14)
                mouse.click(button="left")
                return True
        return False

    def _pre_buff_cta(self):
        wait(0.1, 0.15)
        keyboard.send(self._char_config["weapon_switch"])
        wait(0.3, 0.33)
        keyboard.send(self._char_config["battle_command"])
        wait(0.1, 0.12)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.04)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.1, 0.12)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.04)
        keyboard.send(self._char_config["weapon_switch"])

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
