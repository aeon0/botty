from ast import Break, Return
from pickle import FALSE
import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager, A4
from ui import UiManager
from ui import BeltManager
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
        pickit: PickIt,
        belt_manager: BeltManager
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
        self._belt_manager = belt_manager
        self.used_tps = 0
        self._curr_loc: Union[bool, Location] = Location.A4_TOWN_START

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Diablo")
        if not self._char.can_teleport():
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2)
        return Location.A4_DIABLO_WP
    

    # BUY POTS & STASH
    def _cs_town_visit(self, location:str) -> bool:
        # Do we want to go back to town and restock potions etc? 
        if self._config.char["cs_town_visits"]:
            buy_pots = self._belt_manager.should_buy_pots()
            if not buy_pots:
                Logger.info(location + ": Got enough pots, no need to go to town right now.")
            else:
                Logger.info(location + ": Going back to town to visit our friend Jamella (heal/clear debuffs/restock potions)")
                success = self._char.tp_town()
                if success:
                    self._curr_loc = self._town_manager.wait_for_tp(self._curr_loc)
                    # Check if we should stash while we are in town
                    force_stash = False
                    force_stash = self._ui_manager.should_stash(self._config.char["num_loot_columns"])
                    if force_stash:
                        if self._config.char["id_items"]:
                            Logger.info(location + ": Identifying items")
                            self._curr_loc = self._town_manager.identify(self._curr_loc)
                            if not self._curr_loc:
                                return self.trigger_or_stop("end_game", failed=True)
                        Logger.info(location + ":Stashing items")
                        self._curr_loc = self._town_manager.stash(self._curr_loc)
                        if not self._curr_loc:
                            return self.trigger_or_stop("end_game", failed=True)
                        self._no_stash_counter = 0
                        self._picked_up_items = False
                        wait(1.0)
                    # Shop some pots
                    if self._curr_loc:
                        pot_needs = self._belt_manager.get_pot_needs()
                        self._curr_loc = self._town_manager.buy_pots(self._curr_loc, pot_needs["health"], pot_needs["mana"])
                    Logger.debug(location + ": Done in town, now going back to portal...")
                    # Move from Act 4 NPC Jamella towards WP where we can see the Blue Portal
                    if not self._pather.traverse_nodes([164, 163], self._char, time_out=2): return False
                    wait(0.22, 0.28)
                    roi = self._config.ui_roi["reduce_to_center"]
                    img = self._screen.grab()
                    template_match = self._template_finder.search(
                        ["BLUE_PORTAL","BLUE_PORTAL_2"],
                        img,
                        threshold=0.66,
                        roi=roi,
                        normalize_monitor=True
                    )
                    if template_match.valid:
                        pos = template_match.position
                        pos = (pos[0], pos[1] + 30)
                        Logger.debug(location + ": Going through portal...")
                        # Note: Template is top of portal, thus move the y-position a bit to the bottom
                        mouse.move(*pos, randomize=6, delay_factor=[0.9, 1.1])
                        wait(0.08, 0.15)
                        mouse.click(button="left")
                        if self._ui_manager.wait_for_loading_screen(2.0):
                            Logger.debug(location + ": Waiting for loading screen...")
                            
                        # Recalibrate at Pentagram and set up new TP to improve loop back to penta success  
                        self._pather.traverse_nodes([602], self._char, threshold=0.80, time_out=3)
                        self._pather.traverse_nodes_fixed("dia_pent_rudijump", self._char) # move to TP    
                        if not self._ui_manager.has_tps():
                            Logger.warning("CS after Town: Open TP failed, higher chance of failing runs from now on, you should buy new TPs! (hint: always_repair=1)")
                            self.used_tps += 20
                        mouse.click(button="right")
                        self.used_tps += 1
                        Logger.debug("CS after town: FYI, total TPs used: " + str(self.used_tps))        
        return True


    # OPEN SEALS
    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 4:
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1)+")") # try to select seal
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(i*0.5)
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid # check if seal is opened
            if found:
                #Logger.info(seal_layout +": is open")
                Logger.info(seal_layout +": is open - "+'\033[92m'+" open"+'\033[0m')
                break
            else:
                #Logger.debug(seal_layout +": not open")
                Logger.debug(seal_layout +": is closed - "+'\033[91m'+" closed"+'\033[0m')
                pos_m = self._screen.convert_abs_to_monitor((0, 0)) #remove mouse from seal
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 1:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " times, trying to kill trash now")
                    Logger.debug("Sealdance: Kill trash at location: sealdance")
                    self._char.kill_cs_trash("sealdance")
                    wait(i*0.5) #let the hammers clear & check the template -> the more tries, the longer the wait
                    if not self._pather.traverse_nodes(seal_node, self._char): return False # re-calibrate at seal node
                else:
                    direction = 1 if i % 2 == 0 else -1 
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, direction]) # do a little random hop & try to click the seal
                    self._char.move((x_m, y_m), force_move=True)
                i += 1
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/_failed_seal_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found


    # LOOP TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_TP", "DIA_NEW_PENT_2"] # these templates are just found 2-3 times amongst 100 runs  "DIA_NEW_PENT_TPTOP", "DIA_NEW_PENT_TPBOT"
        start_time = time.time()
        while not found and time.time() - start_time < 15: #increased from 10 to 15 to allow looping back in case of a failed layout check during clearing CS trash
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed(path, self._char)
        if not found:
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + path + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True


    #CLEAR CS TRASH
    def _entrance_hall(self) -> bool:
        Logger.info("CS: Starting to clear Trash")

        Logger.debug("Kill trash at location: entrance_hall_01")
        if not self._pather.traverse_nodes([604], self._char): return False #, time_out=3): return False 
        self._char.kill_cs_trash("entrance_hall_01")
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        
        self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self._char) # 604 -> 671 Hall1
        Logger.debug("Kill trash at location: entrance_hall_02")
        self._char.kill_cs_trash("entrance_hall_02")
        
        if not self._pather.traverse_nodes([672, 670], self._char): return False # pull top mobs 672 to bottom 670
        Logger.debug("Kill trash at location: entrance_hall_03")
        self._char.kill_cs_trash("entrance_hall_03") 
        self._picked_up_items |= self._pickit.pick_up_items(self._char) 
        if not self._pather.traverse_nodes([671], self._char): return False
        self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self._char) # 671 -> LC Hall2
        
        if not self._pather.traverse_nodes([605], self._char): return False # hybrid calibration node
        templates = ["DIABLO_ENTRANCE_12", "DIABLO_ENTRANCE_13", "DIABLO_ENTRANCE_15", "DIABLO_ENTRANCE_16", "DIABLO_ENTRANCE_19", "DIABLO_ENTRANCE_18","DIABLO_ENTRANCE_50", "DIABLO_ENTRANCE_51", "DIABLO_ENTRANCE_52", "DIABLO_ENTRANCE_53", "DIABLO_ENTRANCE_54", "DIABLO_ENTRANCE_55"] #Entrance 1 Refrences
        if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1).valid:
            Logger.info("Entrance 2 Layout_check step 1/2: Entrance 1 templates NOT found")
            templates = ["DIABLO_ENTRANCE2_15", "DIABLO_ENTRANCE2_23", "DIABLO_ENTRANCE2_19", "DIABLO_ENTRANCE2_17", "DIABLO_ENTRANCE2_50", "DIABLO_ENTRANCE2_51", "DIABLO_ENTRANCE2_52","DIABLO_ENTRANCE2_53","DIABLO_ENTRANCE2_54","DIABLO_ENTRANCE2_55","DIABLO_ENTRANCE2_56"] #Entrance 2 Refrences
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1).valid:
                Logger.info("Entrance 2 Layout_check step 2/2: Failed to determine the right Layout, "+'\033[91m'+"trying to loop to pentagram to save the run"+'\033[0m')
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_entrance2_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return True
            else:
                Logger.info("Entrance 2 Layout_check step 2/2: Entrance 2 templates found - "+'\033[96m'+"all fine, proceeding with Entrance 2"+'\033[0m')
                if not self._entrance_2(): return False
                entrance2_layout = "CS Entrance Style 2"
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + entrance2_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                Logger.info("Entrance Layout: " + entrance2_layout)
                Logger.debug("Kill trash at location: entrance2_01")
                self._char.kill_cs_trash("entrance2_01")
                if not self._pather.traverse_nodes([682], self._char): return False # , time_out=3):
                Logger.debug("Kill trash at location: entrance2_02")
                self._char.kill_cs_trash("entrance2_02")
                Logger.info(entrance2_layout + " - cleaning hall 1/3")
                if not self._pather.traverse_nodes([682], self._char): return False # , time_out=3):
                self._pather.traverse_nodes_fixed("diablo_entrance2_1", self._char)
                if not self._pather.traverse_nodes([683], self._char): return False # , time_out=3):
                Logger.info(entrance2_layout + " - cleaning hall 2/3")
                Logger.debug("Kill trash at location: entrance2_03")
                self._char.kill_cs_trash("entrance2_03")
                self._picked_up_items |= self._pickit.pick_up_items(self._char)
                self._pather.traverse_nodes([683,684], self._char, time_out=3)
                self._pather.traverse_nodes_fixed("diablo_entrance2_2", self._char)
                self._pather.traverse_nodes([685,686], self._char, time_out=3)
                Logger.info(entrance2_layout + " - cleaning hall 3/3")
                Logger.debug("Kill trash at location: entrance2_04")
                self._char.kill_cs_trash("entrance2_04")
                self._picked_up_items |= self._pickit.pick_up_items(self._char)
                # HERE SHOULD BE A CALIBRATION AFTER THE LOOT TO ENSURE WE CORRECTLY LOOP TO THE PENTAGRAM 
                return True 
        else:
            Logger.debug("Entrance 1 Layout_check step 1/2: Entrance 1 templates found")
            templates = ["DIABLO_ENTRANCE2_15", "DIABLO_ENTRANCE2_23", "DIABLO_ENTRANCE2_19","DIABLO_ENTRANCE2_17"] #Entrance 2 Refrences
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug("Entrance 1 Layout_check step 2/2: Entrance 2 templates NOT found - "+'\033[95m'+"all fine, proceeding with Entrance 1"+'\033[0m')
                if not self._entrance_1(): return False
                entrance1_layout = "CS Entrance Style 1"
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + entrance1_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                Logger.info("Entrance Layout: " + entrance1_layout)
                Logger.info(entrance1_layout + " - cleaning hall 1/3")
                Logger.debug("Kill trash at location: entrance1_01")
                self._char.kill_cs_trash("entrance1_01") # Lands on location and starts attacking
                if not self._pather.traverse_nodes([673], self._char): return False # , time_out=3): # Re-adjust itself and continues to attack
                Logger.debug("Kill trash at location: entrance1_02")
                self._char.kill_cs_trash("entrance1_02")
                self._picked_up_items |= self._pickit.pick_up_items(self._char)
                self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self._char) # Moves char to postion close to node 674 continues to attack
                self._pather.traverse_nodes([674], self._char, time_out=3)
                Logger.debug("Kill trash at location: entrance1_03")
                self._char.kill_cs_trash("entrance1_03")
                self._picked_up_items |= self._pickit.pick_up_items(self._char)
                Logger.info(entrance1_layout + " - cleaning hall 2/3")
                self._pather.traverse_nodes([675], self._char, time_out=3) # Re-adjust itself
                self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self._char) #static path to get to be able to spot 676
                self._pather.traverse_nodes([676], self._char, time_out=3)
                Logger.info(entrance1_layout + " - cleaning hall 3/3")
                Logger.debug("Kill trash at location: entrance1_04")
                self._char.kill_cs_trash("entrance1_04")
                self._picked_up_items |= self._pickit.pick_up_items(self._char)
                # HERE SHOULD BE A CALIBRATION AFTER THE LOOT TO ENSURE WE CORRECTLY LOOP TO THE PENTAGRAM
                return True
            else:
                Logger.warning("Entrance 1 Layout_check step 2/2: Failed to determine the right Layout, "+'\033[91m'+"trying to loop to pentagram to save the run"+'\033[0m')
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_entrance1_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return True
        

    #GET FROM WP TO PENTAGRAM (clear_trash=0)
    def _river_of_flames(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False
        Logger.debug("ROF: Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_pentagram_1", self._char)
        self._pather.traverse_nodes_fixed("diablo_wp_pentagram_2", self._char) # split into two paths to avoid bypassing PENT
        Logger.info("ROF: Teleporting directly to PENTAGRAM")
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_pentagram_loop", self._char)
        if not found:
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_pent_loop_no_trash_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True
        

    #GET FROM WP TO CS ENTRANCE (clear_trash=1)
    def _river_of_flames_trash(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False
        Logger.debug("CS Trash: Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        if not self._pather.traverse_nodes([603], self._char): return False
        Logger.debug("Kill trash at location: rof_01")
        self._char.kill_cs_trash("rof_01") #outside
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([603], self._char): return False
        Logger.debug("CS Trash: Teleporting to CS ENTRANCE")
        found = False
        templates = ["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char)
        if not found:
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_cs_entrance_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        if not self._pather.traverse_nodes([604], self._char): return False  #threshold=0.8 (ex 601)
        Logger.debug("Kill trash at location: rof_02")
        self._char.kill_cs_trash("rof_02") #inside
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        Logger.debug("CS Trash: Calibrated at CS ENTRANCE")
        if not self._entrance_hall(): return False
        Logger.debug("CS Trash: looping to PENTAGRAM")
        if not self._loop_pentagram("diablo_wp_pentagram_loop"): return False
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_TP", "DIA_NEW_PENT_2"]
        start_time = time.time()
        while not found and time.time() - start_time < 15:
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed("diablo_wp_pentagram_loop", self._char)
        if not found:
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_diablo_wp_pentagram_loop_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True


    #ARRIVE AT PENTAGRAM AFTER LOOP
    def _cs_pentagram(self) -> bool:
        self._pather.traverse_nodes([602], self._char, threshold=0.80, time_out=3)
        self._pather.traverse_nodes_fixed("dia_pent_rudijump", self._char) # move to TP
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


    #CLEAR TRASH BETWEEN PENTAGRAM & LAYOUT CHECK (clear_trash=1)
    def _trash_seals(self) -> bool:
        self._pather.traverse_nodes([602], self._char)
        self._pather.traverse_nodes_fixed("dia_trash_a", self._char)
        Logger.debug("A: Clearing trash betwen Pentagramm & Layoutcheck")
        self._char.kill_cs_trash("trash_a")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_Trash_A_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        if not self._loop_pentagram("dia_a1l_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info("A: finished clearing Trash at Seal & calibrated at PENTAGRAM")

        self._pather.traverse_nodes_fixed("dia_trash_b", self._char)
        Logger.debug("B: Clearing trash betwen Pentagramm & Layoutcheck")
        self._char.kill_cs_trash("trash_b")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_Trash_B_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        if not self._loop_pentagram("dia_b1s_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info("B: finished clearing Trash at Seal & calibrated at PENTAGRAM")
        
        self._pather.traverse_nodes_fixed("dia_trash_c", self._char)
        Logger.debug("C: Clearing trash betwen Pentagramm & Layoutcheck")
        self._char.kill_cs_trash("trash_c")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_Trash_C_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        if not self._loop_pentagram("dia_c1f_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info("C: finished clearing Trash at Seal & calibrated at PENTAGRAM")


    #CHECK SEAL LAYOUT
    def _layoutcheck(self, sealname:str, boss:str, static_layoutcheck:str, trash_location:str , calibration_node:str, calibration_threshold:str, confirmation_node:str, templates_primary:list[str], templates_confirmation:list[str]): 
        if sealname == "A":
            seal_layout1:str = "A1-L"
            seal_layout2:str = "A2-Y"
            params_seal1 = seal_layout1, [614], [615], [611], "dia_a1l_home", "dia_a1l_home_loop", [602], ["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], ["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"]
            params_seal2 = seal_layout2, [625], [626], [622], "dia_a2y_home", "dia_a2y_home_loop", [602], ["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], ["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"]
            threshold_primary=0.8
            threshold_confirmation=0.85
            threshold_confirmation2=0.8
            confirmation_node2=None
        elif sealname == "B":
            seal_layout2:str = "B1-S"
            seal_layout1:str = "B2-U"
            params_seal2 = seal_layout2, None, [634], [632], "dia_b1s_home", "dia_b1s_home_loop", [602], None, None, ["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"]
            params_seal1 = seal_layout1, None, [644], [640], "dia_b2u_home", "dia_b2u_home_loop", [602], None, None, ["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"]        
            confirmation_node2=[634]
            threshold_primary=0.8
            threshold_confirmation2=0.8
            threshold_confirmation=0.75 #B2-U check
        elif sealname == "C":
            seal_layout1:str = "C1-F"
            seal_layout2:str = "C2-G"
            params_seal1 = seal_layout1, [655], [652], [654], "dia_c1f_home", "dia_c1f_home_loop", [602], ["DIA_C1F_OPEN_NEAR"], ["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"], ["DIA_B2U2_16_OPEN", "DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"], ["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"]
            params_seal2 = seal_layout2, [661], [665], [665], "dia_c2g_home", "dia_c2g_home_loop", [602], ["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], ["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"]
            threshold_primary=0.8
            confirmation_node2=None
            threshold_confirmation=0.8
            threshold_confirmation2=0.8

        else:
            Logger.warning(sealname + ": something is wrong - cannot check layouts: Aborting run.")
            return False
        
        self._pather.traverse_nodes_fixed(static_layoutcheck, self._char)
        self._char.kill_cs_trash(trash_location) # this attack sequence increases layout check consistency, we loot when the boss is killed # removed, trying to speed up the LC    
        Logger.info(f"{sealname}: Checking Layout for "f"{boss}")
        if not calibration_node == None:
            if not self._pather.traverse_nodes(calibration_node, self._char, threshold=calibration_threshold,): return False
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_LC_" + sealname + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        #check1 using primary templates
        if not self._template_finder.search_and_wait(templates_primary, threshold =threshold_primary, time_out=0.5).valid:
            Logger.debug(f"{seal_layout1}: Layout_check step 1/2 - templates NOT found for "f"{seal_layout2}")
            #cross-check for confirmation
            if not confirmation_node == None:
                if not self._pather.traverse_nodes(confirmation_node, self._char, threshold=calibration_threshold,): return False
            if not self._template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation, time_out=0.5).valid:
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at" f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout1 + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            else:
                Logger.debug(f"{seal_layout1}: Layout_check step 2/2 - templates found for "f"{seal_layout1} - "+'\033[93m'+"all fine, proceeding with "f"{seal_layout1}"+'\033[0m')
                if not self._seal(*params_seal1): return False
        else:
            Logger.debug(f"{seal_layout2}: Layout_check step 1/2 - templates found for {seal_layout1}")
            #cross-check for confirmation
            if not confirmation_node2 == None:
                if not self._pather.traverse_nodes(confirmation_node2, self._char, threshold=calibration_threshold,): return False
            if not self._template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation2, time_out=0.5).valid:
                Logger.debug(f"{seal_layout2}: Layout_check step 2/2 - templates NOT found for "f"{seal_layout1} - "+'\033[94m'+"all fine, proceeding with "f"{seal_layout2}"+'\033[0m')
                if not self._seal(*params_seal2): return False
            else:
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at" f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout2 + "_LC_fail_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
        return True


#CLEAR SEAL
    def _seal(self, seal_layout:str, node_seal1:str, node_seal2:str, node_calibrate_to_pent:str, static_pent:str, static_loop_pent:str, node_calibrate_at_pent:str, seal1_opentemplates:list[str], seal1_closedtemplates:list[str], seal2_opentemplates:list[str], seal2_closedtemplates:list[str], ) -> bool:
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info(seal_layout +": Starting to clear Seal")
        ### CLEAR TRASH ###
        Logger.debug(seal_layout + "_01: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_01")
        Logger.debug(seal_layout + "_02: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_02")
        Logger.debug(seal_layout + "_03: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_03")
        ### APPROACH SEAL ###
        if not node_seal1 == None: 
            Logger.debug(seal_layout + "_seal1: Kill trash")
            self._char.kill_cs_trash(seal_layout + "_seal1")
            if not self._pather.traverse_nodes(node_seal1, self._char): return False # , time_out=3):
            if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1): return False
        else:
            Logger.debug(seal_layout + ": No Fake Seal for this layout, skipping")
        Logger.debug(seal_layout + "_seal2: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_seal2")
        if not self._pather.traverse_nodes(node_seal2, self._char): return False # , time_out=3):
        if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2): return False
        ### KILL BOSS ###
        if seal_layout == ("A1-L") or seal_layout == ("A2-Y"):
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
            self._char.kill_vizier(seal_layout)
        elif seal_layout == ("B1-S") or seal_layout == ("B2-U"):
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
            self._char.kill_deseis(seal_layout)
        elif seal_layout == ("C1-F") or seal_layout == ("C2-G"):
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
            self._char.kill_infector(seal_layout)
        else:
            Logger.warning(seal_layout + ": Error - no Boss known here - aborting run")
            return False
        ### GO HOME ###
        if not self._pather.traverse_nodes(node_calibrate_to_pent, self._char): return False # , time_out=3): # calibrating here brings us home with higher consistency.
        Logger.debug(seal_layout + ": Static Pathing to Pentagram")
        if not self._pather.traverse_nodes_fixed(static_pent, self._char): return False
        Logger.debug(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram(static_loop_pent): return False
        if not self._pather.traverse_nodes(node_calibrate_at_pent, self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True


    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        self._picked_up_items = False
        self.used_tps = 0
        if do_pre_buff: self._char.pre_buff()
        #Clear Trash in CS
        if self._config.char["kill_cs_trash"]: 
            if not self._river_of_flames_trash(): return False
        else:
            if not self._river_of_flames(): return False

        if not self._cs_pentagram(): return False      
        if self._config.char["kill_cs_trash"]: self._trash_seals()
        
        # Maintenance at Pentagram after Trash & clear Seal A: Vizier (to the left)
        if self._config.char["kill_cs_trash"]: self._char.kill_cs_trash("pent_before_a")
        if not self._pather.traverse_nodes([602], self._char): return False
        if self._config.char["cs_town_visits"]: self._cs_town_visit("A")
        if self._config.char["kill_cs_trash"] and do_pre_buff: self._char.pre_buff()
        if not self._layoutcheck("A", "Vizier", "dia_a_layout", "layoutcheck_a", [610620], 0.81 , None, ["DIA_A2Y_LAYOUTCHECK0", "DIA_A2Y_LAYOUTCHECK1", "DIA_A2Y_LAYOUTCHECK2", "DIA_A2Y_LAYOUTCHECK4", "DIA_A2Y_LAYOUTCHECK5", "DIA_A2Y_LAYOUTCHECK6"], ["DIA_A1L_LAYOUTCHECK0", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK4LEFT", "DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3","DIA_A1L_LAYOUTCHECK4RIGHT","DIA_A1L_LAYOUTCHECK5"]): return False
        
        # Maintenance at Pentagram after Trash & clear Seal B: DeSeis (to the top)
        self._char.kill_cs_trash("pent_before_b")
        if not self._pather.traverse_nodes([602] , self._char , time_out=3): return False
        if self._config.char["cs_town_visits"]: self._cs_town_visit("B")
        if do_pre_buff: self._char.pre_buff()
        if not self._layoutcheck("B", "De Seis", "dia_b_layout_bold", "layoutcheck_b", None, 0.78, [647], ["DIA_B1S_BOSS_CLOSED_LAYOUTCHECK1", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK2", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK3", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK4", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK5", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK6", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK7", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK8"],["DIA_B2U_LAYOUTCHECK2", "DIA_B2U_LAYOUTCHECK1", "DIA_B2U_LAYOUTCHECK2SMALL","DIA_B2U_LAYOUTCHECK3", "DIA_B2U_LAYOUTCHECK4", "DIA_B2U_LAYOUTCHECK5","DIA_B2U_LAYOUTCHECK6","DIA_B2U_LAYOUTCHECK7","DIA_B2U_LAYOUTCHECK8","DIA_B2U_LAYOUTCHECK9"]): return False    
        
        # Maintenance at Pentagram after Trash & clear Seal C: Infector (to the right)
        self._char.kill_cs_trash("pent_before_c")
        if not self._pather.traverse_nodes([602], self._char): return False
        if self._config.char["cs_town_visits"]: self._cs_town_visit("C")
        if do_pre_buff: self._char.pre_buff()
        if not self._layoutcheck("C", "Infector", "dia_c_layout_bold", "layoutcheck_c", [650660], 0.83, None, ["DIA_C2G_BOSS_CLOSED_LAYOUTCHECK1", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK4", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK5", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK2", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK3",], ["DIA_C1F_LAYOUTCHECK1", "DIA_C1F_LAYOUTCHECK2", "DIA_C1F_LAYOUTCHECK3"]): return False
        
        # Kill Diablo
        Logger.info("Waiting for Diablo to spawn")
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        self._char.kill_diablo() 
        wait(0.2, 0.3)
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_dia_kill_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        wait(0.5, 0.7)
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