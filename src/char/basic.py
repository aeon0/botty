import keyboard
from ui import skills
from utils.custom_mouse import mouse
from char import IChar,CharacterCapabilities
import template_finder
from pather import Pather
from logger import Logger
from screen import convert_abs_to_monitor
from config import Config
from utils.misc import wait, cut_roi
import time
from pather import Pather, Location


class Basic(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        Logger.info("Setting up Basic Character")
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._do_pre_move = True

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        # offset shenk final position further to the right and bottom
        if capabilities.can_teleport_natively:
            self._pather.offset_node(149, [120, 70])

    def _cast_attack_pattern(self, time_in_s: float):
        keyboard.send(Config().char["stand_still"], do_release=False)
        wait(0.05, 0.1)
        keyboard.send(self._skill_hotkeys["left_attack"])
        wait(0.05, 0.1)
        keyboard.send(self._skill_hotkeys["right_attack"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            if skills.is_right_skill_active():
                wait(0.05, 0.1)
                mouse.click(button="right")
            else:
                wait(0.05, 0.1)
                mouse.click(button="left")
        wait(0.01, 0.05)
        keyboard.send(Config().char["stand_still"], do_press=False)

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

    def pre_move(self):
        # select teleport if available
        super().pre_move()

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_attack_pattern(atk_len)


#this is where we kill bosses

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
            #  keyboard.send(self._skill_hotkeys["concentration"])
            #  wait(0.05, 0.15)
                self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=self._do_pre_move)
        self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=0.1)
        self._cast_attack_pattern(Config().char["atk_len_pindle"])
        wait(0.1, 0.15)
        return True

    def kill_eldritch(self) -> bool:
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            if not self._do_pre_move:
            #  keyboard.send(self._skill_hotkeys["concentration"])
            #  wait(0.05, 0.15)
                self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_attack_pattern(Config().char["atk_len_eldritch"])
        return True

    def kill_shenk(self):
        # if not self._do_pre_move:
        #     keyboard.send(self._skill_hotkeys["concentration"])
        #     wait(0.05, 0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_attack_pattern(Config().char["atk_len_shenk"])
        wait(0.1, 0.15)
        return True

    def kill_council(self) -> bool:
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = Config().char["atk_len_trav"]
        # Go inside and war cry a bit
        self._pather.traverse_nodes([228, 229], self, timeout=2.5, force_tp=True)
        self._cast_attack_pattern(atk_len)
        # Move a bit back and another round
        self._move_and_attack((40, 20), atk_len)
        # Here we have two different attack sequences depending if tele is available or not
        if self.capabilities.can_teleport_natively:
            # Back to center stairs and more war cry
            self._pather.traverse_nodes([226], self, timeout=2.5, force_tp=True)
            self._cast_attack_pattern(atk_len)
            # move a bit to the top
            self._move_and_attack((65, -30), atk_len)
        else:
            # Stay inside and cast war cry again moving forward
            self._move_and_attack((40, 10), atk_len)
            self._move_and_attack((-40, -20), atk_len)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=False)
        # move mouse to center (leftover from hammerdin)
        pos_m = convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_attack_pattern(Config().char["atk_len_nihlathak"] * 0.4)
        self._cast_attack_pattern(0.8)
        self._move_and_attack((30, 15), Config().char["atk_len_nihlathak"] * 0.3)
        self._cast_attack_pattern(0.8)
        self._move_and_attack((-30, -15), Config().char["atk_len_nihlathak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_attack_pattern(1.2)
        return True

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    pather = Pather()
    char = Basic(Config().basic, Config().char, pather)
