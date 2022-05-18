from char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
import template_finder
from town.town_manager import TownManager
from utils.misc import wait

from ui import waypoint

class Trav:
    def __init__(
        self,
        pather: Pather,
        town_manager: TownManager,
        char: IChar,
        pickit: PickIt
    ):
        self._pather = pather
        self._town_manager = town_manager
        self._char = char
        self._pickit = pickit

    def approach(self, start_loc: Location) -> Union[bool, Location]:
        # Go to Travincal via waypoint
        Logger.info("Run Trav")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if waypoint.use_wp("Travincal"):
            return Location.A3_TRAV_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # Kill Council
        if not template_finder.search_and_wait(["TRAV_0", "TRAV_1", "TRAV_20"], threshold=0.65, timeout=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        if self._char.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("trav_safe_dist", self._char)
        else:
            if not self._pather.traverse_nodes((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), self._char, force_move=True):
                return False
        self._char.kill_council()
        picked_up_items = self._pickit.pick_up_items(self._char)
        wait(0.2, 0.3)
        # If we can teleport we want to move back inside and also check loot there
        if self._char.capabilities.can_teleport_natively or self._char.capabilities.can_teleport_with_charges:
            if not self._pather.traverse_nodes([229], self._char, timeout=2.5, use_tp_charge=True):
                self._pather.traverse_nodes([228, 229], self._char, timeout=2.5, use_tp_charge=True)
            picked_up_items |= self._pickit.pick_up_items(self._char)
        # Make sure we go back to the center to not hide the tp
        self._pather.traverse_nodes([230], self._char, timeout=2.5)
        return (Location.A3_TRAV_CENTER_STAIRS, picked_up_items)
