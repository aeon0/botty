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
            mouse.move(*pos_m, delay_factor=[0.3, 0.6])
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
            mouse.move(*cast_pos_monitor, delay_factor=[0.3, 0.6])
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")

    def _frozen_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if self._skill_hotkeys["frozen_orb"]:
            keyboard.send(self._skill_hotkeys["frozen_orb"])
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
        for _ in range(int(self._char_config["atk_len_shenk"] * 0.5)):
            self._chain_lightning(cast_pos_abs, spray=90)
        pos_m = self._screen.convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_shenk"] * 0.5)):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=60)
        pos_m = self._screen.convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_shenk"])):
            self._chain_lightning(cast_pos_abs, spray=90)
        self._lightning(cast_pos_abs, spray=60)
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        # Move inside to the right
        self._pather.traverse_nodes_fixed([(1110, 120)], self)
        self._pather.offset_node(300, (80, -110))
        self._pather.traverse_nodes([300], self, time_out=1.0, force_tp=True)
        self._pather.offset_node(300, (-80, 110))
        wait(0.5)
        self._frozen_orb((-150, -10), spray=10)
        self._lightning((-150, 0), spray=10)
        self._chain_lightning((-150, 15), spray=10)
        wait(0.5)
        pos_m = self._screen.convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        pos_m = self._screen.convert_abs_to_monitor((-550, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._pather.offset_node(226, (-80, 60))
        self._pather.traverse_nodes([226], self, time_out=1.0, force_tp=True)
        self._pather.offset_node(226, (80, -60))
        wait(0.5)
        self._frozen_orb((-150, -130), spray=10)
        self._chain_lightning((200, -185), spray=20)
        self._chain_lightning((-170, -150), spray=20)
        wait(0.5)
        self._pather.traverse_nodes_fixed([(1110, 15)], self)
        self._pather.traverse_nodes([300], self, time_out=1.0, force_tp=True)
        pos_m = self._screen.convert_abs_to_monitor((300, 150))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        self._frozen_orb((-170, -100), spray=40)
        self._chain_lightning((-300, -100), spray=10)
        self._chain_lightning((-300, -90), spray=10)
        self._lightning((-300, -110), spray=10)
        wait(0.5)
        # Move back outside and attack
        pos_m = self._screen.convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.offset_node(304, (0, -80))
        self._pather.traverse_nodes([304], self, time_out=1.0, force_tp=True)
        self._pather.offset_node(304, (0, 80))
        wait(0.5)
        self._frozen_orb((175, -170), spray=40)
        self._chain_lightning((-170, -150), spray=20)
        self._chain_lightning((300, -200), spray=20)
        self._chain_lightning((-170, -150), spray=20)
        wait(0.5)
        # Move back inside and attack
        pos_m = self._screen.convert_abs_to_monitor((350, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        pos_m = self._screen.convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Attack sequence center
        self._frozen_orb((0, 20), spray=40)
        self._lightning((-50, 50), spray=30)
        self._lightning((50, 50), spray=30)
        wait(0.5)
        # Move inside
        pos_m = self._screen.convert_abs_to_monitor((40, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        wait(0.5)
        self._chain_lightning((-150, 100), spray=20)
        self._chain_lightning((150, 200), spray=40)
        self._chain_lightning((-150, 0), spray=20)
        wait(0.5)
        pos_m = self._screen.convert_abs_to_monitor((-200, 240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        delay = [0.2, 0.3]
        atk_len = int(self._char_config["atk_len_nihlathak"])
        nihlathak_pos_abs = None
        for i in range(atk_len):
            nihlathak_pos_abs_next = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())

            if nihlathak_pos_abs_next is not None:
                nihlathak_pos_abs = nihlathak_pos_abs_next
            else:
                Logger.warning(f"Can't find Nihlathak next position at node {end_nodes[-1]}")
                if nihlathak_pos_abs is not None:
                    Logger.warning(f"Using previous position for attack sequence")
                    
            if nihlathak_pos_abs is not None:
                cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
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
            else:               
                Logger.warning(f"Casting static as the last position isn't known. Skipping attack sequence")
                self._cast_static(duration=2)

        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        cast_pos_abs = np.array([0, 0])
        pos_m = self._screen.convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(self._char_config["atk_len_arc"])):
            self._chain_lightning(cast_pos_abs, spray=11)
            self._lightning(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
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
    char = LightSorc(config.light_sorc, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
