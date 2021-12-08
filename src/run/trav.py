from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui_manager import UiManager
from utils.misc import wait


class Trav:
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
        # Go to Travincal via waypoint
        Logger.info("Run Trav")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(3, 7)
        return Location.A3_TRAV_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # Kill Council
        if not self._template_finder.search_and_wait(["TRAV_0", "TRAV_1", "TRAV_20"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        self._pather.traverse_nodes((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), self._char, force_move=True)
        self._char.kill_council()
        picked_up_items = self._pickit.pick_up_items(self._char)
        wait(0.2, 0.3)
        success = self._pather.traverse_nodes([228, 229], self._char, force_move=True, time_out=2.5)
        if success:
            picked_up_items |= self._pickit.pick_up_items(self._char)
        return (Location.A3_TRAV_CENTER_STAIRS, picked_up_items)
