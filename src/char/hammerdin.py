import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait
import time
from pather import Pather, Location


class Hammerdin(IChar):
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager)
        self._pather = pather
        self._do_pre_move = True
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False
        else:
            # we want to change positions of shenk and eld a bit to be more center for teleport
            self._pather.offset_node(149, (70, 10))

    def _cast_hammers(self, time_in_s: float, aura: str = "concentration"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(self._char_config["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["blessed_hammer"]:
                keyboard.send(self._skill_hotkeys["blessed_hammer"])
            wait(0.05, 0.1)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def pre_buff(self):
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.06)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(["VIGOR"])
        can_teleport = self._skill_hotkeys["teleport"] and self._ui_manager.is_right_skill_active()
        if  should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.can_teleport():
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        self._cast_hammers(self._char_config["atk_len_pindle"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_eldritch(self) -> bool:
        if self.can_teleport():
            # Custom eld position for teleport that brings us closer to eld
            self._pather.traverse_nodes_fixed([(675, 30)], self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_shenk(self):
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_shenk"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_council(self) -> bool:
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"]
        # Go inside and hammer a bit
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True)
        self._cast_hammers(atk_len)
        # Move a bit back and another round
        self._move_and_attack((40, 20), atk_len)
        # Here we have two different attack sequences depending if tele is available or not
        if self.can_teleport():
            # Back to center stairs and more hammers
            self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
            self._cast_hammers(atk_len)
            # move a bit to the top
            self._move_and_attack((65, -30), atk_len)
        else:
            # Stay inside and cast hammers again moving forward
            self._move_and_attack((40, 10), atk_len)
            self._move_and_attack((-40, -20), atk_len)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Move close to nilathak
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_nihlatak"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_nihlatak"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_nihlatak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        return True

    # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo
    def kill_cs_trash(self) -> bool:
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_cs_trashmobs"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        #self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
        return True
        
    def kill_cs_trash_pentagram(self) -> bool:
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_cs_trashmobs"] * 0.2)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.2)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.1)
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        #self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
        return True
    
    def kill_vizier(self, nodes1: list[int], nodes2: list[int]) -> bool:
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes1, self)
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes2, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_vizier"])
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        return True

    def kill_deseis(self, nodes1: list[int], nodes2: list[int], nodes3: list[int]) -> bool:
        """ WIZ VERSION - NOT STABLE FOR CTHU
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._move_and_attack((30, 30), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((-60, -0), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes1, self)
        self._move_and_attack((0, -60), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((60, 0), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes2, self)
        self._move_and_attack((-30, -30), self._char_config["atk_len_diablo_deseis"] * 0.5)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes3, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption") 
        return True
        """
        #CTHU VERSION
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes1, self)
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes2, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"] * 0.5)
        self._cast_hammers(1, "redemption")
        self._pather.traverse_nodes(nodes3, self)
        self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption") 
        return True

    def kill_infector(self) -> bool:
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_diablo_infector"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption") 
        return True

    def kill_diablo(self) -> bool:
        # Move close to diablo
        #self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_diablo"] * 0.5)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((60, 30), self._char_config["atk_len_diablo"])
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-60, -30), self._char_config["atk_len_diablo"])
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        return True

    def kill_summoner(self) -> bool:
        # move mouse to below altar
        pos_m = self._screen.convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._cast_hammers(self._char_config["atk_len_arc"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        # Move a bit back and another round
        self._move_and_attack((0, 80), self._char_config["atk_len_arc"] * 0.5)
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen()
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather)
