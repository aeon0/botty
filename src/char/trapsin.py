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
        if self._skill_hotkeys["burst_of_speed"]:
            keyboard.send(self._skill_hotkeys["burst_of_speed"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
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

    def _lightning_sentry(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.15, 0.20), atk_times: int = 4, spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["lightning_sentry"]:
            keyboard.send(self._skill_hotkeys["lightning_sentry"])
        for _ in range(atk_times):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _death_sentry(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.15, 0.20), atk_times: int = 1, spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["death_sentry"]:
            keyboard.send(self._skill_hotkeys["death_sentry"])
        for _ in range(atk_times):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _left_attack(self, cast_pos_abs: tuple[float, float], spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(1):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.15, 0.2)
            mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def kill_pindle(self) -> bool:
        atk_len = max(1, int(Config().char["atk_len_pindle"] / 2))
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._left_attack(cast_pos_abs, 11)
            self._lightning_sentry(cast_pos_abs,spray=11)
            self._death_sentry(cast_pos_abs,spray=11)
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
            self._left_attack(cast_pos_abs, 90)
            self._lightning_sentry(cast_pos_abs,spray=90)
            self._death_sentry(cast_pos_abs,spray=90)
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
            self._left_attack(cast_pos_abs, 90)
            self._lightning_sentry(cast_pos_abs,spray=90)
            self._death_sentry(cast_pos_abs,spray=90)
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
            self._lightning_sentry(cast_pos_abs,spray=90)
            self._death_sentry(cast_pos_abs,spray=90)
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

    def kill_council(self) -> bool:
        # Move inside to the right
        self._pather.traverse_nodes_fixed([(1110, 120)], self)
        self._pather.offset_node(300, (80, -110))
        self._pather.traverse_nodes([300], self, timeout=1.0, force_tp=True)
        self._pather.offset_node(300, (-80, 110))
        wait(0.5)
        self._left_attack((-150, 0), spray=10)
        self._death_sentry((-150, 0), spray=10)
        self._lightning_sentry((-150, 15), spray=10)
        self._left_attack((-150, 0), spray=10)
        wait(0.5)
        self._death_sentry((-150, 0), spray=10)
        self._lightning_sentry((-150, 15), spray=10)
        self._left_attack((-150, 0), spray=10)
        wait(0.5)
        pos_m = convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        pos_m = convert_abs_to_monitor((-550, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._pather.offset_node(226, (-80, 60))
        self._pather.traverse_nodes([226], self, timeout=1.0, force_tp=True)
        self._pather.offset_node(226, (80, -60))
        wait(0.5)
        self._left_attack((200, -185), spray=10)
        self._lightning_sentry((200, -185), spray=20)
        self._left_attack((-170, -150), spray=10)
        self._lightning_sentry((-170, -150), spray=20)
        wait(0.5)
        self._pather.traverse_nodes_fixed([(1110, 15)], self)
        self._pather.traverse_nodes([300], self, timeout=1.0, force_tp=True)
        pos_m = convert_abs_to_monitor((300, 150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._left_attack((-300, -110), spray=10)
        self._death_sentry((-300, -110), spray=10)
        self._lightning_sentry((-300, -100), atk_times=2, spray=10)
        self._lightning_sentry((-300, -90), atk_times=2, spray=10)
        self._left_attack((-300, -90), spray=10)
        wait(0.5)
        # Move back outside and attack
        pos_m = convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.offset_node(304, (0, -80))
        self._pather.traverse_nodes([304], self, timeout=1.0, force_tp=True)
        self._pather.offset_node(304, (0, 80))
        wait(0.5)
        self._left_attack((-170, -150), spray=10)
        self._death_sentry((-170, -150), spray=10)
        self._lightning_sentry((-170, -150), spray=20)
        self._left_attack((300, -200), spray=10)
        self._death_sentry((300, -200), spray=10)
        self._lightning_sentry((300, -200), spray=20)
        self._left_attack((-170, -150), spray=10)
        self._death_sentry((-170, -150), spray=10)
        self._lightning_sentry((-170, -150), spray=20)
        wait(0.5)
        # Move back inside and attack
        pos_m = convert_abs_to_monitor((350, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Attack sequence center
        self._left_attack((-50, 50), spray=10)
        self._death_sentry((-50, 50), spray=30)
        self._lightning_sentry((-50, 50), spray=20)
        self._left_attack((50, 50), spray=10)
        self._death_sentry((50, 50), spray=30)
        self._lightning_sentry((50, 50), spray=20)
        wait(0.5)
        # Move inside
        pos_m = convert_abs_to_monitor((40, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        wait(0.5)
        self._left_attack((-150, 100), spray=10)
        self._death_sentry((-150, 100), spray=10)
        self._lightning_sentry((-150, 100), spray=20)
        self._left_attack((150, 200), spray=10)
        self._death_sentry((150, 200), spray=10)
        self._lightning_sentry((150, 200), spray=40)
        self._left_attack((-150, 0), spray=10)
        self._death_sentry((-150, 0), spray=10)
        self._lightning_sentry((-150, 0), spray=20)
        wait(0.5)
        pos_m = convert_abs_to_monitor((-200, 240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
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