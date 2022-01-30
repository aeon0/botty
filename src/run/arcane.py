from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from dataclasses import dataclass
from chest import Chest
from screen import Screen


class Arcane:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._chest = Chest(screen, self._char, self._template_finder, 'arcane')
        self.used_tps = 0

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        Logger.info("Run Arcane")
        if not self._char.can_teleport():
            raise ValueError("Arcane requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(2, 7):
            return Location.A2_ARC_START
        return False

    def _find_summoner(self, traverse_to_summoner: list[tuple[float, float]]) -> bool:
        # Check if we arrived at platform
        templates_platform = ["ARC_PLATFORM_1", "ARC_PLATFORM_2", "ARC_PLATFORM_3", "ARC_CENTER"]
        tempaltes_summoner = ["ARC_ALTAR", "ARC_ALTAR3", "ARC_END_STAIRS", "ARC_END_STAIRS_2"]
        match_platform = self._template_finder.search_and_wait(templates_platform, threshold=0.55, time_out=0.5, use_grayscale=True, take_ss=False)
        match_summoner = self._template_finder.search_and_wait(tempaltes_summoner, threshold=0.79, time_out=0.5, use_grayscale=True, take_ss=False)
        if not match_platform.valid and not match_summoner.valid:
            # We might have arrived at summoner, move up stairs with static traverse
            self._pather.traverse_nodes_fixed(traverse_to_summoner, self._char)
            # try to match summoner again
            match_summoner = self._template_finder.search_and_wait(tempaltes_summoner, threshold=0.79, time_out=1.0, use_grayscale=True, take_ss=False)
        if match_summoner.valid:
            if self._pather.traverse_nodes([461], self._char, time_out=2.2, force_tp=True):
                return True
        else:
            # Traverse to center of platform
            self._pather.traverse_nodes([462], self._char, time_out=1.3, force_tp=True)
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        picked_up_items = False
        @dataclass
        class PathData:
            calib_node_start: int
            static_path_forward: str
            jump_to_summoner: list[tuple[float, float]]

        path_arr = [
            PathData(450, "arc_top_right", [(500, 40)]),
            PathData(453, "arc_top_left", [(500, 40)]),
            PathData(456, "arc_bottom_right", [(500, 40)]),
            PathData(459, "arc_bottom_left", [(500, 20), (700, 100)])
        ]

        picked_up_items = False
        self.used_tps = 0

        for i, data in enumerate(path_arr):
            if do_pre_buff:
                self._char.pre_buff()

            # calibrating at start and moving towards the end of the arm
            self._pather.traverse_nodes([data.calib_node_start], self._char, force_tp=True)
            if not self._pather.traverse_nodes_fixed(data.static_path_forward, self._char):
                return False
            found = self._find_summoner(data.jump_to_summoner)
            # Kill the summoner or trash mob
            self._char.kill_summoner()
            if self._config.char["open_chests"]:
                self._chest.open_up_chests()
            picked_up_items |= self._pickit.pick_up_items(self._char)
            if found:
                return (Location.A2_ARC_END, picked_up_items)
            elif i < len(path_arr) - 1:
                # Open TP and return back to town, walk to wp and start over
                if not self._char.tp_town():
                    Logger.warning("TP to town failed, cancel run")
                    self.used_tps += 20
                    return False
                self.used_tps += 1
                if not self._town_manager.wait_for_tp(Location.A2_TP):
                    return False
                if not self.approach(Location.A2_FARA_STASH):
                    return False
        return False


if __name__ == "__main__":
    from screen import Screen
    import keyboard
    from game_stats import GameStats
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    from bot import Bot
    config = Config()
    screen = Screen()
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)
    bot._arcane._find_summoner([(500, 40)])
