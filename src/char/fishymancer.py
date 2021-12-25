import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, rotate_vec, unit_vector
import random
import time
from typing import Tuple
from pather import Location, Pather
import numpy as np


class Fishymancer(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Fishymancer")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pather = pather

    def _raise_skeleton(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10, number: int = 2):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["raise_skeleton"]:
            keyboard.send(self._skill_hotkeys["raise_skeleton"])
        for _ in range(number):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def pre_buff(self):
        delay = [0.2, 0.3]
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        #if self._skill_hotkeys["clay_golem"]:
            #keyboard.send(self._skill_hotkeys["clay_golem"])
            #wait(0.1, 0.13)
            #mouse.click(button="right")
            #wait(self._cast_duration)
        if self._skill_hotkeys["bone_armor"]:
            keyboard.send(self._skill_hotkeys["bone_armor"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        #Raise Skeletons at beginning of Pindle
        if self._template_finder.search_and_wait(["PINDLE_0", "PINDLE_1"], threshold=0.65, time_out=20).valid:
            cast_pos_abs = [260, -310]
            self._raise_skeleton(cast_pos_abs, delay, 11)
            cast_pos_abs = [360, -150]
            self._raise_skeleton(cast_pos_abs, delay, 11,1)

    def _clay_golem(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["clay_golem"]:
            keyboard.send(self._skill_hotkeys["clay_golem"])
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _poisen_nova(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["poisen_nova"]:
            keyboard.send(self._skill_hotkeys["poisen_nova"])
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _amplify_damage(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["amplify_damage"]:
            keyboard.send(self._skill_hotkeys["amplify_damage"])
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _corpse_explosion(self, cast_pos_abs: Tuple[float, float], delay: float, spray: float = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        keyboard.send(self._skill_hotkeys["corpse_explosion"])
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(delay[0], delay[1])
        mouse.release(button="right")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def kill_pindle(self) -> bool:
        delay = [0.2, 0.3]
        if self.can_teleport():
            pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        else:
            pindle_pos_abs = self._pather.find_abs_node_pos(104, self._screen.grab())       
        difficulty=self._config.general["difficulty"]       
        if difficulty == "hell":
            Logger.error("kill_pindle hell with necromancer is not implemented")
            self._ui_manager.save_and_exit()    
        if pindle_pos_abs is not None:
            # Default casts at entrance
            cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
            cast_pos_abs_skel = [pindle_pos_abs[0] * -0.9, pindle_pos_abs[1] * -0.9]
            self._raise_skeleton(cast_pos_abs_skel, delay, 11)
            self._raise_skeleton(cast_pos_abs_skel, delay, 11)
            self._clay_golem(cast_pos_abs, delay, 11)
            wait(self._cast_duration, self._cast_duration + 1.5)
            if difficulty == "normal":
                for _ in range(int(self._char_config["atk_len_pindle"])):
                    self._amplify_damage(cast_pos_abs, delay, 11)
                    self._poisen_nova(cast_pos_abs, delay, 11)
                    wait(self._cast_duration, self._cast_duration + 2.0)
                self._corpse_explosion(cast_pos_abs, delay, 11)
                wait(self._cast_duration, self._cast_duration + 4.5)
            if difficulty == "nightmare":
                for _ in range(int(self._char_config["atk_len_pindle"])+1):
                    self._amplify_damage(cast_pos_abs, delay, 11)
                    self._amplify_damage(cast_pos_abs_skel, delay, 11)
                    self._corpse_explosion(cast_pos_abs, delay, 11)
                    self._raise_skeleton(cast_pos_abs_skel, delay, 11,1)
                    wait(self._cast_duration, self._cast_duration + 2.5)
                self._corpse_explosion(cast_pos_abs, delay, 11)
                wait(self._cast_duration, self._cast_duration + 5.5)
            # Move to items
            if self.can_teleport():
                self._pather.traverse_nodes_fixed("pindle_end", self)
            else:
                self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, force_tp=True)
            return True
        return False

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Fishymancer(config.fishymancer, config.char, screen, t_finder, ui_manager, pather)
    char.pre_buff()
    char.kill_council()
