import keyboard
import mouse
from utils import custom_mouse
from char.i_char import IChar
from template_finder import TemplateFinder
from ui_manager import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait
import random
import time
from typing import Tuple
from pather import Pather, Location


class Hammerdin(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pather = pather

    def pre_buff(self):
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.15, 0.3)
        mouse.click(button="right")
        if self._char_config["cta_available"]:
            wait(1.0, 1.4)
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.25, 0.3)
            keyboard.send(self._char_config["battle_orders"])
            wait(0.25, 0.3)
            mouse.click(button="right")
            wait(1.2, 1.5)
            keyboard.send(self._char_config["battle_command"])
            wait(0.25, 0.3)
            mouse.click(button="right")
            wait(1.1, 1.3)
            keyboard.send(self._char_config["weapon_switch"])
            wait(0.25, 0.3)

    def _cast_hammers(self, time_in_s: float):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        wait(0.05)
        keyboard.send(self._skill_hotkeys["blessed_hammer"])
        wait(0.05)
        keyboard.send(self._skill_hotkeys["concentration"])
        wait(0.05, 0.1)
        mouse.press(button="left")
        start = time.time()
        while (time.time() - start) < time_in_s:
            time.sleep(0.05)
        mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _do_redemption(self):
        keyboard.send(self._skill_hotkeys["redemption"])
        wait(1.5, 2.0)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if not self._pather.traverse_nodes(Location.PINDLE_SAVE_DIST, Location.PINDLE_END, self):
            return False
        self._cast_hammers(1)
        # pindle sometimes knocks back, get back in
        if not self._pather.traverse_nodes(Location.PINDLE_SAVE_DIST, Location.PINDLE_END, self):
            return False
        self._cast_hammers(6)
        wait(0.1, 0.15)
        self._do_redemption()
        return True

    def kill_shenk(self, shenk_pos_screen: Tuple[float, float]):
        pos_monitor = self._screen.convert_screen_to_monitor(shenk_pos_screen)
        keyboard.send(self._skill_hotkeys["teleport"])
        wait(0.05)
        custom_mouse.move(pos_monitor[0], pos_monitor[1], duration=(random.random() * 0.05 + 0.15))
        wait(0.02)
        mouse.click(button="right")
        wait(0.1, 0.15)
        self._cast_hammers(6)
        wait(0.1, 0.15)
        self._do_redemption()

    def kill_eldritch(self) -> bool:
        if not self._pather.traverse_nodes(Location.ELDRITCH_SAVE_DIST, Location.ELDRITCH_END, self):
            return False
        wait(0.1, 0.15)
        self._cast_hammers(6)
        wait(0.1, 0.15)
        self._do_redemption()
        return True
