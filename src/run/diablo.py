import cv2
import time
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
from utils.custom_mouse import mouse
from screen import Screen


class Diablo:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Diablo /!\ BETA Version /!\ please do not run without supervision.")
        if not self._char.can_teleport():
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2)
        return Location.A4_DIABLO_WP

    def _river_of_flames(self) -> bool:
        if self._config.char["kill_cs_trash"]: # APPROACH FOR CLEARING CHAOS SANCTUARY (kill_cs_trash=1)
            if not self._pather.traverse_nodes([600], self._char, time_out=2): return False
            Logger.debug("ROF: Calibrated at WAYPOINT")
            self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
            Logger.info("ROF: Teleporting to CS ENTRANCE")
            found = False
            # adding a trash clear her can help. also maybe we should try to arrive OUTSIDE of CS Entrance
            templates = ["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"]
            start_time = time.time()
            while not found and time.time() - start_time < 10:
                found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
                if not found:
                    self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char)
            if not found:
                #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_cs_entrance_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            if not self._pather.traverse_nodes([601], self._char, threshold=0.8): return False
            self._char.kill_cs_trash()
            self._picked_up_items |= self._pickit.pick_up_items(self._char)
            Logger.info("ROF: Calibrated at CS ENTRANCE")
            return True

        else: # APROACH TO PENTAGRAM DIRECTLY & SKIP CS TRASH (kill_cs_trash=0)
            if not self._pather.traverse_nodes([600], self._char , time_out=2): return False
            Logger.debug("ROF: Calibrated at WAYPOINT")
            self._pather.traverse_nodes_fixed("diablo_wp_pentagram", self._char)
            Logger.info("ROF: Teleporting directly to PENTAGRAM")
            found = False
            templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"] #"DIA_NEW_PENT_3", "DIA_NEW_PENT_5", "DIA_NEW_PENT_6"
            start_time = time.time()
            while not found and time.time() - start_time < 10:
                found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
                if not found:
                    self._pather.traverse_nodes_fixed("diablo_wp_pentagram_loop", self._char)
            if not found:
                #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_wiz_speed_cs_entrance_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            return True

    def _cs_pentagram(self) -> bool:
        if self._config.char["kill_cs_trash"]: # APROACH TO PENTAGRAM DIRECTLY & SKIP CS TRASH (kill_cs_trash=0)
            self._pather.traverse_nodes_fixed("diablo_entrance_pentagram", self._char)
            Logger.info("CS: Teleporting to PENTAGRAM")
            found = False
            templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"]#"DIA_NEW_PENT_3", "DIA_NEW_PENT_5", "DIA_NEW_PENT_6"
            start_time = time.time()
            while not found and time.time() - start_time < 10:
                found = self._template_finder.search_and_wait(templates, threshold=0.82, time_out=0.1).valid
                if not found: 
                    self._pather.traverse_nodes_fixed("diablo_entrance_pentagram_loop", self._char)
            if not found:
                #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
        self._pather.traverse_nodes([602], self._char, threshold=0.80, time_out=3)
        self._pather.traverse_nodes_fixed("dia_pent_rudijump", self._char) # move to TP
        #AEON, I need your help here: she does not buy new tomes when TPs are depleted
        Logger.info("CS: OPEN TP")
        if not self._ui_manager.has_tps():
            Logger.warning("CS: Open TP failed, higher chance of failing runs from now on, you should buy new TPs!")
            self.used_tps += 20
            #return False
        mouse.click(button="right")
        self.used_tps += 1
        Logger.debug("CS: FYI, total TPs used: " + str(self.used_tps))
        self._pather.traverse_nodes([602], self._char, threshold=0.80, time_out=3)
        Logger.info("CS: Calibrated at PENTAGRAM")
        return True

    def _loop_pentagram(self, path) -> bool:
        found = False

        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_TP"]  #"DIA_NEW_PENT_3", "DIA_NEW_PENT_5 -> if these templates are found, you cannot calibrate at [602] #"DIA_NEW_PENT_6", 
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed(path, self._char)
        if not found:
            #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True

    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 6:
            # try to select seal
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1) + " of 7)")
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(i*0.5)
            # check if seal is opened
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid
            if found:
                Logger.info(seal_layout + ": is open")
                break
            else:

                Logger.debug(seal_layout + ": not open")
                pos_m = self._screen.convert_abs_to_monitor((0, 0)) #remove mouse from seal
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 2:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " of 7 times, trying to kill trash now") # ISSUE: if it failed 7/7 times, she does not try to open the seal: this way all the effort of the 7th try are useless. she should click at the end of the whole story. 
                    self._char.kill_cs_trash()
                    self._picked_up_items |= self._pickit.pick_up_items(self._char)
                    wait(i*0.5) #let the hammers clear & check the template -> the more tries, the longer the wait
                    if not self._pather.traverse_nodes(seal_node, self._char): return False # re-calibrate at seal node
                else:
                    # do a little random hop & try to click the seal
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, direction]) #50 *  removed the Y component - we never want to end up BELOW the seal (any curse on our head will obscure the template check)
                    self._char.move((x_m, y_m), force_move=True)
                i += 1
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/_failed_seal_{seal_layout}_{i}tries" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found

    def _seal_A1(self) -> bool:
        seal_layout = "A1-L"
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info(seal_layout +": Starting to clear Seal")
        
        ### CLEAR TRASH & APPROACH SEAL ###
        #self._char.kill_cs_trash() #done during sealcheck
        #self._picked_up_items |= self._pickit.pick_up_items(self._char) # not needed, we loot after vizier
        if not self._pather.traverse_nodes([611], self._char): return False
        if not self._pather.traverse_nodes([612, 613], self._char): return False
        self._char.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([614], self._char): return False
        if not self._sealdance(["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], seal_layout + "-Fake", [614]): return False
        if not self._pather.traverse_nodes([613, 615], self._char): return False
        if not self._sealdance(["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"], seal_layout + "-Boss", [615]): return False
        if not self._pather.traverse_nodes([612], self._char): return False
        
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss A (Vizier)")
        self._char.kill_vizier([611], [610])
        self._picked_up_items |= self._pickit.pick_up_items(self._char)

        ### GO HOME ###
        if not self._pather.traverse_nodes([611], self._char): return False # calibrating here brings us home with higher consistency.
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        if not self._pather.traverse_nodes_fixed("dia_a1l_home", self._char): return False
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_a1l_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True
    
    def _seal_A2(self) -> bool:
        seal_layout = "A2-Y"
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info(seal_layout +": Starting to clear Seal")

        ### CLEAR TRASH & APPROACH SEAL ###
        if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self._char): return False
        Logger.info(seal_layout + ": Hop!")
        if not self._pather.traverse_nodes([622], self._char): return False
        self._char.kill_cs_trash() #could be skipped to be faster, but helps clearing tempaltes at the calibration node 622 for returning home
        if not self._pather.traverse_nodes([623, 624], self._char): return False
        self._char.kill_cs_trash()
        if not self._pather.traverse_nodes([625], self._char): return False
        if not self._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], seal_layout + "-Fake", [625]): return False
        self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self._char) #instead of traversing node 626 which causes issues
        if not self._sealdance(["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"], seal_layout + "-Boss", [626]): return False
        if not self._pather.traverse_nodes([627, 622], self._char): return False
        
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss A (Vizier)")
        self._char.kill_vizier([623], [624])
        if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self._char): return False
        Logger.info(seal_layout + ": Hop!")
        if not self._pather.traverse_nodes([623], self._char): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)

        ### GO HOME ###
        if not self._pather.traverse_nodes([622], self._char): return False
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_a2y_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_B1(self):
        seal_layout = "B1-S"
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info(seal_layout +": Starting to clear Seal")
    
        ### CLEAR TRASH & APPROACH SEAL ###
        #self._char.kill_cs_trash() #done during sealcheck
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([634], self._char): return False
        self._sealdance(["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"], seal_layout + "-Boss", [634])
        
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss B (De Seis)")
        self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self._char) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
        if not self._char.kill_deseis([632], [631], [632]): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        
        ### GO HOME ###
        if not self._pather.traverse_nodes([633, 634], self._char): return False
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        self._pather.traverse_nodes_fixed("dia_b1s_home", self._char)
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_b1s_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char , time_out=5): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_B2(self):
        seal_layout = "B2-U"
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info(seal_layout +": Starting to clear Seal")
    
        ### CLEAR TRASH & APPROACH SEAL ###
        self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self._char)
        self._sealdance(["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"], seal_layout + "-Boss", [644])

        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss B (De Seis)")
        self._pather.traverse_nodes_fixed("dia_b2u_644_646", self._char) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.

        if not self._char.kill_deseis([641], [640], [646]): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([640], self._char): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        
        ### GO HOME ###
        if not self._pather.traverse_nodes([640], self._char): return False
        self._pather.traverse_nodes_fixed("dia_b2u_home", self._char)
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_b2u_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char , time_out=5): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_C1(self) -> bool: #704 is a weak node, not found often
        seal_layout = "C1-F"
        Logger.info(seal_layout +": Starting to clear Seal")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        
        ### CLEAR TRASH & APPROACH SEAL ###
        #self._char.kill_cs_trash() #done during layout check
        self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self._char) # REPLACES: if not self._pather.traverse_nodes([656, 654, 655], self._char, time_out=3): return False #ISSUE: getting stuck on 704 often, reaching maxgamelength
        #self._char.kill_cs_trash()
        if not self._sealdance(["DIA_C1F_OPEN_NEAR"], ["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"], seal_layout + "-Fake", [655]): return False #ISSUE: getting stuck on 705 during sealdance(), reaching maxgamelength
        self._pather.traverse_nodes_fixed("dia_c1f_654_651", self._char)
        if not self._sealdance(["DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"], ["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"], seal_layout + "-Boss", [652]): return False
        self._pather.traverse_nodes_fixed("dia_c1f_652", self._char)
        
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss C (Infector)")
        self._char.kill_infector()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        
        ### GO HOME ###
        if not self._pather.traverse_nodes([654], self._char, time_out=3): return False # this node often is not found
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        self._pather.traverse_nodes_fixed("dia_c1f_home", self._char)
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_c1f_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_C2(self) -> bool: #could make sense to change seal pop order - if infector dies, all mobs die immediatly, on the other hand if infector does not die at his spawn, we have a 2nd chance getting him with sealdance() at fake seal
        seal_layout = "C2-G"
        Logger.info(seal_layout +": Starting to clear Seal")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        
        ### CLEAR TRASH & APPROACH SEAL ###
        if not self._pather.traverse_nodes([663, 662], self._char): return False
        if not self._sealdance(["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], seal_layout + "-Boss", [662]): return False
        self._pather.traverse_nodes_fixed("dia_c2g_663", self._char) # REPLACES for increased consistency: #if not self._pather.traverse_nodes([662, 663], self._char): return False
        Logger.info(seal_layout + ": Kill Boss C (Infector)")
        
        ### KILL BOSS ###
        self._char.kill_infector()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([664, 665], self._char): return False
        if not self._sealdance(["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"], seal_layout + "-Fake", [665]): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        
        ### GO HOME ###
        if not self._pather.traverse_nodes([665], self._char): return False
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        self._pather.traverse_nodes_fixed("dia_c2g_home", self._char)
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_c2g_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        self._picked_up_items = False
        self.used_tps = 0
        if do_pre_buff: self._char.pre_buff()
        if not self._river_of_flames(): return False
        if self._config.char["kill_cs_trash"]: Logger.info("Clearing CS trash is not yet implemented, AZMR is working on it ... continue without trash")
        if not self._cs_pentagram(): return False

        # Seal A: Vizier (to the left)
        if self._config.char["kill_cs_trash"] and do_pre_buff: self._char.pre_buff()
        #self._char.kill_cs_trash() # not needed if seals exectued in order A-B-C
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        self._pather.traverse_nodes_fixed("dia_a_layout", self._char)
        self._char.kill_cs_trash() # this attack sequence increases layout check consistency, we loot when the boss is killed
        Logger.info("A: Checking Layout for Vizier")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_layout_check_A_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        templates = ["DIA_A2Y_LAYOUTCHECK0", "DIA_A2Y_LAYOUTCHECK1", "DIA_A2Y_LAYOUTCHECK2", "DIA_A2Y_LAYOUTCHECK4", "DIA_A2Y_LAYOUTCHECK5", "DIA_A2Y_LAYOUTCHECK6"] ##We check for A2Y templates first, they are more distinct, but we still have a 10% failure rate here amongst 100s of runs. Mostly it is related to NOT perfectly arriving at the layout check position (overshooting by 1 teleport) - maybe looping could help here?. The ratio of seals is typically skewed towards A1L, due to failing here.
        if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
            Logger.debug("A1-L: Layout_check step 1/2 - A2Y templates NOT found")
            if not self._pather.traverse_nodes([619], self._char): return False #seems to be A1L, so we are calibrating at a node of A1L, just to be safe to see the right templates. If the previous check failed, we will get pather stuck or maxgamelenght violation.
            templates = ["DIA_A1L_LAYOUTCHECK0","DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK4LEFT","DIA_A1L_LAYOUTCHECK4RIGHT",]
            if not self._template_finder.search_and_wait(templates, threshold=0.85, time_out=0.5).valid:
                Logger.debug("A1-L: Layout_check step 2/2 - Failed to determine the right Layout at A (Vizier) - aborting run") #this also happens approx (7%) of the times tested amongst 100s of runs
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_A1L_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            else:
                Logger.debug("A1-L: Layout_check step 2/2 - A1L templates found - all fine, proceeding with A1L")
                if not self._seal_A1(): return False
        else:
            Logger.debug("A2-Y: Layout_check step 1/2 - A2Y templates found")
            templates = ["DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK0"]
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug("A2-Y: Layout_check step 2/2 - A1L templates NOT found - all fine, proceeding with A2Y")
                if not self._seal_A2(): return False
            else:
                Logger.debug("A2-Y: Layout_check step 2/2 - Failed to determine the right Layout at A (Vizier) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_A2Y_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
        
        # Seal B: De Seis (to the top)
        if do_pre_buff: self._char.pre_buff()
        self._char.kill_cs_trash()
        if not self._pather.traverse_nodes([602] , self._char , time_out=5): return False
        self._pather.traverse_nodes_fixed("dia_b_layout_bold", self._char)
        self._char.kill_cs_trash() # this attack sequence increases layout check consistency
        Logger.debug("B: Checking Layout for De Seis")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_layout_check_B_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        templates = ["DIA_B1S_BOSS_CLOSED_LAYOUTCHECK1", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK2", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK3"] #We check for B1S templates first, they are more distinct
        if self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
            Logger.debug("B1-S: Layout_check step 1/2 - B1S templates found")
            if not self._pather.traverse_nodes([634], self._char): return False #seems to be B1S, so we are calibrating at a node of B1S, just to be safe to see the right templates
            templates = ["DIA_B2U_LAYOUTCHECK1", "DIA_B2U_LAYOUTCHECK2", "DIA_B2U_LAYOUTCHECK2SMALL","DIA_B2U_LAYOUTCHECK3", "DIA_B2U_LAYOUTCHECK4", "DIA_B2U_LAYOUTCHECK5","DIA_B2U_LAYOUTCHECK6","DIA_B2U_LAYOUTCHECK7","DIA_B2U_LAYOUTCHECK8"]
            if self._template_finder.search_and_wait(templates, threshold=0.75, time_out=0.5).valid:
                Logger.debug("B1-S: Layout_check step 2/2: Failed to determine the right Layout at B (De Seis) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_B1S_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            else:
                Logger.debug("B1-S: Layout_check step 2/2 - B2U templates NOT found - all fine, proceeding with B1S")
                if not self._seal_B1(): return False
        else:
            Logger.debug("B2-U: Layout_check step 1/2: B1S templates NOT found")
            if not self._pather.traverse_nodes([647], self._char, time_out=5): return False #seems to be B2U, so we are calibrating at a node of B2U, just to be safe to see the right templates
            templates = ["DIA_B2U_LAYOUTCHECK1", "DIA_B2U_LAYOUTCHECK2", "DIA_B2U_LAYOUTCHECK2SMALL","DIA_B2U_LAYOUTCHECK3", "DIA_B2U_LAYOUTCHECK4", "DIA_B2U_LAYOUTCHECK5","DIA_B2U_LAYOUTCHECK6","DIA_B2U_LAYOUTCHECK7","DIA_B2U_LAYOUTCHECK8"]
            if self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug("B2-U: Layout_check step 2/2 - B2U templates found - all fine, proceeding with B2U")
                if not self._seal_B2(): return False
            else:
                Logger.debug("B2-U: Layout_check step 2/2 - Failed to determine the right Layout at B (De Seis) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_B2U_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False

        # Seal C: Infector (to the right)
        if do_pre_buff: self._char.pre_buff()
        self._char.kill_cs_trash()
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        self._pather.traverse_nodes_fixed("dia_c_layout_bold", self._char)
        #self._char.kill_cs_trash() # this attack sequence increases layout check consistency
        Logger.debug("C: Checking Layout for Infector")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_layout_check_C_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        templates = ["DIA_C2G_BOSS_CLOSED_LAYOUTCHECK1", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK2", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK3","DIA_C2G_BOSS_CLOSED_LAYOUTCHECK4","DIA_C2G_BOSS_CLOSED_LAYOUTCHECK5"] #We check for C1F templates first, they are more distinct
        if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
            Logger.debug("C1-F: Layout_check step 1/2 - C2G templates NOT found")
            templates = ["DIA_C1F_LAYOUTCHECK1", "DIA_C1F_LAYOUTCHECK2", "DIA_C1F_LAYOUTCHECK3"]
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug("C1-F: Layout_check step 2/2 - Failed to determine the right Layout at C (Infector) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_C1F_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            else:
                Logger.debug("C1-F: Layout_check step 2/2 - C1F templates found - all fine, proceeding with C1F")
                if not self._seal_C1(): return False
        else:
            Logger.debug("C2-G: Layout_check step 1/2 - C2G templates found")
            templates = ["DIA_C1F_LAYOUTCHECK1", "DIA_C1F_LAYOUTCHECK2", "DIA_C1F_LAYOUTCHECK3"]
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug("C2-G: Layout_check step 2/2 - C1F templates NOT found - all fine, proceeding with C2G")
                if not self._seal_C2(): return False
            else:
                Logger.debug("C2-G: Layout_check step 2/2 - Failed to determine the right Layout at C (Infector) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_C2GS_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False

        # Diablo
        Logger.info("Waiting for Diablo to spawn") # we could add a check here, if we take damage: if yes, one of the sealbosses is still alive (otherwise all demons would have died when the last seal was popped)
        if not self._pather.traverse_nodes([602], self._char, time_out=5): return False
        self._char.kill_diablo() 
        wait(0.2, 0.3)
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_dia_kill_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        self._picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A4_DIABLO_END, self._picked_up_items)

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
    screen = Screen()
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)

### ISSUE LOG ###

# stash or shrine located near a node or bossfight will make botty just try to click the stash
# Better Layout Check consistency at A (opportunity for up to 10% more succesful runs)
# Better Looping Home consistency at A & C (if a tombstone stash is on its way, the path gets displaced which might lead to missing the pentagram)
# We could consider a function get_nearest_node() or a path home from where we started to loot to not get off-track after looting trash.
# It could make sense to change ALL the fights to just static paths. in the heat of battle the nodes sometimes are not recognized, leading to chicken - OR to clear all trash thoroughly before attacking the sealboss.

