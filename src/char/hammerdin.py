import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, is_in_roi
import time
from pather import Pather, Location
import math
import threading
import numpy as np
import random

from api.mapassist import MapAssistApi
from pather_v2 import PatherV2


class Hammerdin(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather, pather_v2: PatherV2, api: MapAssistApi):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pather = pather
        self._api = api
        self._pather_v2 = pather_v2
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
            time.sleep(0.01)
            keyboard.send(self._char_config["stand_still"], do_release=False)
            time.sleep(0.01)
            if self._skill_hotkeys["blessed_hammer"]:
                keyboard.send(self._skill_hotkeys["blessed_hammer"])
                time.sleep(0.01)
            start = time.time()
            moved_center = False
            while (time.time() - start) < time_in_s:
                mouse.press(button="left")
                if not moved_center:
                    m = self._screen.convert_abs_to_monitor((0, 0))
                    mouse.move(*m, randomize=35, delay_factor=[0.1, 0.2])
                    moved_center = True
                else:
                    wait(0.1, 0.2)
                mouse.release(button="left")
                wait(0.01, 0.02)
            wait(0.02, 0.04)
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def _cast_holy_bolt(self, time_in_s: float, abs_screen_pos: tuple[float, float]):
        if self._skill_hotkeys["holy_bolt"]:
            keyboard.send(self._skill_hotkeys["concentration"])
            keyboard.send(self._skill_hotkeys["holy_bolt"])
            wait(0.05)
            m = self._screen.convert_abs_to_monitor(abs_screen_pos)
            mouse.move(*m, delay_factor=[0.2, 0.4])
            keyboard.send(self._char_config["stand_still"], do_release=False)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
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

    # Memory reading
    # ===================================
    def _kill_mobs(self, names: list[str]) -> bool:
        start = time.time()
        success = False
        while time.time() - start < 80:
            data = self._api.get_data()
            is_alive = False
            if data is not None:
                for m in data["monsters"]:
                    area_pos = m["position"] - data["area_origin"]
                    proceed = any(m["name"].startswith(startstr) for startstr in names)
                    if proceed:
                        dist = math.dist(area_pos, data["player_pos_area"])
                        self._pather_v2.traverse(area_pos, self, randomize=10)
                        if dist < 8:
                            self._cast_hammers(1.0)
                        is_alive = True
                        success = True
            if not is_alive:
                return success
        return False

    def baal_idle(self, monster_filter: list[str], start_time: float) -> bool:
        stop_hammers = False
        def pre_cast_hammers():
            while not stop_hammers:
                self._cast_hammers(1.0)
        hammer_thread = threading.Thread(target=pre_cast_hammers)
        hammer_thread.daemon = True

        throne_area = [70, 0, 50, 85]
        if not self._pather_v2.traverse((93, 26), self):
            return False
        aura = "redemption"
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
        while 1:
            data = self._api.get_data()
            if data is not None:
                 for m in data["monsters"]:
                    area_pos = m["position"] - data["area_origin"]
                    proceed = True
                    if monster_filter is not None:
                        proceed = any(m["name"].startswith(startstr) for startstr in monster_filter)
                    if is_in_roi(throne_area, area_pos) and proceed:
                        Logger.info("Found wave, attack")
                        stop_hammers = True
                        if hammer_thread.is_alive():
                            hammer_thread.join()
                        return
            elpased = time.time() - start_time
            if elpased > 6.0:
                if not hammer_thread.is_alive():
                    hammer_thread.start()
            time.sleep(0.1)

    def clear_throne(self, full = False, monster_filter = None) -> bool:
        if full:
            throne_area = [70, 0, 50, 95]
        else:
            throne_area = [70, 0, 50, 65]
        aura_after_battle = "redemption"
        success = False
        start = time.time()
        prev_position = None
        prev_pos_counter = time.time()
        while time.time() - start < 70:
            data = self._api.get_data()
            found_a_monster = False
            if data is not None:
                for m in data["monsters"]:
                    area_pos = m["position"] - data["area_origin"]
                    proceed = True
                    if monster_filter is not None:
                        proceed = any(m["name"].startswith(startstr) for startstr in monster_filter)
                    if is_in_roi(throne_area, area_pos) and proceed:
                        if m["name"].startswith("BaalSubjectMummy"):
                            self._cast_holy_bolt(1.2, m["abs_screen_position"])
                            aura_after_battle = "cleansing"
                        else:
                            dist = math.dist(area_pos, data["player_pos_area"])
                            self._pather_v2.traverse(area_pos, self, randomize=12)
                            if dist < 8:
                                self._cast_hammers(1.0)
                        found_a_monster = True
                        break
                if prev_position is None or not np.array_equal(prev_position, data["player_pos_area"]):
                    prev_pos_counter = time.time()
                if time.time() - prev_pos_counter > 3.8:
                    Logger.debug("Reposition for next attack")
                    m_pos = self._screen.convert_abs_to_monitor((random.randint(-100, 100), random.randint(-100, 100)))
                    self.pre_move()
                    self.move(m_pos)
                prev_position = data["player_pos_area"]
            if not found_a_monster:
                success = True
                break
        if aura_after_battle in self._skill_hotkeys and self._skill_hotkeys[aura_after_battle]:
            keyboard.send(self._skill_hotkeys[aura_after_battle])
        return success

    def kill_baal(self) -> bool:
        return self._kill_mobs(["BaalCrab"])

    def kill_meph(self) -> bool:
        return self._kill_mobs(["Mephisto"])

    def kill_andy(self) -> bool:
        return self._kill_mobs(["Andariel"])


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    api = MapAssistApi()
    pather_v2 = PatherV2(screen, api)
    char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather, pather_v2, api)
    pather_v2.traverse((94, 28), char)
    char._cast_hammers(2.0)
