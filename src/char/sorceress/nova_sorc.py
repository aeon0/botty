import keyboard
import time
import numpy as np
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
from pather import Location


class NovaSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Nova Sorc")
        super().__init__(*args, **kwargs)
        # we want to change positions a bit of end points
        self._pather.offset_node(149, (70, 10))

    def _nova(self, time_in_s: float):
        if not self._skill_hotkeys["nova"]:
            raise ValueError("You did not set nova hotkey!")
        keyboard.send(self._skill_hotkeys["nova"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.03, 0.04)
            mouse.press(button="right")
            wait(0.12, 0.2)
            mouse.release(button="right")

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._nova(atk_len)

    def kill_pindle(self) -> bool:
        self._pather.traverse_nodes_fixed("pindle_end", self)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_pindle"])
        return True

    def kill_eldritch(self) -> bool:
        self._pather.traverse_nodes_fixed([(675, 30)], self)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_eldritch"])
        return True

    def kill_shenk(self) -> bool:
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_shenk"])
        return True

    def kill_council(self) -> bool:
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"] * 0.21
        # change node to be further to the right
        offset_229 = np.array([200, 100])
        self._pather.offset_node(229, offset_229)
        def clear_inside():
            self._pather.traverse_nodes_fixed([(1110, 120)], self)
            self._pather.traverse_nodes([229], self, time_out=0.8, force_tp=True)
            self._nova(atk_len)
            self._move_and_attack((-40, -20), atk_len)
            self._move_and_attack((40, 20), atk_len)
            self._move_and_attack((40, 20), atk_len)
        def clear_outside():
            self._pather.traverse_nodes([226], self, time_out=0.8, force_tp=True)
            self._nova(atk_len)
            self._move_and_attack((45, -20), atk_len)
            self._move_and_attack((-45, 20), atk_len)
        clear_inside()
        clear_outside()
        clear_inside()
        clear_outside()
        # change back node as it is used in trav.py
        self._pather.offset_node(229, -offset_229)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        atk_len = self._char_config["atk_len_nihlathak"] * 0.3
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_static(0.6)
        self._nova(atk_len)
        self._move_and_attack((50, 25), atk_len)
        self._move_and_attack((-70, -35), atk_len)
        return True

    def kill_summoner(self) -> bool:
        # move mouse to below altar
        pos_m = self._screen.convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._nova(self._char_config["atk_len_arc"])
        # Move a bit back and another round
        self._move_and_attack((0, 80), self._char_config["atk_len_arc"] * 0.5)
        wait(0.1, 0.15)
        self._nova(self._char_config["atk_len_arc"] * 0.5)
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
    char = NovaSorc(config.nova_sorc, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
