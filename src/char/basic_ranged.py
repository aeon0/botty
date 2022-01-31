import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, cut_roi
import time
import random
import numpy as np
from pather import Pather, Location


class Basic_Ranged(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Basic Ranged Character")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager)
        self._pather = pather
        self._do_pre_move = True

    def _left_attack(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: int = 10):
        if self._skill_hotkeys["left_attack"]:
            keyboard.send(self._skill_hotkeys["left_attack"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*pos_m)
            mouse.click(button="left")

    def _right_attack(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if not self._skill_hotkeys["right_attack"]:
            raise ValueError("You did not set right attack hotkey!")
        keyboard.send(self._skill_hotkeys["right_attack"])
        for _ in range(3):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.click(button="right")

    def pre_buff(self):
        if self._skill_hotkeys["buff_1"]:
            keyboard.send(self._skill_hotkeys["buff_1"])
            wait(0.5, 0.15)
            mouse.click(button="right")
            wait(0.5, 0.15)
        if self._skill_hotkeys["buff_2"]:
            keyboard.send(self._skill_hotkeys["buff_2"])
            wait(0.5, 0.15)
            mouse.click(button="right")
            wait(0.5, 0.15)


#bosses

    def kill_pindle(self) -> bool:
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        start = time.time()
        keyboard.send(self._char_config["stand_still"], do_release=False)
        while (time.time() - start) < self._char_config["atk_len_pindle"]:
            if self._ui_manager.is_right_skill_active():
                wait(0.05, 0.1)
                self._right_attack(cast_pos_abs, spray=11)
            else:
                wait(0.05, 0.1)
                self._left_attack(cast_pos_abs, spray=11)
        keyboard.send(self._char_config["stand_still"], do_press=False)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=1.4, force_tp=True)
        return True


    def kill_eldritch(self) -> bool:
        eld_pos_abs = self._screen.convert_screen_to_abs(self._config.path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        start = time.time()
        keyboard.send(self._char_config["stand_still"], do_release=False)
        while (time.time() - start) < self._char_config["atk_len_eldritch"]:
            if self._ui_manager.is_right_skill_active():
                wait(0.05, 0.1)
                self._right_attack(cast_pos_abs, spray=11)
            else:
                wait(0.05, 0.1)
                self._left_attack(cast_pos_abs, spray=11)
        keyboard.send(self._char_config["stand_still"], do_press=False)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, self._screen.grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        start = time.time()
        keyboard.send(self._char_config["stand_still"], do_release=False)
        while (time.time() - start) < self._char_config["atk_len_shenk"]:
            if self._ui_manager.is_right_skill_active():
                wait(0.05, 0.1)
                self._right_attack(cast_pos_abs, spray=11)
            else:
                wait(0.05, 0.1)
                self._left_attack(cast_pos_abs, spray=11)
        keyboard.send(self._char_config["stand_still"], do_press=False)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        atk_len_trav_2 = int(self._char_config["atk_len_trav"] / 2)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        # Go inside cast stuff in general direction
        self._pather.offset_node(229, [250, 130])
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True)
        self._pather.offset_node(229, [-250, -130])
        atk_pos_abs = self._pather.find_abs_node_pos(230, self._screen.grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [230]. Using static attack coordinates instead.")
            atk_pos_abs = [-300, -200]
        else:
            atk_pos_abs = [atk_pos_abs[0], atk_pos_abs[1] + 70]
        cast_pos_abs = np.array([atk_pos_abs[0] * 0.9, atk_pos_abs[1] * 0.9])
        self._left_attack(cast_pos_abs, spray=80)
        for _ in range(atk_len_trav_2):
            if self._ui_manager.is_right_skill_active():
                self._right_attack(cast_pos_abs, spray=11)
            else:
                self._left_attack(cast_pos_abs, spray=11)
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((160, 30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        atk_pos_abs = self._pather.find_abs_node_pos(229, self._screen.grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [229]. Using static attack coordinates instead.")
            atk_pos_abs = [-200, -80]
            for _ in range(atk_len_trav_2):
                if self._ui_manager.is_right_skill_active():
                    self._right_attack(cast_pos_abs, spray=11)
                else:
                    self._left_attack(cast_pos_abs, spray=11)
        # Move outside
        # Move a bit back and another round
        self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        cast_pos_abs = np.array([-300, -100])
        for _ in range(atk_len_trav_2):
            if self._ui_manager.is_right_skill_active():
                self._right_attack(cast_pos_abs, spray=11)
            else:
                self._left_attack(cast_pos_abs, spray=11)
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((100, 0))
        cast_pos_abs = self._pather.find_abs_node_pos(229, self._screen.grab())
        if cast_pos_abs is not None:
            self.pre_move()
            self.move(pos_m, force_move=True)
            for _ in range(atk_len_trav_2):
                if self._ui_manager.is_right_skill_active():
                    self._right_attack(cast_pos_abs, spray=11)
                else:
                    self._left_attack(cast_pos_abs, spray=11)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_len = int(self._char_config["atk_len_nihlathak"])
        nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
        if nihlathak_pos_abs is None:
            return False
        cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
        for _ in range(atk_len):
            if self._ui_manager.is_right_skill_active():
                self._right_attack(cast_pos_abs, spray=11)
            else:
                self._left_attack(cast_pos_abs, spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    from screen import Screen
    from template_finder import TemplateFinder
    from pather import Pather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen()
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
