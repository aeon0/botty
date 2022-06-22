import random
import keyboard
import time
import numpy as np

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

        if (self.capabilities.can_teleport_natively or self.capabilities.can_teleport_with_charges) and self._use_safer_routines:
            # Slightly retreating, so the Merc gets charged
            if not self._pather.traverse_nodes([102], self, timeout=1.0, do_pre_move=False, force_move=True,force_tp=False, use_tp_charge=False):
                return False
            # Doing one Teleport to safe_dist to grab our Merc
            Logger.debug("Teleporting backwards to let Pindle charge the MERC. Looks strange, but is intended!") #I would leave this message in, so users dont complain that there is a strange movement pattern.
            if not self._pather.traverse_nodes([103], self, timeout=1.0, do_pre_move=False, force_tp=True, use_tp_charge=True):
                return False
            # Slightly retreating, so the Merc gets charged
            if not self._pather.traverse_nodes([103], self, timeout=1.0, do_pre_move=False, force_move=True, force_tp=False, use_tp_charge=False):
                return False
        else:
            keyboard.send(self._skill_hotkeys["conviction"])
            wait(0.15)
            self._pather.traverse_nodes([103], self, timeout=1.0, do_pre_move=False)

        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        self._generic_foh_attack_sequence(default_target_abs=cast_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, default_spray=11)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            
            keyboard.send(self._skill_hotkeys["redemption"])
            wait(0.15)
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=False)

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

        self._generic_foh_attack_sequence(default_target_abs=eld_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, default_spray=70)

        # move to end node
        pos_m = convert_abs_to_monitor((70, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.1)

        # check mobs one more time before pickit
        self._generic_foh_attack_sequence(default_target_abs=eld_pos_abs, max_duration=atk_len_dur, default_spray=70)
        self._activate_cleanse_redemption()

        return True


    def kill_shenk(self):
        atk_len_dur = float(Config().char["atk_len_shenk"])

        # traverse to shenk
        keyboard.send(self._skill_hotkeys["conviction"])
        wait(0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, do_pre_move=False, force_tp=True, use_tp_charge=True)
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

    def kill_cs_trash(self, location:str) -> bool:

        ###########
        # SEALDANCE
        ###########

        #these locations have no traverses and are basically identical.
        #if location in ("sealdance", "rof_01", "rof_02", "entrance_hall_01", "entrance_hall_02", "entrance1_01", "entrance1_02", "entrance1_03", "entrance1_04", "entrance2_01", "entrance2_03"):

        match location:
            case "sealdance": #if seal opening fails & trash needs to be cleared -> used at ANY seal
                ### APPROACH
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###


            ################
            # CLEAR CS TRASH
            ################

            case "rof_01": #node 603 - outside CS in ROF
                ### APPROACH ###
                if not self._pather.traverse_nodes([603], self, timeout=3): return False #calibrate after static path
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([603], self): return False #calibrate after looting


            case "rof_02": #node 604 - inside ROF
                ### APPROACH ###
                if not self._pather.traverse_nodes([604], self, timeout=3): return False  #threshold=0.8 (ex 601)
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            case "entrance_hall_01": ##static_path "diablo_entrance_hall_1", node 677, CS Entrance Hall1
                ### APPROACH ###
                self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self) # 604 -> 671 Hall1
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            case "entrance_hall_02":  #node 670,671, CS Entrance Hall1, CS Entrance Hall1
                ### APPROACH ###
                if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
                self._pather.traverse_nodes_fixed("diablo_entrance_1_670_672", self) # 604 -> 671 Hall1
                if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([671], self): return False # calibrate before static path
                self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self) # 671 -> LC Hall2



            # TRASH LAYOUT A

            case "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([673], self): return False # , timeout=3): # Re-adjust itself and continues to attack

            case "entrance1_02": #node 673
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) # Moves char to postion close to node 674 continues to attack
                if not self._pather.traverse_nodes([674], self): return False#, timeout=3)

            case "entrance1_03": #node 674
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([675], self): return False#, timeout=3) # Re-adjust itself
                self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) #static path to get to be able to spot 676
                if not self._pather.traverse_nodes([676], self): return False#, timeout=3)

            case "entrance1_04": #node 676- Hall3
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            # TRASH LAYOUT B

            case "entrance2_01": #static_path "diablo_entrance_hall_2"
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            case "entrance2_02": #node 682
                ### APPROACH ###
                #if not self._pather.traverse_nodes([682], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            case "entrance2_03": #node 683
                ### APPROACH ###
                #if not self._pather.traverse_nodes([682], self): return False # , timeout=3):
                #self._pather.traverse_nodes_fixed("diablo_entrance2_1", self)
                #if not self._pather.traverse_nodes([683], self): return False # , timeout=3):
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top1", self) #pull mobs from top
                wait (0.2, 0.5)
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top2", self) #pull mobs from top
                if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            case "entrance2_04": #node 686 - Hall3
                ### APPROACH ###
                if not self._pather.traverse_nodes([605], self): return False#, timeout=3)
                #if not self._pather.traverse_nodes([683,684], self): return False#, timeout=3)
                #self._pather.traverse_nodes_fixed("diablo_entrance2_2", self)
                #if not self._pather.traverse_nodes([685,686], self): return False#, timeout=3)
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_hall3", self)
                if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
                self._pather.traverse_nodes_fixed("diablo_trash_b_hall3_pull_609", self)
                if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([609], self): return False#, timeout=3)
                self._cs_pickit()
                if not self._pather.traverse_nodes([609], self): return False#, timeout=3)

            ####################
            # PENT TRASH TO SEAL
            ####################

            case "dia_trash_a" | "dia_trash_b" | "dia_trash_c": #trash before between Pentagramm and Seal A Layoutcheck
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            ###############
            # LAYOUT CHECKS
            ###############

            case "layoutcheck_a" | "layoutcheck_b" | "layoutcheck_c": #layout check seal A, node 619 A1-L, node 620 A2-Y
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            ##################
            # PENT BEFORE SEAL
            ##################

            case "pent_before_a": #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "pent_before_b" | "pent_before_c": #node 602, pentagram, before CTA buff & depature to layout check
                ### APPROACH ###
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            ###########
            # SEAL A1-L
            ###########

            case "A1-L_01":  #node 611 seal layout A1-L: safe_dist
                ### APPROACH ###
                if not self._pather.traverse_nodes([611], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                # we loot at boss

            case "A1-L_02":  #node 612 seal layout A1-L: center
                ### APPROACH ###
                if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                # we loot at boss

            case "A1-L_03":  #node 613 seal layout A1-L: fake_seal
                ### APPROACH ###
                if not self._pather.traverse_nodes([613], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()

            case "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
                ### APPROACH ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([614], self): return False
                ### ATTACK ###
                self._activate_redemption_aura()
                ### LOOT ###
                # we loot at boss

            case "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
                ### APPROACH ###
                if not self._pather.traverse_nodes([613, 615], self): return False # , timeout=3):
                ### ATTACK ###
                self._activate_redemption_aura()
                ### LOOT ###
                # we loot at boss

            ###########
            # SEAL A2-Y
            ###########

            case "A2-Y_01":  #node 622 seal layout A2-Y: safe_dist
                ### APPROACH ###
                if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
                Logger.debug("A2-Y: Hop!")
                #if not self._pather.traverse_nodes([622], self): return False # , timeout=3):
                if not self._pather.traverse_nodes([622], self): return False
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                # we loot at boss

            case "A2-Y_02":  #node 623 seal layout A2-Y: center
                ### APPROACH ###
                # if not self._pather.traverse_nodes([623,624], self): return False #
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                # we loot at boss

            case "A2-Y_03": #skipped
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "A2-Y_seal1":  #node 625 seal layout A2-Y: fake seal
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                if not self._pather.traverse_nodes([625], self): return False # , timeout=3):
                self._activate_redemption_aura()

            case "A2-Y_seal2":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
                self._activate_redemption_aura()

            ###########
            # SEAL B1-S
            ###########

            case "B1-S_01" | "B1-S_02" | "B1-S_03":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "B1-S_seal2": #B only has 1 seal, which is the boss seal = seal2
                ### APPROACH ###
                if not self._pather.traverse_nodes([634], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###


            ###########
            # SEAL B2-U
            ###########

            case "B2-U_01" | "B2-U_02" | "B2-U_03":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "B2-U_seal2": #B only has 1 seal, which is the boss seal = seal2
                ### APPROACH ###
                self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
                if not self._pather.traverse_nodes([644], self): return False # , timeout=3):
                ### ATTACK ###
                self._activate_redemption_aura()
                ### LOOT ###
                # we loot at boss


            ###########
            # SEAL C1-F
            ###########

            case "C1-F_01" | "C1-F_02" | "C1-F_03":
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "C1-F_seal1":
                ### APPROACH ###
                wait(0.1,0.3)
                self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self)
                wait(0.1,0.3)
                if not self._pather.traverse_nodes([655], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([655], self): return False # , timeout=3):
                self._activate_redemption_aura()

            case "C1-F_seal2":
                ### APPROACH ###
                self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
                if not self._pather.traverse_nodes([652], self): return False # , timeout=3):
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([652], self): return False # , timeout=3):
                self._activate_redemption_aura()

            ###########
            # SEAL C2-G
            ###########

            case "C2-G_01" | "C2-G_02" | "C2-G_03": #skipped
                ### APPROACH ###
                ### ATTACK ###
                ### LOOT ###
                # we loot at boss
                Logger.debug("No attack choreography available in fohdin.py for this node " + location + " - skipping to shorten run.")

            case "C2-G_seal1":
                ### APPROACH ###
                if not self._pather.traverse_nodes([663, 662], self) or not self._pather.traverse_nodes_fixed("dia_c2g_lc_661", self):
                    return False
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                if not self._pather.traverse_nodes([662], self): return False
                self._activate_redemption_aura()


            case "C2-G_seal2":
                ### APPROACH ###
                # Killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals
                seal_layout="C2-G"
                if not self._pather.traverse_nodes([662], self) or not self._pather.traverse_nodes_fixed("dia_c2g_663", self):
                    return False
                ### ATTACK ###
                atk_dur_min = Config().char["atk_len_diablo_infector"]
                atk_dur_max = atk_dur_min * 3
                Logger.debug(seal_layout + ": Attacking Infector at position 1/2")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if not self._pather.traverse_nodes([663], self): return False # , timeout=3):
                Logger.debug(seal_layout + ": Attacking Infector at position 2/2")
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                ### LOOT ###
                self._cs_pickit(skip_inspect=True) # inspect on other
                if not self._pather.traverse_nodes([664, 665], self): return False # , timeout=3):

            case _:
                ### APPROACH ###
                Logger.error("No location argument given for kill_cs_trash(" + location + "), should not happen")
                ### ATTACK ###
                self._cs_trash_mobs_attack_sequence()
                ### LOOT ###
                self._cs_pickit()
                return True


    def kill_vizier(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_vizier"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "A1-L":
                ### APPROACH ###
                if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
                ### ATTACK ###
                Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
                self._pather.traverse_nodes([611], self, timeout=3)
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                ### LOOT ###
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([612], self): return False # , timeout=3):
                self._activate_cleanse_redemption()
                self._cs_pickit()
                if not self._pather.traverse_nodes([612], self): return False # , timeout=3): # recalibrate after loot

            case "A2-Y":
                ### APPROACH ###
                if not self._pather.traverse_nodes([627, 622], self): return False # , timeout=3):
                ### ATTACK ###
                Logger.debug(seal_layout + ": Attacking Vizier at position 1/3")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                Logger.debug(seal_layout + ": Attacking Vizier at position 2/3")
                self._pather.traverse_nodes([623], self, timeout=3)
                self._cs_attack_sequence(min_duration=1.5, max_duration=atk_dur_max)
                Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
                if not self._pather.traverse_nodes([624], self): return False
                self._cs_attack_sequence(min_duration=1.5, max_duration=atk_dur_max)
                ### LOOT ###
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([624], self): return False
                if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
                Logger.debug(seal_layout + ": Hop!")
                self._activate_cleanse_redemption()
                if not self._pather.traverse_nodes([622], self): return False #, timeout=3):
                self._activate_redemption_aura()
                self._cs_pickit()
                if not self._pather.traverse_nodes([622], self): return False # , timeout=3): #recalibrate after loot

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_vizier("+ seal_layout +"), should not happen.")
                return False
        return True


    def kill_deseis(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_deseis"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "B1-S":
                ### APPROACH ###
                self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis_foh", self)
                nodes = [631]
                ### ATTACK ###
                Logger.debug(f"{seal_layout}: Attacking De Seis at position 1/{len(nodes)+1}")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                for i, node in enumerate(nodes):
                    Logger.debug(f"{seal_layout}: Attacking De Seis at position {i+2}/{len(nodes)+1}")
                    self._pather.traverse_nodes([node], self, timeout=3)
                    self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._activate_redemption_aura(delay=[1, 2])
                #if Config().general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/info_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                ### LOOT ###
                self._cs_pickit()

            case "B2-U":
                ### APPROACH ###
                self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
                #self._pather.traverse_nodes_fixed("dia_b2u_seal_deseis", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
                nodes = [646, 641]
                ### ATTACK ###
                Logger.debug(seal_layout + ": Attacking De Seis at position 1/{len(nodes)+1}")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                for i, node in enumerate(nodes):
                    Logger.debug(f"{seal_layout}: Attacking De Seis at position {i+2}/{len(nodes)+1}")
                    self._pather.traverse_nodes([node], self, timeout=3)
                    self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                #if Config().general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/info_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                ### LOOT ###
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([641], self): return False # , timeout=3):
                if not self._pather.traverse_nodes([646], self): return False # , timeout=3):
                self._cs_pickit(skip_inspect=True)
                if not self._pather.traverse_nodes([646], self): return False # , timeout=3):
                if not self._pather.traverse_nodes([640], self): return False # , timeout=3):
                self._cs_pickit()

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
                return False
        return True


    def kill_infector(self, seal_layout:str) -> bool:
        atk_dur_min = Config().char["atk_len_diablo_infector"]
        atk_dur_max = atk_dur_min * 3
        match seal_layout:
            case "C1-F":
                ### APPROACH ###
                ### ATTACK ###
                Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                self._pather.traverse_nodes_fixed("dia_c1f_652", self)
                Logger.debug(seal_layout + ": Attacking Infector at position 2/2")
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                ### LOOT ###
                self._cs_pickit()

            case "C2-G":
                ### APPROACH ###
                if not self._pather.traverse_nodes([665], self): return False # , timeout=3):
                ### ATTACK ###
                Logger.debug(seal_layout + ": Attacking Infector at position 1/2")
                self._cs_attack_sequence(min_duration=atk_dur_min, max_duration=atk_dur_max)
                if not self._pather.traverse_nodes([663], self): return False # , timeout=3):
                Logger.debug(seal_layout + ": Attacking Infector at position 2/2")
                self._cs_attack_sequence(min_duration=2, max_duration=atk_dur_max)
                ### LOOT ###
                self._cs_pickit()

            case _:
                Logger.warning(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
                return False
        return True


    #no aura effect on dia. not good for mob detection
    def kill_diablo(self) -> bool:
        ### APPROACH ###
        ### ATTACK ###
        atk_len_dur = float(Config().char["atk_len_diablo"])
        Logger.debug("Attacking Diablo at position 1/1")
        diablo_abs = [100,-100] #hardcoded dia pos.
        self._generic_foh_attack_sequence(default_target_abs=diablo_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, aura="concentration", foh_to_holy_bolt_ratio=2)
        self._activate_cleanse_redemption()
        ### LOOT ###
        #self._cs_pickit()
        return True