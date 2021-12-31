import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import Screen


class Diablo:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Diablo /!\ BETA Version /!\ please do not run without supervision.")
        if not self._char.can_teleport():
            raise ValueError("Diablo requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(4, 2)
        return Location.A4_DIABLO_WP

    def _river_of_flames(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False
        Logger.debug("Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        Logger.info("Moving to CS ENTRANCE")
        found = False
        templates = ["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"]
        # Looping in smaller teleport steps to make sure we find the entrance
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.8, time_out=0.1, take_ss=False).valid 
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char)
        if not found:
        #    if self._config.general["info_screenshots"]:
        #        cv2.imwrite(f"./info_screenshots/failed_cs_entrance_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        if not self._pather.traverse_nodes([601], self._char, threshold=0.8): return False
        Logger.info("Calibrated at CS ENTRANCE")
        return True

    def _cs_pentagram(self) -> bool:
        self._pather.traverse_nodes_fixed("diablo_entrance_pentagram", self._char)
        Logger.info("Moving to PENTAGRAM")
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_3", "DIA_NEW_PENT_5", "DIA_NEW_PENT_6"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.82, time_out=0.1).valid
            if not found:
                self._pather.traverse_nodes_fixed("diablo_entrance_pentagram_loop", self._char)
        if not found:
            if self._config.general["info_screenshots"]:
                cv2.imwrite(f"./info_screenshots/failed_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        self._pather.traverse_nodes([602], self._char, threshold=0.82)
        Logger.info("Calibrated at PENTAGRAM")
        return True

    def _loop_pentagram(self, path) -> bool:
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2", "DIA_NEW_PENT_3", "DIA_NEW_PENT_5", "DIA_NEW_PENT_6"] 
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = self._template_finder.search_and_wait(templates, threshold=0.82, time_out=0.1).valid
            if not found:
                self._pather.traverse_nodes_fixed(path, self._char)
        if not found:
        #    if self._config.general["info_screenshots"]:
        #        cv2.imwrite(f"./info_screenshots/failed_loop_pentagram_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
            return False
        return True

    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str) -> bool:
        i = 0
        while i < 4:
            # try to select seal
            Logger.info(seal_layout + ": trying to open (try #" + str(i+1) + " of 5)")
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(1)
            # check if seal is opened
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid
            if found:
                Logger.info(seal_layout + ": is open")
                break
            else:
                Logger.info(seal_layout + ": not open")
                pos_m = self._screen.convert_abs_to_monitor((0, 0)) #remove mouse from seal
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 2:
                    Logger.info(seal_layout + ": failed " + str(i+2) + " of 5 times, trying to kill trash now")
                    self._char.kill_cs_trash()
                    wait(1) #let the hammers clear & check the template
                else:
                    # do a little random hop & try to click the seal
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, 50 * direction])
                    self._char.move((x_m, y_m), force_move=True) 
                i += 1
        #if self._config.general["info_screenshots"] and not found:
        #    cv2.imwrite(f"./info_screenshots/failed_seal_{seal_layout}_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found

    def _seal_A1(self) -> bool:
        seal_layout = "A1-L"
        Logger.info("Seal Layout: " + seal_layout)
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return False
        if not self._pather.traverse_nodes([611], self._char): return False
        self._char.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([612, 613], self._char): return False
        self._char.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([614], self._char): return False
        if not self._sealdance(["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_MOUSEOVER", "DIA_A1L2_14_CLOSED_DARK"], seal_layout + "-Fake"): return False
        if not self._pather.traverse_nodes([613, 615], self._char): return False
        if not self._sealdance(["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"], seal_layout + "-Boss"): return False
        if not self._pather.traverse_nodes([612, 611, 610], self._char): return False
        Logger.info(seal_layout + ": Kill Boss A (Vizier)")
        self._char.kill_vizier(seal_layout, [612], [611])
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        #if not self._pather.traverse_nodes([610], self._char): return False #not calibrating here brings us home safely.
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_a1l_home_loop"):
            return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_A2(self) -> bool:
        seal_layout = "A2-Y"
        Logger.info("Seal Layout: " + seal_layout)
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return False
        if not self._pather.traverse_nodes([622], self._char): return False
        self._char.kill_cs_trash()
        if not self._pather.traverse_nodes([623, 624], self._char): return False
        self._char.kill_cs_trash()
        #self._picked_up_items |= self._pickit.pick_up_items(self._char) #covered by looting at the end of vizier
        if not self._pather.traverse_nodes([625], self._char): return False
        if not self._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED","DIA_A2Y4_29_MOUSEOVER"], seal_layout + "-Fake"): return False
        self._pather.traverse_nodes_fixed("dia_a2y_sealfake_sealboss", self._char) #instead of traversing node 626
        if not self._sealdance(["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"], seal_layout + "-Boss"): return False
        if not self._pather.traverse_nodes([627, 622], self._char): return False
        Logger.info(seal_layout + ": Kill Boss A (Vizier)")
        self._char.kill_vizier([623], [624])
        if not self._pather.traverse_nodes([623], self._char): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([622], self._char): return False
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_a2y_home_loop"):
            return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_B1(self): #NEW & dirty
        seal_layout = "B1-S"
        Logger.info("Seal Layout: " + seal_layout)
        #self._pather.traverse_nodes_fixed("dia_b1s_layout2_seal", self._char)
        self._char.kill_cs_trash()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([634], self._char): return False # seal boss far
        self._sealdance(["DIA_B1S2_23_OPEN"], ["DIA_B1S2_23_CLOSED", "DIA_B1S2_23_MOUSEOVER"], seal_layout + "-Boss")
        self._pather.traverse_nodes_fixed("dia_b1s_seal_deseis", self._char)
        Logger.info(seal_layout + ": Kill Boss B (De Seis)")
        if not self._char.kill_deseis([632], [631], [632]): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_b1s_home_loop"):
            return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_B2(self): # WORKS STABLE
        seal_layout = "B2-U"
        Logger.info("Seal Layout: " + seal_layout)
        #if not self._pather.traverse_nodes([640], self._char): return False
        #self._char.kill_cs_trash() # at safe_dist
        #if not self._pather.traverse_nodes([641, 642], self._char): return False
        #self._char.kill_cs_trash() # at safe_dist
        #self._picked_up_items |= self._pickit.pick_up_items(self._char)
        #wait(1) #give it some time to clear the templates
        #if not self._pather.traverse_nodes([643, 644], self._char): return False
        self._pather.traverse_nodes_fixed("dia_b2u_bold_seal", self._char)
        self._sealdance(["DIA_B2U2_16_OPEN"], ["DIA_B2U2_16_CLOSED", "DIA_B2U2_16_MOUSEOVER"], seal_layout + "-Boss")
        if not self._pather.traverse_nodes([642, 646], self._char): return False #643, 642, 
        #self._pather.traverse_nodes_fixed("dia_b2u_bold_deseis", self._char) # high failure rate.
        Logger.info(seal_layout + ": Kill Boss B (De Seis)")
        if not self._char.kill_deseis([641], [640], [646]): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([640], self._char): return False
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([640], self._char): return False
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_b2u_home_loop"):
            return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_C1(self) -> bool: # The boss Seal takes several tries to recognize. Maybe we need new templates
        seal_layout = "C1-F"
        Logger.info("Seal Layout: " + seal_layout)
        #if not self._pather.traverse_nodes([701, 702], self._char): return False
        #self._char.kill_cs_trash()
        #self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([703], self._char): return False
        if not self._sealdance(["DIA_C1F2_23_OPEN"], ["DIA_C1F2_23_CLOSED", "DIA_C1F2_23_MOUSEOVER"], seal_layout + "-Fake"): return False
        self._pather.traverse_nodes_fixed("dia_c1f_654_651", self._char) # REPLACES: if not self._pather.traverse_nodes([703, 702, 701], self._char): return False
        if not self._sealdance(["DIA_C1F2_8_OPEN", "DIA_C1F2_11_OPEN", "DIA_C1F2_15_OPEN"], ["DIA_C1F2_8_CLOSED", "DIA_C1F2_11_CLOSED", "DIA_C1F2_11_MOUSEOVER","DIA_C1F2_15_CLOSED", "DIA_C1F2_15_MOUSEOVER"], seal_layout + "-Boss"): return False # "DIA_C1F2_8_MOUSEOVER", is recognized often, but slows seals down. commented out for testing
        self._pather.traverse_nodes_fixed("dia_c1f_702", self._char) #if not self._pather.traverse_nodes([702], self._char): return False
        Logger.info(seal_layout + ": Kill Boss C (Infector)")
        self._char.kill_infector()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_c1f_home_loop"):
            return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def _seal_C2(self) -> bool:
        seal_layout = "C2-G"
        Logger.info("Seal Layout: " + seal_layout)
        #if not self._pather.traverse_nodes([660, 661, 662], self._char): return False
        if not self._pather.traverse_nodes([663, 662], self._char): return False
        if not self._sealdance(["DIA_C2G2_7_OPEN"], ["DIA_C2G2_7_CLOSED", "DIA_C2G2_7_MOUSEOVER"], seal_layout + "-Boss"): return False
        self._pather.traverse_nodes_fixed("dia_c2g_663", self._char) # REPLACES: #if not self._pather.traverse_nodes([662, 663], self._char): return False
        Logger.info(seal_layout + ": Kill Boss C (Infector)")
        self._char.kill_infector()
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        if not self._pather.traverse_nodes([664, 665], self._char): return False
        if not self._sealdance(["DIA_C2G2_21_OPEN"], ["DIA_C2G2_21_CLOSED", "DIA_C2G2_21_MOUSEOVER"], seal_layout + "-Fake"): return False
        # Lets go home
        Logger.info(seal_layout + ": Looping to Pentagram")
        if not self._loop_pentagram("dia_c2g_home_loop"): # looping home finds pentagram3, this calibrates too low :(
            return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.info(seal_layout + ": finished seal & calibrated at PENTAGRAM")
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/calibrated_pentagram_after_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return True

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        self._picked_up_items = False
        if do_pre_buff:
            self._char.pre_buff()
        if not self._river_of_flames():
            return False
        # TODO: Option to clear trash
        if not self._cs_pentagram():
            return False
        
        # Seal A: Vizier (to the left)
        #if do_pre_buff:
        #    self._char.pre_buff() # not needed if seals exectued in right order
        if not self._pather.traverse_nodes([602], self._char): return False
        self._pather.traverse_nodes_fixed("dia_a_layout", self._char) # we go to layout check
        #self._pather.traverse_nodes_fixed("dia_a_layout_bold", self._char) # While this is a faster approach it leads to more failure & chicken
        Logger.info("Checking Layout at A (Vizier)")
        self._char.kill_cs_trash()
        #Logger.info("Waiting to clear the flying hammers")
        #if self._config.general["info_screenshots"]:
        #    cv2.imwrite(f"./info_screenshots/_layout_check_A_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        if self._template_finder.search_and_wait(["DIABLO_A_LAYOUTCHECK0", "DIABLO_A_LAYOUTCHECK1", "DIABLO_A_LAYOUTCHECK2", "DIABLO_A_LAYOUTCHECK4", "DIABLO_A_LAYOUTCHECK5", "DIABLO_A_LAYOUTCHECK6"], threshold=0.8, time_out=0.5).valid:
        #if self._template_finder.search_and_wait(["DIA_A2Y_FAKE_CLOSED_LAYOUTCHECK1", "DIA_A2Y_FAKE_CLOSED_LAYOUTCHECK2", "DIA_A2Y_FAKE_CLOSED_LAYOUTCHECK3", "DIA_A2Y_FAKE_CLOSED_LAYOUTCHECK4", "DIA_A2Y_FAKE_CLOSED_LAYOUTCHECK5"], threshold=0.8, time_out=0.5).valid: #lowered threshold - lots of missed A2Y layouts
            if not self._seal_A2():
                return False
        else:
            if not self._seal_A1():
                return False  

        # Seal B: De Seis (to the top) | Layout check sometimes fails for B1S
        if do_pre_buff:
            self._char.pre_buff()
        self._char.kill_cs_trash()
        if not self._pather.traverse_nodes([602], self._char): return False
        #self._pather.traverse_nodes_fixed("dia_b_layout", self._char) # we go to layout check
        self._pather.traverse_nodes_fixed("dia_b_layout_bold", self._char) # we go to layout check
        Logger.debug("Checking Layout at B (De Seis)")
        #if self._config.general["info_screenshots"]:
        #    cv2.imwrite(f"./info_screenshots/_layout_check_B_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        #if self._template_finder.search_and_wait(["DIABLO_B_LAYOUTCHECK0", "DIABLO_B_LAYOUTCHECK1"], threshold=0.75, time_out=0.5).valid:
        if self._template_finder.search_and_wait(["DIA_B1S_BOSS_CLOSED_LAYOUTCHECK1", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK2", "DIA_B1S_BOSS_CLOSED_LAYOUTCHECK3"], threshold=0.87, time_out=0.5).valid:
            self._seal_B1()
        else:
            self._seal_B2()   

        # Seal C: Infector (to the right)
        if do_pre_buff:
            self._char.pre_buff()
        self._char.kill_cs_trash()
        if not self._pather.traverse_nodes([602], self._char): return False
        #self._pather.traverse_nodes_fixed("dia_c_layout", self._char) # we go to layout check
        self._pather.traverse_nodes_fixed("dia_c_layout_bold", self._char) # we go to layout check
        Logger.debug("Checking Layout at C (Infector)")
        #self._char.kill_cs_trash() #wait(2) #kill trash & wait for hammers to clear to improve layout check consistency
        #if self._config.general["info_screenshots"]:
        #    cv2.imwrite(f"./info_screenshots/_layout_check_C_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        #if self._template_finder.search_and_wait(["DIABLO_C_LAYOUTCHECK0", "DIABLO_C_LAYOUTCHECK1", "DIABLO_C_LAYOUTCHECK2"], threshold=0.75, time_out=0.5).valid:
        if self._template_finder.search_and_wait(["DIA_C2G_BOSS_CLOSED_LAYOUTCHECK1", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK2", "DIA_C2G_BOSS_CLOSED_LAYOUTCHECK3"], threshold=0.87, time_out=0.5).valid:
            if not self._seal_C2():
                return False
        else:
            if not self._seal_C1():
                return False

        # Diablo
        Logger.info("Waiting for Diablo to spawn") # we could add a check here, if we take damage: if yes, one of the sealbosses is still alive (otherwise all demons would have died when the last seal was popped)
        if not self._pather.traverse_nodes([602], self._char): return False
        self._char.kill_diablo() 
        wait(0.2, 0.3)
        if self._config.general["info_screenshots"]:
            cv2.imwrite(f"./info_screenshots/_dia_kill_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        return (Location.A4_DIABLO_END, self._picked_up_items) #there is an error  ValueError: State 'diablo' is not a registered state.

if __name__ == "__main__":
    from screen import Screen
    import keyboard
    from game_stats import GameStats
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from ui import UiManager
    from bot import Bot
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)
    # bot._diablo.battle(True)
    # bot._diablo._traverse_river_of_flames()
    # bot._diablo._cs_pentagram()
    # bot._pather.traverse_nodes_fixed("dia_a_layout", bot._char) # we check for layout of A (1=Y or 2=L) L lower seal pops boss, upper does not. Y upper seal pops boss, lower does not
    # Logger.info("Checking Layout at A")
    # if bot._template_finder.search_and_wait(["DIABLO_A_LAYOUTCHECK0", "DIABLO_A_LAYOUTCHECK1", "DIABLO_A_LAYOUTCHECK2"], threshold=0.8, time_out=0.1).valid:
    #     bot._diablo._seal_A2()
    # else:
    #     bot._diablo._seal_A1()
    bot._diablo._sealdance(["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED","DIA_A2Y4_29_MOUSEOVER"], "TEST-Seal1")


# issue log:
# C1F traverse 702 does not work after opening boss seal (if infector is "fast" and mobs are already approaching) -> fixed by using static path
# A1L - if vizier spawns at 610 pr 611 you tele to nirvana
# C2G looping home brings us too low
# B2U - static path from seal to 646 - otherwise you get stuck whilst searcdhing for nodes & fanamobs just kill you