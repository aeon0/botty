import keyboard
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, cut_roi
import time
from pather import Pather, Location


class Barbarian(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Barbarian")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager)
        self._pather = pather
        self._do_pre_move = True
        # offset shenk final position further to the right and bottom

    def _cast_war_cry(self, time_in_s: float):
        #  keyboard.send(self._skill_hotkeys["concentration"])
        #  wait(0.05, 0.1)
        cry_frequency = min(0.2, self._skill_hotkeys["cry_frequency"])
        keyboard.send(self._char_config["stand_still"], do_release=False)
        wait(0.05, 0.1)
        if self._skill_hotkeys["war_cry"]:
            keyboard.send(self._skill_hotkeys["war_cry"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.06, 0.08)
            mouse.click(button="right")
            wait(cry_frequency, cry_frequency + 0.2)
            mouse.click(button="right")
        wait(0.01, 0.05)
        keyboard.send(self._char_config["stand_still"], do_press=False)
    
    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        if capabilities.can_teleport_natively:
            self._pather.offset_node(149, [120, 70])

    def _do_hork(self, hork_time: int):
        wait(0.5)
        if self._skill_hotkeys["find_item"]:
            keyboard.send(self._skill_hotkeys["find_item"])
            wait(0.5, 0.15)
        pos_m = self._screen.convert_abs_to_monitor((0, -20))
        mouse.move(*pos_m)
        wait(0.5, 0.15)
        mouse.press(button="right")
        wait(hork_time)
        mouse.release(button="right")
        wait(1)

    def pre_buff(self):
        keyboard.send(self._char_config["battle_command"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._char_config["battle_orders"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)
        keyboard.send(self._skill_hotkeys["shout"])
        wait(0.08, 0.19)
        mouse.click(button="right")
        wait(self._cast_duration + 0.08, self._cast_duration + 0.1)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use leap if set
        should_cast_leap = self._skill_hotkeys["leap"] and not self._ui_manager.is_left_skill_selected(["LEAP"])
        can_teleport = IChar.capabilities.can_teleport_natively and self._ui_manager.is_right_skill_active()
        if  should_cast_leap and not can_teleport:
            keyboard.send(self._skill_hotkeys["leap"])
            wait(0.15, 0.25)
            
    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_war_cry(atk_len)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
            #  keyboard.send(self._skill_hotkeys["concentration"])
            #  wait(0.05, 0.15)
                self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=0.1)
        self._cast_war_cry(self._char_config["atk_len_pindle"])
        wait(0.1, 0.15)
        self._do_hork(4)
        return True

    def kill_eldritch(self) -> bool:
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_war_cry(self._char_config["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._do_hork(4)
        return True

    def kill_shenk(self):
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_war_cry(self._char_config["atk_len_shenk"])
        wait(0.1, 0.15)
        self._do_hork(7)
        return True

    def kill_council(self) -> bool:
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"]
        # Go inside and war cry a bit
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True)
        self._cast_war_cry(atk_len)
        # Move a bit back and another round
        self._move_and_attack((40, 20), atk_len)
        # Here we have two different attack sequences depending if tele is available or not
        if self.capabilities.can_teleport_natively:
            # Back to center stairs and more war cry
            self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
            self._cast_war_cry(atk_len)
            # move a bit to the top
            self._move_and_attack((65, -30), atk_len)
        else:
            # Stay inside and cast war cry again moving forward
            self._move_and_attack((40, 10), atk_len)
            self._move_and_attack((-40, -20), atk_len)
        self._do_hork(5)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center (leftover from hammerdin)
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_war_cry(self._char_config["atk_len_nihlathak"] * 0.4)
        self._cast_war_cry(0.8)
        self._move_and_attack((30, 15), self._char_config["atk_len_nihlathak"] * 0.3)
        self._cast_war_cry(0.8)
        self._move_and_attack((-30, -15), self._char_config["atk_len_nihlathak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_war_cry(1.2)
        self._do_hork(5)
        return True

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui.ui_manager import UiManager
    config = Config()
    screen = Screen()
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Barbarian(config.barbarian, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
