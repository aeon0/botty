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
        if self._ui_manager.use_wp(5, 1):
            return Location.A5_ELDRITCH_START
        return False

    def battle(self, do_shenk: bool, do_pre_buff: bool, game_stats) -> Union[bool, tuple[Location, bool]]:
        # Eldritch
        game_stats.update_location("Eld" if self._config.general['discord_status_condensed'] else "Eldritch")
        if not self._template_finder.search_and_wait(["ELDRITCH_0", "ELDRITCH_START"], threshold=0.65, time_out=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
        if self._char.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("eldritch_safe_dist", self._char)
        else:
            if not self._pather.traverse_nodes((Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAFE_DIST), self._char, force_move=True):
                return False
        self._char.kill_eldritch()
        loc = Location.A5_ELDRITCH_END
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)

        # Shenk
        if do_shenk:
            Logger.info("Run Shenk")
            game_stats.update_location("Shk" if self._config.general['discord_status_condensed'] else "Shenk")
            self._curr_loc = Location.A5_SHENK_START
            # No force move, otherwise we might get stuck at stairs!
            if not self._pather.traverse_nodes((Location.A5_SHENK_START, Location.A5_SHENK_SAFE_DIST), self._char):
                return False
            self._char.kill_shenk()
            loc = Location.A5_SHENK_END
            wait(1.9, 2.4) # sometimes merc needs some more time to kill shenk...
            picked_up_items |= self._pickit.pick_up_items(self._char)

        return (loc, picked_up_items)
