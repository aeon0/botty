import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from typing import Tuple
from pather import Location
import numpy as np


class LightSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Light Sorc")
        super().__init__(*args, **kwargs)

    def _left_attack(self, cast_pos_abs: Tuple[float, float], delay: float, spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["chain_lightning"]:
            keyboard.send(self._skill_hotkeys["chain_lightning"])
        for _ in range(5):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _right_attack(self, cast_pos_abs: Tuple[float, float], delay: float, spray: float = 10):
        keyboard.send(self._skill_hotkeys["lightning"])
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="right")
        wait(delay[0], delay[1])
        mouse.release(button="right")

    def kill_pindle(self) -> bool:
        delay = [0.2, 0.3]
        if self.can_teleport():
            pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        else:
            pindle_pos_abs = self._pather.find_abs_node_pos(104, self._screen.grab())
        if pindle_pos_abs is not None:
            cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
            for _ in range(int(self._char_config["atk_len_pindle"])):
                self._right_attack(cast_pos_abs, delay, 11)
                self._left_attack(cast_pos_abs, delay, 11)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            if self.can_teleport():
                self._pather.traverse_nodes_fixed("pindle_end", self)
            else:
                self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, force_tp=True)
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
                self._right_attack(cast_pos_abs, delay, 90)
                self._left_attack(cast_pos_abs, delay, 90)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            if self.can_teleport():
                self._pather.traverse_nodes_fixed("eldritch_end", self)
            else:
                self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=0.6, force_tp=True)
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
                self._right_attack(cast_pos_abs, delay, 90)
                self._left_attack(cast_pos_abs, delay, 90)
            wait(self._cast_duration, self._cast_duration + 0.2)
            # Move to items
            self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
            return True
        return False

    def kill_council(self) -> bool:
        delay = [0.2, 0.3]
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        # Go inside cast stuff in general direction
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True)
        atk_pos_abs = self._pather.find_abs_node_pos(230, self._screen.grab())
        if atk_pos_abs is None:
            atk_pos_abs = [-300, -200]
        cast_pos_abs = np.array([atk_pos_abs[0] * 0.9, atk_pos_abs[1] * 0.9])
        self._right_attack(cast_pos_abs, delay, 80)
        self._cast_static()
        self._left_attack(cast_pos_abs, delay, 80)
        self._right_attack((0, 0), delay, 30)
        self._left_attack(cast_pos_abs, delay, 80)
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((160, 30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        atk_pos_abs = self._pather.find_abs_node_pos(229, self._screen.grab())
        if atk_pos_abs is None:
            atk_pos_abs = [-200, -80]
        self._left_attack(cast_pos_abs, delay, 60)
        self._right_attack(cast_pos_abs, delay, 60)
        self._right_attack((0, 0), delay, 60)
        # Move outside
        # Move a bit back and another round
        self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        cast_pos_abs = np.array([-300, -100])
        self._left_attack(cast_pos_abs, delay, 60)
        self._right_attack(cast_pos_abs, delay, 60)
        self._cast_static()
        self._right_attack((0, 0), delay, 30)
        wait(0.4)
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((100, -100))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._right_attack((0, 0), delay, 80)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_sequences = int(self._char_config["atk_len_nihlatak"])
        for i in range(atk_sequences):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is not None:
                cast_pos_abs = np.array([nihlatak_pos_abs[0] * 0.9, nihlatak_pos_abs[1] * 0.9])
                self._right_attack(cast_pos_abs, delay, 90)
                self._left_attack(cast_pos_abs, delay, 90)
                # Do some tele "dancing" after each sequence
                if i < atk_sequences - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
        # Move to items
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True
        
    def kill_summoner(self) -> bool:
        # Attack
        delay = [0.2, 0.3]
        cast_pos_abs = np.array([0, 0])
        pos_m = self._screen.convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(self._char_config["atk_len_arc"])):
            self._right_attack(cast_pos_abs, delay, 11)
            self._left_attack(cast_pos_abs, delay, 11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        return True
