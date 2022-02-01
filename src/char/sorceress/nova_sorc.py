import keyboard
import time
import random
import numpy as np
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
from pather import Location
import cv2


class NovaSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Nova Sorc")
        super().__init__(*args, **kwargs)
        # we want to change positions a bit of end points
        self._pather.offset_node(149, (70, 10))

    def _nova(self, time_in_s: float):
        if not self._skill_hotkeys["nova"]:
            raise ValueError("You did not set nova hotkey!")
        keyboard.send(self._skill_hotkeys["nova"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.03, 0.04)
            mouse.press(button="right")
            wait(0.12, 0.2)
            mouse.release(button="right")

    def _chain_lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: int = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["chain_lightning"]:
            keyboard.send(self._skill_hotkeys["chain_lightning"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.3, 0.6])
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _lightning(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: float = 10):
        if not self._skill_hotkeys["lightning"]:
            raise ValueError("You did not set lightning hotkey!")
        keyboard.send(self._skill_hotkeys["lightning"])
        for _ in range(3):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor, delay_factor=[0.3, 0.6])
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = self._screen.convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._nova(atk_len)

    def kill_pindle(self) -> bool:
        self._pather.traverse_nodes_fixed("pindle_end", self)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_pindle"])
        return True

    def kill_eldritch(self) -> bool:
        self._pather.traverse_nodes_fixed([(675, 30)], self)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_eldritch"])
        return True

    def kill_shenk(self) -> bool:
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0)
        self._cast_static(0.6)
        self._nova(self._char_config["atk_len_shenk"])
        return True

    def kill_council(self) -> bool:
        # Check out the node screenshot in assets/templates/trav/nodes to see where each node is at
        atk_len = self._char_config["atk_len_trav"] * 0.21
        # change node to be further to the right
        offset_229 = np.array([200, 100])
        self._pather.offset_node(229, offset_229)
        def clear_inside():
            self._pather.traverse_nodes_fixed([(1110, 120)], self)
            self._pather.traverse_nodes([229], self, time_out=0.8, force_tp=True)
            self._nova(atk_len)
            self._move_and_attack((-40, -20), atk_len)
            self._move_and_attack((40, 20), atk_len)
            self._move_and_attack((40, 20), atk_len)
        def clear_outside():
            self._pather.traverse_nodes([226], self, time_out=0.8, force_tp=True)
            self._nova(atk_len)
            self._move_and_attack((45, -20), atk_len)
            self._move_and_attack((-45, 20), atk_len)
        clear_inside()
        clear_outside()
        clear_inside()
        clear_outside()
        # change back node as it is used in trav.py
        self._pather.offset_node(229, -offset_229)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        atk_len = self._char_config["atk_len_nihlatak"] * 0.3
        # Move close to nilathak
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_static(0.6)
        self._nova(atk_len)
        self._move_and_attack((50, 25), atk_len)
        self._move_and_attack((-70, -35), atk_len)
        return True

    def kill_summoner(self) -> bool:
        # move mouse to below altar
        pos_m = self._screen.convert_abs_to_monitor((0, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # Attack
        self._nova(self._char_config["atk_len_arc"])
        # Move a bit back and another round
        self._move_and_attack((0, 80), self._char_config["atk_len_arc"] * 0.5)
        wait(0.1, 0.15)
        self._nova(self._char_config["atk_len_arc"] * 0.5)
        return True

     #-------------------------------------------------------------------------------#   
     # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
     #-------------------------------------------------------------------------------#
    
    def kill_cs_trash(self, location:str) -> bool:

        if location in [
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
            #"layoutcheck_b", #layout check seal B, node 634 B1-S, node 649 B2-U
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
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._picked_up_items |= self._pickit.pick_up_items(self)
                        
        
        elif location in [ #SKIP
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
            "layoutcheck_b", #layout check seal B, node 634 B1-S, node 649 B2-U
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
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)

        elif location == "A1-L_02":  #node 612 seal layout A1-L: center
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)

        elif location == "A1-L_03":  #node 613 seal layout A1-L: fake_seal
            if not self._pather.traverse_nodes([613], self): return False # , time_out=3):
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)

        elif location == "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False

        elif location == "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
            if not self._pather.traverse_nodes([613, 615], self): return False # , time_out=3):
                

        elif location == "A2-Y_01":  #node 622 seal layout A2-Y: safe_dist
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info("A2-Y: Hop!")
            #if not self._pather.traverse_nodes([622], self): return False # , time_out=3):
            if not self._pather.traverse_nodes([622], self): return False
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            #self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "A2-Y_02":  #node 623 seal layout A2-Y: center
            if not self._pather.traverse_nodes([623,624], self): return False # 
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            #self._picked_up_items |= self._pickit.pick_up_items(self)

        #elif location == "A2-Y_03": #skipped
    
        elif location == "A2-Y_seal1":  #node 625 seal layout A2-Y: fake seal
            if not self._pather.traverse_nodes([625], self): return False # , time_out=3):
        
        
        elif location == "A2-Y_seal2":
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            

        #elif location == "B1-S_01": #skipped
        #elif location == "B1-S_02": #skipped
        #elif location == "B1-S_03": #skipped

        elif location == "B1-S_seal2": 
            if not self._pather.traverse_nodes([634], self): return False # , time_out=3):
            


        #elif location == "B2-U_01": #skipped
        #elif location == "B2-U_02": #skipped
        #elif location == "B2-U_03": #skipped

        elif location == "B2-U_seal2": 
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            if not self._pather.traverse_nodes([644], self): return False # , time_out=3):
            
        

        #elif location == "C1-F_01": #skipped
        #elif location == "C1-F_02": #skipped
        #elif location == "C1-F_03": #skipped

        elif location == "C1-F_seal1":
            wait(0.1,0.3)
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) 
            wait(0.1,0.3)
            if not self._pather.traverse_nodes([655], self._char): return False # , time_out=3):
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([655], self): return False # , time_out=3):
            
        elif location == "C1-F_seal2":
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):


        #elif location == "C2-G_01": #skipped
        #elif location == "C2-G_02": #skipped
        #elif location == "C2-G_03": #skipped

        elif location == "C2-G_seal1":
            if not self._pather.traverse_nodes([663, 662], self): return False # , time_out=3):
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._picked_up_items |= self._pickit.pick_up_items(self)           

        elif location == "C2-G_seal2":
            #Kill Infector
            self._pather.traverse_nodes_fixed("dia_c2g_663", self)
            atk_len = self._char_config["atk_len_diablo_infector"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = 120, -72
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([664, 665], self): return False # , time_out=3):
            

        else:
            Logger.debug("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Throwing some random hammers")
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
    
    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            atk_len = self._char_config["atk_len_diablo_vizier"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = 120, 72
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([611], self, time_out=3)
            atk_len = self._char_config["atk_len_diablo_vizier"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = -120, -72
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
            #Logger.debug(seal_layout + ": Attacking Vizier at position 3/3 - i think we can skip this location, let me know if its useful")
            #self._pather.traverse_nodes([610], self, time_out=3)        
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3): # recalibrate after loot
            

        elif seal_layout == "A2-Y":
            if not self._pather.traverse_nodes([627, 622], self): return False # , time_out=3):
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            atk_len = self._char_config["atk_len_diablo_vizier"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = -120, 72
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([623], self, time_out=3)
            atk_len = self._char_config["atk_len_diablo_vizier"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = -120, 0
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
            Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
            if not self._pather.traverse_nodes([624], self): return False
            atk_len = self._char_config["atk_len_diablo_vizier"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = 120, -72
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
            wait(0.2, 0.3)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([624], self): return False 
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([622], self): return False #, time_out=3): 
            
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
            atk_len = self._char_config["atk_len_diablo_deseis"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = -120, 72
            for _ in range(int(atk_len * 2)):
                self._chain_lightning(cast_pos_abs, spray=45)
                self._lightning(cast_pos_abs, spray=45)
            """
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, time_out=3)
            atk_len = self._char_config["atk_len_diablo_deseis"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, time_out=3)
            atk_len = self._char_config["atk_len_diablo_deseis"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, time_out=3)
            atk_len = self._char_config["atk_len_diablo_deseis"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            """
            Logger.debug(seal_layout + ": Waiting with Redemption active to clear more corpses.")
            wait(2.5, 3.5)
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            self._picked_up_items |= self._pickit.pick_up_items(self)
            

        elif seal_layout == "B2-U":
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            nodes1 = [646]
            nodes2 = [646]
            nodes3 = [641]
            atk_len = self._char_config["atk_len_diablo_deseis"]
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = -120, -72
            for _ in range(int(atk_len * 2)):
                self._chain_lightning(cast_pos_abs, spray=45)
                self._lightning(cast_pos_abs, spray=45)
            """
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
        
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)            
            wait(0.2, 0.5)
            """
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
            atk_len = self._char_config["atk_len_diablo_infector"]
            # move mouse to center
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            cast_pos_abs = 120, 0
            for _ in range(int(atk_len)):
                self._chain_lightning(cast_pos_abs, spray=90)
                self._lightning(cast_pos_abs, spray=50)
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
        atk_len = self._char_config["atk_len_diablo"]
        # move mouse to center
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_static(0.6)
        self._nova(atk_len)
        cast_pos_abs = 120, -72
        for _ in range(int(atk_len)):
            self._chain_lightning(cast_pos_abs, spray=90)
            self._lightning(cast_pos_abs, spray=50)
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True

if __name__ == "__main__":
    import os
    import keyboard
    from screen import Screen
    from template_finder import TemplateFinder
    from pather import Pather
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = NovaSorc(config.nova_sorc, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
