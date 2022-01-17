import keyboard
from utils.custom_mouse import mouse
from char import IChar
from template_finder import TemplateFinder
from ui import UiManager
from pather import Pather
from logger import Logger
from screen import Screen
from utils.misc import wait
import time
from pather import Pather, Location
import cv2 #for Diablo
from item.pickit import PickIt #for Diablo


class Hammerdin(IChar):
    def __init__(
        self, 
        skill_hotkeys, 
        char_config, 
        screen: Screen, 
        template_finder: TemplateFinder, 
        ui_manager: UiManager, 
        pather: Pather, 
        pickit: PickIt #for Diablo
        ):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, char_config, screen, template_finder, ui_manager)
        self._pather = pather
        self._do_pre_move = True
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False
        else:
            # we want to change positions of shenk and eld a bit to be more center for teleport
            self._pather.offset_node(149, (70, 10))

    def _cast_hammers(self, time_in_s: float, aura: str = "concentration"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(self._char_config["stand_still"], do_release=False)
            wait(0.05, 0.1)
            if self._skill_hotkeys["blessed_hammer"]:
                keyboard.send(self._skill_hotkeys["blessed_hammer"])
            wait(0.05, 0.1)
            start = time.time()
            while (time.time() - start) < time_in_s:
                wait(0.06, 0.08)
                mouse.press(button="left")
                wait(0.1, 0.2)
                mouse.release(button="left")
            wait(0.01, 0.05)
            keyboard.send(self._char_config["stand_still"], do_press=False)

    def pre_buff(self):
        if self._char_config["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.06)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(["VIGOR"])
        can_teleport = self._skill_hotkeys["teleport"] and self._ui_manager.is_right_skill_active()
        if  should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.can_teleport():
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        self._cast_hammers(self._char_config["atk_len_pindle"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_eldritch(self) -> bool:
        if self.can_teleport():
            # Custom eld position for teleport that brings us closer to eld
            self._pather.traverse_nodes_fixed([(675, 30)], self)
        else:
            if not self._do_pre_move:
                keyboard.send(self._skill_hotkeys["concentration"])
                wait(0.05, 0.15)
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_shenk(self):
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0, do_pre_move=self._do_pre_move)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_shenk"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_council(self) -> bool:
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"]
        # Go inside and hammer a bit
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True)
        self._cast_hammers(atk_len)
        # Move a bit back and another round
        self._move_and_attack((40, 20), atk_len)
        # Here we have two different attack sequences depending if tele is available or not
        if self.can_teleport():
            # Back to center stairs and more hammers
            self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
            self._cast_hammers(atk_len)
            # move a bit to the top
            self._move_and_attack((65, -30), atk_len)
        else:
            # Stay inside and cast hammers again moving forward
            self._move_and_attack((40, 10), atk_len)
            self._move_and_attack((-40, -20), atk_len)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Move close to nilathak
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_nihlatak"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_nihlatak"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_nihlatak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        return True
    
    
    def kill_summoner(self) -> bool:
        # move mouse to below altar
        pos_m = self._screen.convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._cast_hammers(self._char_config["atk_len_arc"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        # Move a bit back and another round
        self._move_and_attack((0, 80), self._char_config["atk_len_arc"] * 0.5)
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True
    
    #-------------------------------------------------------------------------------#
    # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
    #-------------------------------------------------------------------------------#

    #CLEAR CS TRASH

    def clear_entrance_hall(self) -> bool:
        Logger.info("CS: Starting to clear Trash")
        if not self._pather.traverse_nodes([677], self): return False 
        self.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self) # Gets to door and checks starts attacks and picks up items
        self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self) # Moves to first open area
        self.kill_cs_trash() # since theres probably a mob there just lands and attacks
        if not self._pather.traverse_nodes([670,671], self): return False
        self.kill_cs_trash() 
        self._picked_up_items |= self._pickit.pick_up_items(self) # moves back and forth to draw more enemies finishes em off picks up items.
        if not self._pather.traverse_nodes([671], self): return False # re centers it self
        self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self) # Moves to second open area
        return True

    def entrance_1(self) -> bool:
        entrance1_layout = "CS Entrance Style 1 "
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + entrance1_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info("Entrance Layout: " + entrance1_layout)
        Logger.info(entrance1_layout + "cleaning")
        self.kill_cs_trash() # Lands on location and starts attacking
        if not self._pather.traverse_nodes([673], self): return False # Re-adjust itself and continues to attack
        self.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self) 
        self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) # Moves char to postion close to node 674 continues to attack
        self._pather.traverse_nodes([674], self)
        self.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self) 
        Logger.info(entrance1_layout + "cleaning")
        self._pather.traverse_nodes([675], self) # Re-adjust itself
        self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) #static path to get to be able to spot 676
        self._pather.traverse_nodes([676], self)
        Logger.info(entrance1_layout + "cleaning")
        self.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self)
        self._loop_pentagram("diablo_entrance_pentagram_loop")
        if not self._pather.traverse_nodes([602], self , time_out=5): return False
        Logger.info("CS: Looping to PENTAGRAM after clearing CS Trash")
        return True

    def entrance_2(self) -> bool:
        entrance2_layout = "CS Entrance Style 2 "
        if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + entrance2_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        Logger.info("Entrance Layout: " + entrance2_layout)
        self.kill_cs_trash()
        if not self._pather.traverse_nodes([682], self): return False
        self.kill_cs_trash()
        Logger.info(entrance2_layout + " Cleaning area")
        if not self._pather.traverse_nodes([682], self): return False
        self._pather.traverse_nodes_fixed("diablo_entrance2_1", self)
        if not self._pather.traverse_nodes([683], self): return False
        self.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self)
        self._pather.traverse_nodes([683,684], self)
        self._pather.traverse_nodes_fixed("diablo_entrance2_2", self)
        self._pather.traverse_nodes([685,686,687], self)
        self.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self)
        Logger.info("CS: Looping to PENTAGRAM")
        if not self._loop_pentagram("diablo_entrance_pentagram_loop"): return False
        if not self._pather.traverse_nodes([602], self , time_out=5): return False
        Logger.info("CS: Looping to PENTAGRAM after clearing CS Trash")
        return True     
    
    # GET TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_TP"]  #"DIA_NEW_PENT_3", "DIA_NEW_PENT_5 -> if these templates are found, you cannot calibrate at [602] #"DIA_NEW_PENT_6", 
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed(path, self)
        if not found:
            #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + path + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
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
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_cs_trashmobs"] * 0.2)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.2)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.1)
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
        return True
    
    def kill_cs_trash(self) -> bool:
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_cs_trashmobs"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(2, "redemption")
        self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([611], self)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([610], self)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_vizier"])
            wait(0.1, 0.15)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([623], self)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.4)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([624], self)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_vizier"])
            wait(0.1, 0.15)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([632], self)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([631], self)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"] * 0.5)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([632], self)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])
            wait(0.1, 0.15)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic) 
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([641], self)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([640], self)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"] * 0.5)
            self._cast_hammers(1, "redemption")
            self._pather.traverse_nodes([646], self)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])
            wait(0.1, 0.15)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic) 
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_hammers(self._char_config["atk_len_diablo_infector"] * 0.4)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"] * 0.3)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"] * 0.4)
            wait(0.1, 0.15)
            self._cast_hammers(1.2, "redemption")
            self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic) 
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_hammers(self._char_config["atk_len_diablo_infector"] * 0.4)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"] * 0.3)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"] * 0.4)
            wait(0.1, 0.15)
            self._cast_hammers(1.2, "redemption")
            self._cast_hammers(1.2, "cleansing") # would make sense to add cleansing to CS, due to the tons of curses (that also interfere with the seal logic)
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
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_diablo"] * 0.5)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((60, 30), self._char_config["atk_len_diablo"])
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-60, -30), self._char_config["atk_len_diablo"])
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        return True

if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather)
