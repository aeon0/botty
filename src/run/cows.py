from asyncio.log import logger
import cv2
import time
import random
import keyboard
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
import numpy as np


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
        Logger.info("Run Secret Cow Level")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Cows requires teleport")
        #CHECK IF THE LEG IS ALREADY IN THE STASH OR INVENTORY!
            #if yes: open_cows()
            #if no: stony_field()
        logger.info("Opening WP & moving to Stony Field")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(1, 2)
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

    def _scout(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)-> bool:
        pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
        t0 = self._screen.grab()
        self._char.move(pos_m, force_tp=True, force_move=True)
        t1 = self._screen.grab()
        diff = cv2.absdiff(t0, t1)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
        score = (float(np.sum(mask)) / mask.size) * (1/255.0)
        Logger.debug(str(score) + ": is our current score")
        if score < .10:
            stuck_count += 1
            if stuck_count >=2:
                Logger.debug(str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3 teleports")
                pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                self._char.move(pos_m, force_tp=True)
                super_stuck +=1
            if super_stuck >= 2:
                Logger.debug(str(corner_picker) + ": Seems we are still stuck, randomly chosing a different corner: SWAPPING AREA")
                keepernumber = random.randint(1, 4)
                if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                    keepernumber = random.randint(1, 4) 
                    super_stuck = 0
                else:
                    corner_exclude = corner_picker
                    corner_picker = keepernumber
                    super_stuck = 0
                    Logger.debug(str(corner_picker) + ": is now our selected corner.")  

    def _stony_field(self)-> bool:      #do_pre_buff: bool
        # if do_pre_buff: self._char.pre_buff()   
        keyboard.send("tab")
        keyboard.send(self._char._skill_hotkeys["teleport"])
        #setting up variables
        found = False
        score = -1
        corner_picker = 2 #we start searching towards the top, as often the cold plains entrance is at the bottom of the map
        corner_exclude = 2
        exclude1 = corner_picker - 2
        exclude2 = corner_picker + 2 
        stuck_count = 0
        super_stuck = 0
        keepernumber = 0
        #lets start the search
        Logger.debug(str(corner_picker) + ": is our selected corner.")
        while not found:   
            found = self._template_finder.search_and_wait(["COW_STONY_FIELD_0_TRANSPARENT", "COW_STONY_FIELD_1_TRANSPARENT", "COW_STONY_FIELD_SINGLE", "COW_STONY_FIELD_YELLOW",], threshold=0.85, time_out=0.1, take_ss=False, use_grayscale=False).valid #cow_stony_field_exit = exit to the underground passage, if that is found we just have to go to bottom directions to find the portal.

            if corner_picker == 1:
                """
                    self._scout(1, -250, -600, -200, -400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) #top - left
                elif corner_picker == 2:
                    self._scout(2, 250, 600, -200, -400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # top - right
                elif corner_picker == 3:
                    self._scout(3, 250, 600, 200, 400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - right
                elif corner_picker == 4:
                    self._scout(4, -250, -600, 200, 400, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - left
                """
                Logger.debug("Selected Corner 1 - Top Left")
                x1_m = -250
                x2_m = -600
                y1_m = -200
                y2_m = -400
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                if score < .10:
                    stuck_count += 1
                    if stuck_count >=2:
                        Logger.debug("Seems we are stuck, let's go reverse several steps")
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        super_stuck +=1
                    if super_stuck >= 2:
                        Logger.debug("Seems like we were not able to proceed in that direction, chosing another corner: SWAPPING AREA")
                        keepernumber = random.randint(1, 4)
                        if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                           keepernumber = random.randint(1, 4) 
                           super_stuck = 0
                        else:
                            corner_exclude = corner_picker
                            corner_picker = keepernumber
                            super_stuck = 0  

            elif corner_picker == 2:
                Logger.debug("Selected Corner 2 - Top Right")
                x1_m = 250
                x2_m = 600
                y1_m = -200
                y2_m = -400
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                if score < .10:
                    stuck_count += 1
                    if stuck_count >=2:
                        Logger.debug("Seems we are stuck, let's go reverse several steps")
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        super_stuck +=1
                    if super_stuck >= 2:
                        Logger.debug("Seems like we were not able to proceed in that direction, chosing another corner: SWAPPING AREA")
                        keepernumber = random.randint(1, 4)
                        if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                           keepernumber = random.randint(1, 4) 
                           super_stuck = 0
                        else:
                            corner_exclude = corner_picker
                            corner_picker = keepernumber
                            super_stuck = 0  
            
            elif corner_picker == 3:
                Logger.debug("Selected Corner 3 - Bottom Right")
                x1_m = 250
                x2_m = 600
                y1_m = 200
                y2_m = 400
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                
                if score < .10:
                    stuck_count += 1
                    if stuck_count >=2:
                        Logger.debug("Seems we are stuck, let's go reverse several steps")
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        super_stuck +=1
                    if super_stuck >= 2:
                        Logger.debug("Seems like we were not able to proceed in that direction, chosing another corner: SWAPPING AREA")
                        keepernumber = random.randint(1, 4)
                        if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                           keepernumber = random.randint(1, 4) 
                           super_stuck = 0
                        else:
                            corner_exclude = corner_picker
                            corner_picker = keepernumber
                            super_stuck = 0
                              
            elif corner_picker == 4:
                Logger.debug("Selected Corner 4 - Right")
                x1_m = -250
                x2_m = -600
                y1_m = 200
                y2_m = 400
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                
                if score < .10:
                    stuck_count += 1
                    if stuck_count >=2:
                        Logger.debug("Seems we are stuck, let's go reverse several steps")
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        super_stuck +=1
                    if super_stuck >= 2:
                        Logger.debug("Seems like we were not able to proceed in that direction, chosing another corner: SWAPPING AREA")
                        keepernumber = random.randint(1, 4)
                        if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                           keepernumber = random.randint(1, 4) 
                           super_stuck = 0
                        else:
                            corner_exclude = corner_picker
                            corner_picker = keepernumber
                            super_stuck = 0  

        if found == True:
            # We found our template on the minimap. Typically its not yet seen on the screen, so we therefore have to moveo 1-2 times towards the direction where the template was seen on the map & veryify with non-minimap templates that we arrived
            roomfound = False
            badroom = False
            template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_0_TRANSPARENT", "COW_STONY_FIELD_1_TRANSPARENT", "COW_STONY_FIELD_SINGLE", "COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False, normalize_monitor = True)
            if template_match.valid:
                Logger.debug("I found the Portal to Old Tristram on the Minimap, switching Minimap off")
                keyboard.send("tab")         
                Logger.debug("Teleporting towards the coordiantes where I saw the template on the minimap to make sure we have the Portal visible in our current view")
                self._char.move(template_match.center, force_tp=True)
                self._char.move(template_match.center, force_tp=True)

            # Let's confirm we are really in the room, or continue to teleport around
            while not roomfound and not badroom:
                Logger.debug("We should be close enough, trying to approach the portal by finding visual cues in its proximity") 
                roomfound = self._template_finder.search_and_wait(["COW_STONY_FIELD_PORTAL_0", "COW_STONY_FIELD_PORTAL_1", "COW_STONY_FIELD_PORTAL_2"], threshold=0.8, time_out=0.1, take_ss=False, use_grayscale=False).valid
                template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_0_TRANSPARENT", "COW_STONY_FIELD_1_TRANSPARENT", "COW_STONY_FIELD_SINGLE", "COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False)
                if template_match.valid:
                    pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                self._char.move(pos_m, force_tp=True, force_move=True)
                self._char.move(pos_m, force_tp=True, force_move=True)
                self._char.move(pos_m, force_tp=True, force_move=True)
                if score < .15:
                    stuck_count += 1
                    if stuck_count >=3:
                        pos_m = self._screen.convert_abs_to_monitor((500, -350))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        pos_m = self._screen.convert_abs_to_monitor((-485, 350))
                        self._char.move(pos_m, force_tp=True)
                        self._char.move(pos_m, force_tp=True)
                        keyboard.send("tab")
                        wait(1)
                        template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_0", "COW_STONY_FIELD_1_TRANSPARENT", "COW_STONY_FIELD_1", "COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False)
                        stuck_count = 0
                        if not template_match.valid:
                            Logger.debug("GOING DEEP WITH THE COORDS BABYYYY!!!")
                            pos_m = self._screen.convert_abs_to_monitor((500, 350))
                            self._char.move(pos_m, force_tp=True)
                            self._char.move(pos_m, force_tp=True)
                            pos_m = self._screen.convert_abs_to_monitor((485, 350))
                            self._char.move(pos_m, force_tp=True)
                            self._char.move(pos_m, force_tp=True)                            
                            if template_match.valid:
                                pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                                keyboard.send("tab")
                                continue
        
        # OK, we found our location, lets just accesss the portal   
        if roomfound == True:                        
            Logger.debug("I found the Portal to Old Tristram on the Minimap, switching Minimap off")
            keyboard.send("tab") 

            Logger.debug("Ok, let's enter the Portal to Old Tristram") 
            found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
            if not self._char.select_by_template(["COW_STONY_FIELD_PORTAL_1"], found_loading_screen_func, threshold=0.5, time_out=4):
                # do a random tele jump and try again
                # move the mouse to center of the screen
                pos_m = self._screen.convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
                x_rand = random.uniform(-300, 300)
                y_rand = random.uniform(-150, 150)
                pos_m = self._screen.convert_abs_to_monitor((x_rand, y_rand))
                self._char.move(pos_m, force_move=True)
                if not self._char.select_by_template(["COW_STONY_FIELD_PORTAL_1"], found_loading_screen_func, threshold=0.3, time_out=4):
                    return False
            # Wait until templates in Old Tristram entrance are found
            if not self._template_finder.search_and_wait(["COW_TRIST_0", "COW_TRIST_2", "COW_TRIST_3", "COW_TRIST_4"], threshold=0.65, time_out=20).valid:
                 return False


    def _tristram(self, do_pre_buff: bool) -> bool:
        if do_pre_buff: self._char.pre_buff()   
        logger.info("Entering Old Tristram to get the leg")
        logger.info("Calibrating at Entrance TP")
        if not self._pather.traverse_nodes([1000], self._char, time_out=5): return False
        logger.info("Static Path to Corpse")
        self._pather.traverse_nodes_fixed("cow_trist_tp_leg", self._char)
        logger.info("Calibrating at Corpse")
        if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
        logger.info("Looting the leg the Corpse")
        self._legdance(["COW_WIRT_OPEN.PNG"],["COW_WIRT_CLOSED.PNG"],"Old-Tristram", [1001])
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