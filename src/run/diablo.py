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

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Diablo")
        if not self._char.can_teleport():
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2)
        return Location.A4_DIABLO_WP
    
    def _cs_town_visit(self, location:str) -> bool: # WiZ addition for town visits to heal/clear debuffs/restock pots 
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
        while i < 3:
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1)+")") # try to select seal
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(i*0.5)
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid # check if seal is opened
            if found:
                Logger.info(seal_layout +": "'\033[92m'+"is open"+'\033[0m')
                break
            else:
                Logger.debug(seal_layout +": "'\033[91m'+"not open"+'\033[0m')
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
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/_failed_seal_{seal_layout}_{i}tries" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found

    # GET TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_TP", "DIA_NEW_PENT_TPTOP", "DIA_NEW_PENT_TPBOT"]
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
        if not self._pather.traverse_nodes([677], self._char): return False #, time_out=3): return False 
        Logger.debug("Kill trash at location: entrance_hall_01")
        self._char.kill_cs_trash("entrance_hall_01")
        self._picked_up_items |= self._pickit.pick_up_items(self._char) # Gets to door and checks starts attacks and picks up items
        self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self._char) # Moves to first open area
        Logger.debug("Kill trash at location: entrance_hall_02")
        self._char.kill_cs_trash("entrance_hall_02") # since theres probably a mob there just lands and attacks
        if not self._pather.traverse_nodes([670,671], self._char, time_out=3): #): return False # 
            Logger.info("CS Entrance: 671 might be blocked by a shrine, clicking left.")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/shrine_1before_671_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            wait(0.1, 0.2)
            mouse.press(button="left")
            wait(0.1, 0.2)
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/shrine_2after_671_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            if not self._pather.traverse_nodes([671], self._char): return False
        Logger.debug("Kill trash at location: entrance_hall_03")
        self._char.kill_cs_trash("entrance_hall_03") 
        self._picked_up_items |= self._pickit.pick_up_items(self._char) # moves back and forth to draw more enemies finishes em off picks up items.
        if not self._pather.traverse_nodes([671], self._char): return False # , time_out=3): # re centers it self
        self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self._char) # Moves to second open area
        
        templates = ["DIABLO_ENTRANCE_12", "DIABLO_ENTRANCE_13", "DIABLO_ENTRANCE_15", "DIABLO_ENTRANCE_16", "DIABLO_ENTRANCE_19", "DIABLO_ENTRANCE_18"] #Entrance 1 Refrences
        if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
            Logger.info("Entrance 2 Layout_check step 1/2: Entrance 1 templates NOT found")
            templates = ["DIABLO_ENTRANCE2_15", "DIABLO_ENTRANCE2_23", "DIABLO_ENTRANCE2_19","DIABLO_ENTRANCE2_17"] #Entrance 2 Refrences
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.info("Entrance 2 Layout_check step 2/2: Failed to determine the right Layout, trying to loop to pentagram to save the run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_entrance2_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return True
            else:
                Logger.info("Entrance 2 Layout_check step 2/2: Entrance 2 templates found - all fine, proceeding with Entrance 2")
                #if not self._entrance_2(): return False
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
                Logger.debug("Entrance 1 Layout_check step 2/2: Entrance 2 templates NOT found - all fine, proceeding with Entrance 1")
                #if not self._entrance_1(): return False
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
                Logger.debug("Entrance 1 Layout_check step 2/2: Failed to determine Layout, trying to loop to pentagram to save the run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_entrance1_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return True
        

    def _river_of_flames(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False # , time_out=3):
        Logger.debug("ROF: Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_pentagram", self._char)
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
        

    def _river_of_flames_trash(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False # , time_out=3):
        Logger.debug("ROF: Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        Logger.debug("Kill trash at location: rof_01")
        self._char.kill_cs_trash("rof_01") #outside
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        Logger.info("ROF: Teleporting to CS ENTRANCE")
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
        if not self._pather.traverse_nodes([601], self._char, threshold=0.8, time_out=3): #return False
            Logger.info("CS Entrance: 601 might be blocked by a shrine, clicking left.")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/shrine_1before_601_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            wait(0.1, 0.2)
            mouse.press(button="left")
            wait(0.1, 0.2)
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/shrine_2after_601_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            if not self._pather.traverse_nodes([601], self._char): return False
        Logger.debug("Kill trash at location: rof_02")
        self._char.kill_cs_trash("rof_02") #inside
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        Logger.info("ROF: Calibrated at CS ENTRANCE")
        if not self._entrance_hall(): return False
        Logger.info("CS Trash: looping to PENTAGRAM")
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_pentagram_loop", self._char)
        if not found:
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_pent_loop_after_trash_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True


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

    def _trash_seals(self) -> bool:
        self._pather.traverse_nodes([602], self._char)
        self._pather.traverse_nodes_fixed("dia_trash_a", self._char)
        Logger.debug("A: Clearing trash betwen Pentagramm & Layoutcheck")
        self._char.kill_cs_trash("trash_a")
        if not self._loop_pentagram("dia_a1l_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info("A: finished clearing Trash at Seal & calibrated at PENTAGRAM")

        self._pather.traverse_nodes_fixed("dia_trash_b", self._char)
        Logger.debug("B: Clearing trash betwen Pentagramm & Layoutcheck")
        self._char.kill_cs_trash("trash_b")
        if not self._loop_pentagram("dia_b1s_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info("B: finished clearing Trash at Seal & calibrated at PENTAGRAM")
        
        self._pather.traverse_nodes_fixed("dia_trash_c", self._char)
        Logger.debug("C: Clearing trash betwen Pentagramm & Layoutcheck")
        self._char.kill_cs_trash("trash_c")
        if not self._loop_pentagram("dia_c1f_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info("C: finished clearing Trash at Seal & calibrated at PENTAGRAM")


    def _seal_A1(self) -> bool:
        seal_layout = "A1-L"
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
        Logger.debug(seal_layout + "_fake: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Fake")
        if not self._pather.traverse_nodes([614], self._char): return False # , time_out=3):
        if not self._sealdance(["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], seal_layout + ": Fake", [614]): return False
        Logger.debug(seal_layout + "_boss: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Boss")
        if not self._pather.traverse_nodes([615], self._char): return False # , time_out=3):
        if not self._sealdance(["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"], seal_layout + ": Boss", [615]): return False
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss A (Vizier)")
        self._char.kill_vizier(seal_layout)
        ### GO HOME ###
        if not self._pather.traverse_nodes([611], self._char): return False # , time_out=3): # calibrating here brings us home with higher consistency.
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        if not self._pather.traverse_nodes_fixed("dia_a1l_home", self._char): return False
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_a1l_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True
    
    def _seal_A2(self) -> bool:
        seal_layout = "A2-Y"
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
        Logger.debug(seal_layout + "_fake: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Fake")
        if not self._pather.traverse_nodes([625], self._char): return False # , time_out=3): #recalibrate after loot & at seal
        if not self._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], seal_layout + ": Fake", [625]): return False
        self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self._char) #instead of traversing node 626 which causes issues
        Logger.debug(seal_layout + "_boss: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Boss")
        if not self._pather.traverse_nodes([626], self._char): return False # , time_out=3): #recalibrate after loot & at seal
        if not self._sealdance(["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"], seal_layout + ": Boss", [626]): return False
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss A (Vizier)")
        self._char.kill_vizier(seal_layout)
        ### GO HOME ###
        if not self._pather.traverse_nodes([622], self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        if not self._pather.traverse_nodes_fixed("dia_a2y_home", self._char): return False
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_a2y_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True


    def _seal_B1(self) -> bool: #define order for killing trash
        seal_layout = "B1-S"
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
        Logger.debug(seal_layout + "_boss: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Boss")
        if not self._pather.traverse_nodes([634], self._char): return False # , time_out=3): #recalibrate after loot & at seal
        self._sealdance(["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"], seal_layout + ": Boss", [634])
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss B (De Seis)")
        if not self._char.kill_deseis(seal_layout): return False
        ### GO HOME ###
        if not self._pather.traverse_nodes([633, 634], self._char): return False # , time_out=3): 
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        self._pather.traverse_nodes_fixed("dia_b1s_home", self._char)
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_b1s_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char , time_out=3): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_B2(self) -> bool:
        seal_layout = "B2-U"
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
        Logger.debug(seal_layout + "_boss: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Boss")
        if not self._pather.traverse_nodes([644], self._char): return False # , time_out=3): #recalibrate after loot & at seal
        self._sealdance(["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"], seal_layout + ": Boss", [644])
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss B (De Seis)")
        if not self._char.kill_deseis(seal_layout): return False
        ### GO HOME ###
        if not self._pather.traverse_nodes([640], self._char): return False # , time_out=3): # recalibrate after loot
        self._pather.traverse_nodes_fixed("dia_b2u_home", self._char)
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_b2u_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char , time_out=3): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True


    def _seal_C1(self) -> bool:
        seal_layout = "C1-F"
        Logger.info(seal_layout +": Starting to clear Seal")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        ### CLEAR TRASH ###
        Logger.debug(seal_layout + "_01: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_01")
        Logger.debug(seal_layout + "_02: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_02")
        Logger.debug(seal_layout + "_03: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_03")
        ### APPROACH SEAL ###        
        Logger.debug(seal_layout + "_fake: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Fake")
        if not self._pather.traverse_nodes([655], self._char): return False # , time_out=3):
        if not self._sealdance(["DIA_C1F_OPEN_NEAR"], ["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"], seal_layout + ": Fake", [655]): return False #ISSUE: getting stuck on 705 during sealdance(), reaching maxgamelength
        Logger.debug(seal_layout + " Boss: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Boss")
        if not self._pather.traverse_nodes([652], self._char): return False # , time_out=3):
        if not self._sealdance(["DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"], ["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"], seal_layout + ": Boss", [652]): return False
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss C (Infector)")
        self._char.kill_infector(seal_layout)
        ### GO HOME ###
        if not self._pather.traverse_nodes([654], self._char): return False # , time_out=3): # this node often is not found
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        self._pather.traverse_nodes_fixed("dia_c1f_home", self._char)
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_c1f_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_C2(self) -> bool:
        seal_layout = "C2-G"
        Logger.info(seal_layout +": Starting to clear Seal")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        ### CLEAR TRASH ###
        Logger.debug(seal_layout + "_01: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_01") #not needed for most AOE chars, done during layoutcheck, but could be usefull for other classes as entry to clear the full seal
        Logger.debug(seal_layout + "_02: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_02")
        Logger.debug(seal_layout + "_03: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_03")
        ### APPROACH SEAL ###
        Logger.debug(seal_layout + "_boss: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Boss")
        if not self._pather.traverse_nodes([662], self._char): return False # , time_out=3):
        if not self._sealdance(["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], seal_layout + ": Boss", [662]): return False
        ### KILL BOSS ###
        Logger.info(seal_layout + ": Kill Boss C (Infector)")
        self._char.kill_infector(seal_layout)
        Logger.debug(seal_layout + "_fake: Kill trash")
        self._char.kill_cs_trash(seal_layout + ": Fake")
        if not self._pather.traverse_nodes([665], self._char): return False # , time_out=3):  #recalibrate after loot & at seal
        if not self._sealdance(["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"], seal_layout + ": Fake", [665]): return False       
        ### GO HOME ###
        if not self._pather.traverse_nodes([665], self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": Static Pathing to Pentagram")
        self._pather.traverse_nodes_fixed("dia_c2g_home", self._char)
        Logger.info(seal_layout + ": Looping to PENTAGRAM")
        if not self._loop_pentagram("dia_c2g_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True


    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        self._picked_up_items = False
        self.used_tps = 0
        if do_pre_buff: self._char.pre_buff()
        #Clear Trash in CS
        if self._config.char["kill_cs_trash"]: 
            Logger.info("Clearing CS trash")
            if not self._river_of_flames_trash(): return False
        else:
            if not self._river_of_flames(): return False
        if not self._cs_pentagram(): return False
        
        # CLEAR  Trash between Seals & LC
        if self._config.char["kill_cs_trash"]: self._trash_seals()

        # Seal A: Vizier (to the left)
        if self._config.char["kill_cs_trash"]: self._char.kill_cs_trash("pent_before_a") # not needed if seals exectued in order A-B-C and clear_trash = 0
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        if self._config.char["cs_town_visits"]: self._cs_town_visit("A") #buy pots and stash items
        if self._config.char["kill_cs_trash"] and do_pre_buff: self._char.pre_buff()
        self._pather.traverse_nodes_fixed("dia_a_layout", self._char)
        #self._char.kill_cs_trash("layoutcheck_a") # this attack sequence increases layout check consistency, we loot when the boss is killed # removed, trying to speed up the LC
        Logger.info("A: Checking Layout for Vizier")
        if not self._pather.traverse_nodes([619], self._char): return False # , time_out=3): # HEUREKA, I merged the templates of both A1L and A2Y into this node. So it should calibrate independent of layout.
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_layout_check_A_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        templates = ["DIA_A2Y_LAYOUTCHECK0", "DIA_A2Y_LAYOUTCHECK1", "DIA_A2Y_LAYOUTCHECK2", "DIA_A2Y_LAYOUTCHECK4", "DIA_A2Y_LAYOUTCHECK5", "DIA_A2Y_LAYOUTCHECK6"] # We check for A2Y templates first, they are more distinct, but we still have a 10% failure rate here amongst 100s of runs. Mostly it is related to NOT perfectly arriving at the layout check position (overshooting by 1 teleport) - maybe looping could help here?. The ratio of seals is typically skewed towards A1L, due to failing here.
        if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
            Logger.debug("A1-L: Layout_check step 1/2 - A2Y templates NOT found")
            templates = ["DIA_A1L_LAYOUTCHECK0","DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK4LEFT","DIA_A1L_LAYOUTCHECK4RIGHT","DIA_A1L_LAYOUTCHECK5"]
            if not self._template_finder.search_and_wait(templates, threshold=0.85, time_out=0.5).valid:
                Logger.debug('\033[91m'+"A1-L: Layout_check step 2/2 - Failed to determine the right Layout at A (Vizier) - aborting run"+'\033[0m') #this also happens approx (7%) of the times tested amongst 100s of runs
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_A1L_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            else:
                Logger.debug('\033[93m'+"A1-L: Layout_check step 2/2 - A1L templates found - all fine, proceeding with A1L"+'\033[0m')
                if not self._seal_A1(): return False
        else:
            Logger.debug("A2-Y: Layout_check step 1/2 - A2Y templates found")
            templates = ["DIA_A1L_LAYOUTCHECK0","DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK4LEFT","DIA_A1L_LAYOUTCHECK4RIGHT","DIA_A1L_LAYOUTCHECK5"]
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug('\033[94m'+"A2-Y: Layout_check step 2/2 - A1L templates NOT found - all fine, proceeding with A2Y"+'\033[0m')
                if not self._seal_A2(): return False
            else:
                Logger.debug('\033[91m'+"A2-Y: Layout_check step 2/2 - Failed to determine the right Layout at A (Vizier) - aborting run"+'\033[0m')
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_A2Y_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False

        # Seal B: De Seis (to the top)
        self._char.kill_cs_trash("pent_before_b")
        if not self._pather.traverse_nodes([602] , self._char , time_out=3): return False
        if self._config.char["cs_town_visits"]: self._cs_town_visit("B") #buy pots and stash items
        if do_pre_buff: self._char.pre_buff()
        self._pather.traverse_nodes_fixed("dia_b_layout_bold", self._char)
        #self._char.kill_cs_trash("layoutcheck_b") # this attack sequence increases layout check consistency
        Logger.debug("B: Checking Layout for De Seis")
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_layout_check_B_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        templates = ["DIA_B1S_BOSS_CLOSED_LAYOUTCHECK1", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK2", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK3"] #We check for B1S templates first, they are more distinct
        if self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
            Logger.debug("B1-S: Layout_check step 1/2 - B1S templates found")
            if not self._pather.traverse_nodes([634], self._char): return False # , time_out=3):
            templates = ["DIA_B2U_LAYOUTCHECK1", "DIA_B2U_LAYOUTCHECK2", "DIA_B2U_LAYOUTCHECK2SMALL","DIA_B2U_LAYOUTCHECK3", "DIA_B2U_LAYOUTCHECK4", "DIA_B2U_LAYOUTCHECK5","DIA_B2U_LAYOUTCHECK6","DIA_B2U_LAYOUTCHECK7","DIA_B2U_LAYOUTCHECK8","DIA_B2U_LAYOUTCHECK9"]
            if self._template_finder.search_and_wait(templates, threshold=0.75, time_out=0.5).valid:
                Logger.debug("B1-S: Layout_check step 2/2: Failed to determine the right Layout at B (De Seis) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_B1S_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
            else:
                Logger.debug('\033[93m'+"B1-S: Layout_check step 2/2 - B2U templates NOT found - all fine, proceeding with B1S"+'\033[0m')
                if not self._seal_B1(): return False
        else:
            Logger.debug("B2-U: Layout_check step 1/2: B1S templates NOT found")
            if not self._pather.traverse_nodes([647], self._char): return False # , time_out=3): #seems to be B2U, so we are calibrating at a node of B2U, just to be safe to see the right templates
            templates = ["DIA_B2U_LAYOUTCHECK1", "DIA_B2U_LAYOUTCHECK2", "DIA_B2U_LAYOUTCHECK2SMALL","DIA_B2U_LAYOUTCHECK3", "DIA_B2U_LAYOUTCHECK4", "DIA_B2U_LAYOUTCHECK5","DIA_B2U_LAYOUTCHECK6","DIA_B2U_LAYOUTCHECK7","DIA_B2U_LAYOUTCHECK8","DIA_B2U_LAYOUTCHECK9"]
            if self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug('\033[94m'+"B2-U: Layout_check step 2/2 - B2U templates found - all fine, proceeding with B2U"+'\033[0m')
                if not self._seal_B2(): return False
            else:
                Logger.debug("B2-U: Layout_check step 2/2 - Failed to determine the right Layout at B (De Seis) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_B2U_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False
        
        # Seal C: Infector (to the right)
        self._char.kill_cs_trash("pent_before_c")
        if not self._pather.traverse_nodes([602], self._char): return False # , time_out=3):
        if self._config.char["cs_town_visits"]: self._cs_town_visit("C") #buy pots and stash items
        if do_pre_buff: self._char.pre_buff()
        self._pather.traverse_nodes_fixed("dia_c_layout_bold", self._char)
        #self._char.kill_cs_trash("layoutcheck_c") # this attack sequence increases layout check consistency
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
                Logger.debug('\033[93m'+"C1-F: Layout_check step 2/2 - C1F templates found - all fine, proceeding with C1F"+'\033[0m')
                if not self._seal_C1(): return False
        else:
            Logger.debug("C2-G: Layout_check step 1/2 - C2G templates found")
            templates = ["DIA_C1F_LAYOUTCHECK1", "DIA_C1F_LAYOUTCHECK2", "DIA_C1F_LAYOUTCHECK3"]
            if not self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.5).valid:
                Logger.debug('\033[94m'+"C2-G: Layout_check step 2/2 - C1F templates NOT found - all fine, proceeding with C2G"+'\033[0m')
                if not self._seal_C2(): return False
            else:
                Logger.debug("C2-G: Layout_check step 2/2 - Failed to determine the right Layout at C (Infector) - aborting run")
                if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_C2GS_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
                return False

        # Diablo
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
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)

### ISSUE LOG ###

# stash or shrine located near a node or bossfight will make botty just try to click the stash
# Better Looping Home consistency at A & C (if a tombstone stash is on its way, the path gets displaced which might lead to missing the pentagram)
# We could consider a function get_nearest_node() or a path home from where we started to loot to not get off-track after looting trash.

# add a new param: clear_seals = 1