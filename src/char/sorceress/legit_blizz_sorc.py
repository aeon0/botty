import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
from pather import Location
import numpy as np
import time #for Diablo
import cv2 #for Diablo
from item.pickit import PickIt #for Diablo

class BlizzSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Blizz Sorc")
        super().__init__(*args, **kwargs)
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
        atk_sequences = max(2, int(self._char_config["atk_len_nihlatak"]) - 1)
        for i in range(atk_sequences):
            nihlatak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], self._screen.grab())
            if nihlatak_pos_abs is not None:
                cast_pos_abs = np.array([nihlatak_pos_abs[0] * 0.9, nihlatak_pos_abs[1] * 0.9])
                self._blizzard(cast_pos_abs, spray=90)
                self._cast_static()
                # Do some tele "dancing" after each sequence
                if i < atk_sequences - 1:
                    rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                    tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                    pos_m = self._screen.convert_abs_to_monitor(tele_pos_abs)
                    self.pre_move()
                    self.move(pos_m)
        # Move to items
        self._pather.traverse_nodes(end_nodes, self, time_out=0.8)
        self._blizzard((0, 0), spray=10)
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

    # GET TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_TP"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.83, time_out=0.1).valid
            if not found: self._pather.traverse_nodes_fixed(path, self)
        if not found:
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True

    # OPEN SEALS
    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 6:
            # try to select seal
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1) + " of 7)")
            self.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(i*0.5)
            # check if seal is opened
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid
            if found:
                Logger.info(seal_layout + ": is open")
                break
            else:

                Logger.debug(seal_layout + ": not open")
                pos_m = self._screen.convert_abs_to_monitor((0, 0)) #remove mouse from seal
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 2:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " of 7 times, trying to kill trash now") # ISSUE: if it failed 7/7 times, she does not try to open the seal: this way all the effort of the 7th try are useless. she should click at the end of the whole story. 
                    self._blizzard((-50, -50), spray=10)
                    self._picked_up_items |= self._pickit.pick_up_items(self)
                    wait(i*0.5) #let the hammers clear & check the template -> the more tries, the longer the wait
                    if not self._pather.traverse_nodes(seal_node, self): return False # re-calibrate at seal node
                else:
                    # do a little random hop & try to click the seal
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, direction]) #50 *  removed the Y component - we never want to end up BELOW the seal (any curse on our head will obscure the template check)
                    self.move((x_m, y_m), force_move=True)
                i += 1
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/_failed_seal_{seal_layout}_{i}tries" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found
    
    def kill_cs_trash(self) -> bool:   
        self._blizzard((-450, -100), spray=10)
        self._ice_blast((0, 100), spray=30)
        self._ice_blast((-40, -100), spray=30)
        wait(0.3)
        self._blizzard((-50, -50), spray=10)
        pos_m = self._screen.convert_abs_to_monitor((-10, -10))
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._picked_up_items |= self._pickit.pick_up_items(self)
        return True
    
    def kill_cs_trash(self, layout:str) -> bool:
        if layout== "penta":
            self._blizzard((-450, -100), spray=10)
            self._ice_blast((0, 100), spray=30)
            self._ice_blast((-40, -100), spray=30)
            wait(0.3)
            self._blizzard((-50, -50), spray=10)
            pos_m = self._screen.convert_abs_to_monitor((-10, -10))
            self.pre_move()
            self.move(pos_m, force_move=True)
            self._picked_up_items |= self._pickit.pick_up_items(self) 
        if layout== "vizier":
            self._blizzard((-50, -120), spray=10)
            self._ice_blast((150, 50), spray=30)
            wait(0.5)
            self._blizzard((100, -20), spray=10)
            wait(0.9)
        if layout== "seis":
            self._blizzard((-150, -50), spray=10)
            self._ice_blast((-150, -50), spray=30)
            self._cast_static()
            wait(0.3)
            self._blizzard((-100, -50), spray=10)
            wait(0.9)
        if layout== "infector":
            self._blizzard((-50, -50), spray=10)
            self._ice_blast((50, 50), spray=30)
            self._cast_static()
            wait(0.3)
            self._blizzard((50, 50), spray=10)
            wait(0.9)
        return True

    def kill_vizier(self, seal_layout: str) -> bool: 
        if seal_layout== "A1-L":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes([612], self): return False
            self._blizzard((-180, -290), spray=10)
            self._ice_blast((0, 100), spray=30)
            self._cast_static() 
            self._blizzard((-100, -50), spray=10)
            wait(0.9)
            if not self._pather.traverse_nodes([613], self): return False
            wait(0.9)
            self._blizzard((190, -90), spray=10)
            self._ice_blast((-150, 90), spray=30)
            self._cast_static() 
            wait(0.8)
            self._blizzard((-150, 70), spray=10)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([614], self): return False
            if not self._sealdance(["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], seal_layout + "-Fake", [614]): return False
            if not self._pather.traverse_nodes([613, 615], self): return False
            if not self._sealdance(["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"], seal_layout + "-Boss", [615]): return False
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
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
            ### LOOT ###
            #if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            #Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([612], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([612], self): return False
            if not self._pather.traverse_nodes([611], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([611], self): return False
            ### GO HOME ###
            if not self._pather.traverse_nodes([611], self): return False # calibrating here brings us home with higher consistency.
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            if not self._pather.traverse_nodes_fixed("dia_a1l_home", self): return False
            Logger.info(seal_layout + ": Looping to Pentagram")
            if not self._loop_pentagram("dia_a1l_home_loop"): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "A2-Y":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([624], self): return False
            wait(0.8)
            self._blizzard((150, -40), spray=10)
            self._cast_static()
            self._ice_blast((-150, -90), spray=30)
            wait(0.3)
            self._blizzard((-150, -100), spray=10)
            wait(0.8)
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
            if not self._pather.traverse_nodes([623], self): return False
            if not self._pather.traverse_nodes([624], self): return False
            if not self._pather.traverse_nodes([625], self): return False
            if not self._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], seal_layout + "-Fake", [625]): return False
            self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self) #instead of traversing node 626 which causes issues
            self._blizzard((70, -50), spray=10)
            wait(0.8)
            #self._ice_blast((150, 10), spray=30)
            if not self._pather.traverse_nodes([626], self): return False
            if not self._sealdance(["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"], seal_layout + "-Boss", [626]): return False
            self._blizzard((50, 170), spray=10)
            wait(0.8)
            if not self._pather.traverse_nodes([627, 623], self): return False
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss A (Vizier)")
            wait(0.8)
            self._blizzard((200, 150), spray=10)
            self._ice_blast((150, 100), spray=30)
            self._ice_blast((120, -100), spray=30)
            wait(0.4)
            self._blizzard((-400, -50), spray=10)
            self._ice_blast((150, 10), spray=30)
            self._ice_blast((300, 50), spray=30)
            wait(0.4)
            self._blizzard((150, 100), spray=10)
            wait(0.5)
            ### LOOT ###
            #if not self._pather.traverse_nodes_fixed("dia_a2y_hop_622", self): return False
            #Logger.info(seal_layout + ": Hop!")
            if not self._pather.traverse_nodes([624, 625], self): return False
            self._blizzard((250, 200), spray=10)
            self._ice_blast((150, 150), spray=60)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([624], self): return False
            if not self._pather.traverse_nodes([623,622], self): return False
            self._blizzard((0, -100), spray=10)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([622], self): return False
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_a2y_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_deseis(self, seal_layout: str) -> bool:
        if seal_layout == "B1-S":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")  
            ### CLEAR TRASH & APPROACH SEAL ###
            if not self._pather.traverse_nodes([635], self): return False
            self._blizzard((-200, -70), spray=10)
            self._ice_blast((-150, -60), spray=30)
            self._ice_blast((-150, -100), spray=30)
            self._blizzard((-450, -120), spray=10)
            self._picked_up_items |= self._pickit.pick_up_items(self)
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
            self._picked_up_items |= self._pickit.pick_up_items(self)
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
            self._picked_up_items |= self._pickit.pick_up_items(self)
            self._sealdance(["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED","DIA_B1S2_23_MOUSEOVER"], seal_layout + "-Boss", [635])
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
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
            ### LOOT ###
            if not self._pather.traverse_nodes([631], self): return False 
            wait(4.0)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([631], self): return False
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_b1s_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_b1s_home_loop"): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "B2-U":
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            Logger.info(seal_layout +": Starting to clear Seal")
            pos_m = self._screen.convert_abs_to_monitor((-300, 0))
            self.pre_move()
            self.move(pos_m, force_move=True) 
            self._blizzard((100, -70), spray=10)
            self._ice_blast((100, 100), spray=30)
            self._ice_blast((-50, -100), spray=30)
            self._blizzard((100, 100), spray=10)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            pos_m = self._screen.convert_abs_to_monitor((-350, -200))
            self.pre_move()
            self.move(pos_m, force_move=True)
            pos_m = self._screen.convert_abs_to_monitor((-100, -100))
            self.pre_move()
            self.move(pos_m, force_move=True)
            if not self._pather.traverse_nodes([644], self): return False
            self._blizzard((250, 0), spray=10)
            self._ice_blast((150, 20), spray=30)
            wait(0.3)
            self._pather.offset_node(643, (70, 100))
            if not self._pather.traverse_nodes([643], self): return False
            self._pather.offset_node(643, (-70, -100))
            ### CLEAR TRASH & APPROACH SEAL ###
            wait(0.8)
            self._blizzard((-150, 100), spray=10)
            self._cast_static()
            self._ice_blast((-200, 100), spray=30)
            wait(0.3)
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
            self._picked_up_items |= self._pickit.pick_up_items(self)
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
            if not self._pather.traverse_nodes([644], self): return False
            self._sealdance(["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"], seal_layout + "-Boss", [644])
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss B (De Seis)")
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
            self._picked_up_items |= self._pickit.pick_up_items(self)         
            ### LOOT ###
            if not self._pather.traverse_nodes([640], self): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([640], self): return False
            self._pather.traverse_nodes_fixed("dia_b2u_home", self)
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_b2u_home_loop"): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([602], self , time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_infector(self, seal_layout: str) -> bool:
        if seal_layout == "C1-F":
            Logger.info(seal_layout +": Starting to clear Seal")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            ### CLEAR TRASH & APPROACH SEAL ###
            self._blizzard((-250, -100), spray=10)
            self._ice_blast((-200, -50), spray=30)
            self._ice_blast((-200, 0), spray=30)
            wait(0.3)
            self._blizzard((-350, -250), spray=10)
            wait(0.9)
            wait(0.9)
            self._blizzard((150, 0), spray=10)
            wait(0.9)
            self._pather.traverse_nodes_fixed("dia_c1f_hop_fakeseal", self) # REPLACES: if not self._pather.traverse_nodes([656, 654, 655], self, time_out=3): return False #ISSUE: getting stuck on 704 often, reaching maxgamelength
            if not self._sealdance(["DIA_C1F_OPEN_NEAR"], ["DIA_C1F_CLOSED_NEAR","DIA_C1F_MOUSEOVER_NEAR"], seal_layout + "-Fake", [654]): return False #ISSUE: getting stuck on 705 during sealdance(), reaching maxgamelength
            self._pather.traverse_nodes_fixed("dia_c1f_654_651", self)
            wait(0.5)
            self._blizzard((100, -150), spray=10) 
            self._ice_blast((-50, 100), spray=30)
            self._cast_static()
            self._blizzard((100, 50), spray=10)
            wait(0.9)
            if not self._sealdance(["DIA_C1F_BOSS_OPEN_RIGHT", "DIA_C1F_BOSS_OPEN_LEFT"], ["DIA_C1F_BOSS_MOUSEOVER_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_LEFT", "DIA_C1F_BOSS_CLOSED_NEAR_RIGHT"], seal_layout + "-Boss", [652]): return False
            ### KILL BOSS ###
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
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
            ### LOOT ###
            if not self._pather.traverse_nodes([653], self): return False
            self._blizzard((100, 100), spray=10)
            self._picked_up_items |= self._pickit.pick_up_items(self)
            ### GO HOME ###
            if not self._pather.traverse_nodes([653], self, time_out=3): return False # this node often is not found
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_c1f_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_c1f_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        elif seal_layout == "C2-G":
            Logger.info(seal_layout +": Starting to clear Seal")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())            
            ### CLEAR TRASH & APPROACH SEAL ###
            self._blizzard((-250, -70), spray=10)
            self._cast_static() 
            self._ice_blast((-100, 40), spray=20)
            wait(0.3)
            self._blizzard((-150, 150), spray=10)
            wait(0.9)
            if not self._pather.traverse_nodes([663], self): return False
            self._pather.offset_node(662, (0, 150))
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
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([662], self): return False
            if not self._sealdance(["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], seal_layout + "-Boss", [662]): return False
            self._pather.traverse_nodes_fixed("dia_c2g_663", self) # REPLACES for increased consistency: #if not self._pather.traverse_nodes([662, 663], self): return False
            Logger.info(seal_layout + ": Kill Boss C (Infector)")
            ### KILL BOSS ###
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
            self._picked_up_items |= self._pickit.pick_up_items(self)
            if not self._pather.traverse_nodes([663], self): return False
            ### LOOT ###
            if not self._pather.traverse_nodes([665], self): return False
            if not self._sealdance(["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"], seal_layout + "-Fake", [665]): return False
            self._picked_up_items |= self._pickit.pick_up_items(self)
            wait(3.5)
            ### GO HOME ###
            if not self._pather.traverse_nodes([665], self): return False
            Logger.info(seal_layout + ": Static Pathing to Pentagram")
            self._pather.traverse_nodes_fixed("dia_c2g_home", self)
            Logger.info(seal_layout + ": Looping to PENTAGRAM")
            if not self._loop_pentagram("dia_c2g_home_loop"): return False
            if not self._pather.traverse_nodes([602], self, time_out=5): return False
            Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
            if self._config.general["info_screenshots"]: cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return True
        else: 
            Logger.debug("Variable Seal_Layout was " +seal_layout + ". Should not happen, aborting run")
            return False

    def kill_diablo(self) -> bool:
        # Move close to diablo
        #self._pather.traverse_nodes(end_nodes, self, time_out=0.8, do_pre_move=False)
        # move mouse to center, otherwise hammers sometimes dont fly, not sure why
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
