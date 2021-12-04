import keyboard
from utils.custom_mouse import mouse
from char.i_char import IChar
from template_finder import TemplateFinder
from item_finder import ItemFinder
from ui_manager import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait
import random
import time
from typing import Tuple
from pather import Location, Pather


class Sorceress(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Sorceress")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
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

    def pre_buff(self):
        if self._char_config["cta_available"]:
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

    def _left_attack(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(6):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _main_attack(self, cast_pos_abs: Tuple[float, float], delay: float, spray: float = 10):
        keyboard.send(self._skill_hotkeys["skill_right"])
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(delay[0], delay[1])
        mouse.release(button="right")

    def kill_pindle(self) -> bool:
        delay = [0.2, 0.3]
        if self._config.char["static_path_pindle"]:
            pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        else:
            pindle_pos_abs = self._pather.find_abs_node_pos(104, self._screen.grab())
        if pindle_pos_abs is not None:
            cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
            for _ in range(int(self._char_config["atk_len_pindle"])):
                self._main_attack(cast_pos_abs, delay, 11)
                self._left_attack(cast_pos_abs, delay, 11)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            if self._config.char["static_path_pindle"]:
                self._pather.traverse_nodes_fixed("pindle_end", self)
            else:
                self._pather.traverse_nodes(Location.PINDLE_SAVE_DIST, Location.PINDLE_END, self, force_tp=True)
            return True
        return False

    def kill_eldritch(self) -> bool:
        delay = [0.2, 0.3]
        pos_abs = self._pather.find_abs_node_pos(1, self._screen.grab())
        if pos_abs is not None:
            eld_pos_abs = [pos_abs[0] * 0.9, pos_abs[1] * 0.9]
        else:
            eld_pos_abs = self._screen.convert_screen_to_abs(self._config.path["eldritch_end"][0])
        if eld_pos_abs is not None:
            cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
            for _ in range(int(self._char_config["atk_len_eldritch"])):
                self._main_attack(cast_pos_abs, delay, 90)
                self._left_attack(cast_pos_abs, delay, 90)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            if self._config.char["static_path_eldritch"]:
                self._pather.traverse_nodes_fixed("eldritch_end", self)
            else:
                self._pather.traverse_nodes(Location.ELDRITCH_SAVE_DIST, Location.ELDRITCH_END, self, time_out=0.6, force_tp=True)
            return True
        return False

    def kill_shenk(self) -> bool:
        delay = [0.2, 0.3]
        pos_abs = self._pather.find_abs_node_pos(149, self._screen.grab())
        if pos_abs is not None:
            shenk_pos_abs = [pos_abs[0] * 0.9, pos_abs[1] * 0.9]
        else:
            shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        if shenk_pos_abs is not None:
            cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
            for _ in range(int(self._char_config["atk_len_shenk"])):
                self._main_attack(cast_pos_abs, delay, 90)
                self._left_attack(cast_pos_abs, delay, 90)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            self._pather.traverse_nodes(Location.SHENK_SAVE_DIST, Location.SHENK_END, self, time_out=1.4, force_tp=True)
            return True
        return False


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
    char = Sorceress(config.sorceress, config.char, screen, t_finder, ui_manager, pather)
    # char.pre_buff()
    # char.tp_town()
    pather.traverse_nodes_fixed("eldritch_save_dist", char)
    char.kill_eldritch()
    # char.select_by_template(["A5_RED_PORTAL", "A5_RED_PORTAL_TEXT"], expect_loading_screen=True)
