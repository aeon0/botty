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


class Arcane:
    def __init__(
        self,
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
        self._chest = Chest(self._char, self._template_finder, 'arcane')

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        Logger.info("Run Arcane")
        if not self._char.can_teleport():
            raise ValueError("Arcane requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(2, 7)
        return Location.A2_ARC_START

    def _find_summoner(self, traverse_to_summoner: list[tuple[float, float]]) -> bool:
        # Check if we arrived at platform
        template_match_platform = self._template_finder.search_and_wait(["ARC_PLATFORM_1", "ARC_PLATFORM_2", "ARC_PLATFORM_3", "ARC_CENTER"], threshold=0.55, time_out=0.6, take_ss=False)
        if template_match_platform.valid:
            # Check if we found Summoner
            template_match_summoner = self._template_finder.search_and_wait(["ARC_ALTAR", "ARC_ALTAR2"], threshold=0.70, time_out=0.6)
            if template_match_summoner.valid:
                # Seems like we jumped right anot the platform
                if self._pather.traverse_nodes([461], self._char, time_out=2.2, force_tp=True):
                    return True
            return False
        # We might have arrived at summoner, move up stairs with static traverse
        self._pather.traverse_nodes_fixed(traverse_to_summoner, self._char)
        if self._pather.traverse_nodes([461], self._char, time_out=2.2, force_tp=True):
            return True
        return False

    def _return_to_wp(self, calib_node: int, path: str, traverse = list[tuple[float, float]]) -> bool:
        Logger.debug("Returning to wp")
        if not self._pather.traverse_nodes([calib_node], self._char, force_tp=True):
            Logger.debug("Could not find calibration node")
            return False
        if not self._pather.traverse_nodes_fixed(path, self._char):
            return False
        if not self._pather.traverse_nodes_fixed(traverse, self._char):
            return False
        if not self._template_finder.search_and_wait(["ARC_START"], threshold=0.70, time_out=3.5):
            Logger.debug("Could not find start template")
            return False
        return True

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        picked_up_items = False
        @dataclass
        class PathData:
            calib_node_start: int
            # custom calib static jump to have static pathes work for all layouts
            calib_jump_start: list[tuple[float, float]]
            static_path_forward: str
            jump_to_summoner: list[tuple[float, float]]
            calib_node_back: int
            static_path_backward: str
            # custom calib static jump to have static pathes work for all layouts
            calib_jump_back: list[tuple[float, float]]

        path_arr = [
            PathData(450, None, "arc_top_right", [(500, 40)], 452, "arc_bottom_left", [(20, 360)]),
            PathData(453, [(20, 20)], "arc_top_left", [(500, 40)], 454, "arc_bottom_right", [(1250,700)]),
            PathData(456, [(1250, 700)], "arc_bottom_right", [(500, 40)], 457, "arc_top_left", [(20, 20)]),
            PathData(459, [(20, 700)], "arc_bottom_left", [(500, 20), (700, 100)], None, None, None)
        ]

        picked_up_items = False
        for data in path_arr:
            if do_pre_buff:
                self._char.pre_buff()
            # calibrating at start and moving towards the end of the arm
            self._pather.traverse_nodes([data.calib_node_start], self._char, force_tp=True)
            if data.calib_jump_start is not None:
                self._pather.traverse_nodes_fixed(data.calib_jump_start, self._char)
            if not self._pather.traverse_nodes_fixed(data.static_path_forward, self._char):
                return False
            found = self._find_summoner(data.jump_to_summoner)
            # Kill the summoner or trash mob
            self._char.kill_summoner()
            if not found and self._config.char["open_chests"]:
                self._chest.open_up_chests()
            picked_up_items |= self._pickit.pick_up_items(self._char)
            if found:
                return (Location.A2_ARC_END, picked_up_items)
            elif data.static_path_backward is not None:
                # Move back to waypoint
                if not self._return_to_wp(data.calib_node_back, data.static_path_backward, data.calib_jump_back):
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
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)
    print(bot._arcane._return_to_wp(454, "arc_bottom_right", [(1250,700)]))
