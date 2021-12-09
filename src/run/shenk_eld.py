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


class ShenkEld:
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

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Eldritch")
        # Go to Frigid Highlands
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(5, 1)
        return Location.A5_ELDRITCH_START

    def battle(self, do_shenk: bool, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        # Eldritch
        if not self._template_finder.search_and_wait(["ELDRITCH_0", "ELDRITCH_START"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        if self._config.char["static_path_eldritch"]:
            self._pather.traverse_nodes_fixed("eldritch_save_dist", self._char)
        else:
            if not self._pather.traverse_nodes((Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAVE_DIST), self._char, force_move=True):
                return False
        self._char.kill_eldritch()
        loc = Location.A5_ELDRITCH_END
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char, "Eldritch")

        # Shenk
        if do_shenk:
            Logger.info("Run Shenk")
            self._curr_loc = Location.A5_SHENK_START
            # No force move, otherwise we might get stuck at stairs!
            if not self._pather.traverse_nodes((Location.A5_SHENK_START, Location.A5_SHENK_SAVE_DIST), self._char):
                return False
            self._char.kill_shenk()
            loc = Location.A5_SHENK_END
            wait(1.9, 2.4) # sometimes merc needs some more time to kill shenk...
            picked_up_items |= self._pickit.pick_up_items(self._char, "Shenk")

        return (loc, picked_up_items)
