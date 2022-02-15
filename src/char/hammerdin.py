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
        #hammerdin needs to be closer to shenk to reach it with hammers
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

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if capabilities.can_teleport_natively:
            self._do_pre_move = False

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
            self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, time_out=1.0, do_pre_move=self._do_pre_move, force_tp=True, use_tp_charge=True)
        wait(0.05, 0.1)
        self._cast_hammers(self._char_config["atk_len_eldritch"])
        wait(0.1, 0.15)
        self._cast_hammers(1.6, "redemption")
        return True

    def kill_shenk(self):
        if not self._do_pre_move:
            keyboard.send(self._skill_hotkeys["concentration"])
            wait(0.05, 0.15)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.0, do_pre_move=self._do_pre_move, force_tp=True, use_tp_charge=True)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.5, 1.0) #clear seal from corpses
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
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            ### LOOT ###
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([603], self): return False #calibrate after looting


        elif location == "rof_02": #node 604 - inside ROF
            ### APPROACH ###
            if not self._pather.traverse_nodes([604], self, time_out=3): return False  #threshold=0.8 (ex 601)
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance_hall_01": ##static_path "diablo_entrance_hall_1", node 677, CS Entrance Hall1
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_1", self) # 604 -> 671 Hall1
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance_hall_02":  #node 670,671, CS Entrance Hall1, CS Entrance Hall1
            ### APPROACH ###
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            self._pather.traverse_nodes_fixed("diablo_entrance_1_670_672", self) # 604 -> 671 Hall1
            if not self._pather.traverse_nodes([670], self): return False # pull top mobs 672 to bottom 670
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            #Move to Layout Check
            if not self._pather.traverse_nodes([671], self): return False # calibrate before static path
            self._pather.traverse_nodes_fixed("diablo_entrance_hall_2", self) # 671 -> LC Hall2



        # TRASH LAYOUT A

        elif location == "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([673], self): return False # , time_out=3): # Re-adjust itself and continues to attack

        elif location == "entrance1_02": #node 673
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) # Moves char to postion close to node 674 continues to attack
            if not self._pather.traverse_nodes([674], self): return False#, time_out=3)

        elif location == "entrance1_03": #node 674
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([675], self): return False#, time_out=3) # Re-adjust itself
            self._pather.traverse_nodes_fixed("diablo_entrance_1_1", self) #static path to get to be able to spot 676
            if not self._pather.traverse_nodes([676], self): return False#, time_out=3)

        elif location == "entrance1_04": #node 676- Hall3
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-50, -150), self._char_config["atk_len_cs_trashmobs"])
            self._move_and_attack((50, 150), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        # TRASH LAYOUT B

        elif location == "entrance2_01": #static_path "diablo_entrance_hall_2"
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "entrance2_02": #node 682
            ### APPROACH ###
            #if not self._pather.traverse_nodes([682], self): return False # , time_out=3):
            self._pather.traverse_nodes_fixed("diablo_trash_b_hall2_605_right", self) #pull mobs from the right
            wait (0.2, 0.5)
            if not self._pather.traverse_nodes([605], self): return False#, time_out=3)
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((0, 0), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-50, -150), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._move_and_attack((50, 150), self._char_config["atk_len_cs_trashmobs"] * 0.2)
            self._move_and_attack((250, -150), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._move_and_attack((-250, -150), self._char_config["atk_len_cs_trashmobs"] * 0.2)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -100), self._char_config["atk_len_cs_trashmobs"])
            self._move_and_attack((30, 100), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "dia_trash_b": #trash before between Pentagramm and Seal B Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -100), self._char_config["atk_len_cs_trashmobs"])
            self._move_and_attack((30, 100), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "dia_trash_c": ##trash before between Pentagramm and Seal C Layoutcheck
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"])
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -100), self._char_config["atk_len_cs_trashmobs"])
            self._move_and_attack((30, 100), self._char_config["atk_len_cs_trashmobs"])
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ###############
        # LAYOUT CHECKS
        ###############

        elif location == "layoutcheck_a": #layout check seal A, node 619 A1-L, node 620 A2-Y
            ### APPROACH ###
            ### ATTACK ###
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "layoutcheck_b": #layout check seal B, node 634 B1-S, node 649 B2-U
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "layoutcheck_c": #layout check seal C, node 656 C1-F, node 664 C2-G
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ##################
        # PENT BEFORE SEAL
        ##################

        elif location == "pent_before_a": #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            Logger.debug("No attack choreography available in hammerdin.py for this node " + location + " - skipping to shorten run.")

        elif location == "pent_before_b": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        elif location == "pent_before_c": #node 602, pentagram, before CTA buff & depature to layout check
            ### APPROACH ###
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)

        ###########
        # SEAL A1-L
        ###########

        elif location == "A1-L_01":  #node 611 seal layout A1-L: safe_dist
            ### APPROACH ###
            if not self._pather.traverse_nodes([611], self): return False # , time_out=3):
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_02":  #node 612 seal layout A1-L: center
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            ### ATTACK ###
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._cast_hammers(0.5, "cleansing")
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_03":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613], self): return False # , time_out=3):
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._cast_hammers(0.5, "cleansing")
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        elif location == "A1-L_seal1":  #node 613 seal layout A1-L: fake_seal
            ### APPROACH ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            ### ATTACK ###
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            # we loot at boss

        elif location == "A1-L_seal2":  #node 614 seal layout A1-L: boss_seal
            ### APPROACH ###
            if not self._pather.traverse_nodes([613, 615], self): return False # , time_out=3):
            ### ATTACK ###
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            # we loot at boss

        elif location == "A2-Y_02":  #node 623 seal layout A2-Y: center
            ### APPROACH ###
            # if not self._pather.traverse_nodes([623,624], self): return False #
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        elif location == "A2-Y_seal2":
            ### APPROACH ###
            ### ATTACK ###
            ### LOOT ###
            # we loot at boss
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)


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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([655], self): return False # , time_out=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

        elif location == "C1-F_seal2":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([652], self): return False # , time_out=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)

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
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            """

        elif location == "C2-G_seal2":
            ### APPROACH ###
            # Killing infector here, because for C2G its the only seal where a bossfight occures BETWEEN opening seals
            seal_layout="C2-G"
            self._pather.traverse_nodes_fixed("dia_c2g_663", self)
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            Logger.debug(seal_layout + ": Attacking Infector at position 1/1")
            self._cast_hammers(self._char_config["atk_len_diablo_infector"])
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, 15), self._char_config["atk_len_diablo_infector"])
            self._cast_hammers(0.8, "redemption")
            self._move_and_attack((30, -15), self._char_config["atk_len_diablo_infector"])
            wait(0.1, 0.15)
            self._cast_hammers(1.2, "redemption")
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            if not self._pather.traverse_nodes([664, 665], self): return False # , time_out=3):

        else:
            ### APPROACH ###
            Logger.debug("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Throwing some random hammers")
            ### ATTACK ###
            pos_m = self._screen.convert_abs_to_monitor((0, 0))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            self._move_and_attack((30, 15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            self._cast_hammers(0.75, "redemption")
            self._move_and_attack((-30, -15), self._char_config["atk_len_cs_trashmobs"] * 0.5)
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
        return True



    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            ### APPROACH ###
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            ### ATTACK ###
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
            if self._skill_hotkeys["cleansing"]:
                keyboard.send(self._skill_hotkeys["cleansing"])
                wait(0.1, 0.2)
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            wait(0.3, 1.2)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False # , time_out=3): # recalibrate after loot

        elif seal_layout == "A2-Y":
            ### APPROACH ###
            if not self._pather.traverse_nodes([627, 622], self): return False # , time_out=3):
            ### ATTACK ###
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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            ### LOOT ###
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([624], self): return False
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            if not self._pather.traverse_nodes([622], self): return False #, time_out=3):
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([622], self): return False # , time_out=3): #recalibrate after loot

        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis("+ seal_layout +"), should not happen.")
            return False
        return True



    def kill_deseis(self, seal_layout:str) -> bool:
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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(2.5, 3.5) # to keep redemption on for a couple of seconds before the next teleport to have more corpses cleared & increase chance to find next template
                Logger.debug(seal_layout + ": Waiting with Redemption active to clear more corpses.")
            #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/info_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
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
            if self._skill_hotkeys["redemption"]:
                keyboard.send(self._skill_hotkeys["redemption"])
                wait(0.3, 0.6)
            #if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/info_check_deseis_dead" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
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
        if seal_layout == "C1-F":
            ### APPROACH ###
            self._pather.traverse_nodes_fixed("dia_c1f_652", self)
            ### ATTACK ###
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
        ### LOOT ###
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
