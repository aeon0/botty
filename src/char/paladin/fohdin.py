import random
import keyboard
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from utils.custom_mouse import mouse
from char.paladin import Paladin
from logger import Logger
from config import Config
from utils.misc import wait
import time
from pather import Location


class FoHdin(Paladin):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up FoHdin")
        super().__init__(*args, **kwargs)
        self._pather.adapt_path((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), [220, 221, 222, 903, 904, 905, 906])

    def _cast_foh(self, cast_pos_abs: tuple[float, float], spray: int = 10, time_in_s: float = 1, aura: str = "conviction"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(Config().char["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["foh"]:
                keyboard.send(self._skill_hotkeys["foh"])
            wait(0.05, 0.1)
            start = time.time()
            while (time.time() - start) < time_in_s:
                x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
                y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
                pos_m = convert_abs_to_monitor((x, y))
                mouse.move(*pos_m, delay_factor=[0.3, 0.6])
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(Config().char["stand_still"], do_press=False)
            
    def _cast_holy_bolt(self, cast_pos_abs: tuple[float, float], spray: int = 10, time_in_s: float = 4, aura: str = "conviction"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(Config().char["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["holy_bolt"]:
                keyboard.send(self._skill_hotkeys["holy_bolt"])
            wait(0.05, 0.1)
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.3, 0.6])
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(Config().char["stand_still"], do_press=False)

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(Config().char["atk_len_pindle"])):
            self._cast_foh(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=self._do_pre_move)
        
        return True



    def kill_council(self) -> bool:
        # Attack towards stairs
        trav_attack_pos = self._pather.find_abs_node_pos(225, grab())
        Logger.info(f"trav_attack_pos: {trav_attack_pos}")
        if trav_attack_pos is None:
            trav_attack_pos = self._pather.find_abs_node_pos(906, grab())
        self._cast_foh(trav_attack_pos, spray=80, time_in_s=4)
        self._cast_holy_bolt(trav_attack_pos, spray=80, time_in_s=4)

        self._pather.traverse_nodes([225], self, timeout=2.5, force_tp=True)
        trav_attack_pos = self._pather.find_abs_node_pos(226, grab())
        self._cast_foh(trav_attack_pos, spray=80,time_in_s=4)
        self._cast_holy_bolt(trav_attack_pos, spray=80, time_in_s=4)

        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        trav_attack_pos = self._pather.find_abs_node_pos(228, grab())
        self._cast_foh(trav_attack_pos, spray=80,time_in_s=4)
        self._cast_holy_bolt(trav_attack_pos, spray=80, time_in_s=4)

        self._pather.traverse_nodes([300], self, timeout=2.5, force_tp=True)
        trav_attack_pos = self._pather.find_abs_node_pos(907, grab())
        self._cast_foh(trav_attack_pos, spray=80,time_in_s=4)
        self._cast_holy_bolt(trav_attack_pos, spray=80, time_in_s=4)
        
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        return True

        # Tele back and attack
        pos_m = convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_foh((-235, -230), spray=40)
        wait(1.0)
        pos_m = convert_abs_to_monitor((-285, -320))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Move to far left
        self._pather.offset_node(301, (-80, -50))
        self._pather.traverse_nodes([301], self, timeout=2.5, force_tp=True)
        self._pather.offset_node(301, (80, 50))
        # Attack to RIGHT
        self._cast_foh((100, 150), spray=40)
        wait(0.5)
        self._cast_foh((310, 260), spray=40)
        wait(1.0)
        # Move to bottom of stairs
        self.pre_move()
        for p in [(450, 100), (-190, 200)]:
            pos_m = convert_abs_to_monitor(p)
            self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([304], self, timeout=2.5, force_tp=True)
        # Attack to center of stairs
        self._cast_foh((-175, -200), spray=40)
        wait(0.5)
        self._cast_foh((-175, -270), spray=40)
        wait(1.0)
        # Move back inside
        # self._pather.traverse_nodes_fixed([(1110, 15)], self)
        self._pather.traverse_nodes([300], self, timeout=2.5, force_tp=False)
        # Attack to center
        self._cast_foh((-100, 0), spray=40)
        self._cast_foh((-175, 50), spray=40)
        wait(1.0)
        # Move back outside and attack
        pos_m = convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_foh((-50, -150), spray=40)
        wait(0.5)
        # Move back inside and attack
        pos_m = convert_abs_to_monitor((150, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence center
        self._cast_foh((-100, 35), spray=40)
        self._cast_foh((-150, 20), spray=40)
        wait(1.0)
        # Move inside
        pos_m = convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        self._cast_foh((-50, 50), spray=40)
        self._cast_foh((-30, 50), spray=40)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
        return True