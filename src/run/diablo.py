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
        """ RIVER OF FLAME PART """
        found = False
        self._pather.traverse_nodes([600], self._char) # we use the template of WP to orient ourselves & bring is in the best postion to start our tele journey
        while not found:
            found = self._template_finder.search_and_wait(["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"], threshold=0.8, time_out=0.1).valid
            self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char) # THIS THING TYPICALLY OVERSHOOTS BY ONE TELEPORT.
        self._pather.traverse_nodes([601], self._char) #Calibrating Position exactly at Door to Chaos Sanctuary Entrance HERE, WE HAVE AN ISSUE OF THE STEP BEFORE WAS OVERSHOOTING. WE MIGHT NEED MORE TEMPLATES DEEPER INTO THE CS ENTRANCE
        Logger.debug("I calibrated at CS entrance")
        # CHAOS SANTUARY PART 
        found = False
        while not found:
            found = self._template_finder.search_and_wait(["DIABLO_PENTX_0", "DIABLO_PENTX_1", "DIABLO_PENTX_2", "DIABLO_PENTX_3", "DIABLO_PENTX_4"], threshold=0.8, time_out=0.1).valid # searching for pentagram tempaltes...
            self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char) # we tele top right towards the pentagram
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        Logger.debug("I calibrated at Pentagram")
        # SEAL (A) VIZIER PART
        # we tele to A
        # we check for layout of A (L=1 or Y=2) L first seal pops boss, upper does not. Y upper seal pops boss, lower does not
        # we pop the seals and kill vizier
        # we tele back to pentagram
        # SEAL (B) DE SEIS PART 
        self._pather.traverse_nodes_fixed("diablo_pentagram_b_layout_check", self._char) # we tele to B
        Logger.debug("Checking Layout")
        if self._template_finder.search_and_wait(["DIABLO_B_LAYOUTCHECK0", "DIABLO_B_LAYOUTCHECK1", ], threshold=0.8, time_out=0.1).valid: #Seal B First Layout S found"
            Logger.debug("B = FIRST LAYOUT (S)")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b1_seal", self._char) #pop De Seis Seal (B-S)
            Logger.debug("go to seal")
            self._char.select_by_template(["DIABLO_SEAL_B1_3"], threshold=0.63, time_out=4)
            Logger.debug("pop to seal")
            self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
            #Logger.debug("Kill these Demon Trash")
            #self._char.kill_cs_trash()
            #Logger.debug("Loot their bloody corpses")
            #picked_up_items = self._pickit.pick_up_items(self._char) # after looting we are completely off-track, we need to calibrate again.
            Logger.debug("Calibrating at Seal B SECPOND Layout S")
            wait(1)
            self._pather.traverse_nodes([630], self._char)
            self._pather.traverse_nodes_fixed("diablo_pentagram_b1_safe_dist", self._char) # go to de seis
            self._char.kill_deseis()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes_fixed("diablo_b1_end_pentagram", self._char)
            self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        else: #Then it has to be Seal B Layout U
            Logger.debug("B = SECOND LAYOUT (U)")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b2_seal", self._char)
            #self._char.kill_cs_trash()
            #picked_up_items = self._pickit.pick_up_items(self._char)
            if not self._char.select_by_template(["DIABLO_SEAL_B2_DESEIS"], threshold=0.63, time_out=4): # Pop the seal we migt have to add a failsafe check here: if the active template is found.
                return False
            wait(2) # give her some time to walk & click
            self._pather.traverse_nodes([640], self._char) #Calibrating at Seal B Layout U
            self._pather.traverse_nodes_fixed("diablo_pentagram_b2_safe_dist", self._char) # go to de seis
            self._char.kill_deseis()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes_fixed("diablo_b2_end_pentagram", self._char) 
            self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        """
        # SEAL (C) INFECTOR PART 
        # we tele to C
        # we check for layout of C
        # we pop the seals and kill infector (F=1 or G=2) F first seal pops boss, upper does not. G lower seal pops boss, upper does not (can moat trick infector here)
        # we tele back to pentagram
        # KILL DIABLO PART        
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        #self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        # Attack & Pick items
        self._char.kill_diablo() #should be relative to current location ( a = vizier, b = deseis, c = infector, d = diablo)
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        """
        return (Location.A4_DIABLO_END, picked_up_items)
