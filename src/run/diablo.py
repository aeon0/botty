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
        Logger.info("I calibrated at ROF WP")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char) # WITHOUT LOOP TO SPEED UP
        Logger.info("I head towards CS entrance & now switch to Template Looping to slow down & not to overshoot")
        while not found:
            found = self._template_finder.search_and_wait(["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"], threshold=0.8, time_out=0.1).valid
            self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char) # THIS THING TYPICALLY OVERSHOOTS BY ONE TELEPORT.
        #self._char.kill_cs_trash()
        #Logger.info("Clear Trash at CS Entrance")
        #picked_up_items = self._pickit.pick_up_items(self._char) #might be needed for hell difficulty not go get into FHR whilst calibrating. But the attack position is bad for hammers - everything in the wall :/
        self._pather.traverse_nodes([601], self._char) #Calibrating Position exactly at Door to Chaos Sanctuary Entrance HERE, WE HAVE AN ISSUE OF THE STEP BEFORE WAS OVERSHOOTING. WE MIGHT NEED MORE TEMPLATES DEEPER INTO THE CS ENTRANCE
        Logger.info("I calibrated at CS Entrance")
        # CHAOS SANTUARY PART
        self._pather.traverse_nodes_fixed("diablo_entrance_pentagram", self._char) # WITHOUT LOOP TO SPEED UP
        Logger.info("I head towards CS PENTRAGRAM & now switch to Template Looping to slow down & not to overshoot")
        found = False
        while not found:
            found = self._template_finder.search_and_wait(["DIABLO_PENT_0", "DIABLO_PENT_1", "DIABLO_PENT_2", "DIABLO_PENT_3"], threshold=0.8, time_out=0.1).valid # searching for pentagram tempaltes... same, like for 610
            #found = self._template_finder.search_and_wait(["DIABLO_PENTX_0", "DIABLO_PENTX_1", "DIABLO_PENTX_2", "DIABLO_PENTX_3", "DIABLO_PENTX_4"], threshold=0.8, time_out=0.1).valid # searching for pentagram tempaltes... unique templates for this step of code
            self._pather.traverse_nodes_fixed("diablo_entrance_pentagram_loop", self._char) # we tele top right towards the pentagram
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        Logger.info("I calibrated at PENTAGRAM")
        # SEAL (A) VIZIER PART
        # we tele to A
        self._pather.traverse_nodes_fixed("diablo_pentagram_a_layout_check", self._char) # we tele to B
        # we check for layout of A (Y=1 or L=2) L first seal pops boss, upper does not. Y upper seal pops boss, lower does not
        Logger.info("Checking Layout at A")
        if self._template_finder.search_and_wait(["DIABLO_A_LAYOUTCHECK0", "DIABLO_A_LAYOUTCHECK1", "DIABLO_A_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid: #Seal B First Layout S found"
            Logger.info("A = FIRST LAYOUT (Y) - upper seal pops")
            self._pather.traverse_nodes_fixed("diablo_a1_seal1", self._char)
            Logger.info("A1Y SAFE_DIST")
            self._char.kill_cs_trash()
            picked_up_items = self._pickit.pick_up_items(self._char)
            Logger.info("Clear Trash A1Y Fake Seal from SAFE_DIST")
            self._pather.traverse_nodes([610], self._char) # calibrate A1Y Seal1 Noboss - we fight bit away from the seal to keep the template-check later on clear
            self._pather.traverse_nodes([611], self._char) # yes it looks stupid but going back between 610 and 611 ensures we are at the right place to pop the seal
            self._pather.traverse_nodes([610], self._char) # here we go, lets pop the seal
            Logger.info("Calibrating after Loot")            
            self._char.select_by_template(["DIA_A1Y_0", "DIA_A1Y_0_MOUSEOVER"], threshold=0.50, time_out=5) #threshold lowered
            wait(1)
            Logger.info("A1Y Pop Fake Seal")
            self._pather.traverse_nodes([611], self._char) # go to A1Y Seal2 Boss
            self._char.kill_cs_trash()
            Logger.info("Clear Trash A1Y Boss Seal")
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes([611], self._char) # go to A1Y Seal2 Boss recalibrate after loot
            self._pather.traverse_nodes([610], self._char) # go to A1Y Seal2 Boss recalibrate after loot
            self._pather.traverse_nodes([611], self._char) # go to A1Y Seal2 Boss recalibrate after loot
            Logger.info("Calibrating after Loot")   
            self._char.select_by_template(["DIA_A1Y_8", "DIA_A1Y_8_MOUSEOVER"], threshold=0.50, time_out=5) #threshold lowered
            wait(1)
            Logger.info("A1Y Pop Boss Seal")            
            self._pather.traverse_nodes([614], self._char) # go to fight vizier
            Logger.info("A1Y Calibrate at SAFE DIST")
            self._pather.traverse_nodes([614], self._char) # go to fight vizier
            Logger.info("A1Y REALLY Calibrate at SAFE DIST")
            self._char.kill_vizier()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes([614], self._char) # calibrate at SAFE_DIST before headding back to pentagram
            Logger.info("A1Y Calibrate at SAFE DIST")
            self._pather.traverse_nodes_fixed("diablo_a1_end_pentagram", self._char) #lets go home
            self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
            Logger.info("I calibrated at PENTAGRAM")
        else: #Then it has to be Seal A second Layout L
            Logger.info("A = SECOND LAYOUT (L) - first seal pops")            
            self._pather.traverse_nodes_fixed("diablo_pentagram_a2_seal", self._char) # we tele to upper seal (not popping boss, to have a common template between both seals)
            self._pather.traverse_nodes([620], self._char) #Calibrating at upper Seal A SECOND Layout (L)
            self._char.kill_cs_trash()
            wait(2)
            self._pather.traverse_nodes([620], self._char) #Calibrating AGAIN at upper Seal A SECOND Layout (L) AFTER KILLING TRASH
            self._char.select_by_template(["DIABLO_A2_CALIBRATION_5"], threshold=0.5, time_out=4) #threshold lowered
            wait(1) # give me some time to click it
            Logger.info("pop seal boss")
            self._pather.traverse_nodes([621], self._char) #Calibrating at lower Seal A SECOND Layout (L)
            self._char.kill_cs_trash()
            self._pather.traverse_nodes([622], self._char) #Move to pop upper seal
            self._char.kill_cs_trash()
            self._char.select_by_template(["DIABLO_A2_VIZIER_MOUSEOVER"], threshold=0.5, time_out=4) 
            wait(1) # give me some time to click it
            Logger.info("pop seal")
            self._pather.traverse_nodes([614], self._char) #Calibrating at Vizier attack position -> we might need to remove the seals from the 614 orientation point
            Logger.info("calibrating at attack position to fight Vizier")
            self._char.kill_vizier()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes([614], self._char) #Calibrating at Vizier attack position -> we might need to remove the seals from the 614 orientation point
            Logger.info("calibrating at attack position to return home")
            self._pather.traverse_nodes_fixed("diablo_a2_end_pentagram", self._char) #lets go home
            self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        # we pop the seals and kill vizier
        # we tele back to pentagram
        # SEAL (B) DE SEIS PART 
        self._pather.traverse_nodes_fixed("diablo_pentagram_b_layout_check", self._char) # we tele to B
        Logger.debug("Checking Layout")
        if self._template_finder.search_and_wait(["DIABLO_B_LAYOUTCHECK0", "DIABLO_B_LAYOUTCHECK1"], threshold=0.8, time_out=0.1).valid: #Seal B First Layout S found"
            Logger.debug("B = FIRST LAYOUT (S)")
            self._pather.traverse_nodes_fixed("diablo_pentagram_b1_seal", self._char) #pop De Seis Seal (B-S)
            Logger.debug("go to seal")
            self._char.select_by_template(["DIABLO_SEAL_B1_3"], threshold=0.5, time_out=4)
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
            if not self._char.select_by_template(["DIABLO_SEAL_B2_DESEIS"], threshold=0.5, time_out=4): # Pop the seal we migt have to add a failsafe check here: if the active template is found.
                return False
            wait(2) # give her some time to walk & click
            self._pather.traverse_nodes([640], self._char) #Calibrating at Seal B Layout U
            self._pather.traverse_nodes_fixed("diablo_pentagram_b2_safe_dist", self._char) # go to de seis
            self._char.kill_deseis()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes_fixed("diablo_b2_end_pentagram", self._char) 
            self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        # SEAL (C) INFECTOR PART 
        self._pather.traverse_nodes_fixed("diablo_pentagram_c_layout_check", self._char) # we tele to B
        if self._template_finder.search_and_wait(["DIABLO_C_LAYOUTCHECK0", "DIABLO_C_LAYOUTCHECK1", "DIABLO_C_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid: #Seal C First Layout G found"
            Logger.debug("C = FIRST LAYOUT (G)")
            self._pather.traverse_nodes_fixed("diablo_pentagram_c1_seal", self._char)
            self._pather.traverse_nodes([650], self._char) # pop seal1 boss
            self._char.select_by_template(["DIABLO_C1_CALIBRATE_2_CLOSED"], threshold=0.5, time_out=4)
            wait(2)
            self._pather.traverse_nodes([651], self._char) # fight
            self._char.kill_infector()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes([651], self._char) # fight
            self._pather.traverse_nodes([652], self._char) # pop seal2
            self._char.select_by_template(["DIABLO_C1_CALIBRATE_8"], threshold=0.5, time_out=4)
            wait(2)
            self._pather.traverse_nodes_fixed("diablo_c1_end_pentagram", self._char)
            self._pather.traverse_nodes([602], self._char) # calibrate pentagram
            wait(15)#waiting for Diablo to spawn
        else: #Then it has to be Seal C Layout F
            Logger.debug("C = SECOND LAYOUT (F)")
            # we pop the seals and kill infector (F=1 or G=2) F first seal pops boss, upper does not. G lower seal pops boss, upper does not (can moat trick infector here)
            self._pather.traverse_nodes_fixed("diablo_pentagram_c2_seal", self._char)
            self._char.select_by_template(["DIABLO_C2_SEAL_NOBOSS"], threshold=0.5, time_out=4)
            wait(2)
            self._pather.traverse_nodes([660], self._char) # fight
            self._char.select_by_template(["DIABLO_C2_SEAL_BOSS"], threshold=0.5, time_out=4)
            wait(2)
            self._char.kill_infector()
            picked_up_items = self._pickit.pick_up_items(self._char)
            self._pather.traverse_nodes([661], self._char) # fight
            # we tele back to pentagram
            self._pather.traverse_nodes_fixed("diablo_c2_end_pentagram", self._char)
            self._pather.traverse_nodes([602], self._char) # calibrate pentagram
            wait(20)#waiting for Diablo to spawn
        # KILL DIABLO PART        
        self._pather.traverse_nodes([602], self._char) #calibrating at Pentagram to kill diablo
        self._char.kill_diablo() 
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A4_DIABLO_END, picked_up_items)
