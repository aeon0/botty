import time
import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
import random
from pather import Location
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from config import Config

class HydraSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up HydraSorc Sorc")
        super().__init__(*args, **kwargs)
        self._hydra_time = None        

    def _alt_attack(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["alt_attack"]:
            keyboard.send(self._skill_hotkeys["alt_attack"])
        for _ in range(5):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _hydra(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if self._hydra_time is None or time.time() - self._hydra_time > 10:
            if not self._skill_hotkeys["hydra"]:
                raise ValueError("You did not set a hotkey for hydra!")
            keyboard.send(self._skill_hotkeys["hydra"])
            self._hydra_time = time.time()            
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(2,3)
            mouse.release(button="right")        

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_pindle"])):
            self._hydra(cast_pos_abs, spray=0)
            self._alt_attack(cast_pos_abs, spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        self._hydra_time = None
        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_eldritch"])):
            self._hydra(cast_pos_abs, spray=0)
            self._alt_attack(cast_pos_abs, spray=90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        self._hydra_time = None
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_shenk"] * 0.5)):
            self._hydra(cast_pos_abs, spray=0)
            self._alt_attack(cast_pos_abs, spray=90)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_shenk"] * 0.5)):
            self._hydra(cast_pos_abs, spray=0)
            self._alt_attack(cast_pos_abs, spray=90)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_shenk"])):
            self._hydra(cast_pos_abs, spray=0)
            self._alt_attack(cast_pos_abs, spray=90)
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        self._hydra_time = None
        return True