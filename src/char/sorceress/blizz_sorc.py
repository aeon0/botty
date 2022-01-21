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
        #Diablo
        self._pather.offset_node(611, (100, 0))
        self._pather.offset_node(626, (220, 0))
        self._pather.offset_node(643, (65, 28))
        self._pather.offset_node(612, (270, 0))
        self._pather.offset_node(635, (150, -80))
        #self._pather.offset_node(634, (400, 150))
        #self._pather.offset_node(649, (150, -150))

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

        #-----------------------------
        # ONLY FOR CS_CLEAR_TRASH = 1
        #-----------------------------
        ### ROF
        if location == "rof_01": #static_path WP-> CS Entrance, outside CS Entrance 
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "rof_02": #node 601, CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        ### CS Entrance
        elif location == "entrance_hall_01": #node 677, CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "entrance_hall_02": #static_path "diablo_entrance_hall_1", CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "entrance_hall_03": #node 670,671, CS Entrance
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder

        ### Entrance Layout1
        elif location == "entrance1_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "entrance1_02": #node 673, CS Hall1/3 layout1
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "entrance1_03": #node 674, CS Hall2/3 layout1
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder
        
        elif location == "entrance1_04": #node 676, CS Hall3/3 layout1
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder 

        ### Entrance Layout2
        elif location == "entrance2_01": #static_path "diablo_entrance_hall_2", Hall1 (before layout check)
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "entrance2_02": #node 682, CS Hall1/3 layout2
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   

        elif location == "entrance2_03": #node 683, CS Hall2/3 layout2
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder
        
        elif location == "entrance2_04": #node 686, CS Hall3/3 layout2
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder  

        #-----------------------------
        # FOR ALL RUNS
        #-----------------------------
        
        elif location == "sealdance": #if seal opening fails & trash needs to be cleared -> used at ANY seal
            self._frost_nova(0.5) #self._char_config["atk_len_cs_trashmobs"]
            self._blizzard((-450, -100), spray=10)
            self._glacial_spike((0, 100), spray=30) # slow mobs
            self._glacial_spike((-40, -100), spray=30) # slob mobs
            self._ice_blast((0, 100), spray=30)
            self._ice_blast((-40, -100), spray=30)
            self._frost_nova(0.3) #wait(0.3) #instead of waiting, we can do novas
            self._blizzard((-50, -50), spray=10)
            pos_m = self._screen.convert_abs_to_monitor((-10, -10))
            self.pre_move()
            self.move(pos_m, force_move=True)
            #pickit at current char position in diablo.py 
                    
        ### Pentagram
        #all locations have the same attack sequence, therefore they elif check is "in []" instead of "==". Pent_before_a is only used if cs_clear_trash is 1
        elif location in ["pent_before_a, pent_before_b","pent_before_b"]: #node 602, pentagram, before CTA buff & depature to layout check 
            self._blizzard((-450, -100), spray=10)
            self._ice_blast((0, 100), spray=30)
            self._ice_blast((-40, -100), spray=30)
            self._frost_nova(0.3) #we cast a nova instead of wait(0.3)
            self._blizzard((-50, -50), spray=10)
            pos_m = self._screen.convert_abs_to_monitor((-10, -10))
            self.pre_move()
            self.move(pos_m, force_move=True)
            #pickit diablo.py, afterwards calibration at 602. If we get off-track during the pickit there, the run is failed.
        
        ### Layout Checks
        elif location == "layoutcheck_a": #layout check seal A, node 619 A1-L, node 620 A2-Y
            self._blizzard((-50, -120), spray=10)
            self._ice_blast((150, 50), spray=30)
            self._frost_nova(0.5) #wait (0.5)
            self._blizzard((100, -20), spray=10)
            self._frost_nova(0.9) # wait(0.9)
            #no pickit in diablo.py (loot dropping here can be picked up later at position 610 for A1-L and 624 for A2-Y (only if we overshot the teleport for LC)

        elif location == "layoutcheck_b": #layout check seal B, node 634 B1-S, node 649 B2-U
            self._blizzard((-150, -50), spray=10)
            self._ice_blast((-150, -50), spray=30)
            self._cast_static()
            self._frost_nova(0.3) #wait (0.3)
            self._blizzard((-100, -50), spray=10)
            self._frost_nova(0.9) # wait(0.9) 
            #no pickit in diablo.py (loot dropping here can be picked up later at position 647 for B2-U and 634 for B1-S (has to be during clearing the seal: _01 _02 _03 _boss))

        elif location == "layoutcheck_c": #layout check seal C, node 656 C1-F, node 664 C2-G
            self._blizzard((-50, -50), spray=10)
            self._ice_blast((50, 50), spray=30)
            self._cast_static()
            self._frost_nova(0.3) #wait (0.3)
            self._blizzard((50, 50), spray=10)
            self._frost_nova(0.9) # wait(0.9)        
            #no pickit in diablo.py (loot dropping here can be picked up later at position 664 for C2-G and 656 for C1-F (has to be during clearing the seal: _01 _02 _03 _fake _boss))

        ### -----------------
        ### SEAL A
        ### -----------------
        ### LAYOUT 1:  A1-L
        ### -----------------
        elif location == "A1-L_01":
            if not self._pather.traverse_nodes([612], self): return False
            self._blizzard((-180, -290), spray=10)
            self._ice_blast((0, 100), spray=30)
            self._cast_static() 
            self._blizzard((-100, -50), spray=10)
            wait(0.9)
            #pickit at current char position (called in diablo.py), next location is A1-L_02"

        elif location == "A1-L_02":
            if not self._pather.traverse_nodes([613], self): return False
            wait(0.9)
            self._blizzard((190, -90), spray=10)
            self._ice_blast((-150, 90), spray=30)
            self._cast_static() 
            wait(0.8)
            self._blizzard((-150, 70), spray=10)
            #pickit at current char position (called in diablo.py), next location is A1-L_03"

        # not used, added in last elif of this function to skip this location
        #elif location == "A1-L_03": #node 613 seal layout A1-L: center, # you need to end your attack sequence at node [613] center
            # self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder
            #pickit at current char position (called in diablo.py), next location is A1-L_fake"

        # not used, added in last elif of this function to skip this location
        #elif location == "A1-L_fake": #node 614 layout A1-L: fake seal
            #self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder 
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 614, followed by sealdance_fake, then back to blizz_sorc.py for "A1-L-boss"
        
        elif location == "A1-L_boss": #node 615 layout A1-L: boss seal
            if not self._pather.traverse_nodes([613], self): return False #just used for moving from 614 fake seal to 613 center, because next step in diablo.py is 615 boss seal
            #pickit at current char position (called in diablo.py)
            #next location in diablo.py is node 615, followed by sealdance_boss, then back to blizz_sorc.py for "Kill_Vizier(A1-L)"
        
        ### -----------------
        ### LAYOUT : A2Y
        ### -----------------
        elif location == "A2-Y_01":
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info("A2-Y Hop!")
            if not self._pather.traverse_nodes([624], self): return False
            wait(0.8)
            self._blizzard((150, -40), spray=10)
            self._cast_static()
            self._ice_blast((-150, -90), spray=30)
            wait(0.3)
            self._blizzard((-150, -100), spray=10)
            wait(0.8)
            #pickit at current char position (called in diablo.py), next location is A2-Y_02"

        elif location == "A2-Y_02":
            self._pather.offset_node(623, (-100, 50))
            if not self._pather.traverse_nodes([623], self): return False
            self._pather.offset_node(623, (100, -50))
            wait(0.8)
            self._blizzard((150, -70), spray=10)
            self._cast_static()
            self._ice_blast((150, 40), spray=30)
            wait(0.3)
            self._blizzard((100, 100), spray=10)
            wait(0.8) 
            #pickit at current char position (called in diablo.py), next location is A2-Y_03"

        elif location == "A2-Y_03":
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder               
            self._pather.offset_node(627, (200, 90))
            if not self._pather.traverse_nodes([627], self): return False
            self._pather.offset_node(627, (-200, -90))
            wait(0.8)
            self._blizzard((-150, -110), spray=10)
            self._ice_blast((0, 50), spray=30)
            self._cast_static()
            wait(0.3)
            self._blizzard((-150, 100), spray=10)
            wait(0.8)
            #pickit at current char position (called in diablo.py), next location is A2-Y_fake"

        elif location == "A2-Y_fake": 
            if not self._pather.traverse_nodes([623, 624], self): return False
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 625, followed by sealdance_fake, then back to blizz_sorc.py for "A2-Y_boss"

        elif location == "A2-Y_boss": 
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            self._blizzard((70, -50), spray=10)
            wait(0.8)
            self._ice_blast((150, 10), spray=30)
            self._blizzard((50, 170), spray=10)
            wait(0.8)
            #next location in diablo.py is node 626, followed by sealdance_boss, then back to blizz_sorc.py for "Kill_Vizier(A2-Y)"

        ### B1-S
        elif location == "B1-S_01": 
            if not self._pather.traverse_nodes([635], self): return False
            self._blizzard((-200, -70), spray=10)
            self._ice_blast((-150, -60), spray=30)
            self._ice_blast((-150, -100), spray=30)
            self._blizzard((-450, -120), spray=10)
            #pickit at current char position (called in diablo.py), next location is B1-S_02"

        elif location == "B1-S_02": 
            self._pather.offset_node(633, (150, -30))
            if not self._pather.traverse_nodes([633], self): return False
            self._pather.offset_node(631, (-150, 30))
            wait(0.8)
            self._blizzard((-200, 100), spray=10)
            self._ice_blast((150, 130), spray=60)
            self._cast_static() 
            wait(0.3)
            self._blizzard((-400, 150), spray=10)
            wait(0.9)
            self._pather.traverse_nodes([632], self, time_out=2.5, force_tp=False)
            wait(0.9)
            self._blizzard((-150, 100), spray=10)
            self._ice_blast((150, -150), spray=30)
            self._ice_blast((150, 100), spray=30)
            wait(0.3)
            #pickit at current char position (called in diablo.py), next location is B1-S_03"

        elif location == "B1-S_03":
            self._pather.traverse_nodes([632], self, time_out=2.5, force_tp=False)
            self._pather.traverse_nodes([631], self, time_out=2.5, force_tp=False)
            wait(0.3)
            pos_m = self._screen.convert_abs_to_monitor((300, 200))
            self.pre_move()
            self.move(pos_m, force_move=True) 
            wait(0.2)
            self._blizzard((-150, -75), spray=10)
            self._ice_blast((150, 70), spray=30)
            self._ice_blast((-150, -75), spray=30)
            self._blizzard((220, 150), spray=10)
            wait(0.5)
            if not self._pather.traverse_nodes([636], self): return False
            if not self._pather.traverse_nodes([634], self): return False
            #pickit at current char position (called in diablo.py), next location is B1-S_boss"

        elif location == "B1-S_boss": # node 634 layout B1-S: boss seal
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder 
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 634, followed by sealdance_boss, then back to blizz_sorc.py for kill_deseis(B1-S)

        ### B2-U
        elif location == "B2-U_01":
            pos_m = self._screen.convert_abs_to_monitor((-300, 0))
            self.pre_move()
            self.move(pos_m, force_move=True) 
            self._blizzard((100, -70), spray=10)
            self._ice_blast((100, 100), spray=30)
            self._ice_blast((-50, -100), spray=30)
            self._blizzard((100, 100), spray=10)
            pos_m = self._screen.convert_abs_to_monitor((-350, -200))
            self.pre_move()
            self.move(pos_m, force_move=True)
            pos_m = self._screen.convert_abs_to_monitor((-100, -100))
            self.pre_move()
            self.move(pos_m, force_move=True)
            #pickit at current char position (called in diablo.py), next location is "B2-U_02"

        elif location == "B2-U_02": 
            if not self._pather.traverse_nodes([644], self): return False
            self._blizzard((250, 0), spray=10)
            self._ice_blast((150, 20), spray=30)
            wait(0.3)
            self._pather.offset_node(643, (70, 100))
            if not self._pather.traverse_nodes([643], self): return False
            self._pather.offset_node(643, (-70, -100))
            wait(0.8)
            self._blizzard((-150, 100), spray=10)
            self._cast_static()
            self._ice_blast((-200, 100), spray=30)
            wait(0.3)
            #pickit at current char position (called in diablo.py), next location is "B2-U_03"

        elif location == "B2-U_03":
            if not self._pather.traverse_nodes([640], self): return False
            self._blizzard((-70, 70), spray=10)
            self._ice_blast((150, -150), spray=30)
            self._cast_static()
            self._blizzard((50, -50), spray=10)
            wait(0.8)
            pos_m = self._screen.convert_abs_to_monitor((100, -150))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(0.8)
            self._blizzard((-250, 250), spray=10)
            wait(0.8)
            if not self._pather.traverse_nodes([646], self): return False
            wait(0.8)
            self._blizzard((-100, -50), spray=10)
            self._ice_blast((-150, -10), spray=30)
            self._cast_static()
            self._blizzard((50, 100), spray=10)
            wait(0.3)
            #pickit at current char position (called in diablo.py), next location is "B2-U_boss"

        elif location == "B2-U_boss":
            if not self._pather.traverse_nodes([646], self): return False
            if not self._pather.traverse_nodes([645], self): return False
            wait(0.3)
            pos_m = self._screen.convert_abs_to_monitor((400, -300))
            self.pre_move()
            self.move(pos_m, force_move=True)
            pos_m = self._screen.convert_abs_to_monitor((100, -150))
            self.pre_move()
            self.move(pos_m, force_move=True)
            pos_m = self._screen.convert_abs_to_monitor((-50, -300))
            self.pre_move()
            self.move(pos_m, force_move=True)
            pos_m = self._screen.convert_abs_to_monitor((-500, -150))
            self.pre_move()
            self.move(pos_m, force_move=True)
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 644, followed by sealdance_boss, then back to blizz_sorc.py for kill_deseis("B2-U")

        ### C1-F
        elif location == "C1-F_01":
            self._blizzard((-250, -100), spray=10)
            self._ice_blast((-200, -50), spray=30)
            self._ice_blast((-200, 0), spray=30)
            wait(0.3)
            self._blizzard((-350, -250), spray=10)
            wait(0.9)
            wait(0.9)
            self._blizzard((150, 0), spray=10)
            wait(0.9)
            #pickit at current char position (called in diablo.py), next location is "C1-F_02"

        elif location == "C1-F_02": 
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) # REPLACES: if not self._pather.traverse_nodes([656, 654, 655], self, time_out=3): return False #ISSUE: getting stuck on 704 often, reaching maxgamelength
            #pickit at current char position (called in diablo.py), next location is "C1-F_03"

        # not used, leaving it in for now to see during the run where the frostnova occurs
        elif location == "C1-F_03":
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder   
            #pickit at current char position (called in diablo.py), next location is

        # not used, leaving it in for now to see during the run where the frostnova occurs
        elif location == "C1-F_fake":
            self._frost_nova(self._char_config["atk_len_cs_trashmobs"]) #placeholder              
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 655, followed by sealdance_fake, then back to blizz_sorc.py for "C1-F_boss"

        elif location == "C1-F_boss":
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self) #hop over from fake seal to boss seal 
            wait(0.5)
            self._blizzard((100, -150), spray=10) 
            self._ice_blast((-50, 100), spray=30)
            self._cast_static()
            self._blizzard((100, 50), spray=10)
            wait(0.9)
            # pickit in diablo.py, next location is node 652, followed by sealdance_boss, then back to blizz_sorc.py for kill_deseis("B2-U")
        
        ### C2-G
        elif location == "C2-G_01":
            self._blizzard((-250, -70), spray=10)
            self._cast_static() 
            self._ice_blast((-100, 40), spray=20)
            wait(0.3)
            self._blizzard((-150, 150), spray=10)
            wait(0.9)
            #pickit at current char position (called in diablo.py), next location is "C2-G_02"

        elif location == "C2-G_02":
            if not self._pather.traverse_nodes([663], self): return False
            self._pather.offset_node(662, (0, 150))
            #pickit at current char position (called in diablo.py), next location is "C2-G_03"

        elif location == "C2-G_03":
            if not self._pather.traverse_nodes([662], self): return False
            self._pather.offset_node(662, (0, -150))
            wait(0.9)
            self._blizzard((-260, -100), spray=10)
            self._cast_static() 
            self._ice_blast((250, -130), spray=30)
            wait(0.3)
            self._blizzard((150, -100), spray=10)
            wait(1.8)
            if not self._pather.traverse_nodes([662], self): return False 
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 662, then back to blizz_sorc.py for "C2-G_boss"

        elif location == "C2-G_boss":
            if not self._pather.traverse_nodes([662], self): return False # just movement
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 662, followed by sealdance_boss, then back to blizz_sorc.py for kill_infector("C2-G")

        elif location == "C2-G_fake":
            if not self._pather.traverse_nodes([665], self): return False # just movement
            #pickit at current char position (called in diablo.py), next location in diablo.py is node 665, followed by sealdance_fake, then back to blizz_sorc.py for kill_diablo()

        # add here ALL the locations where no trash should be killed
        elif location in ["pent_before_a", "A1-L_03", "A1-L_fake"]:  #could add C1-F_03 and C1-F_fake (currently just doing frostnova there)
            Logger.debug("No attack choreography available in blizz_sorc.py for this location " + location + " - skipping to shorten run.")
            #pickit at current char position (called in diablo.py)
        
        else:
            Logger.debug("I have no location argument given for kill_cs_trash(" + location + "), should not happen. Casting a Blizzard on my head instead!")
            self._frost_nova(0.5) #self._char_config["atk_len_cs_trashmobs"]
            self._blizzard((0, 0), spray=10)
            #pickit at current char position (called in diablo.py)

        return True
    
    def kill_vizier(self, seal_layout:str) -> bool:
        if seal_layout == "A1-L":
            #previous node in diablo.py is [615], this is our current location
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
            #diablo.py loots after killing vizier at current char position and 612. Then hops to 611 for calibration to loop to pentagram

        elif seal_layout == "A2-Y":
            #previous node in diablo.py is [626], this is our current location
            if not self._pather.traverse_nodes([627, 623], self): return False # this might be a weak traverse: 627 is not very strong
            self._frost_nova(0.8) # instead of wait(0.8) #self._char_config["atk_len_cs_trashmobs"] #replace waits with frostnova
            self._blizzard((200, 150), spray=10)
            self._ice_blast((150, 100), spray=30)
            self._ice_blast((120, -100), spray=30)
            self._frost_nova(0.4) # instead of wait(0.4)
            self._blizzard((-400, -50), spray=10)
            self._ice_blast((150, 10), spray=30)
            self._ice_blast((300, 50), spray=30)
            self._frost_nova(0.4) # instead of wait(0.4)
            self._blizzard((150, 100), spray=10)
            self._frost_nova(0.5) # instead of wait(0.4)
            #diablo.py loots after killing vizier current char position (ideally 623) and then hops to 622 for calibration to loop to pentagram
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis(" + seal_layout + "), should not happen.")
            return False
        return True

    def kill_deseis(self, seal_layout:str) -> bool:
        if seal_layout == "B1-S":
            #previous node in diablo.py is [634], this is our current location
            if not self._pather.traverse_nodes([633], self): return False
            self._blizzard((-300, 0), spray=10)
            self._ice_blast((-100, 0), spray=30)
            self._cast_static()
            wait(0.3)
            pos_m = self._screen.convert_abs_to_monitor((-100, -50))
            self.pre_move()
            self.move(pos_m, force_move=True) 
            self._blizzard((-200, 100), spray=10)
            self._ice_blast((-200, 100), spray=30)
            self._cast_static()
            self._pather.traverse_nodes([632], self, time_out=2.5, force_tp=False)
            wait(0.3)
            self._blizzard((-200, 150), spray=10)
            self._ice_blast((-100, 100), spray=30)
            self._cast_static()
            self._blizzard((-100, 100), spray=10)
            self._pather.traverse_nodes([631], self, time_out=2.5, force_tp=False)
            wait(0.9)
            self._blizzard((100, -100), spray=10)
            self._cast_static() 
            self._ice_blast((100, 70), spray=30)
            wait(0.3)
            self._blizzard((100, 50), spray=10)
            #if not self._pather.traverse_nodes([630], self): return False
            wait(4.0)
            pos_m = self._screen.convert_abs_to_monitor((-100, 100))
            self.pre_move()
            self.move(pos_m, force_move=True)  
            #self._cast_static()
            #self._blizzard((-50, 50), spray=10)   
            self._cast_static()
            wait(4.0)
            pos_m = self._screen.convert_abs_to_monitor((200, -200))
            self.pre_move()
            self.move(pos_m, force_move=True)  
            self._cast_static()
            wait(3.0)
            if not self._pather.traverse_nodes([632], self): return False
            #diablo.py loots after killing De Seis at current char position (ideally 632) and then hops to 633, 634 for calibration to loop to pentagram 

        elif seal_layout == "B2-U":
            #previous node in diablo.py is [644], this is our current location
            if not self._pather.traverse_nodes([643], self): return False
            wait(0.3) 
            self._blizzard((-120, 150), spray=10)
            self._ice_blast((-70, 150), spray=30)
            wait(0.5) 
            pos_m = self._screen.convert_abs_to_monitor((80, 70))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(0.5)
            self._blizzard((-250, 70), spray=10)
            self._ice_blast((-250, 70), spray=30)
            wait(0.5) 
            pos_m = self._screen.convert_abs_to_monitor((-150, 50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(0.5) 
            self._blizzard((-280, 70), spray=10)
            self._ice_blast((-280, 70), spray=30)
            wait(0.9)   
            if not self._pather.traverse_nodes([641], self): return False
            wait(0.3) 
            self._blizzard((-150, 100), spray=10)
            wait(0.5) 
            pos_m = self._screen.convert_abs_to_monitor((100, -150))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(0.5)
            self._blizzard((-280, 200), spray=10)
            self._ice_blast((-280, 200), spray=30)
            wait(0.8)      
            if not self._pather.traverse_nodes([640], self): return False
            self._blizzard((-100, 50), spray=10)
            self._cast_static()
            self._cast_static()
            wait(3.0)
            pos_m = self._screen.convert_abs_to_monitor((100, -100))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self._cast_static()
            wait(2.5)      
            pos_m = self._screen.convert_abs_to_monitor((50, -50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self._cast_static()
            wait(3.5)
            #diablo.py loots after killing De Seis at current char position and afterwards a second time at [640] from there hops to 640 for calibration to loop to pentagram 
        
        else:
            Logger.debug(seal_layout + ": Invalid location for kill_deseis(" + seal_layout + "), should not happen.")
            return False
        return True 


    def kill_infector(self, seal_layout:str) -> bool:
        if seal_layout == "C1-F":
            #previous node in diablo.py is [652], this is our current location
            self._pather.traverse_nodes_fixed("dia_c1f_652", self._char)
            wait(0.5)
            pos_m = self._screen.convert_abs_to_monitor((150, 0))
            self.pre_move()
            self.move(pos_m, force_move=True)  
            self._blizzard((200, 20), spray=10)
            self._cast_static() 
            self._ice_blast((150, 20), spray=30)
            wait(0.3)
            self._blizzard((100, 20), spray=10)
            wait(0.8)
            pos_m = self._screen.convert_abs_to_monitor((200, -50))
            self.pre_move()
            self.move(pos_m, force_move=True)
            wait(0.8)  
            self._blizzard((100, 20), spray=10)
            self._cast_static() 
            self._ice_blast((100, 20), spray=30)
            wait(0.3)
            self._blizzard((120, 20), spray=10)
            self._cast_static()
            wait(2.0)
            if not self._pather.traverse_nodes([653], self): return False
            self._blizzard((100, 100), spray=10)
            #diablo.py loots after killing Infector at current char position and then hops to 654 for calibration to loop to pentagram 

        elif seal_layout == "C2-G":
            #previous node in diablo.py is [662], this is our current location
            self._pather.traverse_nodes_fixed("dia_c2g_663", self) # REPLACES for increased consistency: #if not self._pather.traverse_nodes([662, 663], self): return False
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
            #diablo.py loots after killing Infector at current char position. next location is C2-G_fake.
        
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
        #pickit at current char position (called in diablo.py)
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
