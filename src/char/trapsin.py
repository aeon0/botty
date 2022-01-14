import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait, rotate_vec, unit_vector
import random
from typing import Tuple
from pather import Location, Pather
import numpy as np
import cv2 #for Diablo
from item.pickit import PickIt #for Diablo



class Trapsin(IChar):
    def __init__(self, skill_hotkeys, char_config, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather, pickit: PickIt):
        Logger.info("Setting up Trapsin")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo
        self._pather = pather

    def pre_buff(self):
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        if self._skill_hotkeys["fade"]:
            keyboard.send(self._skill_hotkeys["fade"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["shadow_warrior"]:
            keyboard.send(self._skill_hotkeys["shadow_warrior"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["burst_of_speed"]:
            keyboard.send(self._skill_hotkeys["burst_of_speed"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)

    def _debuff(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["cloak_of_shadows"]:
            keyboard.send(self._skill_hotkeys["cloak_of_shadows"])
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
        def atk(num: int):
            for _ in range(num):
                mouse.press(button="right")
                wait(0.20)
                mouse.release(button="right")
                wait(0.15)
        atk(1)
        if self._skill_hotkeys["mind_blast"]:
            keyboard.send(self._skill_hotkeys["mind_blast"])
        atk(2)

    def _left_attack(self, cast_pos_abs: Tuple[float, float], spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.2, 0.3)
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)


    def _right_attack(self, cast_pos_abs: Tuple[float, float], spray: float = 10):
        keyboard.send(self._skill_hotkeys["lightning_sentry"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        def atk(num: int):
            for _ in range(num):
                mouse.press(button="right")
                wait(0.20)
                mouse.release(button="right")
                wait(0.15)
        atk(4)
        keyboard.send(self._skill_hotkeys["death_sentry"])
        atk(1)
    
    def kill_summoner(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_arc"] / 2))
        cast_pos_abs = [0, 0]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
        wait(0.5, 1)
        return True
    
    def kill_pindle(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_pindle"] / 2))
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 11)
            self._left_attack(cast_pos_abs, 11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        if self.can_teleport():
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, force_tp=True)
        return True

    def kill_eldritch(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_eldritch"] / 2))
        eld_pos_abs = self._screen.convert_screen_to_abs(self._config.path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 90)
            self._left_attack(cast_pos_abs, 90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        if self.can_teleport():
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=0.6, force_tp=True)
        return True

    def kill_shenk(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_shenk"] / 2))
        shenk_pos_abs = self._pather.find_abs_node_pos(149, self._screen.grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = self._screen.convert_screen_to_abs(self._config.path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 90)
            self._left_attack(cast_pos_abs, 90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_len = max(1, int(self._char_config["atk_len_nihlatak"] / 2))
        for i in range(atk_len):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is None:
                return False
            cast_pos_abs = np.array([nihlatak_pos_abs[0] * 0.9, nihlatak_pos_abs[1] * 0.9])
            self._left_attack(cast_pos_abs, 90)
            self._right_attack(cast_pos_abs, 90)
            # Do some tele "dancing" after each sequence
            if i < atk_len - 1:
                rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                self.move(pos_m)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True
    #-------------------------------------------------------------------------------#
    # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
    #-------------------------------------------------------------------------------#

    # GET TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False

        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_TP"]  #"DIA_NEW_PENT_3", "DIA_NEW_PENT_5 -> if these templates are found, you cannot calibrate at [602] #"DIA_NEW_PENT_6", 
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed(path, self)
        if not found:
            #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True

    # OPEN SEALS
    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 6:
            # try to select seal
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1) + " of 7)")
            self.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
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
                    self.kill_cs_trash()
                    self._picked_up_items |= self._pickit.pick_up_items(self)
                    wait(i*0.5) #let the hammers clear & check the template -> the more tries, the longer the wait
                    if not self._pather.traverse_nodes(seal_node, self): return False # re-calibrate at seal node
                else:
                    # do a little random hop & try to click the seal
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, direction]) #50 *  removed the Y component - we never want to end up BELOW the seal (any curse on our head will obscure the template check)
                    self.move((x_m, y_m), force_move=True)
                i += 1
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/_failed_seal_{seal_layout}_{i}tries" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found
        
    def kill_cs_trash_pentagram(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_cs_trashmobs"] / 2))
        cast_pos_abs = [0, 0]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
        return True
    
    def kill_cs_trash(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_cs_trashmobs"] / 2))
        cast_pos_abs = [0, 0]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
        return True
    
    def kill_vizier(self, seal_layout: str) -> bool: 
        #nodes1: list[int], nodes2: list[int]) -> bool:
        if seal_layout== "A1-L":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            #self.kill_cs_trash() #done during sealcheck
            #self._picked_up_items |= self._pickit.pick_up_items(self) # not needed, we loot after vizier
            if not self._pather.traverse_nodes([611], self): return False
            if not self._pather.traverse_nodes([612, 613], self): return False
            self.kill_cs_trash()
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            if not self._sealdance(["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], seal_layout + "-Fake", [614]): return False
            if not self._pather.traverse_nodes([613, 615], self): return False
            if not self._sealdance(["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"], seal_layout + "-Boss", [615]): return False
            if not self._pather.traverse_nodes([612], self): return False
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
            atk_len = max(1, int(self._char_config["atk_len_diablo_vizier"]))
            cast_pos_abs = [0, 0]
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([611], self)
            if 2 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([610], self)
            if 1 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            wait(0.5, 1)
            ### LOOT ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([611], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([611], self): return False # calibrating here brings us home with higher consistency.
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            if not self._pather.traverse_nodes_fixed("dia_a1l_home", self): return False
            Logger.info(seal_layout + ": Looping to Pentagram")
            if not self._loop_pentagram("dia_a1l_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "A2-Y":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([622], self): return False
            self.kill_cs_trash() #could be skipped to be faster, but helps clearing tempaltes at the calibration node 622 for returning home
            if not self._pather.traverse_nodes([623, 624], self): return False
            self.kill_cs_trash()
            if not self._pather.traverse_nodes([625], self): return False
            if not self._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], seal_layout + "-Fake", [625]): return False
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            if not self._sealdance(["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"], seal_layout + "-Boss", [626]): return False
            if not self._pather.traverse_nodes([627, 622], self): return False
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
            atk_len = max(1, int(self._char_config["atk_len_diablo_vizier"]))
            cast_pos_abs = [0, 0]
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([623], self)
            if 2 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([624], self)
            if 1 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            wait(0.5, 1)
            ### LOOT ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([623], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([622], self): return False
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_a2y_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_deseis(self, seal_layout: str) -> bool: 
        #nodes1: list[int], nodes2: list[int], nodes3: list[int]) -> bool:
        if seal_layout == "B1-S":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            #self.kill_cs_trash() #done during sealcheck
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([634], self): return False
            self._sealdance(["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"], seal_layout + "-Boss", [634])
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
            self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
            atk_len = max(1, int(self._char_config["atk_len_diablo_deseis"]))
            cast_pos_abs = [0, 0]
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([632], self)
            if 1 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([631], self)
            if 2 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([632], self)
            if 3 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            wait(0.5, 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([633, 634], self): return False
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_b1s_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_b1s_home_loop"): return False
            if not self._pather.traverse_nodes([602], self , time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "B2-U":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            self._sealdance(["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"], seal_layout + "-Boss", [644])
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            atk_len = max(1, int(self._char_config["atk_len_diablo_deseis"]))
            cast_pos_abs = [0, 0]
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([641], self)
            if 1 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([640], self)
            if 2 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            self._pather.traverse_nodes([646], self)
            if 3 < atk_len:
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            wait(0.5, 1)            
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([640], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([640], self): return False
            self._pather.traverse_nodes_fixed("dia_b2u_home", self)
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_b2u_home_loop"): return False
            if not self._pather.traverse_nodes([602], self , time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_infector(self, seal_layout: str) -> bool:
        if seal_layout == "C1-F":
            Logger.info(seal_layout +": Starting to clear Seal")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            ### CLEAR TRASH & APPROACH SEAL ###
            #self.kill_cs_trash() #done during layout check
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) # REPLACES: if not self._pather.traverse_nodes([656, 654, 655], self, time_out=3): return False #ISSUE: getting stuck on 704 often, reaching maxgamelength
            #self.kill_cs_trash()
            if not self._sealdance(["DIA_C1F_OPEN_NEAR"], ["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"], seal_layout + "-Fake", [655]): return False #ISSUE: getting stuck on 705 during sealdance(), reaching maxgamelength
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._sealdance(["DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"], ["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"], seal_layout + "-Boss", [652]): return False
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
            atk_len = max(1, int(self._char_config["atk_len_diablo_infector"] / 2))
            cast_pos_abs = [0, 0]
            for _ in range(atk_len):
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            wait(0.5, 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([654], self, time_out=3): return False # this node often is not found
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_c1f_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_c1f_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "C2-G":
            Logger.info(seal_layout +": Starting to clear Seal")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())            
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes([663, 662], self): return False
            if not self._sealdance(["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], seal_layout + "-Boss", [662]): return False
            self._pather.traverse_nodes_fixed("dia_c2g_663", self) # REPLACES for increased consistency: #if not self._pather.traverse_nodes([662, 663], self): return False
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
            ### KILL BOSS ###
            atk_len = max(1, int(self._char_config["atk_len_diablo_infector"] / 2))
            cast_pos_abs = [0, 0]
            for _ in range(atk_len):
                self._right_attack(cast_pos_abs, 30)
                self._debuff(cast_pos_abs, 30)
                self._left_attack(cast_pos_abs, 30)
            wait(0.5, 1)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([664, 665], self): return False
            if not self._sealdance(["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"], seal_layout + "-Fake", [665]): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([665], self): return False
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_c2g_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_c2g_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_diablo(self) -> bool:
        atk_len = max(1, int(self._char_config["atk_len_diablo"] / 2))
        cast_pos_abs = [0, 0]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 30)
            self._debuff(cast_pos_abs, 30)
            self._left_attack(cast_pos_abs, 30)
        wait(0.5, 1)
        return True

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char import Trapsin
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Trapsin(config.trapsin, config.char, screen, t_finder, ui_manager, pather)
