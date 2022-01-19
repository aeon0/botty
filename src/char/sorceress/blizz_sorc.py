import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location
import numpy as np
import time

class BlizzSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Blizz Sorc")
        super().__init__(*args, **kwargs)
        #Nihlathak Bottom Right
        self._pather.offset_node(505, (50, 200))
        self._pather.offset_node(506, (40, -10))
        #Nihlathak Top Right
        self._pather.offset_node(510, (700, -55))
        self._pather.offset_node(511, (30, -25))
        #Nihlathak Top Left
        self._pather.offset_node(515, (-120, -100))
        self._pather.offset_node(517, (-18, -58))
        #Nihlathak Bottom Left
        self._pather.offset_node(500, (-150, 200))
        self._pather.offset_node(501, (10, -33))

    def _ice_blast(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["ice_blast"]:
            keyboard.send(self._skill_hotkeys["ice_blast"])
        for _ in range(5):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _blizzard(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["blizzard"]:
            raise ValueError("You did not set a hotkey for blizzard!")
        keyboard.send(self._skill_hotkeys["blizzard"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        click_tries = random.randint(2, 4)
        for _ in range(click_tries):
            mouse.press(button="right")
            wait(0.09, 0.12)
            mouse.release(button="right")

    def _glacial_spike(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.16, 0.23), spray: float = 10):
        keyboard.send(self._char_config["stand_still"], do_release=False)
        if self._skill_hotkeys["glacial_spike"]:
            keyboard.send(self._skill_hotkeys["glacial_spike"])
        for _ in range(5):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = self._screen.convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(delay[0], delay[1])
            mouse.release(button="left")
        keyboard.send(self._char_config["stand_still"], do_press=False)

    def _frost_nova(self, time_in_s: float):
        if not self._skill_hotkeys["frost_nova"]:
            raise ValueError("You did not set frost_nova hotkey!")
        keyboard.send(self._skill_hotkeys["frost_nova"])
        wait(0.05, 0.1)
        start = time.time()
        while (time.time() - start) < time_in_s:
            wait(0.03, 0.04)
            mouse.press(button="right")
            wait(0.12, 0.2)
            mouse.release(button="right")
    
    def kill_pindle(self) -> bool:
        pindle_pos_abs = self._screen.convert_screen_to_abs(self._config.path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        for _ in range(int(self._char_config["atk_len_pindle"])):
            self._blizzard(cast_pos_abs, spray=11)
            self._ice_blast(cast_pos_abs, spray=11)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        #move up
        pos_m = self._screen.convert_abs_to_monitor((0, -175))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-50, -50), spray=10)
        self._cast_static()
        #move down
        pos_m = self._screen.convert_abs_to_monitor((0, 85))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.70)
        self._blizzard((-170, -350), spray=10)
        self._cast_static()
        #move down
        pos_m = self._screen.convert_abs_to_monitor((0, 75))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((100, -300), spray=10)
        self._cast_static()
        pos_m = self._screen.convert_abs_to_monitor((0, 55))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(1.0)
        self._blizzard((-50, -130), spray=10)
        self._cast_static()
        wait(3.0)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        return True

    def kill_shenk(self) -> bool:
        pos_m = self._screen.convert_abs_to_monitor((100, 170))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #lower left posistion
        self._pather.traverse_nodes([151], self, time_out=2.5, force_tp=False)
        self._cast_static()
        self._blizzard((-250, 100), spray=10)
        self._ice_blast((60, 70), spray=60)
        self._blizzard((400, 200), spray=10)
        self._cast_static()
        self._ice_blast((-300, 100), spray=60)
        self._blizzard((185, 200), spray=10)
        pos_m = self._screen.convert_abs_to_monitor((-10, 10))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_static()
        self._blizzard((-300, -270), spray=10)
        self._ice_blast((-20, 30), spray=60)
        wait(1.0)
        #teledance 2
        pos_m = self._screen.convert_abs_to_monitor((150, -240))
        self.pre_move()
        self.move(pos_m, force_move=True)
        #teledance attack 2
        self._cast_static()
        self._blizzard((450, -250), spray=10)
        self._ice_blast((150, -100), spray=60)
        self._blizzard((0, -250), spray=10)
        wait(0.3)
        #Shenk Kill
        self._cast_static()
        self._blizzard((100, -50), spray=10)
        # Move to items
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, time_out=1.4, force_tp=True)
        return True

    def kill_council(self) -> bool:
        # Move inside to the right
        self._pather.traverse_nodes_fixed([(1110, 120)], self)
        self._pather.offset_node(300, (80, -110))
        self._pather.traverse_nodes([300], self, time_out=5.5, force_tp=True)
        self._pather.offset_node(300, (-80, 110))
        # Attack to the left
        self._blizzard((-150, 10), spray=80)
        self._ice_blast((-300, 50), spray=40)
        # Tele back and attack
        pos_m = self._screen.convert_abs_to_monitor((-50, 200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-235, -230), spray=80)
        wait(1.0)
        pos_m = self._screen.convert_abs_to_monitor((-285, -320))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.5)
        # Move to far left
        self._pather.offset_node(301, (-80, -50))
        self._pather.traverse_nodes([301], self, time_out=2.5, force_tp=True)
        self._pather.offset_node(301, (80, 50))
        # Attack to RIGHT
        self._blizzard((100, 150), spray=80)
        self._ice_blast((230, 230), spray=20)
        wait(0.5)
        self._blizzard((310, 260), spray=80)
        wait(1.0)
        # Move to bottom of stairs
        self.pre_move()
        for p in [(450, 100), (-190, 200)]:
            pos_m = self._screen.convert_abs_to_monitor(p)
            self.move(pos_m, force_move=True)
        self._pather.traverse_nodes([304], self, time_out=2.5, force_tp=True)
        # Attack to center of stairs
        self._blizzard((-175, -200), spray=30)
        self._ice_blast((30, -60), spray=30)
        wait(0.5)
        self._blizzard((175, -270), spray=30)
        wait(1.0)
        # Move back inside
        self._pather.traverse_nodes_fixed([(1110, 15)], self)
        self._pather.traverse_nodes([300], self, time_out=2.5, force_tp=False)
        # Attack to center
        self._blizzard((-100, 0), spray=10)
        self._cast_static()
        self._ice_blast((-300, 30), spray=50)
        self._blizzard((-175, 50), spray=10)
        wait(1.0)
        # Move back outside and attack
        pos_m = self._screen.convert_abs_to_monitor((-430, 230))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._blizzard((-50, -150), spray=30)
        self._cast_static()
        wait(0.5)
        # Move back inside and attack
        pos_m = self._screen.convert_abs_to_monitor((150, -350))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence center
        self._blizzard((-100, 35), spray=30)
        self._cast_static()
        self._blizzard((-150, 20), spray=30)
        wait(1.0)
        # Move inside
        pos_m = self._screen.convert_abs_to_monitor((100, -30))
        self.pre_move()
        self.move(pos_m, force_move=True)
        # Attack sequence to center
        self._blizzard((-50, 50), spray=30)
        self._cast_static()
        self._ice_blast((-30, 50), spray=10)
        # Move outside since the trav.py expects to start searching for items there if char can teleport
        self._pather.traverse_nodes([226], self, time_out=2.5, force_tp=True)
        return True

    def kill_nihlatak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_sequences = max(1, int(self._char_config["atk_len_nihlatak"]) - 1)
        for i in range(atk_sequences):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is not None:
                cast_pos_abs = np.array([nihlatak_pos_abs[0] * 1.0, nihlatak_pos_abs[1] * 1.0])
                wait(0.8)  
                self._blizzard(cast_pos_abs, spray=0)
                wait(0.3)  
                is_nihl = self._template_finder.search(["NIHL_BAR"], self._screen.grab(), threshold=0.8, roi=self._config.ui_roi["enemy_info"]).valid
                nihl_immune = self._template_finder.search(["COLD_IMMUNE","COLD_IMMUNES"], self._screen.grab(), threshold=0.8, roi=self._config.ui_roi["enemy_info"]).valid
                if is_nihl:
                    Logger.info("Found him!")
                    if nihl_immune:
                        Logger.info("Cold Immune! - Exiting")
                        return True
        wait(0.8)      
        self._cast_static()
        self._blizzard(cast_pos_abs, spray=15)                                     
        # Move to items
        wait(1.3)
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        cast_pos_abs = np.array([0, 0])
        pos_m = self._screen.convert_abs_to_monitor((-20, 20))
        mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        for _ in range(int(self._char_config["atk_len_arc"])):
            self._blizzard(cast_pos_abs, spray=11)
            self._ice_blast(cast_pos_abs, spray=11)
        wait(self._cast_duration, self._cast_duration + 0.2)
        return True
    

    #-------------------------------------------------------------------------------#   
    # Chaos Sanctuary, Seal Bosses (a = Vizier, b = De Seis, c = Infector) & Diablo #
    #-------------------------------------------------------------------------------#
    
    def kill_cs_trash(self, location:str) -> bool:
         
        ### Seals
        if location == "sealdance": #if seal opening fails & trash needs to be cleared -> used at ANY seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        ### ROF
        elif location == "rof_01": #static_path WP-> CS Entrance, outside CS Entrance 
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "rof_02": #node 601, CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        ### CS Entrance
        elif location == "entrance_hall_01": #node 677, CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "entrance_hall_02": #static_path "diablo_entrance_hall_1", CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "entrance_hall_03": #node 670,671, CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder

        ### Entrance Layout1
        elif location == "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "entrance1_02": #node 673, CS Hall1/3 layout1
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "entrance1_03": #node 674, CS Hall2/3 layout1
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder
        
        elif location == "entrance1_04": #node 676, CS Hall3/3 layout1
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        ### Entrance Layout2
        elif location == "entrance2_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "entrance2_02": #node 682, CS Hall1/3 layout2
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "entrance2_03": #node 683, CS Hall2/3 layout2
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder
        
        elif location == "entrance2_04": #node 686, CS Hall3/3 layout2
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder  

        ### Pentagram
        #elif location == "pent_before_a": #node 602, pentagram, before CTA buff & depature to layout check - not needed when trash is skipped & seals run in right order, it is therefore added below in the function to skip 
        #    self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "pent_before_b": #node 602, pentagram, before CTA buff & depature to layout check 
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "pent_before_c": #node 602, pentagram, before CTA buff & depature to layout check
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder  
        
        ### Layout Checks
        elif location == "layoutcheck_a": #layout check seal A, node 619 A1-L, node 620 A2-Y
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "layoutcheck_b": #layout check seal B, node 634 B1-S, node 649 B2-U
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "layoutcheck_c": #layout check seal C, node 656 C1-F, node 664 C2-G
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder               

        ### A1-L
        elif location == "A2-Y_01": #node 611 seal layout A1-L: approach
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "A2-Y_02": #node 612 seal layout A1-L: safe_dist
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "A2-Y_03": #node 613 seal layout A1-L: center, # you need to end your attack sequence at node [613] center
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder               

        elif location == "A2-Y_boss": #node 614 layout A1-L: fake seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        elif location == "A2-Y_boss": #node 615 layout A1-L: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        ### A2-Y
        elif location == "A2-Y_01": #node 622 seal layout A2-Y: safe_dist
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "A2-Y_02": #node 623 seal layout A2-Y: center
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "A2-Y_03": #node 624 seal layout A2-Y: seal fake far, you need to end your attack sequence at node [624] fake seal far
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder               

        elif location == "A2-Y_boss": # node 625 seal layout A2-Y: fake seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        elif location == "A2-Y_boss": # static_path "dia_a2y_sealfake_sealboss" (at node 626) seal layout A2-Y: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        ### B1-S
        elif location == "B1-S_01": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "B1-S_02": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "B1-S_03": # no movement, but you need to end your char attack sequence at layout check node [656]
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder               

        elif location == "B1-S_boss": # node 634 layout B1-S: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        ### B2-U
        elif location == "B2-U_01": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "B2-U_02": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "B2-U_03": # no movement, but you need to end your char attack sequence at layout check node [656]
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder               

        elif location == "B2-U_boss": # node 644 layout B2-U: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder 

        ### C1-F
        elif location == "C1-F_01": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "C1-F_02": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "C1-F_03": # no movement, but you need to end your char attack sequence at layout check node [656]
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "C1-F_fake": # static_path "dia_c1f_hop_fakeseal" C1-F: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder            

        elif location == "C1-F_boss": # static_path "dia_c1f_654_651" C1-F: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder       
        
        ### C2-G
        elif location == "C2-G_01": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "C2-G_02": # no movement
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "C2-G_03": # no movement, but you need to end your char attack sequence at layout check node [664]
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder   

        elif location == "C2-G_fake": # fake seal layout C2-G
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder            

        elif location == "C2-G_boss": # boss seal layout C2-G
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder

        # add here ALL the locations where no trash should be killed
        elif location in ["pent_before_a",]:  
            Logger.debug("No attack choreography available in blizz_sorc.py for this node " + location + " - skipping to shorten run.")
        
        else:
            Logger.debug("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Doing a Frost Nova instead!")
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10])
        return True
    
    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            #previous node in diablo.py is [612], this is our current location
            atk_len = self._char_config["atk_len_diablo_vizier"] * 0.3
            wait(0.5)
            self._blizzard((20, 100), spray=10)
            self._ice_blast((70, 90), spray=10)
            self._ice_blast((100, 90), spray=10)
            wait(0.3)
            self._blizzard((130, 200), spray=10)
            wait(0.9)
            pos_m = self._screen.convert_abs_to_monitor((100, 50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            if not self._pather.traverse_nodes([611, 610], self): return False
            wait(0.9)
            self._blizzard((-250, -80), spray=10)
            self._ice_blast((100, 50), spray=30)
            self._ice_blast((-200, -120), spray=30)
            wait(0.3)
            self._blizzard((-50, 0), spray=10)
            wait(0.3)
            #Next node in diablo.py is [611], this is where we should be able to go next from the current position at the end of this attack sequence        

        elif seal_layout == "A2-Y":
            #previous node in diablo.py is [622], this is our current location
            wait(0.8)
            self._blizzard((20, 150), spray=10)
            self._ice_blast((150, 100), spray=30)
            self._ice_blast((120, -100), spray=30)
            wait(0.4)
            self._blizzard((-400, -50), spray=10)
            self._ice_blast((150, 10), spray=30)
            self._ice_blast((300, 50), spray=30)
            wait(0.4)
            self._blizzard((150, 100), spray=10)
            wait(0.5)
            #this attack sequence has to end at node [624], as the next move in diablo.py is a static path hop! from [624] to [622]
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis(" + seal_layout + "), should not happen.")
            return False
        return True

    def kill_deseis(self, seal_layout:str) -> bool:
        if seal_layout == "B1-S":
            #previous node in diablo.py is [634], this is our current location
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder
            #we should end at node [632], as the next move in diablo.py is towards [633]

        elif seal_layout == "B2-U":
            #we start at node [646], coming from a quite aggressive stativ path traversing from seal to [646] "dia_b2u_644_646"
            self._frost_nova(self._char_config["atk_len_cs_trashmobs" / 10]) #placeholder
            #the next move in diablo.py is loot at the current position, then move to [640] and loot there, too. We thus need to ensure this attack sequence ends at a point where you can see node [640]
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis(" + seal_layout + "), should not happen.")
            return False
        return True 


    def kill_infector(self, seal_layout:str) -> bool:
        if seal_layout == "C1-F":
            #we tranistioned from the boss seal using a static path "dia_c1f_652" to the center between seals and should be close to node [654]
            wait(0.5)
            pos_m = self._screen.convert_abs_to_monitor((100, 0))
            self.pre_move()
            self.move(pos_m, force_move=True)  
            self._blizzard((200, 20), spray=10)
            self._cast_static() 
            self._ice_blast((150, 20), spray=30)
            wait(0.3)
            self._blizzard((100, 20), spray=10)
            wait(0.8)
            pos_m = self._screen.convert_abs_to_monitor((150, -50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(0.8)  
            self._blizzard((100, 150), spray=10)
            self._cast_static() 
            self._ice_blast((100, 120), spray=30)
            wait(0.3)
            self._blizzard((100, 100), spray=10)
            self._cast_static()
            wait(2.0)
            #next move in diablo.py is to loot and traverse to node [654], so our attack sequence should end where you can see node [654]

        elif seal_layout == "C2-G":
            #we start at node [663], after having done a static path "dia_c2g_663" bringing us from the boss seal to the center between seals. Infector here can be moat-tricked, if we tele back to [662] where the Boss seal is at and cast towards the Fake seal [665]
            pos_m = self._screen.convert_abs_to_monitor((-150, 50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self._blizzard((200, -100), spray=10)
            self._cast_static() 
            self._ice_blast((200, -100), spray=30)
            pos_m = self._screen.convert_abs_to_monitor((-150, 50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self._blizzard((250, -150), spray=10)
            self._cast_static()
            self._ice_blast((200, -150), spray=30)
            self._blizzard((200, -120), spray=10)
            wait(0.8)
            pos_m = self._screen.convert_abs_to_monitor((320, -120))
            self.pre_move()
            self.move(pos_m, force_move=True)
            if not self._pather.traverse_nodes([663], self): return False
            wait(0.8)
            self._blizzard((100, -70), spray=10)
            self._cast_static()
            self._ice_blast((90, -150), spray=30)
            self._blizzard((100, -100), spray=10)
            if not self._pather.traverse_nodes([663], self): return False
            #we end at node [663], the next step in diablo.py is to travers from [664,665] to the fake seal & open it.
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_infector("+ seal_layout +"), should not happen.")
            return False 
        return True


    def kill_diablo(self) -> bool:
        #we start this piece of code at node 602 (Pentagram)
        atk_len = self._char_config["atk_len_diablo"]
        #for _ in range(int(self._char_config["atk_len_diablo"])):
        diablo_pos_abs =  0, -72
        cast_pos_abs = [diablo_pos_abs[0] * 0.9, diablo_pos_abs[1] * 0.9]
        wait(2.5)
        self._blizzard(cast_pos_abs, spray=45)
        self._cast_static(0.6)
        self._ice_blast(cast_pos_abs, spray=90)
        wait(0.3)
        self._blizzard(cast_pos_abs, spray=50)
        wait(0.8)
        pos_m = self._screen.convert_abs_to_monitor((0, -200))
        self.pre_move()
        self.move(pos_m, force_move=True)
        wait(0.8)
        self._blizzard((0, 150), spray=10) 
        self._ice_blast((0, 150), spray=30)
        self._blizzard((-50, 120), spray=10)
        #we end this piece of code at node 602 (Pentagram)
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
    char = BlizzSorc(config.blizz_sorc, config.char, screen, t_finder, ui_manager, pather)
    char.kill_council()
