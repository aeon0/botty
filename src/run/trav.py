from char import IChar
from logger import Logger
from pather import Location, Pather
from item.pickit import PickIt
import template_finder
from town.town_manager import TownManager
from utils.misc import wait
from config import Config
from ui import waypoint
from screen import grab #for layoutcheck A1 WP
from health_manager import get_panel_check_paused, set_panel_check_paused


class Trav:

    name = "run_trav"

    def __init__(
        self,
        pather: Pather,
        town_manager: TownManager,
        char: IChar,
        pickit: PickIt,
        runs: list[str]
    ):
        self._pather = pather
        self._town_manager = town_manager
        self._char = char
        self._pickit = pickit
        self._runs = runs

    def approach(self, start_loc: Location) -> bool | Location:
        # Go to Travincal via waypoint
        Logger.info("Run Trav")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if waypoint.use_wp("Travincal"):
            return Location.A3_TRAV_START
        return False

    def battle(self, do_pre_buff: bool) -> bool | tuple[Location, bool]:
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
            if not self._pather.traverse_nodes([229], self._char, timeout=2.5, use_tp_charge=self._char.capabilities.can_teleport_natively):
                self._pather.traverse_nodes([228, 229], self._char, timeout=2.5, use_tp_charge=True)
            picked_up_items |= self._pickit.pick_up_items(self._char)
        
        if self.name != self._runs[-1] or not Config().char["end_run_in_act"] == 0:# If travincal run is not the last run OR we set a preferred act to end in
            self._pather.traverse_nodes([230], self._char, timeout=2.5)# Make sure we go back to the center to not hide the tp
            
            if Config().char["end_run_in_act"] == 0:
                return (Location.A3_TRAV_CENTER_STAIRS, picked_up_items) #ending run in the current town
            
            else:
                Logger.debug("Going to A" + str(Config().char["end_run_in_act"]) + " town to shorten run duration.")
                self._char.tp_town()
                wait(0.4)
                curr_loc = Location.A3_STASH_WP #it would make sense to directly walk to WP, instead of first walking to stash - this will save another second (screen coordinates: x 950, y 100)
                set_panel_check_paused(True)
                if not self._town_manager.open_wp(curr_loc):
                    return False
                wait(0.4)

                if Config().char["end_run_in_act"] == 1:
                    if waypoint.use_wp("Rogue Encampment"):
                        set_panel_check_paused(False)
                        if not template_finder.search("A1_WP", grab()).valid:
                            curr_loc = Location.A1_WP_SOUTH
                        else:
                            curr_loc = Location.A1_WP_NORTH
                        return (curr_loc, picked_up_items)

                elif Config().char["end_run_in_act"] ==2:
                    if waypoint.use_wp("Lut Gholein"):
                        set_panel_check_paused(False)
                        return (Location.A2_WP, picked_up_items)

                elif Config().char["end_run_in_act"] ==3:
                    #if waypoint.use_wp("Kurast Docks"): # No need, we are already in A3!
                    #    set_panel_check_paused(False)
                    return (Location.A3_STASH_WP, picked_up_items)

                elif Config().char["end_run_in_act"] ==4:
                    if waypoint.use_wp("The Pandemonium Fortress"):
                        set_panel_check_paused(False)
                        return (Location.A4_WP, picked_up_items)

                elif Config().char["end_run_in_act"] ==5:
                    if waypoint.use_wp("Harrogath"):
                        set_panel_check_paused(False)
                        return (Location.A5_WP, picked_up_items)
        
        else:
            return (Location.A3_TRAV_CENTER_STAIRS, picked_up_items)
