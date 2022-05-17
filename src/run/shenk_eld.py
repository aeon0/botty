from char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from utils.misc import wait
from ui import waypoint

class ShenkEld:
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

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Eldritch")
        # Go to Frigid Highlands
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if waypoint.use_wp("Frigid Highlands"):
            return Location.A5_ELDRITCH_START
        return False

    def battle(self, do_shenk: bool, do_pre_buff: bool, game_stats) -> Union[bool, tuple[Location, bool]]:
        # Eldritch
        game_stats.update_location("Eld")
        if not TemplateFinder().search_and_wait(["ELDRITCH_0", "ELDRITCH_0_V2", "ELDRITCH_0_V3", "ELDRITCH_START", "ELDRITCH_START_V2"], threshold=0.65, timeout=20).valid:
            return False
        if do_pre_buff:
            self._char.pre_buff()
            self._char.pre_buff_bone_armor()
            #            (Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAFE_DIST): [120, 121, 122],
            #(Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END): [123],
            if not self._pather.traverse_nodes((Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAFE_DIST), self._char, force_move=True):
                return False
            #if not self._pather.traverse_nodes([120, 121, 122], self._char): return False            
            self._char.kill_eld_one()
            if not self._pather.traverse_nodes([121], self._char): return False            
            self._char.kill_eld_two()
        loc = Location.A5_ELDRITCH_END
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)

        # Shenk
        if do_shenk:
            Logger.info("Run Shenk")
            game_stats.update_location("Shk")
            self._curr_loc = Location.A5_SHENK_START
            # No force move, otherwise we might get stuck at stairs!
            #if not self._pather.traverse_nodes((Location.A5_SHENK_START, Location.A5_SHENK_SAFE_DIST), self._char):
            if not self._pather.traverse_nodes([121, 120, 143, 144, 145], self._char): return False
            #if not self._pather.traverse_nodes([142], self._char): return False
            #if not self._pather.traverse_nodes([143], self._char): return False
            #if not self._pather.traverse_nodes([144], self._char): return False
            self._char.kill_shenk_stair_one()
            if not self._pather.traverse_nodes([145], self._char): return False
            if not self._pather.traverse_nodes([146], self._char): return False
            self._char.kill_shenk_stair_two()
            picked_up_items |= self._pickit.pick_up_items(self._char)
            if not self._pather.traverse_nodes([146], self._char): return False
            if not self._pather.traverse_nodes([147], self._char): return False
            self._char.kill_shenk_stair_three()
            picked_up_items |= self._pickit.pick_up_items(self._char)
            if not self._pather.traverse_nodes([147], self._char): return False
            if not self._pather.traverse_nodes([148], self._char): return False
            self._char.kill_shenk_stair_four()
            if not self._pather.traverse_nodes([148], self._char): return False
            if not self._pather.traverse_nodes([149], self._char): return False
            self._char.kill_shenk()
            if not self._pather.traverse_nodes([149], self._char): return False
            self._char.kill_shenk_cleanup()
            loc = Location.A5_SHENK_END
            wait(1.9, 2.4) # sometimes merc needs some more time to kill shenk...
            picked_up_items |= self._pickit.pick_up_items(self._char)

        return (loc, picked_up_items)
