from distutils.command.build import build
import cv2
import time
import keyboard
from automap_finder import toggle_automap
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from item.pickit import PickIt
import template_finder
from town.town_manager import TownManager, A4
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import convert_abs_to_monitor, convert_monitor_to_screen, grab
from ui_manager import detect_screen_object, ScreenObjects
from ui import skills, loading, waypoint
from inventory import belt, personal

class Diablo:

    name = "run_diablo"

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
        self._picked_up_items = False
        self.used_tps = 0
        self._curr_loc: bool | Location = Location.A4_TOWN_START
        self._runs = runs

        
    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 4:
            if Config().general["use_automap_navigation"] == 1 : toggle_automap(False) # just to ensure we switch off Automap, so it does not interfere with sealcheck
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1)+")")
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, timeout=0.1, telekinesis=True)
            wait(i*1)
            found = template_finder.search_and_wait(seal_opentemplates, threshold=0.75, timeout=0.1).valid
            if found:
                Logger.info(seal_layout +": is open - "+'\033[92m'+" open"+'\033[0m')
                break
            else:
                Logger.debug(seal_layout +": is closed - "+'\033[91m'+" closed"+'\033[0m')
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 1:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " times, trying to kill trash now")
                    Logger.debug("Sealdance: Kill trash at location: sealdance")
                    self._char.kill_cs_trash("sealdance")
                    wait(i*0.5)
                    Logger.debug("Sealdance: Recalibrating at seal_node")
                    if not self._pather.traverse_nodes_automap(seal_node, self._char): return False
                else:
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = convert_abs_to_monitor([50 * direction, direction])
                    self._char.move((x_m, y_m), force_move=True)
                i += 1
        if Config().general["info_screenshots"] and not found: cv2.imwrite(f"./log/screenshots/info/info_failed_seal_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        return found


    def approach(self, start_loc: Location) -> bool | Location:
        Logger.info("Run Diablo")
        if not self._char.capabilities.can_teleport_natively or self._char.capabilities.can_teleport_with_charges:
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        waypoint.use_wp("River of Flame")
        return Location.A4_DIABLO_WP

      
    def battle(self, do_pre_buff: bool) -> bool | tuple[Location, bool]:
        self._picked_up_items = False
        self.used_tps = 0
        if do_pre_buff: self._char.pre_buff()
        
        ##############
        # WP to PENT #
        ##############
        
        if not self._pather.traverse_nodes([600], self._char): return False #not using automap works better here
        Logger.debug("ROF: Calibrated at WAYPOINT")
                
        self._pather.traverse_nodes_fixed("dia_wp_cs-e", self._char) #Traverse River of Flame (no chance to traverse w/o fixed, there is no reference point between WP & CS Entrance)
        toggle_automap(False) # just to be safe
        if not self._pather.traverse_nodes_automap([1601], self._char): return False # Calibrate at CS Entrance
        Logger.debug("ROF: Calibrated at CS ENTRANCE")
        
        #make leecher TP (make param for it): DIA_CS_LEECHER_TP=1
        #Logger.debug("CS: OPEN LEECHER TP AT ENTRANCE")
        #self._char.kill_cs_trash("cs_entrance") #clear the area aound TP #DIA_CLEAR_TRASH=1 , DIA_CS_LEECHER_TP=1
        #if not skills.has_tps():
        #    Logger.warning("CS: failed to open TP, you should buy new TPs!")
        #    self.used_tps += 20
        #mouse.click(button="right")
                
        #decision if we go walking and clear trash
        #<kill trash up to pent part>

        #or we go fast and directly tp pentagram
        Logger.debug("ROF: Teleporting directly to PENTAGRAM")
        self._pather.traverse_nodes_fixed("dia_cs-e_pent", self._char) #Skip killing CS Trash & directly go to PENT, thereby revelaing key templates
        if not self._pather.traverse_nodes_automap([1600], self._char): return False # calibrate at Pentagram
        Logger.info("CS: Calibrated at PENTAGRAM")
 
        ##########
        # Seal A #
        ##########

        # Settings
        static_layoutcheck = "dia_am_lc_a"
        sealname = "A"
        boss = "Vizier"
        seal_layout1= "A1-L"
        seal_layout2= "A2-Y"

        calibration_node = [1620]
        calibration_threshold = 0.8
        
        templates_primary= ["DIA_AM_A2Y"]
        threshold_primary= 0.8
                
        templates_confirmation= ["DIA_AM_A1L"]
        confirmation_node= None 
        confirmation_node2=None
        threshold_confirmation= 0.8
        threshold_confirmation2= 0.8
  
        ###############
        # Layoutcheck #
        ###############
        
        #if do_pre_buff: self._char.pre_buff() #only for cs_kill_trash
        self._char.kill_cs_trash("pent_before_a") # Clear Pentagram 
        self._pather.traverse_nodes_automap([1620], self._char) # Go to Layout Check A
        self._char.kill_cs_trash("layoutcheck_a") # Clear Trash & Loot at Layout Check
        Logger.debug("==============================")
        Logger.debug(f"{sealname}: Checking Layout for "f"{boss}")
        
        if not calibration_node == None:
            if not self._pather.traverse_nodes_automap(calibration_node, self._char, threshold=calibration_threshold,): return False
        
        toggle_automap(True)
        if not template_finder.search_and_wait(templates_primary, threshold =threshold_primary, timeout=0.2).valid: # check1 using primary templates
            toggle_automap(False)
            Logger.debug(f"{seal_layout1}: Layout_check step 1/2 - templates NOT found for "f"{seal_layout2}")
        
            if not confirmation_node == None: # cross-check for confirmation
                if not self._pather.traverse_nodes_automap(confirmation_node, self._char, threshold=calibration_threshold, toggle_map=True): return False
        
            toggle_automap(True)
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation, timeout=0.2).valid:
                toggle_automap(False)
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at " f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                wait(5)
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout1 + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
        
            else:
                Logger.info(f"{seal_layout1}: Layout_check step 2/2 - templates found for "f"{seal_layout1} - "+'\033[93m'+"all fine, proceeding with "f"{seal_layout1}"+'\033[0m')
                
                ###################
                # Clear Seal A1-L #
                ###################
                
                #Settings
                seal_layout = seal_layout1
                node_seal1_automap=[1621] # Fake
                node_seal2_automap=[1622] # Boss
                seal1_opentemplates=["DIA_A1L2_14_OPEN"] # Fake
                seal1_closedtemplates=["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"] # Fake
                seal2_opentemplates=["DIA_A1L2_5_OPEN"] # Boss
                seal2_closedtemplates=["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"] # Boss
                
                #SEAL
                toggle_automap(False) # just to be safe
                Logger.info(seal_layout +": Starting to pop seals")
                if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char): return False # Calibrate at Fake seal 
                if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1_automap): return False # Open Fake seal
                if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char): return False # Calibrate at Boss seal
                if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2_automap): return False # Open Boss Seal
                Logger.debug(seal_layout + ": Kill Boss A (Vizier)") 
                self._char.kill_vizier_automap(seal_layout) # Kill Boss
                Logger.debug(seal_layout + ": Traversing back to Pentagram")
                if not self._pather.traverse_nodes_automap([1600], self._char): return False # go to Pentagram
                Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
                
        
        else:
            Logger.debug(f"{seal_layout2}: Layout_check step 1/2 - templates found for {seal_layout1}")
        
            if not confirmation_node2 == None: # cross-check for confirmation
                if not self._pather.traverse_nodes_automap(confirmation_node2, self._char, threshold=calibration_threshold,): return False
            
            toggle_automap(True)
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation2, timeout=0.2).valid:
                toggle_automap(False)
                Logger.info(f"{seal_layout2}: Layout_check step 2/2 - templates NOT found for "f"{seal_layout1} - "+'\033[96m'+"all fine, proceeding with "f"{seal_layout2}"+'\033[0m')
                
                ###################
                # Clear Seal A2-Y #
                ###################
                
                #Settings
                seal_layout = seal_layout2
                node_seal1_automap=[1620] # Fake
                node_seal2_automap=[1625] # Boss
                seal1_opentemplates=["DIA_A2Y4_29_OPEN"] # Fake
                seal1_closedtemplates=["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"] # Fake
                seal2_opentemplates=["DIA_A2Y4_36_OPEN"] # Boss
                seal2_closedtemplates=["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"] # Boss
                
                #SEAL
                toggle_automap(False) # just to be safe
                Logger.info(seal_layout +": Starting to pop seals")
                if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char): return False # Calibrate at Fake seal 
                if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1_automap): return False # Open Fake seal
                if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char): return False # Calibrate at Boss seal 
                if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2_automap): return False # Open Boss seal
                Logger.debug(seal_layout + ": Kill Boss A (Vizier)")
                self._char.kill_vizier_automap(seal_layout)
                Logger.debug(seal_layout + ": Traversing back to Pentagram")
                if not self._pather.traverse_nodes_automap([1600], self._char): return False
                Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
                

            else:
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at " f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                wait(5)
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout2 + "_LC_fail_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
    
        
        
        ##########
        # Seal B #
        ##########

        # Settings
        static_layoutcheck = "dia_am_lc_b"
        sealname = "B"
        boss = "De Seis"
        seal_layout1= "B2-U"
        seal_layout2= "B1-S"

        calibration_node = [1630]
        calibration_threshold = 0.78
        
        templates_primary= ["DIA_AM_B1S"]
        threshold_primary= 0.75
                
        templates_confirmation= ["DIA_AM_B2U"]
        confirmation_node=[1630] 
        confirmation_node2=None
        threshold_confirmation= 0.75
        threshold_confirmation2= 0.75

        #################
        # Layoutcheck B #
        #################
        
        self._char.kill_cs_trash("pent_before_b")
        if do_pre_buff: self._char.pre_buff()
        if not self._pather.traverse_nodes_automap(calibration_node, self._char, threshold=calibration_threshold, toggle_map=True): return False
        self._char.kill_cs_trash("layoutcheck_b")
        Logger.debug("==============================")
        Logger.debug(f"{sealname}: Checking Layout for "f"{boss}")
        
        if not calibration_node == None:
            if not self._pather.traverse_nodes_automap(calibration_node, self._char, threshold=calibration_threshold, toggle_map=True): return False
        
        toggle_automap(True)
        if not template_finder.search_and_wait(templates_primary, threshold =threshold_primary, timeout=0.2).valid: #check1 using primary templates
            toggle_automap(False)
            Logger.debug(f"{seal_layout1}: Layout_check step 1/2 - templates NOT found for "f"{seal_layout2}")
            
            if not confirmation_node == None:#cross-check for confirmation
                if not self._pather.traverse_nodes_automap(confirmation_node, self._char, threshold=calibration_threshold, toggle_map=True): return False

            toggle_automap(True)
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation, timeout=0.2).valid:
                toggle_automap(False)
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at " f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                wait(5)
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout1 + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
        
            else:
                Logger.info(f"{seal_layout1}: Layout_check step 2/2 - templates found for "f"{seal_layout1} - "+'\033[93m'+"all fine, proceeding with "f"{seal_layout1}"+'\033[0m')
                
                ###################
                # Clear Seal B2-U #
                ###################
                
                #Settings
                seal_layout = seal_layout1
                node_seal1_automap=None #Fake
                node_seal2_automap=[1635] #Boss
                seal1_opentemplates=None
                seal1_closedtemplates=None
                seal2_opentemplates=["DIA_B2U2_16_OPEN"]
                seal2_closedtemplates=["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"]

                #SEAL
                toggle_automap(False) # just to be safe
                Logger.info(seal_layout +": Starting to pop seals")
                if node_seal1_automap is not None:
                    if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char): return False
                    if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1_automap): return False
                if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char): return False
                if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2_automap): return False
                Logger.debug(seal_layout + ": Kill Boss B (DeSeis)")
                self._char.kill_deseis_automap(seal_layout)
                Logger.debug(seal_layout + ": Traversing back to Pentagram")
                if not self._pather.traverse_nodes_automap([1600], self._char): return False
                Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")   
        
        else:
            Logger.debug(f"{seal_layout2}: Layout_check step 1/2 - templates found for {seal_layout2}")
        
            if not confirmation_node2 == None: #cross-check for confirmation
                if not self._pather.traverse_nodes_automap(confirmation_node2, self._char, threshold=calibration_threshold, toggle_map=True): return False
            
            toggle_automap(True)
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation2, timeout=0.2).valid:
                toggle_automap(False)
                Logger.info(f"{seal_layout2}: Layout_check step 2/2 - templates NOT found for "f"{seal_layout1} - "+'\033[96m'+"all fine, proceeding with "f"{seal_layout2}"+'\033[0m')

                ###################
                # Clear Seal B1-S #
                ###################
                
                #Settings
                seal_layout = seal_layout2
                node_seal1_automap=None #Fake
                node_seal2_automap=[1631] #Boss
                seal1_opentemplates=None
                seal1_closedtemplates=None
                seal2_opentemplates=["DIA_B1S2_23_OPEN"]
                seal2_closedtemplates=["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"]
                
                #SEAL
                toggle_automap(False) # just to be safe
                Logger.info(seal_layout +": Starting to pop seals")
                if node_seal1_automap is not None:
                    if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char): return False
                    if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1_automap): return False
                if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char): return False
                if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2_automap): return False
                Logger.debug(seal_layout + ": Kill Boss B (DeSeis)")
                self._char.kill_deseis_automap(seal_layout)
                Logger.debug(seal_layout + ": Traversing back to Pentagram")
                if not self._pather.traverse_nodes_automap([1600], self._char): return False
                Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")

            else:
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at " f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                wait(5)
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout2 + "_LC_fail_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
  

        ##########
        # Seal C #
        ##########

        # Settings
        static_layoutcheck = "dia_am_lc_c"
        sealname = "C"
        boss = "Infector"
        seal_layout1= "C1-F"
        seal_layout2= "C2-G"

        calibration_node = [1640]
        calibration_threshold = 0.83
        
        templates_primary= ["DIA_AM_C2G"]
        threshold_primary= 0.75
                
        templates_confirmation= ["DIA_AM_C1F"]
        confirmation_node= None 
        confirmation_node2=None
        threshold_confirmation= 0.75
        threshold_confirmation2= 0.75

        ##################
        # Layoutcheck  C #
        ##################
        
        self._char.kill_cs_trash("pent_before_c")
        if do_pre_buff: self._char.pre_buff()
        self._pather.traverse_nodes_fixed(static_layoutcheck, self._char) # could optionally be a traverse walking, as the node is visible & defined based on corner_L and pentagram
        self._char.kill_cs_trash("layoutcheck_a")
        Logger.debug("===============================")
        Logger.debug(f"{sealname}: Checking Layout for "f"{boss}")
        
        if not calibration_node == None:
            if not self._pather.traverse_nodes_automap(calibration_node, self._char, threshold=calibration_threshold,): return False
        
        toggle_automap(True)
        if not template_finder.search_and_wait(templates_primary, threshold =threshold_primary, timeout=0.2).valid: #check1 using primary templates
            toggle_automap(False)
            Logger.debug(f"{seal_layout1}: Layout_check step 1/2 - templates NOT found for "f"{seal_layout2}")
        
            if not confirmation_node == None:#cross-check for confirmation
                if not self._pather.traverse_nodes_automap(confirmation_node, self._char, threshold=calibration_threshold, toggle_map=True): return False
        
            toggle_automap(True)
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation, timeout=0.2).valid:
                toggle_automap(False)
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at " f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                wait(5)
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout1 + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
        
            else:
                Logger.info(f"{seal_layout1}: Layout_check step 2/2 - templates found for "f"{seal_layout1} - "+'\033[93m'+"all fine, proceeding with "f"{seal_layout1}"+'\033[0m')
                
                ###################
                # Clear Seal C1-F #
                ###################

                #Settings
                seal_layout = seal_layout1
                node_seal1_automap=[1641] #Fake
                node_seal2_automap=[1642] #Boss
                seal1_opentemplates=["DIA_C1F_OPEN_NEAR"]
                seal1_closedtemplates=["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"]
                seal2_opentemplates=["DIA_B2U2_16_OPEN", "DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"]
                seal2_closedtemplates=["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"]
                
                #SEAL
                toggle_automap(False) # just to be safe
                Logger.info(seal_layout +": Starting to pop seals")
                if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char): return False
                if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1_automap): return False
                if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char): return False
                if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2_automap): return False
                Logger.debug(seal_layout + ": Kill Boss C (Infector)")
                self._char.kill_infector_automap(seal_layout)
                Logger.debug(seal_layout + ": Traversing back to Pentagram")
                if not self._pather.traverse_nodes_automap([1600], self._char): return False
                Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")     
        
        else:
            Logger.debug(f"{seal_layout2}: Layout_check step 1/2 - templates found for {seal_layout1}")
        
            if not confirmation_node2 == None: #cross-check for confirmation
                if not self._pather.traverse_nodes_automap(confirmation_node2, self._char, threshold=calibration_threshold,): return False
            
            toggle_automap(True)
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation2, timeout=0.2).valid:
                toggle_automap(False)
                Logger.info(f"{seal_layout2}: Layout_check step 2/2 - templates NOT found for "f"{seal_layout1} - "+'\033[96m'+"all fine, proceeding with "f"{seal_layout2}"+'\033[0m')

                ###################
                # Clear Seal C2-G #
                ###################
                
                #Settings
                seal_layout = seal_layout2
                node_seal1_automap=[1645] #Fake
                node_seal2_automap=[1646] #Boss
                seal1_opentemplates=["DIA_C2G2_21_OPEN"]
                seal1_closedtemplates=["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"]  
                seal2_opentemplates=["DIA_C2G2_7_OPEN"]
                seal2_closedtemplates=["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"]

                #SEAL
                toggle_automap(False) # just to be safe
                Logger.info(seal_layout +": Starting to pop seals")
                if not self._pather.traverse_nodes_automap(node_seal1_automap, self._char): return False
                if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1_automap): return False
                if not self._pather.traverse_nodes_automap(node_seal2_automap, self._char): return False
                if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2_automap): return False
                Logger.debug(seal_layout + ": Kill Boss C (Infector)")
                self._char.kill_infector_automap(seal_layout)
                Logger.debug(seal_layout + ": Traversing back to Pentagram")
                if not self._pather.traverse_nodes_automap([1600], self._char): return False
                Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")

            else:
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at " f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                wait(5)
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout2 + "_LC_fail_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
 
        ##########
        # Diablo #
        ##########
  
        Logger.info("Waiting for Diablo to spawn")
        if not self._pather.traverse_nodes_automap([1600], self._char): return False
        self._char.kill_diablo()
        self._picked_up_items |= self._pickit.pick_up_items(char=self._char)
        wait(0.5, 0.7)
        return (Location.A4_DIABLO_END, self._picked_up_items)

        #############
        # TODO LIST #
        #############
        
        # complete the remaing templates for each node in pather.py -> slows down automap
        # add walkadin pathing (Seal B is teleporting a lot right now)
        # rework automap shrine detection -> switched templates
        # recalibrate after looting bosses, you get carried away in one direction whilst pickit, losing the second direction if there were mobs