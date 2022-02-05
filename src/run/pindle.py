from char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait


class Pindle:
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

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        # Go through Red Portal in A5
        Logger.info("Run Pindle")
        loc = self._town_manager.go_to_act(5, start_loc)
        if not loc:
            return False
        if not self._pather.traverse_nodes((loc, Location.A5_NIHLATHAK_PORTAL), self._char):
            return False
        wait(0.5, 0.6)
        found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
        if not self._char.select_by_template(["A5_RED_PORTAL", "A5_RED_PORTAL_TEXT"], found_loading_screen_func, telekinesis=False):
            return False
        return Location.A5_PINDLE_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # Kill Pindle
        if not self._template_finder.search_and_wait(["PINDLE_0", "PINDLE_1"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        # move to pindle
        if self._char.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_safe_dist", self._char)
        else:
            if not self._pather.traverse_nodes((Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST), self._char):
                return False
        self._char.kill_pindle()
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A5_PINDLE_END, picked_up_items)
