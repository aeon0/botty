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

    def run(self, start_loc: Location, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # Go to Travincal via waypoint
        Logger.info("Run Trav")
        if not self._char.can_teleport():
            Logger.error("Trav is currently only supported for teleporting builds. Skipping trav")
            return True
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(3, 7)

        # Kill Council
        if not self._template_finder.search_and_wait(["TRAV_0", "TRAV_1"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        self._pather.traverse_nodes_fixed("trav_save_dist", self._char)
        self._char.kill_council()
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A3_TRAV_END, picked_up_items)
