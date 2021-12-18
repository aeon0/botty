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

    def _river_of_flames(self):
        self._pather.traverse_nodes([600], self._char) # Calibrate postion at wp to ensure success for all river of flames layouts
        Logger.debug("Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        Logger.info("Moving towards CS ENTRANCE")
        found = False
        templates = ["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"]
        while not found: # Looping in smaller teleport steps to make sure we find the entrance
            found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char)
        self._pather.traverse_nodes([601], self._char, threshold=0.8) # Calibrate at entrance to Chaos Sanctuary to ensure success reaching pentagram
        Logger.debug("Calibrated at CS ENTRANCE")

    def _cs_pentagram(self):
        self._pather.traverse_nodes_fixed("diablo_entrance_pentagram", self._char)
        Logger.info("Moving towards PENTAGRAM")
        found = False
        templates = ["DIABLO_PENT_0", "DIABLO_PENT_1", "DIABLO_PENT_2", "DIABLO_PENT_3"]
        while not found:
            found = self._template_finder.search_and_wait(templates, threshold=0.82, time_out=0.1).valid
            if not found:
                self._pather.traverse_nodes_fixed("diablo_entrance_pentagram_loop", self._char) # Looping in smaller teleport steps to make sure we find the pentagram
        self._pather.traverse_nodes([602], self._char, threshold=0.82)
        Logger.info("Calibrated at PENTAGRAM")

    def _seal_A1(self):
        Logger.info("Layout: A1Y")
        self._pather.traverse_nodes_fixed("diablo_a1_seal1", self._char)
        Logger.info("A1Y SAFE_DIST")
        self._char.kill_cs_trash()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        Logger.info("Clear Trash A1Y Fake Seal from SAFE_DIST")
        self._pather.traverse_nodes([610, 611, 610], self._char) # calibrate A1Y Seal1 Noboss - we fight bit away from the seal to keep the template-check later on clear
        Logger.info("Calibrating after Loot")
        #found = False
        #templates = ["DIA_A1Y_5"]
        #while not found: # Looping to click the seal while the open seal is not found
        #    found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
        #    if not found:
            	# might add a small displacement teleport here to change the perspective on the seal
        self._char.select_by_template(["DIA_A1Y_0", "DIA_A1Y_0_MOUSEOVER"], threshold=0.50, time_out=5) #low threshold seal pop nonboss seal both for mouseover and non mouseover graphic
        wait(1)
        Logger.info("A1Y Pop Fake Seal")
        self._pather.traverse_nodes([611], self._char) # go to A1Y Seal2 Boss
        self._char.kill_cs_trash()
        Logger.info("Clear Trash A1Y Boss Seal")
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([611, 610, 611], self._char) # go to A1Y Seal2 Boss recalibrate after loot
        Logger.info("Calibrating after Loot")   
        self._char.select_by_template(["DIA_A1Y_8", "DIA_A1Y_8_MOUSEOVER"], threshold=0.50, time_out=5) #threshold lowered
        wait(1)
        Logger.info("A1Y Pop Boss Seal")            
        self._pather.traverse_nodes([614], self._char) # go to fight vizier
        Logger.info("A1Y Calibrate at SAFE DIST")
        self._pather.traverse_nodes([614], self._char) # go to fight vizier
        Logger.info("A1Y REALLY Calibrate at SAFE DIST")
        self._char.kill_vizier()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([614], self._char) # calibrate at SAFE_DIST before headding back to pentagram
        Logger.info("A1Y Calibrate at SAFE DIST")
        self._pather.traverse_nodes_fixed("diablo_a1_end_pentagram", self._char) #lets go home
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        Logger.info("I calibrated at PENTAGRAM")

    def _seal_A2(self):
        Logger.info("A = SECOND LAYOUT (L) - first seal pops")            
        self._pather.traverse_nodes_fixed("diablo_a2_safe_dist", self._char) # we between the seals
        self._char.kill_cs_trash()
        Logger.info("Clear Trash A2L SAFE DIST")
        self._pather.traverse_nodes([622, 621, 620], self._char) #traverse
        self._char.kill_cs_trash()
        wait(2) #let hammercloud clear up
        self._char.select_by_template(["DIA_A2L_2", "DIA_A2L_3", "DIA_A2L_2_621", "DIA_A2L_2_620", "DIA_A2L_2_620_MOUSEOVER"], threshold=0.50, time_out=5) #threshold lowered            
        wait(1)
        self._pather.traverse_nodes([621], self._char) #traverse
        self._char.select_by_template(["DIA_A2L_2", "DIA_A2L_3", "DIA_A2L_2_621", "DIA_A2L_2_620", "DIA_A2L_2_620_MOUSEOVER"], threshold=0.50, time_out=5) #failsafe 2nd try           
        wait(1)
        Logger.info("A2L Pop Fake Seal")
        self._pather.traverse_nodes([622, 623], self._char) #traverse
        self._char.kill_cs_trash() # sometimes there is a single caster below seal2 blocking viziers spawn.
        wait(2) #let hammercloud clear up
        self._char.select_by_template(["DIA_A2L_0", "DIA_A2L_1"], threshold=0.50, time_out=5) #threshold lowered    
        wait(1)
        Logger.info("A2L Pop Boss Seal")
        self._pather.traverse_nodes([622], self._char) #go to safe dist -> the idea is to make the merc move away from vizier spawn. if there is a stray monster at the spawn, vizier will only come if cleared and our attack sequence might miss.
        self._char.kill_vizier()
        Logger.info("Kill Vizier")
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([622], self._char) #go to safe dist
        Logger.info("A2L Calibrate at Safe Dist after Loot")
        self._pather.traverse_nodes_fixed("diablo_a2_end_pentagram", self._char)
        Logger.info("A2L Going Home to Pentagram")
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram
        Logger.info("Calibrated at Pentagram")

    def _seal_B1(self):
        Logger.debug("B = FIRST LAYOUT (S)")
        self._pather.traverse_nodes_fixed("diablo_pentagram_b1_seal", self._char) #pop De Seis Seal (B-S)
        Logger.debug("go to seal")
        Logger.debug("Kill these Demon Trash")
        self._char.kill_cs_trash()
        Logger.debug("Loot their bloody corpses")
        self._picked_up_items = self._pickit.pick_up_items(self._char) # after looting we are completely off-track, we need to calibrate again.
        Logger.debug("Calibrating at Seal B SECPOND Layout S")
        wait(1)
        self._char.select_by_template(["DIABLO_SEAL_B1_3"], threshold=0.5, time_out=4)
        Logger.debug("pop to seal")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        self._pather.traverse_nodes([630], self._char)
        self._pather.traverse_nodes_fixed("diablo_pentagram_b1_safe_dist", self._char) # go to de seis
        self._char.kill_deseis()
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes_fixed("diablo_b1_end_pentagram", self._char)
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram

    def _seal_B2(self):
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
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes_fixed("diablo_b2_end_pentagram", self._char) 
        self._pather.traverse_nodes([602], self._char) #we arrived there and are now calibrating at Pentagram

    def _seal_C1(self):
        Logger.debug("C = FIRST LAYOUT (G)")
        self._pather.traverse_nodes_fixed("diablo_pentagram_c1_seal", self._char)
        self._pather.traverse_nodes([650], self._char) # pop seal1 boss
        self._char.select_by_template(["DIABLO_C1_CALIBRATE_2_CLOSED"], threshold=0.5, time_out=4)
        wait(2)
        self._pather.traverse_nodes([652], self._char) # fight 651
        self._char.kill_infector()
        picked_up_items = self._pickit.pick_up_items(self._char)
        self._pather.traverse_nodes([652], self._char) # pop seal 651, 
        self._char.select_by_template(["DIABLO_C1_CALIBRATE_8"], threshold=0.5, time_out=4)
        wait(2)
        self._pather.traverse_nodes_fixed("diablo_c1_end_pentagram", self._char)
        self._pather.traverse_nodes([602], self._char) # calibrate pentagram

    def _seal_C2(self):
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

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if do_pre_buff:
            self._char.pre_buff()
        self._river_of_flames()
        self._cs_pentagram()
        # Seal A: Vizier (to the left)
        self._pather.traverse_nodes_fixed("diablo_pentagram_a_layout_check", self._char) # we check for layout of A (1=Y or 2=L) L lower seal pops boss, upper does not. Y upper seal pops boss, lower does not
        Logger.info("Checking Layout at A")
        if self._template_finder.search_and_wait(["DIABLO_A_LAYOUTCHECK0", "DIABLO_A_LAYOUTCHECK1", "DIABLO_A_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid:
            self._seal_A1()
        else:
            self._seal_A2()
        # Seal B: De Seis (to the top)
        self._pather.traverse_nodes_fixed("diablo_pentagram_b_layout_check", self._char) # we check for layout of B (1=S or 2=U) - just one seal to pop.
        Logger.debug("Checking Layout at B")
        if self._template_finder.search_and_wait(["DIABLO_B_LAYOUTCHECK0", "DIABLO_B_LAYOUTCHECK1"], threshold=0.8, time_out=0.1).valid:
            self._seal_B1()
        else:
            self._seal_B2()
        # Seal C: Infector (to the right)    
        self._pather.traverse_nodes_fixed("diablo_pentagram_c_layout_check", self._char)  # we check for layout of C (1=G or 2=F) G lower seal pops boss, upper does not. F first seal pops boss, second does not
        if self._template_finder.search_and_wait(["DIABLO_C_LAYOUTCHECK0", "DIABLO_C_LAYOUTCHECK1", "DIABLO_C_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid:
            self._seal_C1()
        else:
            self._seal_C2()
        # Diablo
        wait(9)# waiting for Diablo to spawn 
        self._char.kill_diablo() 
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return True
        return (Location.A4_DIABLO_END, picked_up_items)#there is an error  ValueError: State 'diablo' is not a registered state.

"""
if __name__ == "__main__":
    from screen import Screen
    import keyboard
    from game_stats import GameStats
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    from bot import Bot
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)
    # bot._diablo.battle(True)
    # bot._diablo._traverse_river_of_flames()
    # bot._diablo._cs_pentagram()
    bot._diablo._seal_a()
"""