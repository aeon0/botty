import keyboard
import random
import time

from char import CharacterCapabilities
from char.paladin import Paladin
from config import Config
from logger import Logger
from pather import Location
from pather import Pather
from pather import Pather, Location
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from target_detect import get_visible_targets, log_targets
from ui import skills
from utils.custom_mouse import mouse
from utils.misc import wait
from item.pickit import PickIt
from health_manager import set_panel_check_paused
from inventory.personal import inspect_items

class Hammerdin(Paladin):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Hammerdin")
        super().__init__(*args, **kwargs)
        #hammerdin needs to be closer to shenk to reach it with hammers
        self._pather.offset_node(149, (70, 10)) # THIS NODE NODE LONGER EXISTS FOR AUTMAP CHARS
        self._pather.offset_node(1149, (70, 10)) # not sure this node has to be offset for automap, keeping it to be safe

    def _cast_hammers(self, time_in_s: float, aura: str = "concentration"):
        if aura in self._skill_hotkeys and self._skill_hotkeys[aura]:
            keyboard.send(self._skill_hotkeys[aura])
            wait(0.05, 0.1)
            keyboard.send(Config().char["stand_still"], do_release=False)
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
            keyboard.send(Config().char["stand_still"], do_press=False)

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.06)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not skills.is_right_skill_selected(["VIGOR"])
        can_teleport = self.capabilities.can_teleport_natively and skills.is_right_skill_active()
        if should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def _cs_pickit(self, skip_inspect: bool = False):
        new_items = self._pickit.pick_up_items(self)
        self._picked_up_items |= new_items
        if not skip_inspect and new_items:
            set_panel_check_paused(True)
            inspect_items(grab(), ignore_sell=True)
            set_panel_check_paused(False)        

    def _generic_hammer_attack_sequence(
        self,
        #default_target_abs: tuple[int, int] = (0, 0),
        min_duration: float = 0,
        max_duration: float = 15,
        target_detect: bool = True,
        aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        hammer_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            #cast_pos_abs = default_target_abs
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_targets()):
                #log_targets(targets)
                target_check_count += 1

            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                    Logger.debug("No More Targets Skip to next Area")
                    break
            #else:

                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                #self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)
            targets = get_visible_targets()
            if targets:
                        Logger.debug("Targets Found Attacking")
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                        self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)
                        self._cast_hammers(1.0, "redemption")

            else:            
                    self._cast_hammers(1.0, "redemption")   
                    target_check_count += 1
                    Logger.debug("Couldn't Locate Targets Checking Again")
        return True

    def _fast_hammer_attack_sequence(
        self,
        #default_target_abs: tuple[int, int] = (0, 0),
        min_duration: float = 0,
        max_duration: float = 15,
        target_detect: bool = True,
        aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        hammer_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            #cast_pos_abs = default_target_abs
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_targets()):
                #log_targets(targets)
                target_check_count += 1

            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                    Logger.debug("No More Targets Skip to next Area")
                    break
            #else:

                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                #self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)
            targets = get_visible_targets()
            if targets:
                        Logger.debug("Targets Found Attacking")
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                        self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)
                        self._cast_hammers(1.0, "redemption")

            else:            
                    self._cast_hammers(1.0, "redemption")   
                    target_check_count += 1
                    Logger.debug("Couldn't Locate Targets Checking Again")
        return True    

    def _dia_hammer_attack_sequence(
        self,
        #default_target_abs: tuple[int, int] = (0, 0),
        min_duration: float = 0,
        max_duration: float = 15,
        target_detect: bool = True,
        aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        hammer_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            #cast_pos_abs = default_target_abs
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_targets()):
                #log_targets(targets)
                target_check_count += 1

            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                    Logger.debug("No More Targets Skip to next Area")
                    break
            #else:

                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                #self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)
            targets = get_visible_targets()
            if targets:
                        Logger.debug("Targets Found Attacking")
                        closest_target_position_monitor = targets[0].center_monitor
                        self.pre_move()
                        self.move(closest_target_position_monitor, force_move=True)
                        self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)

            else:            
                    self._cast_hammers(Config().char["atk_len_cs_trashmobs"] * 0.4)
                    target_check_count += 1
                    Logger.debug("Couldn't Locate Targets Checking Again")
        return True                

        #Sorc Attack Sequence Optimized for trash
    def _cs_attack_sequence(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_cs_trashmobs"] * 3):
        self._generic_hammer_attack_sequence()

        #Sorc Attack Sequence Optimized for trash
    def _cs_attack_sequence_static(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_cs_trashmobs"] * 3):
        self._generic_hammer_attack_sequence()

        #Sorc Attack Sequence Optimized for trash
    def _cs_fast_attack_sequence(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_cs_trashmobs"] * 1):
        self._fast_hammer_attack_sequence()

    def _cs_dia_attack_sequence(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_diablo"] * 3):
        self._dia_hammer_attack_sequence()                                       

    def _cs_trash_mobs_attack_sequence(self, min_duration: float = 1.2, max_duration: float = Config().char["atk_len_cs_trashmobs"]):
        self._cs_attack_sequence()        

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.capabilities.can_teleport_with_charges:
            if not self._pather.traverse_nodes([104], self, timeout=1.0, force_tp=True, use_tp_charge=True):
                return False
        elif self.capabilities.can_teleport_natively:
            if not self._pather.traverse_nodes_fixed("pindle_end", self):
                return False
        else:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.15)
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=False, force_tp=True, use_tp_charge=True)
        self._cast_hammers(Config().char["atk_len_pindle"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_eldritch(self) -> bool:
        if self.capabilities.can_teleport_natively:
            # Custom eld position for teleport that brings us closer to eld
            self._pather.traverse_nodes_fixed([(675, 30)], self)
        else:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.15)
            # Traverse without pre_move, because we don't want to activate vigor when walking!
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=1.0, do_pre_move=False, force_tp=True, use_tp_charge=True)
        wait(0.05, 0.1)
        self._cast_hammers(Config().char["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_shenk(self):
        keyboard.send(self._skill_hotkeys["concentration"])
        wait(0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, do_pre_move=False, force_tp=True, use_tp_charge=True)
        wait(0.05, 0.1)
        self._cast_hammers(Config().char["atk_len_shenk"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_council(self) -> bool:
        keyboard.send(self._skill_hotkeys["concentration"])
        wait(.15)
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = Config().char["atk_len_trav"]
        # Go inside and hammer a bit
        self._pather.traverse_nodes([228, 229], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
        # Move a bit back and another round
        self._move_and_attack((40, 20), atk_len)
        # Here we have two different attack sequences depending if tele is available or not
        if self.capabilities.can_teleport_natively or self.capabilities.can_teleport_with_charges:
            # Back to center stairs and more hammers
            self._pather.traverse_nodes([226], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
            self._cast_hammers(atk_len)
            # move a bit to the top
            self._move_and_attack((65, -30), atk_len)
        else:
            # Stay inside and cast hammers again moving forward
            self._move_and_attack((40, 10), atk_len)
            self._move_and_attack((-40, -20), atk_len)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(Config().char["atk_len_nihlathak"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), Config().char["atk_len_nihlathak"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), Config().char["atk_len_nihlathak"] * 0.4)
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        return True

    def kill_summoner(self) -> bool:
        # move mouse to below altar
        pos_m = convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._cast_hammers(Config().char["atk_len_arc"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        # Move a bit back and another round
        self._move_and_attack((0, 80), Config().char["atk_len_arc"] * 0.5)
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

     ########################################################################################
     # Chaos Sanctuary, Trash, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
     ########################################################################################

    def dia_kill_trash(self, location:str) -> bool:

        match location:
            
            case "outside_cs" | "outside_cs_stairs" | "aisle_1" | "aisle_3" | "hall1_4" | "to_hall2_4" | "hall2_1" | "hall2_3" | "hall2_4" | "to_hall3_1" | "trash_to_a1" | "trash_to_a3" | "a_boss" | "trash_to_b3" | "trash_to_b4" | "b_boss" | "trash_to_c2":
                if self._use_safer_routines or Config().char["dia_kill_trash"]:  
                    self._cs_attack_sequence()
                    self._cs_pickit()    
                else:
                    wait(.30)
                    Logger.debug("Skip attack Sequence")      

            # faster seal skips
            case "approach_b1s" | "b_seal" | "approach_c2g" | "fake_c2g" | "layoutcheck_a" | "layoutcheck_c" | "layoutcheck_b" :

                if self._use_safer_routines or Config().char["dia_kill_trash"]:  
                    self._cs_attack_sequence()
                    self._cs_pickit()    
                else:
                    wait(.30)
                    Logger.debug("Skip attack Sequence")        

            case "pent_before_a" | "pent_before_b" | "pent_before_c":
                if self._use_safer_routines or Config().char["dia_kill_trash"]:  
                    self._cs_attack_sequence()
                    self._cs_pickit()    
                else:
                    wait(.30)
                    Logger.debug("Skip attack Sequence")    

            case "aisle_2"| "hall1_1"| "hall1_2" | "hall1_3" | "to_hall2_2" | "to_hall2_3" | "hall2_2"  | "to_hall3_2" | "to_hall3_3" | "hall3_4" | "hall3_5" :
                if self._use_safer_routines or Config().char["dia_kill_trash"]:  
                    self._cs_attack_sequence()
                    self._cs_pickit()    
                else:
                    wait(.30)
                    Logger.debug("Skip attack Sequence")    

            #Cast frost nova first interaction and while hole freeze procs
            case "to_hall2_1" | "aisle_4" | "hall3_3" | "sealdance":
                    self._cs_attack_sequence()
                    self._cs_pickit()    
          

            # at these spots (and after each seal boss) checks if inv is full and discards items
            case "to_hall2_2" | "to_hall3_1" | "trash_to_a4" | "approach_b2u" | "approach_c2g":
                if self._use_safer_routines or Config().char["dia_kill_trash"]:  
                    self._cs_attack_sequence()
                    self._cs_pickit()    
                else:
                    wait(.30)
                    Logger.debug("Skip attack Sequence")      
            
            # For each seal-area: 3 positions to start fights & loot (triggered in diablo.py), followed by 1 position for each seal.

            case "trash_to_a2" |  "trash_to_a4" | "trash_to_b1" | "trash_to_b2" | "approach_b2u" | "trash_to_c1" | "trash_to_c3":
                if self._use_safer_routines or Config().char["dia_kill_trash"]:  
                    self._cs_attack_sequence()
                    self._cs_pickit()    
                else:
                    wait(.30)
                    Logger.debug("Skip attack Sequence")      


            case "A1-L_01":
                ### APPROACH ###
                ### ATTACK ###
            #    self._frost_nova(.2)
            #    wait(.20)
                ### LOOT ###
                Logger.debug("Skip attack Sequence")

            case "A1-L_02" | "A1-L_03" | "A1-L_seal1" | "A1-L_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("Skip attack Sequence")                

            case "A2-Y_01":
                ### APPROACH ###
                ### ATTACK ###
            #    self._frost_nova(.2)
            #    wait(.20)
                ### LOOT ###
                Logger.debug("Skip attack Sequence")
                            
                            
            case "A2-Y_02" | "A2-Y_03" | "A2-Y_seal1" | "A2-Y_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("Skip attack Sequence")

            case "B1-S_01" | "B1-S_02" | "B1-S_03" | "B1-S_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("Skip attack Sequence")

            case "B2-U_01" | "B2-U_02" | "B2-U_03" | "B2-U_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("Skip attack Sequence")

            case "C1-F_01" | "C1-F_02" | "C1-F_03" | "C1-F_seal1" | "C1-F_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("Skip attack Sequence")

            case "C2-G_01" | "C2-G_02" | "C2-G_03" | "C2-G_seal1" | "C2-G_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("Skip attack Sequence")


            case _:
                ### APPROACH ###
                Logger.error("No location argument given for dia_kill_trash(" + location + "), should not happen - killing mobs instead just to be safe")
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                return True

    
    def kill_vizier_automap(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_vizier"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "A1-L":
                if not self._pather.traverse_nodes_automap([1623], self, use_tp_charge=True): return False
                Logger.debug(seal_layout + ": Attacking Vizier")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()
                self._activate_cleanse_redemption()
            case "A2-Y":
                if not self._pather.traverse_nodes_automap([1627], self, use_tp_charge=True): return False
                Logger.debug(seal_layout + ": Attacking Vizier")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()
                self._activate_cleanse_redemption()
            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_vizier("+ seal_layout +"), should not happen.")
                return False
        return True


    def kill_deseis_automap(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_deseis"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "B1-S":
                if not self._pather.traverse_nodes_automap([1632], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                Logger.debug(seal_layout + ": Attacking DeSeis")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes_automap([1635], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes_automap([1632], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                self._cs_fast_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()
                self._activate_cleanse_redemption()
                
            case "B2-U":
                if not self._pather.traverse_nodes_automap([1636], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                Logger.debug(seal_layout + ": Attacking DeSeis")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes_automap([1637], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes_automap([1636], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                self._cs_fast_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()
                self._activate_cleanse_redemption()

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
                return False
        return True


    def kill_infector_automap(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_infector"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "C1-F":
                #if not self._pather.traverse_nodes_automap([1643], self, use_tp_charge=True): return False
                Logger.debug(seal_layout + ": Attacking Infector")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes_automap([1643], self, use_tp_charge=True): return False
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()
                self._activate_cleanse_redemption()
            case "C2-G":
                if not self._pather.traverse_nodes_automap([1647], self, use_tp_charge=True): return False
                Logger.debug(seal_layout + ": Attacking Infector")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes_automap([1645], self, use_tp_charge=True): return False
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._cs_pickit()
                self._activate_cleanse_redemption()
            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
                return False
        return True


    def kill_diablo(self) -> bool: #dia cannot be frozen, but be poisoned, so can be identified by mob detection!
        ### APPROACH ###
        ### ATTACK ###
        atk_dur_min = Config().char["atk_len_diablo"]
        atk_dur_max = atk_dur_min * 3
        Logger.debug("Attacking Diablo at position 1/1")
        diablo_abs = [100,-100] #hardcoded dia pos.
        pos_m = convert_abs_to_monitor((0, -75))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cs_dia_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
        self._cs_dia_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
        self._cs_pickit(skip_inspect=True)
        ### LOOT ###
        #self._cs_pickit()
        return True


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    pather = Pather()
    char = Hammerdin(Config().hammerdin, Config().char, pather)