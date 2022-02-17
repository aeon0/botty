from asyncio.log import logger
import cv2
import time
import random
import keyboard
import math
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


    #thus function randomly teleports around until we either get stuck or find the exit we search for
    def _scout(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)-> bool:
        found = False
        templates_scout = ["COW_STONY_FIELD_YELLOW"]
        templates_avoid = ["COW_COLD_PLAINS", "COW_COLD_PLAINS_TRANSPARENT"]
        Logger.debug('\033[93m' + "Scout: Starting to explore map" + '\033[0m')
        if not self._template_finder.search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
            keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
            keyboard.send(self._config.char["minimap"]) #turn on minimap
            Logger.debug('\033[93m' + "Scout: Opening Minimap" + '\033[0m')

        avoid = self._template_finder.search_and_wait(templates_avoid, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False).valid

        while not found and not avoid:
                found = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False).valid
                avoid = self._template_finder.search_and_wait(templates_avoid, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False).valid
                founder = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False)
                
                if avoid:
                    Logger.debug('\033[93m' + "Scout: Ended up in Cold Plains, stopping to move" + '\033[0m')
                    return False

                if founder.valid:
                    pos_m = self._screen.convert_screen_to_monitor(founder.center)
                    Logger.debug('\033[93m' + "Scout: target template is at position:" + str(pos_m) + '\033[0m')
                    break
                
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m)))
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                Logger.debug("Scout: " + str(score) + ": is our current score")
                self._char.move(pos_m, force_tp=True, force_move=True)
                if score < .10:
                    stuck_count += 1
                    Logger.debug('\033[93m' + "Scout: We did not move, stuck count now: " + str(stuck_count) + '\033[0m')               
                    if stuck_count >=2:
                        """
                        super_stuck += 1
                        Logger.debug('\033[93m' + "Scout: We still did not move, stuck count now: " + str(stuck_count) + ", super_stuck count now: " + str(super_stuck) + ", calling stuck()" + '\033[0m')               
                        self.stuck(corner_picker, x2_m, y2_m, stuck_count, super_stuck)                         
                        if super_stuck >= 2:
                        """
                        Logger.debug('\033[93m' + "Scout: We seem super stuck, super_stuck count now: " + str(super_stuck) + ", calling super_stuck() to change direction" + '\033[0m')
                        self.super_stuck(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) 
        if found == True:
            Logger.debug('\033[93m' + "Scout: Found our Template, trying to click the exit template, calling exitclicker()" + '\033[0m')
            self._exitclicker(pos_m)


    # this function is called when we are stuck and teleports backwards to get us unstuck
    def stuck(self, corner_picker, x2_m, y2_m, stuck_count, super_stuck)-> bool:
        tele_math = random.randint(1, 3)
        if math.fmod(tele_math, 3) == 0:
            Logger.debug('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck (telemath: "+ str(tele_math) +"), let's go reverse 2 x 3, first x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            Logger.debug('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3, second x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            stuck_count += 1
            super_stuck += 3 #was 1, i want her to change corners earlier
            Logger.debug('\033[94m' + "Stuck: " + str(corner_picker) + ": stuck_count: "+str(stuck_count)+", super_stuck count: "+str(super_stuck)+ '\033[0m')
        else:
            Logger.debug('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck (telemath: "+ str(tele_math) +"), let's go reverse 2 x 3, first x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            Logger.debug('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3, second x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            stuck_count = 0
            super_stuck += 3 #was 1, i want her to change corners earlier 
            Logger.debug('\033[94m' + "Stuck: " + str(corner_picker) + ": stuck_count: "+str(stuck_count)+", super_stuck count: "+str(super_stuck)+ '\033[0m')
        

    # this function is called when we cannot unstuck ourselves using stuck() and need to change directions
    def super_stuck(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)-> bool:
        Logger.debug('\033[95m' + "Super_Stuck: Got super stuck in corner " + str(corner_picker) + '\033[0m')
        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)

    #this function decides which corner to explore & hands over the x,y coordinate ranges
    def _corner_roller(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber)-> bool:
            keepernumber = random.randint(1, 4)
            if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                keepernumber = random.randint(1, 4) 
                super_stuck = 0
                stuck_count = 0
            else:
                corner_exclude = corner_picker
                corner_picker = keepernumber
                super_stuck = 0
                stuck_count = 0
                if corner_picker == 1:
                    Logger.debug('\033[92m' + "Cornerpicker: Picked Corner 1 = top-left" + '\033[0m')
                    #x1_m = -250
                    #x2_m = -600
                    #y1_m = -200
                    #y2_m = -345
                    self._scout(1, -250, -600, -200, -300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) #top - left
                elif corner_picker == 2:
                    Logger.debug('\033[92m' + "Cornerpicker: Picked Corner 2 = top-right" + '\033[0m')
                    self._scout(2, 250, 600, -200, -300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # top - right
                elif corner_picker == 3:
                    Logger.debug('\033[92m' + "Cornerpicker: Picked Corner 3 = bottom-right" + '\033[0m')
                    self._scout(3, 485, 600, 200, 300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - right
                elif corner_picker == 4:
                    Logger.debug('\033[92m' + "Cornerpicker: Picked Corner 4 = bottom-left" + '\033[0m')
                    self._scout(4, -485, -600, 200, 300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - left
            #return corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber

   
    # This function makes us click on the purple exit tile to enter the next level
    def _exitclicker(self, pos_m)-> bool:
            Logger.debug('\033[92m' + "Exit_Clicker: Trying to approach the Exit" + '\033[0m')
            closetoexit = False
            stuck_count = 0
            super_stuck = 0
            templates_scout = ["COW_STONY_FIELD_YELLOW"]
            templates_mapcheck = ["MAP_CHECK"]
            templates_exit = ["COW_STONY_FIELD_PORTAL_1", "COW_STONY_FIELD_PORTAL_0", "COW_STONY_FIELD_PORTAL_2"]
            templates_nextlevel = ["COW_TRIST_0", "COW_TRIST_2", "COW_TRIST_3"]
            mapcheck = self._template_finder.search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False)
            template_match = self._template_finder.search_and_wait(templates_exit, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False)
            if template_match.valid and mapcheck.valid:
                pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                if self._template_finder.search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
                    Logger.debug('\033[92m' + "Exit_Clicker: Template Found, Minimap off" + '\033[0m')
                    keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                    keyboard.send(self._config.char["minimap"]) #turn on minimap
            
            while not closetoexit:    
                closetoexit = self._template_finder.search_and_wait(templates_exit, best_match=True, threshold=0.7,  time_out=0.1, use_grayscale=False).valid
                template_match = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False)
                if closetoexit == True or template_match == True:
                    if self._template_finder.search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
                        keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                        keyboard.send(self._config.char["minimap"]) #turn on minimap
                        Logger.debug('\033[92m' + "Exit_Clicker: Template Found, Minimap off" + '\033[0m')
                        if self._template_finder.search_and_wait(templates_exit, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False) == True:
                            pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                            pos_m2 = (template_match.center)#SCREEN                    
                t0 = self._screen.grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = self._screen.grab()
                # check difference between the two frames to determine if tele was good or not
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0)
                super_stuck = 0
                self._char.move(pos_m, force_tp=True, force_move=True)
                self._char.move(pos_m, force_tp=True, force_move=True)
                #self._char.move(pos_m, force_tp=True, force_move=True)              
                if score < .15 and not closetoexit:
                    stuck_count += 1
                    if stuck_count >= 2 and super_stuck < 2 and not closetoexit:
                        super_stuck += 1
                        self.exit_stuck(pos_m, stuck_count, super_stuck, closetoexit) 
                    elif super_stuck >= 3 and not closetoexit:
                        Logger.debug('\033[92m' + "Exit_Clicker: Super Stuck, super_stuck count: " + str(super_stuck) + '\033[0m')
                        self.exit_super_stuck(pos_m, stuck_count, super_stuck, closetoexit)
            Logger.debug('\033[93m' + "Exit_Clicker: Found Exit" + '\033[0m')
            found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
            if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                # do a random tele jump and try again
                Logger.debug('\033[93m' + "Exit_Clicker: Found Exit, but didnt click it" + '\033[0m')
                pos_m = self._screen.convert_abs_to_monitor((315, -150))
                self._char.move(pos_m, force_move=True)
                if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                    self._char.move(pos_m, force_move=True)
                    if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                        pos_m = self._screen.convert_abs_to_monitor((-315, -100))
                        self._char.move(pos_m, force_move=True)
                        Logger.debug('\033[92m' + "Exit_Clicker: Found Exit, but cannot click it" + '\033[0m')
                        if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4,telekinesis=True):
                            Logger.debug('\033[92m' + "Exit_Clicker: Found Exit, but didnt click it repeatedly, aborting run" + '\033[0m')
                            return False
            if not self._template_finder.search_and_wait(templates_nextlevel, threshold=0.8, time_out=.5).valid:
                if not self._template_finder.search_and_wait(templates_nextlevel, threshold=0.8, time_out=1).valid:
                    self._scout(4, -250, -400, 200, 300, 0, 0, 4, 2, 2, 4) # bottom - left
            else:
                keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                keyboard.send(self._config.char["minimap"]) #turn on minimap
            return True
            self._tristram()

    
    #this function helps us to unstuck ourselves, when we already found our exit tile, but got stuck entering the exit.
    def exit_stuck(self, pos_m, stuck_count, super_stuck, closetoexit)-> bool:
        x, y = pos_m
        pos_m2 = x, y
        coordlog = x, y
        Logger.debug(coordlog)
        x, y = self._screen.convert_monitor_to_screen(pos_m2)
        pos_m2 = x, y
        x, y = self._screen.convert_screen_to_abs(pos_m2)                        
        pos_m2 = x, y
        coordlog = x, y
        Logger.debug(coordlog)
        # x, y = self._screen.convert_abs_to_monitor((pos_m2))
        #########################
        if x < 0 and y < 0 and not closetoexit: # -, - Corner 1 Top Left
            Logger.debug('\033[91m' + "Exit_stuck: corner one stuck" + '\033[0m')
            t0 = self._screen.grab()                      
            pos_m2 = self._screen.convert_abs_to_monitor((-600, -300))
            self._char.move(pos_m2, force_move=True)
            t1 = self._screen.grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = self._screen.convert_abs_to_monitor((600, -300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y < 0 and not closetoexit: #corner 2
            Logger.debug('\033[91m' + "Exit_stuck: corner two stuck" + '\033[0m')
            t0 = self._screen.grab()                      
            pos_m2 = self._screen.convert_abs_to_monitor((600, -300))
            self._char.move(pos_m2, force_move=True)
            t1 = self._screen.grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = self._screen.convert_abs_to_monitor((600, 300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y > 0 and not closetoexit: #corner 3
            Logger.debug('\033[91m' + "Exit_stuck: corner three stuck" + '\033[0m')
            t0 = self._screen.grab()                      
            pos_m2 = self._screen.convert_abs_to_monitor((600, 300))
            self._char.move(pos_m2, force_move=True)
            t1 = self._screen.grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = self._screen.convert_abs_to_monitor((-600, 300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x < 0 and y > 0 and not closetoexit: #corner 4
            Logger.debug('\033[91m' + "Exit_stuck: corner four stuck" + '\033[0m')
            t0 = self._screen.grab()                      
            pos_m2 = self._screen.convert_abs_to_monitor((-600, 350))
            self._char.move(pos_m2, force_move=True)
            t1 = self._screen.grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = self._screen.convert_abs_to_monitor((-600, 300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0


     #this function is called when we get stuck whilst clicking the exit after our template was found
    def exit_super_stuck(self, pos_m, stuck_count, super_stuck, closetoexit)-> bool:
        x, y = pos_m
        pos_m2 = x, y
        coordlog = x, y
        Logger.debug(coordlog)
        x, y = self._screen.convert_monitor_to_screen(pos_m2)
        pos_m2 = x, y
        x, y = self._screen.convert_screen_to_abs(pos_m2)                        
        pos_m2 = x, y
        coordlog = x, y
        Logger.debug('\033[93m' + "Exit_Super_stuck: " + str(coordlog) + '\033[0m')
        if x < 0 and y < 0: # -, - Corner 1 Top Left
            Logger.debug('\033[93m' + "Exit_Super_stuck: Corner 1 Top Left" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((600, 350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((-20, -300))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y < 0 and not closetoexit: #corner 2
            Logger.debug('\033[93m' + "Exit_Super_stuck: Corner 2 Top Right" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((-600, 350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((20, -300))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y > 0 and not closetoexit: #corner 3
            Logger.debug('\033[93m' + "Exit_Super_stuck: Corner 3 Bottom Right" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((-600, -350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((-35, 250))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x < 0 and y > 0 and not closetoexit: #corner 4
            Logger.debug('\033[93m' + "Exit_Super_stuck: Corner 4 Bottom Left" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((600, -350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((-35, 250))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
        if template_match.valid: 
            template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
            pos_m = self._screen.convert_screen_to_monitor(template_match.center)
            if self._template_finder.search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.7, time_out=0.1, use_grayscale=False).valid:
                keyboard.send(self._char._skill_hotkeys["teleport"])
                keyboard.send(self._config.char["minimap"])
                Logger.debug('\033[93m' + "Exit_Super_Stuck: Found the template again, trying to click the exit with Minimap Off" + '\033[0m')
            stuck_count = 0
            super_stuck = 0
        elif template_match == False:
            Logger.debug('\033[93m' + "Exit_Super_Stuck: No match no Position" + '\033[0m')                                      
            stuck_count = 0
            super_stuck = 0


    #this function checks for the leg in inventory, stash & cube.
    def _legcheck(self) -> bool:
        Logger.debug('\033[96m' + "Checking Inventory for Leg" + '\033[0m')  
        keyboard.send(self._config.char["inventory_screen"])
        template_match = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
        keyboard.send(self._config.char["inventory_screen"])
        if template_match.valid: 
            template_match = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
            Logger.debug('\033[96m' + "Checking Inventory for Leg: found, calling open_cow_portal()" + '\033[0m')
            self._open_cow_portal()
        else:
            Logger.debug('\033[96m' + "Checking Inventory for Leg: not found" + '\033[0m')
            Logger.debug('\033[96m' + "Checking Stash for Leg" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((160, 45))
            mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
            mouse.click(button="right")
            template_match = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
            if template_match.valid: 
                template_match = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
                Logger.debug('\033[96m' + "Checking Stash for Leg: found, calling open_cow_portal()" + '\033[0m')
                self._open_cow_portal()
            else:
                Logger.debug('\033[96m' + "Checking Stash for Leg: not found" + '\033[0m')
                Logger.debug('\033[96m' + "Checking Cube for Leg" + '\033[0m')
                template_match = self._template_finder.search_and_wait(["HORADRIC_CUBE"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
                #pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                pos_m = template_match.center
                mouse.move(pos_m)
                wait(0.1, 0.15)
                mouse.click(button="right")
                template_match = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
                if template_match.valid: 
                    template_match = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False)
                    Logger.debug('\033[96m' + "Checking Cube for Leg: found, calling open_cow_portal()" + '\033[0m')
                    self._open_cow_portal()
                else:
                    Logger.debug('\033[96m' + "Checking Cube for Leg: not found, need to get it in stony field" + '\033[0m')
                    


        #open inventory, search for leg
            #open stash, search for leg
                #open cube, search for leg
        return True

    
    #this function gets the leg in tristram
    def _tristram(self) -> bool:
        logger.info('\033[93m' + "Entering Old Tristram to get the leg" + '\033[0m')
        logger.info('\033[93m' + "Calibrating at Entrance TP" + '\033[0m')
        if not self._pather.traverse_nodes([1000], self._char, time_out=5): return False
        logger.info('\033[93m' + "Static Path to Corpse" + '\033[0m')
        self._pather.traverse_nodes_fixed("cow_trist_tp_leg", self._char)
        logger.info('\033[93m' + "Calibrating at Corpse" + '\033[0m')
        if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
        logger.info('\033[93m' + "Looting the leg the Corpse" + '\033[0m')
        if not self._char.select_by_template(["COW_WIRT_CLOSED"], threshold=0.63, time_out=4,telekinesis=True):
            # do a random tele jump and try again
            pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            #and recalibrate at wirt
            if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
            if not self._char.select_by_template(["COW_WIRT_CLOSED"], threshold=0.63, time_out=4, telekinesis=True):
                return False
        #self._legdance(["COW_WIRT_OPEN.PNG"],["COW_WIRT_CLOSED"],"Old-Tristram", [1001])
        logger.info('\033[93m' + "Grabbing the leg" + '\033[0m')
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        logger.info('\033[93m' + "Making TP to go home" + '\033[0m')
        if not self._ui_manager.has_tps():
            Logger.warning('\033[93m' + "Cows: Open TP failed. Aborting run." + '\033[0m')
            self.used_tps += 20
            return False
        mouse.click(button="right")
        self.used_tps += 1
        #return True
        #enter portal
        if not self._char.select_by_template(["BLUE_PORTAL"], threshold=0.7, time_out=4,telekinesis=True):
            # do a random tele jump and try again
            pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            if not self._char.select_by_template(["BLUE_PORTAL"], threshold=0.7, time_out=4,telekinesis=True): return False
        #return True
        

    
    #this function opens the cow portal
    def _open_cow_portal(self)-> bool:
        #go to akara, buy a tome
        #go to stash & cube leg & top
        #enter portal
        self._cows()
        #return True


    # this function kills cows
    def _cows(self) -> bool:
        #train neuronal network to search for heads and feet of cows that are not dead as positive
        #train it with images from dead cows and from empty cow levels as negative
        #search for template head or feet, cast attack rotation & pickit, repeat until?
        return True

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Secret Cow Level")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Cows requires teleport")
        #CHECK IF THE LEG IS ALREADY IN THE STASH OR INVENTORY!
            #if yes: open_cows()
            #if no: stony_field()
        logger.info("Legcheck")
        #self._legcheck()
        logger.info("Opening WP & moving to Stony Field")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(1, 2)
        return Location.A1_STONY_FIELD_WP
        

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if do_pre_buff: self._char.pre_buff()   
        self._picked_up_items = False
        self.used_tps = 0
        stuck_count = 0
        keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
        self._scout(1, -50, 50, -150, -250, stuck_count, 0, 4, 2, 2, 0) #tries to get to exit   
        #pre, during_1, during_2, diffed = self._map_capture()
        #self.map_diff(pre, during_1, during_2)
        if not self._tristram(): return False
        if not self._open_cow_portal(): return False
        """
        if not self._stony_field(): return False
        if not self._tristram(): return False
        if not self._cows(): return False
        """
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