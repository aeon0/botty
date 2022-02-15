import keyboard
import time
import random
import numpy as np
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
from pather import Location
from item.pickit import PickIt #for Diablo

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

    #for Diablo
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

    #for Diablo
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

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        atk_len = self._char_config["atk_len_nihlathak"] * 0.3
        # Move close to nihlathak
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

    ########################################################################################   
    # Chaos Sanctuary, Trash, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
    ########################################################################################
    
    def kill_cs_trash(self, location:str) -> bool:
    
        ###########
        # SEALDANCE
        ###########
        
        if location == "sealdance": #if seal opening fails & trash needs to be cleared -> used at ANY seal
            ### APPROACH 
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        ################
        # CLEAR CS TRASH
        ################
        
        elif location == "rof_01": #node 603 - outside CS in ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([603], self, time_out=3): return False #calibrate after static path
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([603], self): return False #calibrate after looting

            
        elif location == "rof_02": #node 604 - inside ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([604], self, time_out=3): return False  #threshold=0.8 (ex 601)
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "entrance_hall_01": ##static_path "diablo_entrance_hall_1", node 677, CS Entrance Hall1
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self) # 604 -> 671 Hall1
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "entrance_hall_02":  #node 670,671, CS Entrance Hall1, CS Entrance Hall1
            ### APPROACH ###
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            self._pather.traverse_nodes_fixed("diablo_entrance_1_670_672", self) # 604 -> 671 Hall1
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            #Move to Layout Check
            if not self._pather.traverse_nodes([671], self): return False # calibrate before static path
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self) # 671 -> LC Hall2
            


        # TRASH LAYOUT A

        elif location == "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([673], self): return False # , time_out=3): # Re-adjust itself and continues to attack

        elif location == "entrance1_02": #node 673
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) # Moves char to postion close to node 674 continues to attack
            if not self._pather.traverse_nodes([674], self): return False#, time_out=3)

        elif location == "entrance1_03": #node 674
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([675], self): return False#, time_out=3) # Re-adjust itself
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) #static path to get to be able to spot 676
            if not self._pather.traverse_nodes([676], self): return False#, time_out=3)

        elif location == "entrance1_04": #node 676- Hall3
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        # TRASH LAYOUT B

        elif location == "entrance2_01": #static_path "diablo_entrance_hall_2"
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_02": #node 682
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , time_out=3):
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_right", self) #pull mobs from the right
            wait (0.2, 0.5)
            if not self._pather.traverse_nodes([605], self): return False#, time_out=3)
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_03": #node 683
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , time_out=3):
            #self._pather.traverse_nodes_fixed("diablo_entrance2_1", self)
            #if not self._pather.traverse_nodes([683], self): return False # , time_out=3):
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top1", self) #pull mobs from top
            wait (0.2, 0.5)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_top2", self) #pull mobs from top
            if not self._pather.traverse_nodes([605], self): return False#, time_out=3)
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_04": #node 686 - Hall3
            ### APPROACH ###
            if not self._pather.traverse_nodes([605], self): return False#, time_out=3)
            #if not self._pather.traverse_nodes([683,684], self): return False#, time_out=3)
            #self._pather.traverse_nodes_fixed("diablo_entrance2_2", self)
            #if not self._pather.traverse_nodes([685,686], self): return False#, time_out=3)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_hall3", self)
            if not self._pather.traverse_nodes([609], self): return False#, time_out=3)
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall3_pull_609", self)
            if not self._pather.traverse_nodes([609], self): return False#, time_out=3)
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"]
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((-50, -150), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._move_and_attack((50, 150), self._char_config["atk_len_cs_trashmobs"] * 0.2)
            self._move_and_attack((250, -150), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._move_and_attack((-250, -150), self._char_config["atk_len_cs_trashmobs"] * 0.2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([609], self): return False#, time_out=3)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([609], self): return False#, time_out=3)

        ####################
        # PENT TRASH TO SEAL
        ####################

        elif location == "dia_trash_a": #trash before between Pentagramm and Seal A Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "dia_trash_b": #trash before between Pentagramm and Seal B Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "dia_trash_c": ##trash before between Pentagramm and Seal C Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ###############
        # LAYOUT CHECKS
        ###############

        elif location == "layoutcheck_a": #layout check seal A, node 619 A1-L, node 620 A2-Y
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "layoutcheck_b": #layout check seal B, node 634 B1-S, node 649 B2-U
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "layoutcheck_c": #layout check seal C, node 656 C1-F, node 664 C2-G
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ##################
        # PENT BEFORE SEAL
        ##################

        elif location == "pent_before_a": #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
        
        elif location == "pent_before_b": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        
        elif location == "pent_before_c": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ###########
        # SEAL A1-L
        ###########

        elif location == "A1-L_01":  #node 611 seal layout A1-L: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes([611], self): return False # , time_out=3):
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_02":  #node 612 seal layout A1-L: center
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_03":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613], self): return False # , time_out=3):
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613, 615], self): return False # , time_out=3):
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss

        ###########
        # SEAL A2-Y
        ###########

        elif location == "A2-Y_01":  #node 622 seal layout A2-Y: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info("A2-Y: Hop!")
            #if not self._pather.traverse_nodes([622], self): return False # , time_out=3):
            if not self._pather.traverse_nodes([622], self): return False
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_02":  #node 623 seal layout A2-Y: center
            ### APPROACH ###
            # if not self._pather.traverse_nodes([623,624], self): return False # 
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_03": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
    
        elif location == "A2-Y_seal1":  #node 625 seal layout A2-Y: fake seal
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            if not self._pather.traverse_nodes([625], self): return False # , time_out=3):
        
        elif location == "A2-Y_seal2":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues

        ###########
        # SEAL B1-S
        ###########

        elif location == "B1-S_01": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_02": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_03": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B1-S_seal2": #B only has 1 seal, which is the boss seal = seal2
            ### APPROACH ###
            if not self._pather.traverse_nodes([634], self): return False # , time_out=3):
            ### ATTACK ###
            ### LOOT ###
            

        ###########
        # SEAL B2-U
        ###########

        elif location == "B2-U_01": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_02": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_03":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "B2-U_seal2": #B only has 1 seal, which is the boss seal = seal2
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self)
            if not self._pather.traverse_nodes([644], self): return False # , time_out=3):
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
        
        ###########
        # SEAL C1-F
        ###########

        elif location == "C1-F_01":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
        
        elif location == "C1-F_02": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
        
        elif location == "C1-F_03": 
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C1-F_seal1":
            ### APPROACH ###
            wait(0.1,0.3)
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) 
            wait(0.1,0.3)
            if not self._pather.traverse_nodes([655], self): return False # , time_out=3):
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([655], self): return False # , time_out=3):
            
        elif location == "C1-F_seal2":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):

        ###########
        # SEAL C2-G
        ###########

        elif location == "C2-G_01": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_02": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_03": #skipped
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "C2-G_seal1":
            ### APPROACH ###
            #if not self._pather.traverse_nodes([663, 662], self): return False # , time_out=3): #caused 7% failed runs, replaced by static path.
            self._pather.traverse_nodes_fixed("dia_c2g_lc_661", self)
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")
            """
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            """

        elif location == "C2-G_seal2":
            ### APPROACH ###
            # Killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals
            seal_layout="C2-G"
            self._pather.traverse_nodes_fixed("dia_c2g_663", self)
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            wait(0.3, 0.5)
            if not self._pather.traverse_nodes([664, 665], self): return False # , time_out=3):

        else:
            ### APPROACH ###
            Logger.debug("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Throwing some random hammers")
            ### ATTACK ###
            atk_len = self._char_config["atk_len_cs_trashmobs"] * 0.3
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
    


    def kill_vizier(self, seal_layout:str) -> bool:
        atk_len = self._char_config["atk_len_diablo_vizier"]
        if seal_layout == "A1-L":
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([611], self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3): # recalibrate after loot

        elif seal_layout == "A2-Y":
            ### APPROACH ###
            if not self._pather.traverse_nodes([627, 622], self): return False # , time_out=3):
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking Vizier at position 1/2")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking Vizier at position 2/2")
            self._pather.traverse_nodes([623], self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking Vizier at position 3/3")
            if not self._pather.traverse_nodes([624], self): return False
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
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


    #NEED TO CHANGE PATHING, NOVA SORC DIES WITH HAMMERDIN ATTACK PATTERNS
    def kill_deseis(self, seal_layout:str) -> bool:
        atk_len = self._char_config["atk_len_diablo_deseis"]
        if seal_layout == "B1-S":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self) # quite aggressive path, but has high possibility of directly killing De Seis with first hammers, for 50% of his spawn locations
            nodes1 = [632]
            nodes2 = [631]
            nodes3 = [632]
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)     

        elif seal_layout == "B2-U":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_b2u_644_646", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            #self._pather.traverse_nodes_fixed("dia_b2u_seal_deseis", self) # We try to breaking line of sight, sometimes makes De Seis walk into the hammercloud. A better attack sequence here could make sense.
            nodes1 = [640]
            nodes2 = [646]
            nodes3 = [641]
            ### ATTACK ###
            Logger.debug(seal_layout + ": Attacking De Seis at position 1/4")
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 2/4")
            self._pather.traverse_nodes(nodes1, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 3/4")
            self._pather.traverse_nodes(nodes2, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            Logger.debug(seal_layout + ": Attacking De Seis at position 4/4")
            self._pather.traverse_nodes(nodes3, self, time_out=3)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)

            ### LOOT ###
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
        atk_len = self._char_config["atk_len_diablo_infector"]
        if seal_layout == "C1-F":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._cast_static(0.6)
            self._nova(atk_len)
            self._move_and_attack((50, 25), atk_len)
            self._move_and_attack((-70, -35), atk_len)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif seal_layout == "C2-G":
            # NOT killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals his attack sequence can be found in C2-G_seal2
            Logger.debug(seal_layout + ": No need for attacking Infector at position 1/1 - he was killed during clearing the seal")
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
            return False 
        return True



    def kill_diablo(self) -> bool:
        ### APPROACH ###
        ### ATTACK ###
        atk_len = self._char_config["atk_len_diablo"]
        Logger.debug("Attacking Diablo at position 1/1")
        pos_m = self._screen.convert_abs_to_monitor((0, 0))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        self._cast_static(0.6)
        self._nova(atk_len)
        self._move_and_attack((50, 25), atk_len)
        self._move_and_attack((-70, -35), atk_len)
        ### LOOT ###
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
    screen = Screen()
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = NovaSorc(config.nova_sorc, config.char, screen, t_finder, ui_manager, pather)
