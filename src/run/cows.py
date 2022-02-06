from asyncio.log import logger
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


class Cows:
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
        self.used_tps = 0


    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Cows /!\ BETA Version /!\ please do not run without supervision.")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Cows requires teleport")
        #CHECK IF THE LEG IS ALREADY IN THE STASH OR INVENTORY!
            #if yes: open_cows()
            #if no: stony_field()
        logger.info("Opening WP & moving to Stony Field")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(0, 2)
        return Location.A1_STONY_FIELD_WP

    def _legdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 6:
            # try to select wirts corpse
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1) + " of 7)")
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, time_out=0.5)
            wait(i*0.5)
            # check if wirts corpse is opened
            found = self._template_finder.search_and_wait(seal_opentemplates, threshold=0.75, time_out=0.5, take_ss=False).valid
            if found:
                Logger.info(seal_layout + ": is open")
                break

            else:
                Logger.debug(seal_layout + ": not open")
                pos_m = self._screen.convert_abs_to_monitor((0, 0)) #remove mouse from corpse
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 2:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " of 7 times, trying to kill trash now") 
                    self._char.kill_cow_trash()
                    self._picked_up_items |= self._pickit.pick_up_items(self._char)
                    wait(i*0.5) #let the spells clear & check the template -> the more tries, the longer the wait
                    if not self._pather.traverse_nodes(seal_node, self._char): return False # re-calibrate at corpse node
                else:
                    # do a little random hop & try to click the corpse
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = self._screen.convert_abs_to_monitor([50 * direction, direction])
                    self._char.move((x_m, y_m), force_move=True)
                i += 1
        if self._config.general["info_screenshots"] and not found: cv2.imwrite(f"./info_screenshots/cows_failed_corpse" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())
        return found


    def _stony_field(self)-> bool:      
        if do_pre_buff: self._char.pre_buff()   
        #random tele to find yellow
        #click red portal
        return True


    def _tristram(self) -> bool:
        if do_pre_buff: self._char.pre_buff()   
        logger.info("Entering Old Tristram to get the leg")
        logger.info("Calibrating at Entrance TP ")
        if not self._pather.traverse_nodes([1000], self._char, time_out=5): return False
        logger.info("Static Path to Corpse")
        self._pather.traverse_nodes_fixed("dia_a_layout", self._char)
        logger.info("Calibrating at Corpse")
        if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
        logger.info("Looting the leg the Corpse")
        self._legdance(["WIRTOPEN.PNG"],["WIRTCLOSED.PNG"],"Old-Tristram", [1001])
        logger.info("Grabbing the leg")
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        logger.info("Making TP to go home")
        if not self._ui_manager.has_tps():
            Logger.warning("Cows: Open TP failed. Aborting run.")
            self.used_tps += 20
            return False
        mouse.click(button="right")
        self.used_tps += 1
        return True


    def _open_cow_portal(self)-> bool:
        #go to akara, buy a tome
        #go to stash & cube leg & top
        #enter portal
        return True


    def _cows(self) -> bool:
        #this is where the magic happens...
        return True


    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        self._picked_up_items = False
        self.used_tps = 0   
        if not self._stony_field(): return False
        if not self._tristram(): return False
        if not self._cows(): return False
       
        return (Location.A1_COWS_END, self._picked_up_items)

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
    screen = Screen()
    game_stats = GameStats()
    bot = Bot(screen, game_stats, False)
