import time
import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
import random
from pather import Pather, Location
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from config import Config
from target_detect import get_visible_targets
from item.pickit import PickIt

class HydraOrbSorc(Sorceress):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        Logger.info("Setting up HydraOrbSorc Sorc")
        super().__init__(skill_hotkeys, pather)
        self._pickit = pickit
        self._pather = pather
        self._picked_up_items = False
        self._hydra_time = None
        self._frozen_orb_time = None

    def _skill(self, hotkey: str, count: int, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        for _ in range(count):
            if not self._skill_hotkeys[hotkey]:
                raise ValueError(f'You did not set a hotkey for {hotkey}!')
            keyboard.send(self._skill_hotkeys[hotkey])
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _fireball(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10, count: int = 5):
        self._skill('fireball', count, cast_pos_abs, delay, spray)

    def _frozen_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 0, count: int = 1, force_recast: bool = False):
        if force_recast or self._frozen_orb_time is None or time.time() - self._frozen_orb_time > 3:
            self._frozen_orb_time = time.time()
            self._skill('frozen_orb', count, cast_pos_abs, delay, spray)

    def _fb_orb(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), fireball_spray: float = 10, frozen_orb_spray: float = 0, count: int = 2):
        start = time.time()
        while time.time() - start < count:
            self._frozen_orb(cast_pos_abs, delay=delay, spray=frozen_orb_spray, count=1)
            self._fireball(cast_pos_abs, delay=delay, spray=fireball_spray, count=1)

    def _hydra(self, cast_pos_abs: tuple[float, float], spray: float = 10, count = 6, force_recast: bool = False):
        if force_recast or self._hydra_time is None or time.time() - self._hydra_time > 10:
            if not self._skill_hotkeys["hydra"]:
                raise ValueError("You did not set a hotkey for hydra!")
            keyboard.send(self._skill_hotkeys["hydra"])
            self._hydra_time = time.time()
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(count / 3, count / 2)
            mouse.release(button="right")

    def _attack(self, abs_pos: tuple[int, int], atk_len: float, hydra_spray: float = 0, hydra_count: int = 6, fireball_spray: float = 10, frozen_orb_spray: float = 0, force_recast: bool = False):
        for atk in range(int(atk_len)):
            self._hydra(abs_pos, spray=hydra_spray, force_recast=force_recast, count=hydra_count)
            self._fb_orb(abs_pos, fireball_spray=fireball_spray, frozen_orb_spray=frozen_orb_spray, count=2, delay=(self._cast_duration, self._cast_duration + 0.2))

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float, hydra_spray: float = 0, fireball_spray: float = 10):
        pos_m = convert_abs_to_monitor(abs_move)
        for atk in range(int(atk_len)):
            self._hydra(pos_m, spray=hydra_spray)
            self._fb_orb(pos_m, fireball_spray=fireball_spray)
        self.pre_move()
        self.move(pos_m, force_move=True)

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.8, pindle_pos_abs[1] * 0.8]
        self._frozen_orb(cast_pos_abs)
        self._attack(cast_pos_abs, Config().char["atk_len_pindle"], fireball_spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        self._hydra_time = None
        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.8, eld_pos_abs[1] * 0.8]
        self._attack(cast_pos_abs, Config().char["atk_len_eldritch"], fireball_spray=75, frozen_orb_spray=100, hydra_spray=0)
        self._hydra(cast_pos_abs, count=3, force_recast=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        self._hydra_time = None
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.1, shenk_pos_abs[1] * 1.1]
        self._frozen_orb(cast_pos_abs)
        self._attack(cast_pos_abs, Config().char["atk_len_shenk"] * 0.5, fireball_spray=90, frozen_orb_spray=200, hydra_count=6)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_tp=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.01, shenk_pos_abs[1] * 1.01]
        self._attack(cast_pos_abs, Config().char["atk_len_shenk"] * 0.5, fireball_spray=90, frozen_orb_spray=200, force_recast=True)
        wait(self._cast_duration, self._cast_duration + 1)
        pos_m = convert_abs_to_monitor((150, 50))
        self.pre_move()
        self.move(pos_m, force_move=True)
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.01, shenk_pos_abs[1] * 1.01]
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        self._hydra_time = None
        return True
