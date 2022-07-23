import time

from utils.custom_mouse import mouse
from char.paladin import Paladin
from config import Config
from health_manager import set_panel_check_paused
from inventory.personal import inspect_items
from logger import Logger
from pather import Location
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from target_detect import get_visible_targets
from utils.misc import wait

class FoHdin(Paladin):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up FoHdin")
        super().__init__(*args, **kwargs)
        self._pather.adapt_path((Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS), [220, 221, 222, 903, 904, 905, 906])

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float, aura: str = "concentration"):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def _cast_hammers(
        self,
        max_duration: float = 0,
        aura: str = "concentration"
    ): #for nihlathak
        return self._cast_at_position(skill_name = "blessed_hammer", spray = 0, spread_deg=0, max_duration = max_duration, aura = aura)

    def _cast_foh(
        self,
        cast_pos_abs: tuple[float, float],
        spray: float = 10,
        spread_deg: float = 10,
        min_duration: float = 0,
        max_duration: float = 0,
        teleport_frequency: float = 0,
        use_target_detect: bool = False,
        aura: str = "conviction",
    ):
        return self._cast_at_position(skill_name = "foh", cast_pos_abs = cast_pos_abs, spray = spray, spread_deg = spread_deg, min_duration = min_duration, max_duration = max_duration, use_target_detect = use_target_detect, teleport_frequency = teleport_frequency, aura = aura)

    def _cast_holy_bolt(
        self,
        cast_pos_abs: tuple[float, float],
        spray: float = 10,
        spread_deg: float = 10,
        max_duration: float = 0,
        aura: str = "concentration",
    ):
        return self._cast_at_position(skill_name = "holy_bolt", cast_pos_abs = cast_pos_abs, spray = spray, spread_deg = spread_deg, max_duration = max_duration, aura = aura)

    def _generic_foh_attack_sequence(
        self,
        cast_pos_abs: tuple[int, int] = (0, 0),
        min_duration: float = 0,
        max_duration: float = 15,
        spray: float = 20,
        spread_deg: float = 10,
        aura: str = "conviction"
    ) -> bool:
        # custom FOH alternating with holy bolt routine
        if Config().char["faster_cast_rate"] >= 75:
            self._activate_conviction_aura()
            self._stand_still(True)
            start = time_of_last_tp = time.perf_counter()
            # cast while time is less than max duration
            while (elapsed_time := time.perf_counter() - start) < max_duration:
                targets = get_visible_targets()
                if targets:
                    pos_abs = targets[0].center_abs
                    pos_abs = self._randomize_position(pos_abs = pos_abs, spray = 5, spread_deg = 0)
                # otherwise, use the given position with randomization parameters
                else:
                    pos_abs = self._randomize_position(cast_pos_abs, spray = spray, spread_deg = spread_deg)
                pos_m = convert_abs_to_monitor(pos_abs)
                mouse.move(*pos_m, delay_factor= [0.4, 0.6])
                # at frame 0, press key
                # frame 1-6 startup of FOH
                # frame 6 can cast HB
                # frame 15 FOH able to be cast again
                # frame 16 FOH startup
                self._send_skill("foh", hold_time=3/25, cooldown=False)
                time.sleep(2/25) #total of 5 frame startup
                self._send_skill("holy_bolt", hold_time=8/25, cooldown=False) # now at frame 6
                time.sleep(2/25) # now at frame 15
                # if teleport frequency is set, teleport every teleport_frequency seconds
                if (elapsed_time - time_of_last_tp) >= 3.5:
                    self._teleport_to_origin()
                    time_of_last_tp = elapsed_time
                # if target detection is enabled and minimum time has elapsed and no targets remain, end casting
                if (elapsed_time > min_duration) and not targets:
                    break
            self._stand_still(False)
        else:
            self._cast_at_position(skill_name = "foh", cast_pos_abs = cast_pos_abs, spray = spray, spread_deg = spread_deg, min_duration = min_duration, max_duration = max_duration, teleport_frequency = 3.5, use_target_detect = True, aura = aura)
        return True

    #FOHdin Attack Sequence Optimized for trash
    def _cs_attack_sequence(self, min_duration: float, max_duration: float):
        self._generic_foh_attack_sequence(cast_pos_abs=(0, 0), min_duration = min_duration, max_duration = max_duration, spread_deg=100)
        self._activate_redemption_aura()

    def _cs_trash_mobs_attack_sequence(self):
        self._cs_attack_sequence(min_duration = Config().char["atk_len_cs_trashmobs"], max_duration = Config().char["atk_len_cs_trashmobs"]*3)

    def _cs_pickit(self, skip_inspect: bool = False):
        new_items = self._pickit.pick_up_items(self)
        self._picked_up_items |= new_items
        if not skip_inspect and new_items:
            wait(1)
            set_panel_check_paused(True)
            inspect_items(grab(), ignore_sell=True)
            set_panel_check_paused(False)


    def kill_pindle(self) -> bool:
        atk_len_dur = float(Config().char["atk_len_pindle"])
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])

        if (self.capabilities.can_teleport_natively or self.capabilities.can_teleport_with_charges) and self._use_safer_routines:
            # Slightly retreating, so the Merc gets charged
            if not self._pather.traverse_nodes([102], self, timeout=1.0, force_move=True, force_tp=False):
                return False
            # Doing one Teleport to safe_dist to grab our Merc
            Logger.debug("Teleporting backwards to let Pindle charge the MERC. Looks strange, but is intended!") #I would leave this message in, so users dont complain that there is a strange movement pattern.
            if not self._pather.traverse_nodes([103], self, timeout=1.0, force_tp=True):
                return False
            # Slightly retreating, so the Merc gets charged
            if not self._pather.traverse_nodes([103], self, timeout=1.0, force_move=True, force_tp=False):
                return False
        else:
            self._pather.traverse_nodes([103], self, timeout=1.0, active_skill="conviction")

        cast_pos_abs = (pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9)
        self._generic_foh_attack_sequence(cast_pos_abs=cast_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, spray = 20)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            self._activate_redemption_aura()
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0)

        # Use target-based attack sequence one more time before pickit
        self._generic_foh_attack_sequence(cast_pos_abs=cast_pos_abs, max_duration=atk_len_dur, spray=11)
        self._activate_cleanse_redemption()

        return True


    def kill_council(self) -> bool:
        atk_len_dur = float(Config().char["atk_len_trav"])

        # traverse to nodes and attack
        nodes = [225, 226, 300]
        for i, node in enumerate(nodes):
            self._pather.traverse_nodes([node], self, timeout=2.2, do_pre_move = False, force_tp=(i > 0))
            cast_pos_abs = self._pather.find_abs_node_pos(node, img := grab()) or self._pather.find_abs_node_pos(906, img) or (-50, -50)
            self._generic_foh_attack_sequence(cast_pos_abs=cast_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, spray=80)

        # return to 226 and prepare for pickit
        self._pather.traverse_nodes([226], self, timeout=2.2, do_pre_move = False, force_tp=True)
        cast_pos_abs = self._pather.find_abs_node_pos(226, img := grab()) or self._pather.find_abs_node_pos(906, img) or (-50, -50)
        self._generic_foh_attack_sequence(cast_pos_abs=cast_pos_abs, max_duration=atk_len_dur*3, spray=80)

        self._activate_cleanse_redemption()

        return True

    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        atk_len_dur = float(Config().char["atk_len_eldritch"])
        self._generic_foh_attack_sequence(cast_pos_abs=eld_pos_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, spray=70)
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=0.1)
        # check mobs one more time before pickit
        self._generic_foh_attack_sequence(cast_pos_abs=eld_pos_abs, max_duration=atk_len_dur, spray=70)
        self._activate_cleanse_redemption()

        return True


    def kill_shenk(self):
        atk_len_dur = float(Config().char["atk_len_shenk"])

        # traverse to shenk
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.0, force_tp=True, active_skill="conviction")
        wait(0.05, 0.1)

        # bypass mob detect first
        self._cast_foh((0, 0), spray=11, min_duration = 2, aura = "conviction", use_target_detect=False)
        # then do generic mob detect sequence
        diff = atk_len_dur if atk_len_dur <= 2 else (atk_len_dur - 2)
        self._generic_foh_attack_sequence(min_duration=atk_len_dur - diff, max_duration=atk_len_dur*3 - diff, spray=10)
        self._activate_cleanse_redemption()

        return True


    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        atk_len_dur = Config().char["atk_len_nihlathak"]
        # Move close to nihlathak
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        if self._get_hotkey("blessed_hammer"):
            self._cast_hammers(atk_len_dur/4)
            self._cast_hammers(2*atk_len_dur/4, "redemption")
            self._move_and_attack((30, 15), atk_len_dur/4, "redemption")
        else:
            Logger.warning("FOHDin without blessed hammer is not very strong vs. Nihlathak!")
            self._generic_foh_attack_sequence(min_duration=atk_len_dur/2, max_duration=atk_len_dur, spray=70, aura="redemption")
            self._generic_foh_attack_sequence(min_duration=atk_len_dur/2, max_duration=atk_len_dur, spray=70, aura="redemption")
        self._generic_foh_attack_sequence(max_duration=atk_len_dur*2, spray=70)
        self._activate_cleanse_redemption()
        return True

    def kill_summoner(self) -> bool:
        # Attack
        atk_len_dur = Config().char["atk_len_arc"]
        self._generic_foh_attack_sequence(min_duration=atk_len_dur, max_duration=atk_len_dur*2, spray=80)
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
        self._generic_foh_attack_sequence(cast_pos_abs=diablo_abs, min_duration=atk_len_dur, max_duration=atk_len_dur*3, aura="concentration", foh_to_holy_bolt_ratio=2)
        self._activate_cleanse_redemption()
        ### LOOT ###
        #self._cs_pickit()
        return True

if __name__ == "__main__":
    import os
    from config import Config
    from char.paladin import FoHdin
    from pather import Pather
    from item.pickit import PickIt
    import keyboard
    from logger import Logger
    from screen import start_detecting_window, stop_detecting_window

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    start_detecting_window()
    print("Move to d2r window and press f11")
    print("Press F9 to test attack sequence")
    keyboard.wait("f11")

    pather = Pather()
    pickit = PickIt()
    char = FoHdin(Config().fohdin, pather, pickit)

    char.discover_capabilities()

    def routine():
        char._key_press(char._get_hotkey("foh"), hold_time=4/25)
        time.sleep(1/25) #total of 5 frame startup
        char._key_press(char._get_hotkey("holy_bolt"), hold_time=(1/25))
        char._key_press(char._get_hotkey("foh"), hold_time=(3))
        # for _ in range(0, 10):
        #     char._key_press(char._get_hotkey("foh"), hold_time=(0.1))
        #     time.sleep(0.3)

    keyboard.add_hotkey('f9', lambda: routine())
    while True:
        wait(0.01)
