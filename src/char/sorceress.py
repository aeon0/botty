import keyboard
import mouse
from utils import custom_mouse
from char.i_char import IChar
from template_finder import TemplateFinder
from item_finder import ItemFinder
from ui_manager import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait
import random
from typing import Tuple
from pather import Location, Pather


class Sorceress(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Sorceress")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pather = pather

    def pre_buff(self):
        keyboard.send(self._skill_hotkeys["frozen_armor"])
        wait(0.1, 0.13)
        mouse.click(button="right")
        wait(self._cast_duration)
        if self._char_config["cta_available"]:
            self._pre_buff_cta()

    def _left_attack(self, cast_pos: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        custom_mouse.move(cast_pos[0], cast_pos[1], duration=(random.random() * 0.05 + 0.15))
        keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(6):
            x = cast_pos[0] + (random.random() * 2*spray - spray)
            y = cast_pos[1] + (random.random() * 2*spray - spray)
            custom_mouse.move(x, y, duration=(random.random() * 0.05 + 0.15))
            mouse.click(button="left")
            wait(delay[0], delay[1])
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _main_attack(self, cast_pos: Tuple[float, float], delay: float, spray: float = 10):
        keyboard.send(self._skill_hotkeys["skill_right"])
        x = cast_pos[0] + (random.random() * 2*spray - spray)
        y = cast_pos[1] + (random.random() * 2*spray - spray)
        custom_mouse.move(x, y, duration=(random.random() * 0.05 + 0.15))
        mouse.click(button="right")
        wait(delay[0], delay[1])

    def kill_pindle(self) -> bool:
        delay = [0.2, 0.3]
        pindle_pos_abs = self._pather.find_abs_node_pos(104, self._screen.grab())
        if pindle_pos_abs is not None:
            cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
            cast_pos_monitor = self._screen.convert_abs_to_monitor(cast_pos_abs)
            for _ in range(int(self._char_config["atk_len_pindle"])):
                self._main_attack(cast_pos_monitor, delay)
                self._left_attack(cast_pos_monitor, delay)
            wait(0.1, 0.15)
            # Move to items
            self._pather.traverse_nodes(Location.PINDLE_SAVE_DIST, Location.PINDLE_END, self)
            return True
        return False

    def kill_eldritch(self) -> bool:
        delay = [0.2, 0.3]
        pos_abs = self._pather.find_abs_node_pos(123, self._screen.grab())
        if pos_abs is not None:
            cast_pos_abs = [pos_abs[0] * 0.9, pos_abs[1] * 0.9]
            cast_pos_monitor = self._screen.convert_abs_to_monitor(cast_pos_abs)
            for _ in range(int(self._char_config["atk_len_eldritch"])):
                self._main_attack(cast_pos_monitor, delay, 90)
                self._left_attack(cast_pos_monitor, delay, 90)
            wait(0.2, 0.3)
            # Move to items
            self._pather.traverse_nodes(Location.ELDRITCH_SAVE_DIST, Location.ELDRITCH_END, self, time_out=2.0)
            return True
        return False

    def kill_shenk(self):
        delay = [0.2, 0.3]
        pos_abs = self._pather.find_abs_node_pos(149, self._screen.grab())
        cast_pos_abs = [pos_abs[0] * 0.9, pos_abs[1] * 0.9]
        cast_pos_monitor = self._screen.convert_abs_to_monitor(cast_pos_abs)
        for _ in range(int(self._char_config["atk_len_shenk"])):
            self._main_attack(cast_pos_monitor, delay, 90)
            self._left_attack(cast_pos_monitor, delay, 90)
        wait(0.2, 0.3)
        # Move to items
        self._pather.traverse_nodes(Location.SHENK_SAVE_DIST, Location.SHENK_END, self, time_out=2.0)



if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char.sorceress import Sorceress
    from ui_manager import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Sorceress(config.sorceress, config.char, screen, t_finder, ui_manager)
    char.pre_buff()
    # char.tp_town()
