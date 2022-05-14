import keyboard
from ui import skills
from utils.custom_mouse import mouse
from char import IChar
import template_finder
from pather import Pather
from logger import Logger
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from config import Config
from utils.misc import wait, cut_roi
import time
import random
import numpy as np
from pather import Pather, Location


class Basic_Ranged(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        Logger.info("Setting up Basic Ranged Character")
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._do_pre_move = True

    def _left_attack(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: int = 10):
        if self._skill_hotkeys["left_attack"]:
            keyboard.send(self._skill_hotkeys["left_attack"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m)
            mouse.click(button="left")

    def _right_attack(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if not self._skill_hotkeys["right_attack"]:
            raise ValueError("You did not set right attack hotkey!")
        keyboard.send(self._skill_hotkeys["right_attack"])
        for _ in range(3):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.click(button="right")

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
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
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        start = time.time()
        keyboard.send(Config().char["stand_still"], do_release=False)
        while (time.time() - start) < Config().char["atk_len_pindle"]:
            if skills.is_right_skill_active():
                wait(0.05, 0.1)
                self._right_attack(cast_pos_abs, spray=11)
            else:
                wait(0.05, 0.1)
                self._left_attack(cast_pos_abs, spray=11)
        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.4, force_tp=True)
        return True


    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        start = time.time()
        keyboard.send(Config().char["stand_still"], do_release=False)
        while (time.time() - start) < Config().char["atk_len_eldritch"]:
            if skills.is_right_skill_active():
                wait(0.05, 0.1)
                self._right_attack(cast_pos_abs, spray=11)
            else:
                wait(0.05, 0.1)
                self._left_attack(cast_pos_abs, spray=11)
        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=1.4, force_tp=True)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        start = time.time()
        keyboard.send(Config().char["stand_still"], do_release=False)
        while (time.time() - start) < Config().char["atk_len_shenk"]:
            if skills.is_right_skill_active():
                wait(0.05, 0.1)
                self._right_attack(cast_pos_abs, spray=11)
            else:
                wait(0.05, 0.1)
                self._left_attack(cast_pos_abs, spray=11)
        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        atk_len_trav_2 = int(Config().char["atk_len_trav"] / 2)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        # Go inside cast stuff in general direction
        self._pather.offset_node(229, [250, 130])
        self._pather.traverse_nodes([228, 229], self, timeout=2.5, force_tp=True)
        self._pather.offset_node(229, [-250, -130])
        atk_pos_abs = self._pather.find_abs_node_pos(230, grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [230]. Using static attack coordinates instead.")
            atk_pos_abs = [-300, -200]
        else:
            atk_pos_abs = [atk_pos_abs[0], atk_pos_abs[1] + 70]
        cast_pos_abs = np.array([atk_pos_abs[0] * 0.9, atk_pos_abs[1] * 0.9])
        self._left_attack(cast_pos_abs, spray=80)
        for _ in range(atk_len_trav_2):
            if skills.is_right_skill_active():
                self._right_attack(cast_pos_abs, spray=11)
            else:
                self._left_attack(cast_pos_abs, spray=11)
        # move a bit back
        pos_m = convert_abs_to_monitor((160, 30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        atk_pos_abs = self._pather.find_abs_node_pos(229, grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [229]. Using static attack coordinates instead.")
            atk_pos_abs = [-200, -80]
            for _ in range(atk_len_trav_2):
                if skills.is_right_skill_active():
                    self._right_attack(cast_pos_abs, spray=11)
                else:
                    self._left_attack(cast_pos_abs, spray=11)
        # Move outside
        # Move a bit back and another round
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        cast_pos_abs = np.array([-300, -100])
        for _ in range(atk_len_trav_2):
            if skills.is_right_skill_active():
                self._right_attack(cast_pos_abs, spray=11)
            else:
                self._left_attack(cast_pos_abs, spray=11)
        # move a bit back
        pos_m = convert_abs_to_monitor((100, 0))
        cast_pos_abs = self._pather.find_abs_node_pos(229, grab())
        if cast_pos_abs is not None:
            self.pre_move()
            self.move(pos_m, force_move=True)
            for _ in range(atk_len_trav_2):
                if skills.is_right_skill_active():
                    self._right_attack(cast_pos_abs, spray=11)
                else:
                    self._left_attack(cast_pos_abs, spray=11)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_len = int(Config().char["atk_len_nihlathak"])
        nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
        if nihlathak_pos_abs is None:
            return False
        cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
        for _ in range(atk_len):
            if skills.is_right_skill_active():
                self._right_attack(cast_pos_abs, spray=11)
            else:
                self._left_attack(cast_pos_abs, spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    import template_finder
    from pather import Pather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    pather = Pather()