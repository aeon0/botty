import keyboard
from utils.custom_mouse import mouse
from char import IChar
from pather import Pather
from logger import Logger
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from config import Config
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location, Pather
import numpy as np


class Trapsin(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        Logger.info("Setting up Trapsin")
        super().__init__(skill_hotkeys)
        self._pather = pather

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        if self._skill_hotkeys["fade"]:
            keyboard.send(self._skill_hotkeys["fade"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["shadow_warrior"]:
            keyboard.send(self._skill_hotkeys["shadow_warrior"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["burst_of_speed"]:
            keyboard.send(self._skill_hotkeys["burst_of_speed"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)

    def _left_attack(self, cast_pos_abs: tuple[float, float], spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.2, 0.3)
            mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)


    def _right_attack(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        keyboard.send(self._skill_hotkeys["lightning_sentry"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        def atk(num: int):
            for _ in range(num):
                mouse.press(button="right")
                wait(0.20)
                mouse.release(button="right")
                wait(0.15)
        atk(4)
        keyboard.send(self._skill_hotkeys["death_sentry"])
        atk(1)

    def kill_pindle(self) -> bool:
        atk_len = max(1, int(Config().char["atk_len_pindle"] / 2))
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 11)
            self._left_attack(cast_pos_abs, 11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, force_tp=True)
        return True

    def kill_eldritch(self) -> bool:
        atk_len = max(1, int(Config().char["atk_len_eldritch"] / 2))
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 90)
            self._left_attack(cast_pos_abs, 90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.6, force_tp=True)
        return True

    def kill_shenk(self) -> bool:
        atk_len = max(1, int(Config().char["atk_len_shenk"] / 2))
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 90)
            self._left_attack(cast_pos_abs, 90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_len = max(1, int(Config().char["atk_len_nihlathak"] / 2))
        for i in range(atk_len):
            nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
            if nihlathak_pos_abs is None:
                return False
            cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
            self._left_attack(cast_pos_abs, 90)
            self._right_attack(cast_pos_abs, 90)
            # Do some tele "dancing" after each sequence
            if i < atk_len - 1:
                rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                pos_m = convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                self.move(pos_m)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char import Trapsin
    pather = Pather()
    char = Trapsin(Config().trapsin, Config().char, pather)