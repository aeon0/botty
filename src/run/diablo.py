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


class Diablo:
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
        Logger.info("Run Diablo")
        if not self._char.can_teleport():
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2) # use Halls of Pain Waypoint (3rd in A4)
        return Location.A4_DIABLO_WP

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if do_pre_buff:
            self._char.pre_buff()
        found = False
        # we use the template of WP to orient ourselves & bring is in the best postion to start our tele journey
        self._pather.traverse_nodes([600], self._char)
        Logger.debug("Calibrating Postion to start my Tele Journey through River of Flame")
        #while not found:
        #    found = self._template_finder.search_and_wait(["DIABLO_CS_0", "DIABLO_CS_1", "DIABLO_CS_2", "DIABLO_CS_3", "DIABLO_CS_4"], threshold=0.8, time_out=0.1).valid
        #    self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        #Logger.debug("Arrived at Chaos Sanctuary Entrance")
        #Logger.debug("Kill these Demon Trash")
        #self._char.kill_cs_trash()
        #Logger.debug("Loot their bloody corpses")
        #picked_up_items = self._pickit.pick_up_items(self._char)
        #Logger.debug("Calibrating Position exactly at Door to Chaos Sanctuary Entrance")
        #self._pather.traverse_nodes([601], self._char)
        # we tele from Entrance upwards until we find our tempalte for Pentagram
        while not found:
            found = self._template_finder.search_and_wait(["DIABLO_PENT_0", "DIABLO_PENT_1", "DIABLO_PENT_2", "DIABLO_PENT_3"], threshold=0.8, time_out=0.1).valid
            self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        Logger.debug("Arrived at Pentagram")
        # we tele to pentagram
        self._pather.traverse_nodes([602], self._char)
        Logger.debug("Calibrating at Pentagram")
        # we tele to A
        # we check for layout of A (L or Y ) L first seal pops boss, upper does not. Y upper seal pops boss, lower does not
        # we pop the seals and kill vizier
        # we tele back to pentagram
        # we tele to B
        self._pather.traverse_nodes_fixed("diablo_pentagram_b_layout_check", self._char)
        # we check for layout of B (U or S) - just one seal. U = seal top left, S = seal top right
        Logger.debug("Checking Layout of Seal B")
        if self._template_finder.search_and_wait(["DIABLO_B_LAYOUTCHECK0", "DIABLO_B_LAYOUTCHECK1", ], threshold=0.8, time_out=0.1).valid:
            Logger.debug("Seal B Layout S found")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b_s_seal", self._char)
            Logger.debug("Gonna pop De Seis Seal (B-S) now")
            while not found:
                found = self._template_finder.search_and_wait(["DIABLO_SEAL_B_U_DESEIS_ACTIVE"], threshold=0.8, time_out=0.1).valid
            if not self._char.select_by_template(["DIABLO_SEAL_B_S_DESEIS"], threshold=0.63, time_out=4):
                pos_m = self._screen.convert_abs_to_monitor((0, 0))
                self.mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                return False
            self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
            Logger.debug("Kill these Demon Trash")
            self._char.kill_cs_trash()
            Logger.debug("Loot their bloody corpses")
            picked_up_items = self._pickit.pick_up_items(self._char)
            Logger.debug("Calibrating at Seal B Layout S")
            self._pather.traverse_nodes([630], self._char)
        else:
            Logger.debug("Seal B Layout U found")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b_u_seal", self._char)
            Logger.debug("Kill these Demon Trash")
            self._char.kill_cs_trash()
            Logger.debug("Loot their bloody corpses")
            picked_up_items = self._pickit.pick_up_items(self._char)
            wait(3)
            Logger.debug("Gonna pop De Seis Seal (B-U) now")
            if not self._char.select_by_template(["DIABLO_SEAL_B_U_DESEIS"], threshold=0.63, time_out=4): #we migt have to add a failsafe check here: if the active template is found.
                return False
            wait(2)
            Logger.debug("Kill these Demon Trash again")
            self._char.kill_cs_trash()
            Logger.debug("Loot their bloody corpses")
            picked_up_items = self._pickit.pick_up_items(self._char)
            Logger.debug("Calibrating at Seal B Layout U")
            self._pather.traverse_nodes([640], self._char)
            Logger.debug("I am now calibrated at Seal B Layout U")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b_u_safe_dist", self._char)
            Logger.debug("I am now on my way to save_dist at Seal B Layout U to kill De Seis")
            Logger.debug("Kill these Demon Trash")
            self._char.kill_deseis()
            Logger.debug("Loot their bloody corpses")
            picked_up_items = self._pickit.pick_up_items(self._char)
            Logger.debug("lets go back to Pentagram")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b_u_safe_dist", self._char)
            while not found:
                found = self._template_finder.search_and_wait(["DIABLO_PENT_0", "DIABLO_PENT_1", "DIABLO_PENT_2", "DIABLO_PENT_3"], threshold=0.8, time_out=0.1).valid
                self._pather.traverse_nodes_fixed("diablo_b_end_pentagram", self._char)
            Logger.debug("Arrived at Pentagram")           
            # we tele back to pentagram

        # we tele to C
        # we check for layout of C
        # we pop the seals and kill infector (F or G) F first seal pops boss, upper does not. G lower seal pops boss, upper does not (can moat trick infector here)
        # we tele back to pentagram
        
        # we kill diablo

        #self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        # Attack & Pick items
        self._char.kill_diablo() #should be relative to current location ( a = vizier, b = deseis, c = infector, d = diablo)
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A4_DIABLO_END, picked_up_items)
