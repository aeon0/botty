from cgitb import text
import keyboard
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
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
    def __init__(self, skill_hotkeys: dict, screen: Screen, template_finder: TemplateFinder, ui_manager: UiManager, pather: Pather, pickit: PickIt):
        Logger.info("Setting up Hammerdin")
        super().__init__(skill_hotkeys, screen, template_finder, ui_manager)
        self._pather = pather
        self._do_pre_move = True

        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo
        # <<<<<< MASTER MIGHT REQUIRE DELETION FROM HERE DUE TO THE NEW CAPABILITIES FEATURE. LEAVING IT IN FOR NOW
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if not self._skill_hotkeys["teleport"]:
            self._do_pre_move = False
        else:
            # we want to change positions of shenk and eld a bit to be more center for teleport
            self._pather.offset_node(149, (70, 10))
        # >>>>> MASTER MIGHT REQUIRE DELETION UP TO HERE HERE DUE TO THE NEW CAPABILITIES FEATURE. LEAVING IT IN FOR NOW

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

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if capabilities.can_teleport_natively:
            self._do_pre_move = False
        else:
            # we want to change positions of shenk and eld a bit to be more center for teleport
            self._pather.offset_node(149, (70, 10))

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not self._ui_manager.is_right_skill_selected(["VIGOR"])
        can_teleport = self.capabilities.can_teleport_natively and self._ui_manager.is_right_skill_active()
        if should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def kill_pindle(self) -> bool:
        wait(0.1, 0.15)
        if self.capabilities.can_teleport_natively:
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
        if self.capabilities.can_teleport_natively:
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
        self._pather.traverse_nodes([228, 229], self, time_out=2.5, force_tp=True, use_tp_charge=True)
        self._cast_hammers(atk_len)
        # Move a bit back and another round
        self._move_and_attack((40, 20), atk_len)
        # Here we have two different attack sequences depending if tele is available or not
        if self.capabilities.can_teleport_natively or self.capabilities.can_teleport_with_charges:
            # Back to center stairs and more hammers
            self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True, use_tp_charge=True)
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
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_hammers(self._char_config["atk_len_nihlathak"] * 0.4)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((30, 15), self._char_config["atk_len_nihlathak"] * 0.3)
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-30, -15), self._char_config["atk_len_nihlathak"] * 0.4)
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
    
    def kill_cs_trash(self, location:str) -> bool:

        if location in [ #KILL TRASH ACTIVE
            "sealdance", #if seal opening fails & trash needs to be cleared -> used at ANY seal
            ### ROF
            "rof_01", #static_path WP-> CS Entrance, outside CS Entrance
            "rof_02", #node 601, CS Entrance
            ### CS entrance
            "entrance_hall_01", #node 677, CS Entrance
            "entrance_hall_02", #static_path "diablo_entrance_hall_1", CS Entrance
            "entrance_hall_03", #node 670,671, CS Entrance
            ### layout 1
            "entrance1_01", #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            "entrance1_02", #node 673, CS Hall1/3 layout1
            "entrance1_03", #node 674, CS Hall2/3 layout1
            "entrance1_04", #node 676, CS Hall3/3 layout1
            ### layout 2
            "entrance2_01", #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            "entrance2_02", #node 682, CS Hall1/3 layout2
            "entrance2_03", #node 683, CS Hall2/3 layout2
            "entrance2_04", #node 686, CS Hall3/3 layout2
            ### Seal Trash
            "trash_a", #trash before between Pentagramm and Seal A Layoutcheck
            "trash_b", #trash before between Pentagramm and Seal A Layoutcheck
            "trash_c", #trash before between Pentagramm and Seal A Layoutcheck
            ### Pentagram
            #"pent_before_a", #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
            "pent_before_b", #node 602, pentagram, before CTA buff & depature to layout check 
            "pent_before_c", #node 602, pentagram, before CTA buff & depature to layout check
            ### Layout Checks
            #"layoutcheck_a", #layout check seal A, node 619 A1-L, node 620 A2-Y
            "layoutcheck_b", #layout check seal B, node 634 B1-S, node 649 B2-U
            #"layoutcheck_c", #layout check seal C, node 656 C1-F, node 664 C2-G
            ### A1-L
            #"A1-L_01",  #node 611 seal layout A1-L: approach
            #"A1-L_02",  #node 612 seal layout A1-L: safe_dist
            #"A1-L_03",  #node 613 seal layout A1-L: center, # you need to end your attack sequence at node [613] center
            #"A1-L_seal1", #node 614 layout A1-L: fake seal
            #"A1-L_seal2", #node 615 layout A1-L: boss seal
            ### A2-Y
            #"A2-Y_01", #node 622 seal layout A2-Y: safe_dist
            #"A2-Y_02", #node 623 seal layout A2-Y: center
            #"A2-Y_03", #node 624 seal layout A2-Y: seal fake far, you need to end your attack sequence at node [624] fake seal far
            #"A2-Y_seal1", #node 625 seal layout A2-Y: fake seal
            #"A2-Y_seal2", #static_path "dia_a2y_sealfake_sealboss" (at node 626) seal layout A2-Y: boss seal
            ### B1-S
            #"B1-S_01", # no movement
            #"B1-S_02", # no movement
            #"B1-S_03", # no movement, but you need to end your attack sequence at layout check node [634]
            #"B1-S_seal2", #node 634 layout B1-S: boss seal
            ### B2-U
            #"B2-U_01", # no movement
            #"B2-U_02", # no movement
            #"B2-U_03", # no movement, but you need to end your attack sequence at layout check node [649]
            #"B2-U_seal2", #node 644 layout B2-U: boss seal
            ### C1-F
            #"C1-F_01", # no movement
            #"C1-F_02", # no movement
            #"C1-F_03", # no movement, but you need to end your char attack sequence at layout check node [656]
            "C1-F_seal1", #static_path "dia_c1f_hop_fakeseal" C1-F: boss seal
            #"C1-F_seal2", #static_path "dia_c1f_654_651" C1-F: boss seal
            ### C2-G
            #"C2-G_01", # no movement
            #"C2-G_02", # no movement
            #"C2-G_03", # no movement, but you need to end your char attack sequence at layout check node [664]
            #"C2-G_seal1", #fake seal layout C2-G
            #"C2-G_seal2", #boss seal layout C2-G
            ]:        
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"]) # to keep redemption on for a couple of seconds before the next teleport to have more corpses cleared & increase chance to find next template
            self._picked_up_items |= self._pickit.pick_up_items(self)
                        
        
        elif location in [ #SKIP KILLING TRASH HERE
            #"sealdance", #if seal opening fails & trash needs to be cleared -> used at ANY seal
            ### ROF
            #"rof_01", #static_path WP-> CS Entrance, outside CS Entrance
            #"rof_02", #node 601, CS Entrance
            ### CS entrance
            #"entrance_hall_01", #node 677, CS Entrance
            #"entrance_hall_02", #static_path "diablo_entrance_hall_1", CS Entrance
            #"entrance_hall_03", #node 670,671, CS Entrance
            ### layout 1
            #"entrance1_01", #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            #"entrance1_02", #node 673, CS Hall1/3 layout1
            #"entrance1_03", #node 674, CS Hall2/3 layout1
            #"entrance1_04", #node 676, CS Hall3/3 layout1
            ### layout 2
            #"entrance2_01", #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            #"entrance2_02", #node 682, CS Hall1/3 layout2
            #"entrance2_03", #node 683, CS Hall2/3 layout2
            #"entrance2_04", #node 686, CS Hall3/3 layout2
            ### Seal Trash
            #"trash_a", #trash before between Pentagramm and Seal A Layoutcheck
            #"trash_b", #trash before between Pentagramm and Seal A Layoutcheck
            #"trash_c", #trash before between Pentagramm and Seal A Layoutcheck
            ### Pentagram
            "pent_before_a", #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
            #"pent_before_b", #node 602, pentagram, before CTA buff & depature to layout check 
            #"pent_before_c", #node 602, pentagram, before CTA buff & depature to layout check
            ### Layout Checks
            "layoutcheck_a", #layout check seal A, node 619 A1-L, node 620 A2-Y
            #"layoutcheck_b", #layout check seal B, node 634 B1-S, node 649 B2-U
            "layoutcheck_c", #layout check seal C, node 656 C1-F, node 664 C2-G
            ### A1-L
            #"A1-L_01",  #node 611 seal layout A1-L: approach
            #"A1-L_02",  #node 612 seal layout A1-L: safe_dist
            #"A1-L_03",  #node 613 seal layout A1-L: center, # you need to end your attack sequence at node [613] center
            #"A1-L_seal1", #node 614 layout A1-L: fake seal
            #"A1-L_seal2", #node 615 layout A1-L: boss seal
            ### A2-Y
            #"A2-Y_01", #node 622 seal layout A2-Y: safe_dist
            #"A2-Y_02", #node 623 seal layout A2-Y: center
            "A2-Y_03", #node 624 seal layout A2-Y: seal fake far, you need to end your attack sequence at node [624] fake seal far
            #"A2-Y_seal1", #node 625 seal layout A2-Y: fake seal
            #"A2-Y_seal2", #static_path "dia_a2y_sealfake_sealboss" (at node 626) seal layout A2-Y: boss seal
            ### B1-S
            "B1-S_01", # no movement
            "B1-S_02", # no movement
            "B1-S_03", # no movement, but you need to end your attack sequence at layout check node [634]
            #"B1-S_seal2", #node 634 layout B1-S: boss seal
            ### B2-U
            "B2-U_01", # no movement
            "B2-U_02", # no movement
            "B2-U_03", # no movement, but you need to end your attack sequence at layout check node [649]
            #"B2-U_seal2", #node 644 layout B2-U: boss seal
            ### C1-F
            "C1-F_01", # no movement
            "C1-F_02", # no movement
            "C1-F_03", # no movement, but you need to end your char attack sequence at layout check node [656]
            #"C1-F_seal1", #static_path "dia_c1f_hop_fakeseal" C1-F: boss seal
            #"C1-F_seal2", #static_path "dia_c1f_654_651" C1-F: boss seal
            ### C2-G
            "C2-G_01", # no movement
            "C2-G_02", # no movement
            "C2-G_03", # no movement, but you need to end your char attack sequence at layout check node [664]
            #"C2-G_seal1", #fake seal layout C2-G
            #"C2-G_seal2", #boss seal layout C2-G
            ]:  
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
        
        elif location == "A1-L_01":  #node 611 seal layout A1-L: safe_dist
            if not self._pather.traverse_nodes([611], self): return False # , time_out=3):
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])

        elif location == "A1-L_02":  #node 612 seal layout A1-L: center
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._cast_hammers(0.5, "cleansing")
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])

        elif location == "A1-L_03":  #node 613 seal layout A1-L: fake_seal
            if not self._pather.traverse_nodes([613], self): return False # , time_out=3):
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._cast_hammers(0.5, "cleansing")
            self._picked_up_items |= self._pickit.pick_up_items(self)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])

        elif location == "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            keyboard.send(self._skill_hotkeys["redemption"])

        elif location == "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
            if not self._pather.traverse_nodes([613, 615], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])


        elif location == "A2-Y_01":  #node 622 seal layout A2-Y: safe_dist
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info("A2-Y: Hop!")
            #if not self._pather.traverse_nodes([622], self): return False # , time_out=3):
            if not self._pather.traverse_nodes([622], self): return False
            keyboard.send(self._skill_hotkeys["redemption"])
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            #self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "A2-Y_02":  #node 623 seal layout A2-Y: center
            if not self._pather.traverse_nodes([623,624], self): return False # 
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            #self._picked_up_items |= self._pickit.pick_up_items(self)

        #elif location == "A2-Y_03": #skipped
    
        elif location == "A2-Y_seal1":  #node 625 seal layout A2-Y: fake seal
            if not self._pather.traverse_nodes([625], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])
        
        elif location == "A2-Y_seal2":
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            keyboard.send(self._skill_hotkeys["redemption"])

        #elif location == "B1-S_01": #skipped
        #elif location == "B1-S_02": #skipped
        #elif location == "B1-S_03": #skipped

        elif location == "B1-S_seal2": 
            if not self._pather.traverse_nodes([634], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])


        #elif location == "B2-U_01": #skipped
        #elif location == "B2-U_02": #skipped
        #elif location == "B2-U_03": #skipped

        elif location == "B2-U_seal2": 
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            if not self._pather.traverse_nodes([644], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])
        

        #elif location == "C1-F_01": #skipped
        #elif location == "C1-F_02": #skipped
        #elif location == "C1-F_03": #skipped

        elif location == "C1-F_seal1":
            wait(0.1,0.3)
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) 
            wait(0.1,0.3)
            if not self._pather.traverse_nodes([655], self._char): return False # , time_out=3):
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([655], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])
            
        elif location == "C1-F_seal2":
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])


        #elif location == "C2-G_01": #skipped
        #elif location == "C2-G_02": #skipped
        #elif location == "C2-G_03": #skipped

        elif location == "C2-G_seal1":
            if not self._pather.traverse_nodes([663, 662], self): return False # , time_out=3):
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
            keyboard.send(self._skill_hotkeys["redemption"])

        elif location == "C2-G_seal2":
            # Killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals
            seal_layout="C2-G"
            self._pather.traverse_nodes_fixed("dia_c2g_663", self)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
            self._cast_hammers(self._char_config["atk_len_diablo_infector"] * 0.4)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"] * 0.3)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"] * 0.4)
            wait(0.1, 0.15)
            self._cast_hammers(1.2, "redemption")
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([664, 665], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])

        else:
            Logger.debug("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Throwing some random hammers")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
    
    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([611], self, time_out=3)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"]) # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
            self._cast_hammers(1, "redemption")
            #Logger.debug(seal_layout + ": Attacking Vizier at position 3/3 - i think we can skip this location, let me know if its useful")
            #self._pather.traverse_nodes([610], self, time_out=3)
            #self._move_and_attack((0, 0), self._char_config["atk_len_diablo_vizier"]) # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
            #wait(0.1, 0.15)
            #self._cast_hammers(2, "redemption")
            #self._cast_hammers(1, "cleansing")
            keyboard.send(self._skill_hotkeys["cleansing"])
            wait(0.1, 0.2)
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3): # recalibrate after loot
            

        elif seal_layout == "A2-Y":
            if not self._pather.traverse_nodes([627, 622], self): return False # , time_out=3):
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([623], self, time_out=3)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
            if not self._pather.traverse_nodes([624], self): return False
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_vizier"] * 0.5)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_vizier"])
            wait(0.1, 0.15)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1, "cleansing")
            keyboard.send(self._skill_hotkeys["redemption"]) # to keep redemption on for a couple of seconds before the next teleport to have more corpses cleared & increase chance to find next template
            wait(0.2, 0.3)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([624], self): return False 
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([622], self): return False #, time_out=3): 
            keyboard.send(self._skill_hotkeys["redemption"])
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([622], self): return False # , time_out=3): #recalibrate after loot
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True

    def kill_deseis(self, seal_layout:str) -> bool:
        if seal_layout == "B1-S":
            self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
            nodes1 = [632]
            nodes2 = [631]
            nodes3 = [632]
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, time_out=3)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, time_out=3)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"] * 0.5)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, time_out=3)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])  # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
            wait(0.1, 0.2)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1, "cleansing")
            keyboard.send(self._skill_hotkeys["redemption"]) # to keep redemption on for a couple of seconds before the next teleport to have more corpses cleared & increase chance to find next template
            Logger.debug(seal_layout + ": Waiting with Redemption active to clear more corpses.")
            wait(2.5, 3.5)
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            self._picked_up_items |= self._pickit.pick_up_items(self)
            

        elif seal_layout == "B2-U":
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            #self._pather.traverse_nodes_fixed("dia_b2u_seal_deseis", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            nodes1 = [640]
            nodes2 = [646]
            nodes3 = [641]
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, time_out=3)
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._move_and_attack((-30, -15), self._char_config["atk_len_diablo_deseis"] * 0.2)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, time_out=3)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"] * 0.5)
            self._cast_hammers(1, "redemption")
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, time_out=3)
            self._move_and_attack((0, 0), self._char_config["atk_len_diablo_deseis"])  # no factor, so merc is not reset by teleport and he his some time to move & kill stray bosses
            wait(0.1, 0.2)
            self._cast_hammers(2, "redemption")
            self._cast_hammers(1, "cleansing")
            keyboard.send(self._skill_hotkeys["redemption"]) # to keep redemption on for a couple of seconds before the next teleport to have more corpses cleared & increase chance to find next template
            wait(0.2, 0.5)
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([641], self): return False # , time_out=3):
            if not self._pather.traverse_nodes([646], self): return False # , time_out=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([646], self): return False # , time_out=3):
            if not self._pather.traverse_nodes([640], self): return False # , time_out=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True 


    def kill_infector(self, seal_layout:str) -> bool:
        if seal_layout == "C1-F":
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
            self._cast_hammers(self._char_config["atk_len_diablo_infector"] * 0.4)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"] * 0.3)
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"] * 0.4)
            wait(0.1, 0.15)
            self._cast_hammers(1.2, "redemption")
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif seal_layout == "C2-G":
            # NOT killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals his attack sequence can be found in C2-G_seal2
            Logger.debug(seal_layout + ": No need for attacking Infector at position 1/1 - he was killed during clearing the seal")
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
            return False 
        return True


    def kill_diablo(self) -> bool:
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        Logger.debug("Attacking Diablo at position 1/1")
        self._cast_hammers(self._char_config["atk_len_diablo"])
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((60, 30), self._char_config["atk_len_diablo"])
        self._cast_hammers(0.8, "redemption")
        self._move_and_attack((-60, -30), self._char_config["atk_len_diablo"])
        wait(0.1, 0.15)
        self._cast_hammers(1.2, "redemption")
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen()
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather)
