import random
import keyboard
import time
import numpy as np
from automap_finder import toggle_automap

from health_manager import get_panel_check_paused, set_panel_check_paused
from inventory.personal import inspect_items
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab, convert_abs_to_screen
from utils.custom_mouse import mouse
from char.paladin import Paladin
from logger import Logger
from config import Config
from utils.misc import wait
from pather import Location
from target_detect import get_visible_targets, TargetInfo, log_targets
import cv2 # for info screenshots to gather more pics from diablo

class FoHdin(Paladin):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up FoHdin")
        super().__init__(*args, **kwargs)
        self._pather.adapt_path((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), [220, 221, 222, 903, 904, 905, 906])


    def _cast_foh(self, cast_pos_abs: tuple[float, float], spray: int = 10, min_duration: float = 0, aura: str = "conviction"):
        return self._cast_skill_with_aura(skill_name = "foh", cast_pos_abs = cast_pos_abs, spray = spray, min_duration = min_duration, aura = aura)

    def _cast_holy_bolt(self, cast_pos_abs: tuple[float, float], spray: int = 10, min_duration: float = 0, aura: str = "concentration"):
        #if skill is bound : concentration, use concentration, otherwise move on with conviction. alternatively use redemption whilst holybolting. conviction does not help holy bolt (its magic damage)
        return self._cast_skill_with_aura(skill_name = "holy_bolt", cast_pos_abs = cast_pos_abs, spray = spray, min_duration = min_duration, aura = aura)

    def _cast_hammers(self, min_duration: float = 0, aura: str = "concentration"): #for nihlathak
        return self._cast_skill_with_aura(skill_name = "blessed_hammer", spray = 0, min_duration = min_duration, aura = aura)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float, aura: str = "concentration"): #for nihalthak
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len, aura=aura)

    def _generic_foh_attack_sequence(
        self,
        default_target_abs: tuple[int, int] = (0, 0),
        min_duration: float = 0,
        max_duration: float = 15,
        foh_to_holy_bolt_ratio: int = 3,
        target_detect: bool = True,
        default_spray: int = 50,
        aura: str = ""
    ) -> bool:
        start = time.time()
        target_check_count = 1
        foh_aura = aura if aura else "conviction"
        holy_bolt_aura = aura if aura else "concentration"
        while (elapsed := (time.time() - start)) <= max_duration:
            cast_pos_abs = default_target_abs
            spray = default_spray
            # if targets are detected, switch to targeting with reduced spread rather than present default cast position and default spread
            if target_detect and (targets := get_visible_targets()):
                # log_targets(targets)
                spray = 5
                cast_pos_abs = targets[0].center_abs

            # if time > minimum and either targets aren't set or targets don't exist, exit loop
            if elapsed > min_duration and (not target_detect or not targets):
                break
            else:

                # TODO: add delay between FOH casts--doesn't properly cast each FOH in sequence
                # cast foh to holy bolt with preset ratio (e.g. 3 foh followed by 1 holy bolt if foh_to_holy_bolt_ratio = 3)
                if foh_to_holy_bolt_ratio > 0 and not target_check_count % (foh_to_holy_bolt_ratio + 1):
                    self._cast_holy_bolt(cast_pos_abs, spray=spray, aura=holy_bolt_aura)
                else:
                    self._cast_foh(cast_pos_abs, spray=spray, aura=foh_aura)

            target_check_count += 1
        return True

    #FOHdin Attack Sequence Optimized for trash
    def _cs_attack_sequence(self, min_duration: float = Config().char["atk_len_cs_trashmobs"], max_duration: float = Config().char["atk_len_cs_trashmobs"] * 3):
        self._generic_foh_attack_sequence(default_target_abs=(20,20), min_duration = min_duration, max_duration = max_duration, default_spray=100, foh_to_holy_bolt_ratio=6)
        self._activate_redemption_aura()

    def _cs_trash_mobs_attack_sequence(self, min_duration: float = 1.2, max_duration: float = Config().char["atk_len_cs_trashmobs"]):
        self._cs_attack_sequence(min_duration = min_duration, max_duration = max_duration)

    def _cs_pickit(self, skip_inspect: bool = False):
        new_items = self._pickit.pick_up_items(self)
        self._picked_up_items |= new_items
        if not skip_inspect and new_items:
            set_panel_check_paused(True)
            inspect_items(grab(), ignore_sell=True)
            set_panel_check_paused(False)


    def kill_pindle(self) -> bool:
        atk_len_dur = float(Config().char["atk_len_pindle"])
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])

        if (self.capabilities.can_teleport_natively) and self._use_safer_routines:
            toggle_automap(True)
            # Slightly retreating, so the Merc gets charged
            self._pather.traverse_nodes_automap([1102], self, timeout=1.0, do_pre_move=False, force_move=True, force_tp=False, use_tp_charge=False, toggle_map=False)
            # Doing one Teleport to safe_dist to grab our Merc
            Logger.debug("Teleporting backwards to let Pindle charge the MERC. Looks strange, but is intended!") #I would leave this message in, so users dont complain that there is a strange movement pattern.
            self._pather.traverse_nodes_automap([1103], self, timeout=1.0, do_pre_move=False, force_tp=True, use_tp_charge=True, toggle_map=False)
            # Slightly retreating, so the Merc gets charged
            self._pather.traverse_nodes_automap([1103], self, timeout=1.0, do_pre_move=False, force_move=True, force_tp=False, use_tp_charge=False, toggle_map=False)
            toggle_automap(False)
        elif (self.capabilities.can_teleport_with_charges) and self._use_safer_routines:
            toggle_automap(True)
            self._pather.traverse_nodes_automap([1102], self, timeout=1.0, do_pre_move=False, toggle_map=False)
            self._pather.traverse_nodes_automap([1103], self, timeout=1.0, do_pre_move=False, use_tp_charge=True, toggle_map=False)
            toggle_automap(False)
        else:
            keyboard.send(self._skill_hotkeys["conviction"])
            wait(0.15)
            self._pather.traverse_nodes_automap([1103], self, timeout=1.0, do_pre_move=False)

        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        self._generic_foh_attack_sequence(default_target_abs=cast_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, default_spray=11)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            keyboard.send(self._skill_hotkeys["redemption"])
            wait(0.15)
            self._pather.traverse_nodes_automap((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=False)

        # Use target-based attack sequence one more time before pickit
        self._generic_foh_attack_sequence(default_target_abs=cast_pos_abs, max_duration=atk_len_dur, default_spray=11)
        self._activate_cleanse_redemption()

        return True


    def kill_council(self) -> bool:
        atk_len_dur = float(Config().char["atk_len_trav"])

        keyboard.send(self._skill_hotkeys["conviction"])
        wait(.15)
        # traverse to nodes and attack
        nodes = [225, 226, 300]
        for i, node in enumerate(nodes):
            self._pather.traverse_nodes([node], self, timeout=2.2, do_pre_move = False, force_tp=(self.capabilities.can_teleport_natively or i > 0), use_tp_charge=(self.capabilities.can_teleport_natively or i > 0))
            default_target_abs = self._pather.find_abs_node_pos(node, img := grab()) or self._pather.find_abs_node_pos(906, img) or (-50, -50)
            self._generic_foh_attack_sequence(default_target_abs=default_target_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, default_spray=80)

        # return to 226 and prepare for pickit
        self._pather.traverse_nodes([226], self, timeout=2.2, do_pre_move = False, force_tp=True, use_tp_charge=True)
        default_target_abs = self._pather.find_abs_node_pos(226, img := grab()) or self._pather.find_abs_node_pos(906, img) or (-50, -50)
        self._generic_foh_attack_sequence(default_target_abs=default_target_abs, max_duration=atk_len_dur*3, default_spray=80)

        self._activate_cleanse_redemption()

        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        atk_len_dur = float(Config().char["atk_len_eldritch"])

        if (self.capabilities.can_teleport_natively or self.capabilities.can_teleport_with_charges) and self._use_safer_routines:
            Logger.debug("Slightly retreating, so the Merc gets hit. Looks strange, but is intended!") #I would leave this message in, so users dont complain that there is a strange movement pattern.
            if not self._pather.traverse_nodes_automap([1121], self, timeout=1.0, do_pre_move=False, force_move=True, force_tp=False, use_tp_charge=False):
                return False

        self._generic_foh_attack_sequence(default_target_abs=eld_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, default_spray=70)

        # move to end node
        pos_m = convert_abs_to_monitor((70, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes_automap((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.1)

        # check mobs one more time before pickit
        self._generic_foh_attack_sequence(default_target_abs=eld_pos_abs, max_duration=atk_len_dur, default_spray=70)
        self._activate_cleanse_redemption()

        return True


    def kill_shenk(self):
        atk_len_dur = float(Config().char["atk_len_shenk"])

        # traverse to shenk
        if self.capabilities.can_teleport_natively:
            self.select_tp()
            if not self._pather.traverse_nodes_automap((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, force_tp=True):
                return False
        elif self.capabilities.can_teleport_with_charges:
            self.select_tp()
            if not self._pather.traverse_nodes_automap((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, use_tp_charge=True, do_pre_move=False): 
                return False
        else:
            self.select_tp()
            wait(0.15)
            if not self._pather.traverse_nodes_automap((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, do_pre_move=False): 
                return False
        wait(0.05, 0.1)

        # bypass mob detect first
        self._cast_foh((0, 0), spray=11, min_duration = 2, aura = "conviction")
        # then do generic mob detect sequence
        diff = atk_len_dur if atk_len_dur <= 2 else (atk_len_dur - 2)
        self._generic_foh_attack_sequence(min_duration=atk_len_dur - diff, max_duration=atk_len_dur*3 - diff, default_spray=10, target_detect=False)
        self._activate_cleanse_redemption()

        return True


    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        atk_len_dur = Config().char["atk_len_nihlathak"]
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8, do_pre_move=False)
        if self._select_skill("blessed_hammer"):
            self._cast_hammers(atk_len_dur/4)
            self._cast_hammers(2*atk_len_dur/4, "redemption")
            self._move_and_attack((30, 15), atk_len_dur/4, "redemption")
        else:
            Logger.warning("FOHDin without blessed hammer is not very strong vs. Nihlathak!")
            self._generic_foh_attack_sequence(min_duration=atk_len_dur/2, max_duration=atk_len_dur, default_spray=70, aura="redemption")
            self._generic_foh_attack_sequence(min_duration=atk_len_dur/2, max_duration=atk_len_dur, default_spray=70, aura="redemption")
        self._generic_foh_attack_sequence(max_duration=atk_len_dur*2, default_spray=70)
        self._activate_cleanse_redemption()
        return True

    def kill_summoner(self) -> bool:
        # Attack
        atk_len_dur = Config().char["atk_len_arc"]
        self._generic_foh_attack_sequence(min_duration=atk_len_dur, max_duration=atk_len_dur*2, default_spray=80)
        self._activate_cleanse_redemption()
        return True


     ########################################################################################
     # Chaos Sanctuary, Trash, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
     ########################################################################################

    def dia_kill_trash(self, location:str) -> bool:

        match location:
            
            case "sealdance" | "layoutcheck_a" | "layoutcheck_b" | "layoutcheck_c" | "pent_before_a" | "pent_before_b" | "pent_before_c" | "outside_cs" | "outside_cs_stairs" | "aisle_1" | "aisle_2" | "aisle_3" | "aisle_4" | "hall1_1" | "hall1_2" | "hall1_3" | "hall1_4" | "to_hall2_1" | "to_hall2_2" | "to_hall2_3" | "to_hall2_4" | "hall2_1" | "hall2_2" | "hall2_3" | "hall2_4" | "to_hall3_1" | "to_hall3_2" | "to_hall3_3" | "hall3_1" | "hall3_2" | "hall3_3" | "hall3_4" | "hall3_5" | "trash_to_a1" | "trash_to_a2" | "trash_to_a3" |  "trash_to_a4" | "a_boss" | "trash_to_b1" | "trash_to_b2" | "trash_to_b3" | "trash_to_b4" | "approach_b1s" | "approach_b2u" | "b_boss" | "b_seal" | "trash_to_c1" | "trash_to_c2" | "trash_to_c3" | "approach_c2g" | "fake_c2g":
                self._cs_trash_mobs_attack_sequence()
                self._picked_up_items |= self._pickit.pick_up_items(self)

            # at these spots (and after each seal boss) checks if inv is full and discards items
            case "aisle_4" | "to_hall2_2" | "to_hall3_1" | "trash_to_a4" | "approach_b2u" | "approach_c2g":
                self._cs_trash_mobs_attack_sequence()
                self._cs_pickit() 
            
            # For each seal-area: 3 positions to start fights & loot (triggered in diablo.py), followed by 1 position for each seal.

            case "A1-L_01" | "A1-L_02" | "A1-L_03" | "A1-L_seal1" | "A1-L_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "A2-Y_01" | "A2-Y_02" | "A2-Y_03" | "A2-Y_seal1" | "A2-Y_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "B1-S_01" | "B1-S_02" | "B1-S_03" | "B1-S_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "B2-U_01" | "B2-U_02" | "B2-U_03" | "B2-U_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "C1-F_01" | "C1-F_02" | "C1-F_03" | "C1-F_seal1" | "C1-F_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "C2-G_01" | "C2-G_02" | "C2-G_03" | "C2-G_seal1" | "C2-G_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

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
                if not self._pather.traverse_nodes_automap([1623], self): return False
                Logger.debug(seal_layout + ": Attacking Vizier")
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_vizier" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_vizier_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
            case "A2-Y":
                if not self._pather.traverse_nodes_automap([1627], self, use_tp_charge=True): return False
                Logger.debug(seal_layout + ": Attacking Vizier")
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_vizier" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_vizier_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_pickit(skip_inspect=True)
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
                if self.capabilities.can_teleport_with_charges:
                    if not self._pather.traverse_nodes_automap([1638], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive    
                if not self._pather.traverse_nodes_automap([1632], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                Logger.debug(seal_layout + ": Attacking DeSeis")
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_deseis" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_deseis_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
                
            case "B2-U":
                if not self._pather.traverse_nodes_automap([1636], self, use_tp_charge=True): return False #this node requres teleport, quite aggressive
                Logger.debug(seal_layout + ": Attacking DeSeis")
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/monsters/info_deseis_killsequence" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_deseis" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_deseis_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_pickit(skip_inspect=True)
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
                Logger.debug(seal_layout + ": Attacking Infector")
                #if not self._pather.traverse_nodes_automap([1643], self, use_tp_charge=True): return False #he stops us most of the time at the seal anyways
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_infector" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_infector_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
            case "C2-G":
                if not self._pather.traverse_nodes_automap([1647], self, use_tp_charge=True): return False
                Logger.debug(seal_layout + ": Attacking Infector")
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_infector" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_infector_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
                self._cs_pickit(skip_inspect=True)
                self._activate_cleanse_redemption()
            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
                return False
        return True


    def kill_diablo(self) -> bool: #dia cannot be frozen, but be poisoned, so can be identified by mob detection!
        ### APPROACH ###
        ### ATTACK ###
        atk_len_dur = float(Config().char["atk_len_diablo"])
        Logger.debug("Attacking Diablo at position 1/1")
        diablo_abs = [100,-100] #hardcoded dia pos.
        if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
        self._generic_foh_attack_sequence(default_target_abs=diablo_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, aura="concentration", foh_to_holy_bolt_ratio=2)
        if Config().advanced_options["gather_mob_screenshots_for_modelling"]: cv2.imwrite(f"./log/screenshots/monsters/info_diablo_loot" + time.strftime("%Y%m%d_%H%M%S") + "automap.png", grab())
        self._activate_cleanse_redemption()
        ### LOOT ###
        #self._cs_pickit()
        return True