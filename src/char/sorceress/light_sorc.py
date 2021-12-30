import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location
import numpy as np


class LightSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Light Sorc")
        super().__init__(*args, **kwargs)

    def _chain_lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["chain_lightning"]:
            keyboard.send(self._skill_hotkeys["chain_lightning"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*pos_m)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if not self._skill_hotkeys["lightning"]:
            raise ValueError("You did not set lightning hotkey!")
        keyboard.send(self._skill_hotkeys["lightning"])
        for _ in range(3):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")

    def kill_pindle(self) -> bool:
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_pindle"])):
            self._chain_lightning(cast_pos_abs, spray=11)
        self._lightning(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = self._screen.convert_screen_to_abs(self._config.path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_eldritch"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=50)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, self._screen.grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_shenk"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=60)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
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
        self._chain_lightning(cast_pos_abs, spray=80)
        self._cast_static()
        for _ in range(atk_len_trav_2):
            self._chain_lightning(cast_pos_abs, spray=80)
        self._lightning(cast_pos_abs, spray=60)
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((160, 30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        atk_pos_abs = self._pather.find_abs_node_pos(229, self._screen.grab())
        if atk_pos_abs is None:
            Logger.debug("Could not find node [229]. Using static attack coordinates instead.")
            atk_pos_abs = [-200, -80]
        self._chain_lightning(cast_pos_abs, spray=60)
        self._lightning(cast_pos_abs, spray=60)
        # Move outside
        # Move a bit back and another round
        self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        cast_pos_abs = np.array([-300, -100])
        for _ in range(atk_len_trav_2):
            self._chain_lightning(cast_pos_abs, spray=60)
        self._cast_static()
        # move a bit back
        pos_m = self._screen.convert_abs_to_monitor((100, 0))
        cast_pos_abs = self._pather.find_abs_node_pos(229, self._screen.grab())
        if cast_pos_abs is not None:
            self.pre_move()
            self.move(pos_m, force_move=True)
            for _ in range(atk_len_trav_2):
                self._chain_lightning(cast_pos_abs, spray=60)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_len = int(self._char_config["atk_len_nihlatak"])
        for i in range(atk_len):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is None:
                return False
            cast_pos_abs = np.array([nihlatak_pos_abs[0] * 0.9, nihlatak_pos_abs[1] * 0.9])
            self._chain_lightning(cast_pos_abs, delay, 90)
            # Do some tele "dancing" after each sequence
            if i < atk_len - 1:
                rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                self.move(pos_m)
            else:
                self._lightning(cast_pos_abs, spray=60)
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
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = LightSorc(config.light_sorc, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
