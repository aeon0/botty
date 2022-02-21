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
from town import TownManager, A1, A2, A3, A4, A5 #for buying tomes & interacting with Stash
from npc_manager import NpcManager, Npc #for buying tomes
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
        pickit: PickIt,
        npc_manager: NpcManager,


    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._npc_manager = npc_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0



    #this function randomly teleports around until we either get stuck or find the exit we search for
    def _scout(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)-> bool:
        
        templates_scout = ["COW_STONY_FIELD_YELLOW"] #the template we scout for on the minimap, either an exit (purple) or portal (yellow)
        templates_avoid = ["COW_COLD_PLAINS0"] #in case our scout can bring us to other locations, we add the "Entering ..." message here, so we know when we accidently leave the area
        avoid = self._template_finder.search_and_wait(templates_avoid, best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False).valid # boolean of avoid template

        #lets make sure our minimap is on
        Logger.info('\033[93m' + "Scout: Starting to explore map" + '\033[0m')
        if not self._template_finder.search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False, take_ss=False).valid: #check if the minimap is already on
            keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
            keyboard.send(self._config.char["minimap"]) #turn on minimap
            Logger.info('\033[93m' + "Scout: Opening Minimap" + '\033[0m')

        found = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False).valid
        #so lets loop teleporting around until we find our templates
        while not found and not avoid:
                found = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False).valid #boolean, if we found it
                founder = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False) #template
                avoid = self._template_finder.search_and_wait(templates_avoid, best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False, take_ss=False).valid #have to repeat it from above, so its defined in the loop

                #we check if we exited our scouting location and take measures if this is the case
                if avoid:
                    Logger.info('\033[93m' + "Scout: Ended up in Cold Plains, stopping to move" + '\033[0m')
                    #we might have to teleport backwards 3 times & change corners.
                    return False

                # we break the loop if the template is found & return its x, y position to pos_m
                if founder.valid:
                    pos_m = self._screen.convert_screen_to_monitor(founder.center)
                    Logger.info('\033[93m' + "Scout: target template is at position:" + str(pos_m) + '\033[0m')
                    break
              
                #teleporting part
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m))) # randomize our position
                t0 = self._screen.grab() # take screenshot before teleport
                self._char.move(pos_m, force_tp=True, force_move=True) # first of two teleports to randomized position
                t1 = self._screen.grab() # take screenshot after teleport

                # check by making a diff of the screenshots, if we moved between the teleports
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0) #score to check how much difference there is between screenshots (high = movement, low = stuck)
                Logger.debug("Scout: " + str(score) + ": is our current score")
                pos_m = self._screen.convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m))) # randomize our position
                self._char.move(pos_m, force_tp=True, force_move=True) # second of two teleports to randomized position
                
                #if we didnt move, we need to unstuck ourselves
                if score < .10:
                    #lets change scouting direction:
                    Logger.info('\033[93m' + "Scout: score was too low, we seem stuck, changing direction from corner: " + str(corner_picker) + '\033[0m')
                    self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    """
                    stuck_count += 1
                    Logger.info('\033[93m' + "Scout: We did not move, stuck count now: " + str(stuck_count) + '\033[0m')               
                    #we are still stuck, so lets call the stuck() function to go reverse & free ourselves
                    if stuck_count >=2:
                        super_stuck += 1
                        Logger.info('\033[93m' + "Scout: We still did not move, stuck count now: " + str(stuck_count) + ", super_stuck count now: " + str(super_stuck) + ", calling stuck()" + '\033[0m')               
                        self.stuck(corner_picker, x2_m, y2_m, stuck_count, super_stuck)                         
                        
                        #we were not able to unstuck oursevles using the stuck() function, we thus switch the direction (corner) in which we teleport.
                        if super_stuck >= 2:
                        Logger.info('\033[93m' + "Scout: We seem super stuck, super_stuck count now: " + str(super_stuck) + ", calling super_stuck() to change direction" + '\033[0m')
                        self.super_stuck(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) 
                    """
        
        #we found our template and should leave the scout() function.
        if found == True:
            Logger.info('\033[93m' + "Scout: Found our Template, trying to click the exit template, calling exitclicker()" + '\033[0m')
            self._exitclicker(pos_m)
            return True


    # this function is called when we are stuck and teleports backwards to get us unstuck
    def stuck(self, corner_picker, x2_m, y2_m, stuck_count, super_stuck)-> bool:
        tele_math = random.randint(1, 3) #lets roll a 3-sided dice to decide in which direction we should go now.
        if math.fmod(tele_math, 3) == 0:
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck (telemath: "+ str(tele_math) +"), let's go reverse 2 x 3, first x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            # we go opposite of our last direction
            pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            # and now we change direction along Y
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3, second x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            stuck_count += 1
            super_stuck += 1
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": stuck_count: "+str(stuck_count)+", super_stuck count: "+str(super_stuck)+ '\033[0m')
        else:
            # we go opposite of our last direction
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck (telemath: "+ str(tele_math) +"), let's go reverse 2 x 3, first x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m * -1, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            # and now we change direction along X
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3, second x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = self._screen.convert_abs_to_monitor((x2_m, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            stuck_count = 0
            super_stuck += 1
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": stuck_count: "+str(stuck_count)+", super_stuck count: "+str(super_stuck)+ '\033[0m')
        

    # this function is called when we cannot unstuck ourselves using stuck() and need to change directions
    def super_stuck(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)-> bool:
        Logger.info('\033[95m' + "Super_Stuck: Got super stuck in corner " + str(corner_picker) + '\033[0m')
        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)

    #this function decides which corner to explore & hands over the x,y coordinate ranges
    def _corner_roller(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)-> bool:
            keepernumber = random.randint(1, 8)
            if keepernumber == corner_exclude or keepernumber == corner_picker or keepernumber == exclude1 or keepernumber == exclude2:
                keepernumber = random.randint(1, 8) 
                super_stuck = 0
                stuck_count = 0
            else:
                corner_exclude = corner_picker
                corner_picker = keepernumber
                super_stuck = 0
                stuck_count = 0
                if corner_picker == 1:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 1 = left" + '\033[0m')
                    #self._scout(1, -250, -600, -200, -300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) #top - left
                    #self._scout(1, 225, -325, 125, -225, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # random with tendency top - left
                    self._scout(1, -250, -525, 0, -0, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # left
                elif corner_picker == 2:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 2 = right" + '\033[0m')
                    #self._scout(2, 250, 600, -200, -300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # top - right
                    self._scout(2, 525, 250, 0, -0, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # right
                elif corner_picker == 3:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 3 = top " + '\033[0m')
                    #self._scout(3, 485, 600, 200, 300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - right
                    self._scout(3, 0, -0, -250, -325, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # top
                elif corner_picker == 4:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 4 = bottom" + '\033[0m')
                    #self._scout(4, -485, -600, 200, 300, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber) # bottom - left
                    self._scout(4, 0, -0, 225, 150, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottom
                """
                elif corner_picker == 5:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 5 = top right" + '\033[0m')
                    y1_m == -300
                    y2_m == -150
                    x1_m == y1_m * -1,7
                    x2_m == y2_m * -1,7
                    self._scout(5, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # topright
                elif corner_picker == 6:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 6 = top left " + '\033[0m')
                    y1_m == -300
                    y2_m == -150
                    x1_m == y1_m * 1,7
                    x2_m == y2_m * 1,7
                    self._scout(6, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # topleft
                elif corner_picker == 7:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 7 = bottom right" + '\033[0m')
                    y1_m == 300
                    y2_m == 150
                    x1_m == y1_m * 1,7
                    x2_m == y2_m * 1,7
                    self._scout(7, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottomright
                elif corner_picker == 8:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 8 = bottom left" + '\033[0m')
                    y1_m == 300
                    y2_m == 150
                    x1_m == y1_m * -1,7
                    x2_m == y2_m * -1,7
                    self._scout(8, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottomleft
                """

            #return corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber

   
    # This function makes us click on the purple exit tile to enter the next level
    def _exitclicker(self, pos_m)-> bool:
            Logger.info('\033[92m' + "Exit_Clicker: Step1: Trying to approach the Exit" + '\033[0m')
            closetoexit = False
            stuck_count = 0
            super_stuck = 0
            templates_scout = ["COW_STONY_FIELD_YELLOW"]
            templates_mapcheck = ["MAP_CHECK"]
            templates_exit = ["COW_STONY_FIELD_PORTAL_1", "COW_STONY_FIELD_PORTAL_0", "COW_STONY_FIELD_PORTAL_2"]
            templates_nextlevel = ["COW_TRIST_0", "COW_TRIST_2", "COW_TRIST_3", "COW_TRIST_4"]
            mapcheck = self._template_finder.search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False, take_ss=False)
            template_match = self._template_finder.search_and_wait(templates_exit, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False, take_ss=False)
            if template_match.valid and mapcheck.valid:
                pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                if self._template_finder.search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
                    Logger.info('\033[92m' + "Exit_Clicker: Step2: Minimap Scout Template Found, Minimap off" + '\033[0m')
                    keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                    keyboard.send(self._config.char["minimap"]) #turn on minimap
            
            while not closetoexit:    
                closetoexit = self._template_finder.search_and_wait(templates_exit, best_match=True, threshold=0.7,  time_out=0.1, use_grayscale=False).valid
                template_match = self._template_finder.search_and_wait(templates_scout, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False)
                if closetoexit == True or template_match == True:
                    if self._template_finder.search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
                        keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                        keyboard.send(self._config.char["minimap"]) #turn on minimap
                        Logger.info('\033[92m' + "Exit_Clicker: Step3a: Minimap off to identify Exit Templates" + '\033[0m')
                        if self._template_finder.search_and_wait(templates_exit, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False) == True:
                            pos_m = self._screen.convert_screen_to_monitor(template_match.center)
                            pos_m = template_match.center                   
                            Logger.info('\033[92m' + "Exit_Clicker: Step3b (in while): Found Exit Template, clicking on it" + '\033[0m')
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
                        Logger.info('\033[92m' + "Exit_Clicker: Super Stuck, super_stuck count: " + str(super_stuck) + '\033[0m')
                        self.exit_super_stuck(pos_m, stuck_count, super_stuck, closetoexit)
            
            Logger.info('\033[92m' + "Exit_Clicker: Step4a: Found Exit Template, clicking on it" + '\033[0m')
            found_loading_screen_func = lambda: self._ui_manager.wait_for_loading_screen(2.0)
            if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                # do a random tele jump and try again
                Logger.info('\033[92m' + "Exit_Clicker: Step4b: Found Exit, but didn't manage to click it, moving left and right and top" + '\033[0m')
                pos_m = self._screen.convert_abs_to_monitor((315, -150))
                self._char.move(pos_m, force_move=True)
                if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                    self._char.move(pos_m, force_move=True)
                    if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                        pos_m = self._screen.convert_abs_to_monitor((-315, -100))
                        self._char.move(pos_m, force_move=True)
                        Logger.info('\033[92m' + "Exit_Clicker: Step4c: Found Exit, but cannot click it, retry" + '\033[0m')
                        if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4,telekinesis=True):
                            Logger.info('\033[92m' + "Exit_Clicker: Step4d: Found Exit, but didn't manage to click it repeatedly, aborting run" + '\033[0m')
                            return False

            if not self._template_finder.search_and_wait(templates_nextlevel, threshold=0.8, time_out=.5, take_ss=False).valid:
                if not self._template_finder.search_and_wait(templates_nextlevel, threshold=0.8, time_out=1, take_ss=False).valid:
                    Logger.info('\033[92m' + "Exit_Clicker: Step5: CANNOT confirm to be at the right new location, starting again to scout()" + '\033[0m')
                    self._scout(4, -250, -400, 200, 300, 0, 0, 4, 2, 2, 4, False) # bottom - left
            else:
                Logger.info('\033[92m' + "Exit_Clicker: Step5: Confirmed to be at the right new location, switching off minimap, stopping to scout()" + '\033[0m')
                wait(2)
                keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                keyboard.send(self._config.char["minimap"]) #turn on minimap
            return True
            #self._tristram()

    
    #this function helps us to unstuck ourselves, when we already found our exit tile, but got stuck entering the exit.
    def exit_stuck(self, pos_m, stuck_count, super_stuck, closetoexit)-> bool:
        x, y = pos_m
        pos_m2 = x, y
        coordlog = x, y
        Logger.info(coordlog)
        x, y = self._screen.convert_monitor_to_screen(pos_m2)
        pos_m2 = x, y
        x, y = self._screen.convert_screen_to_abs(pos_m2)                        
        pos_m2 = x, y
        coordlog = x, y
        Logger.info(coordlog)
        # x, y = self._screen.convert_abs_to_monitor((pos_m2))
        #########################
        if x < 0 and y < 0 and not closetoexit: # -, - Corner 1 Top Left
            Logger.info('\033[91m' + "Exit_stuck: corner one stuck" + '\033[0m')
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
            Logger.info('\033[91m' + "Exit_stuck: corner two stuck" + '\033[0m')
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
            Logger.info('\033[91m' + "Exit_stuck: corner three stuck" + '\033[0m')
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
            Logger.info('\033[91m' + "Exit_stuck: corner four stuck" + '\033[0m')
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
        Logger.info(coordlog)
        x, y = self._screen.convert_monitor_to_screen(pos_m2)
        pos_m2 = x, y
        x, y = self._screen.convert_screen_to_abs(pos_m2)                        
        pos_m2 = x, y
        coordlog = x, y
        Logger.info('\033[93m' + "Exit_Super_stuck: " + str(coordlog) + '\033[0m')
        if x < 0 and y < 0: # -, - Corner 1 Top Left
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 1 Top Left" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((600, 350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((-20, -300))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y < 0 and not closetoexit: #corner 2
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 2 Top Right" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((-600, 350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((20, -300))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y > 0 and not closetoexit: #corner 3
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 3 Bottom Right" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((-600, -350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((-35, 250))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x < 0 and y > 0 and not closetoexit: #corner 4
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 4 Bottom Left" + '\033[0m')
            pos_m2 = self._screen.convert_abs_to_monitor((600, -350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = self._screen.convert_abs_to_monitor((-35, 250))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False)
        if template_match.valid: 
            template_match = self._template_finder.search_and_wait(["COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False)
            pos_m = self._screen.convert_screen_to_monitor(template_match.center)
            if self._template_finder.search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.7, time_out=0.1, use_grayscale=False, take_ss=False).valid:
                keyboard.send(self._char._skill_hotkeys["teleport"])
                keyboard.send(self._config.char["minimap"])
                Logger.info('\033[93m' + "Exit_Super_Stuck: Found the template again, trying to click the exit with Minimap Off" + '\033[0m')
            stuck_count = 0
            super_stuck = 0
        elif template_match == False:
            Logger.info('\033[93m' + "Exit_Super_Stuck: No match no Position" + '\033[0m')                                      
            stuck_count = 0
            super_stuck = 0

       
    #this function gets the leg in tristram
    def _tristram(self) -> bool:
        #lets make sure our minimap is OFF
        if self._template_finder.search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False, take_ss=False).valid: #check if the minimap is already on
            keyboard.send(self._config.char["minimap"]) #turn off minimap
            Logger.info('\033[95m' + "Old Tristram: Closing Minimap" + '\033[0m')
        
        #Calibrate at WP
        logger.info('\033[95m' + "Old Tristram: Entering Old Tristram to get the leg" + '\033[0m')
        logger.info('\033[95m' + "Old Tristram: Calibrating at Entrance TP" + '\033[0m')
        if not self._pather.traverse_nodes([1000], self._char, time_out=5): return False
        
        #Static path to Wirt
        logger.info('\033[95m' + "Old Tristram: Static Path to Corpse" + '\033[0m')
        self._pather.traverse_nodes_fixed("cow_trist_tp_leg", self._char)
        
        #Calibrate at Wirt
        logger.info('\033[95m' + "Old Tristram: Calibrating at Corpse" + '\033[0m')
        if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
        
        #Loot Wirt
        logger.info('\033[95m' + "Old Tristram: Looting the leg the Corpse" + '\033[0m')
        if not self._char.select_by_template(["COW_WIRT_CLOSED"], threshold=0.63, time_out=4,telekinesis=True):
            # do a random tele jump and try again
            pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            #and recalibrate at wirt
            if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
            if not self._char.select_by_template(["COW_WIRT_CLOSED"], threshold=0.63, time_out=4, telekinesis=True):
                logger.info('\033[95m' + "Old Tristram: Unable to interact with the wirt" + '\033[0m')
                return False

        #Loot Leg
        logger.info('\033[95m' + "Old Tristram: Grabbing the leg" + '\033[0m')
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        
        #TP Home
        logger.info('\033[95m' + "Old Tristram: Making TP to go home" + '\033[0m')
        if not self._ui_manager.has_tps():
            Logger.warning('\033[95m' + "Old Tristram: Open TP failed. Aborting run." + '\033[0m')
            self.used_tps += 20
            return False
        mouse.click(button="right")
        self.used_tps += 1
        if not self._char.select_by_template(["BLUE_PORTAL"], threshold=0.7, time_out=4,telekinesis=True):
            # do a random tele jump and try again
            pos_m = self._screen.convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            if not self._char.select_by_template(["BLUE_PORTAL"], threshold=0.7, time_out=4,telekinesis=True): Logger.info('\033[93m' + "Tristram: didnt make it through Portal :/" + '\033[0m')
            wait(1)
        return True


    #stolen from Transmute.py
    def open_cube(self):
        self._ui_manager._move_to_stash_tab(0)
        screen = self._screen.grab()
        match = self._template_finder.search(
            ["HORADRIC_CUBE"], screen, threshold=0.9, roi=Config.ui_roi["left_inventory"])
        if match.valid:
            x, y = self._screen.convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            wait(0.2)
            mouse.click("right")
            wait(0.2)
        else:
            Logger.error(f"Can't find cube: {match.score}")


    #stolen from Transmute.py
    def transmute(self):
        screen = self._screen.grab()
        match = self._template_finder.search(
            ["CUBE_TRANSMUTE_BTN"], screen, roi=Config.ui_roi["cube_btn_roi"])
        if match.valid:
            x, y = self._screen.convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            wait(0.2)
            mouse.click("left")
            wait(0.2)


    #stolen from Transmute.py
    def close_cube(self):
        wait(0.2)
        keyboard.send("esc")
    

    #this function checks for the leg in inventory, stash & cube.
    def _legcheck(self) -> bool:
        
        #open inventory, search for leg
        Logger.info('\033[96m' + "Legcheck: Checking Inventory for Leg" + '\033[0m')  
        keyboard.send(self._config.char["inventory_screen"])
        legfound = self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False).valid
        #wait(2)
        keyboard.send(self._config.char["inventory_screen"])
        
        #we found the leg
        if legfound: 
            Logger.info('\033[96m' + "Checking Inventory for Leg: found, calling open_cow_portal()" + '\033[0m')
            return True
        
        #open stash, search for leg
        else:
            Logger.info('\033[96m' + "Legcheck: Checking Inventory for Leg: not found" + '\033[0m')
            Logger.info('\033[96m' + "Legcheck: Checking Stash for Leg" + '\033[0m')
            self._town_manager.open_stash(Location.A1_TOWN_START)
            #wait(2)
            if self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False).valid: 
                Logger.info('\033[96m' + "Legcheck: Checking Stash for Leg: found, moving it to inventory" + '\033[0m')
                leg = self._template_finder.search_and_wait("LEG_INVENTORY", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True, take_ss=False) 
                if not leg.valid:
                    Logger.info('\033[96m' + "Legcheck: Failed to transfer Leg to Inventory, aborting run)" + '\033[0m')
                    return False
                keyboard.send('ctrl', do_release=False)
                mouse.move(*leg.center, randomize=8, delay_factor=[1.0, 1.5])
                wait(0.1, 0.15)
                mouse.click(button="left")
                wait(0.1, 0.15)
                keyboard.send('ctrl', do_press=False)
                Logger.info('\033[96m' + "Legcheck: Transferred Leg to from Stash Inventory, calling open_cow_portal())" + '\033[0m')
                return True
            
            #open cube, search for leg
            else:
                Logger.info('\033[96m' + "Legcheck: Checking Stash for Leg: not found" + '\033[0m')
                Logger.info('\033[96m' + "Legcheck: Checking Cube for Leg" + '\033[0m')
                #wait(2)
                self.open_cube() #self.transmute.open_cube()
                if self._template_finder.search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False).valid: 
                    Logger.info('\033[96m' + "Legcheck: Checking Cube for Leg: found, moving it to inventory" + '\033[0m')
                    leg = self._template_finder.search_and_wait("LEG_INVENTORY", roi=self._config.ui_roi["cube_area_roi"], time_out=3, normalize_monitor=True, take_ss=False) 
                    if not leg.valid:
                        Logger.info('\033[96m' + "Legcheck: Failed to transfer Leg to Inventory, aborting run)" + '\033[0m')
                        return False
                    keyboard.send('ctrl', do_release=False)
                    mouse.move(*leg.center, randomize=8, delay_factor=[1.0, 1.5])
                    wait(0.1, 0.15)
                    mouse.click(button="left")
                    wait(0.1, 0.15)
                    keyboard.send('ctrl', do_press=False)
                    Logger.info('\033[96m' + "Legcheck: Transferred Leg from Cube to Inventory, calling open_cow_portal())" + '\033[0m')
                    return True
                else:
                    Logger.info('\033[96m' + "Legcheck: Checking Cube for Leg: not found, need to get it in stony field" + '\033[0m')
                    #i assume we leave the cube in the stash
                    return False



    #this function opens the cow portal
    def _open_cow_portal(self)-> bool:
        
        #go to stash, get cube & leg
        
        #go to Akara, get a Tome of TP
        logger.info('\033[91m' + "Open_Cow_Portal: TP to Akara - buy Tome" + '\033[0m')
        #self._pather.traverse_nodes([708, 700,705,706,707], self._char) #Stash to Akara
        self._pather.traverse_nodes([700], self._char) #calibrate at a1_town_start
        if not self._pather.traverse_nodes((Location.A1_TOWN_START, Location.A1_AKARA), self._char, force_move=True): return False #walk to Akara
        self._npc_manager.open_npc_menu(Npc.AKARA)
        self._npc_manager.press_npc_btn(Npc.AKARA, "trade")

        #check if there is a tome for sale & buy it
        tp_tome = self._template_finder.search_and_wait("TP_TOME", roi=self._config.ui_roi["left_inventory"], time_out=3, normalize_monitor=True, take_ss=False) 
        if not tp_tome.valid: return False
        keyboard.send('ctrl', do_release=False)
        mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="right")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        self._ui_manager.close_vendor_screen()

        logger.info('\033[91m' + "Open_Cow_Portal: Akara to Stash - get Cube"+ '\033[0m')
        self._pather.traverse_nodes([707,706,705, 700, 701], self._char) #Akara to Stash
        self._town_manager.open_stash(Location.A1_TOWN_START) # this causes issues: using this function, she stashes the leg & drops the tome :D - At this stage we just want to open the stash and NOT put items into it.

        Logger.info('\033[91m' + "Open_Cow_Portal: Opening Cube"+ '\033[0m')
        self.open_cube()
        tp_tome = self._template_finder.search_and_wait("TP_TOME", roi=self._config.ui_roi["4loot_columns"], time_out=3, normalize_monitor=True, take_ss=False) #we must search for the tome in our loot columns. I run with loot columns=4, so we take an ROI of 4x 40px = 160x160 from the left inventory.
        if not tp_tome.valid:
            Logger.info('\033[91m' + "Open_Cow_Portal: Did not find TOME to transmute, aborting run"+ '\033[0m')
            return False
        keyboard.send('ctrl', do_release=False)
        mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        #we might need to let botty learn where the leg is right now, it needs to be either in the inv & cube. if in inv, we move it to cube. if in stash, it has to go to inv.
        legmove = self._template_finder.search_and_wait("LEG_INVENTORY", roi=self._config.ui_roi["right_inventory"], time_out=3, normalize_monitor=True, take_ss=False)
        if not legmove.valid:
            Logger.info('\033[91m' + "Open_Cow_Portal: Did not find LEG to transmute, aborting run"+ '\033[0m')
            return False
        keyboard.send('ctrl', do_release=False)
        mouse.move(*legmove.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        logger.info('\033[91m' + "Open_Cow_Portal: Transmuting"+ '\033[0m')
        self.transmute()
        self.close_cube()
        return True


    #image manipulation testing for COWS
    def bright_contrast(self, img, brightness=255, contrast=127):
            brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
            contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
            if brightness != 0:
                if brightness > 0:
                    shadow = brightness
                    max = 255
                else:
                    shadow = 0
                    max = 255 + brightness
                al_pha = (max - shadow) / 255
                ga_mma = shadow
                cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma)
            else:
                cal = img

            if contrast != 0:
                alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
                gamma = 127 * (1 - alpha)
                cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)
            return cal
    
    #image manipulation testing for COWS
    def apply_filter(self, img, mask_char:bool=False, erode:int=None, dilate:int=None, blur:int=None, lh:int=None, ls:int=None, lv:int=None, uh:int=None, us:int=None, uv:int=None, bright:int=None, contrast:int=None, thresh:int=None, invert:int=None):
        _hud_mask = cv2.imread(f"./hud_mask.png", cv2.IMREAD_GRAYSCALE)
        self.image = img
        self.image = cv2.bitwise_and(self.image, self.image, mask=_hud_mask)
        if mask_char:
            # black out character by drawing a black box above him (e.g. ignore set glow)
            self.image = cv2.rectangle(self.image, (600,250), (700,400), (0,0,0), -1)
        if erode:
            kernel = np.ones((erode, erode), 'uint8')
            self.image = cv2.erode(self.image, kernel, None, iterations=1)
        
        if dilate:
            kernel = np.ones((dilate, dilate), 'uint8')
            self.image = cv2.dilate(self.image, kernel, iterations=1)

        if blur:
            self.image = cv2.blur(self.image, (blur, blur))
        
        self.image = self.bright_contrast(self.image, bright, contrast)
        
        lower = np.array([lh, ls, lv])
        upper = np.array([uh, us, uv])

        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        cont_mask = cv2.inRange(self.hsv, lower, upper)
        self.image = cv2.bitwise_and(self.image, self.image, mask=cont_mask)
        
        if thresh:
            self.image = cv2.threshold(self.image, thresh, 255, cv2.THRESH_BINARY)[1]
        threshz = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        if thresh:
            _, threshz = cv2.threshold(threshz, thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if invert:
            self.image = 255 - self.image
        self.image = img
        cv2.imwrite(f"./info_screenshots/cows_filtered_infunction" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.image)
        return img, threshz

    #image manipulation testing for COWS
    def add_markers(self, img, threshz, rect_min_size:int, rect_max_size:int, marker:bool, marker_color=(255, 255, 0), marker_type=cv2.MARKER_CROSS, line_color=(0, 255,0), line_type=cv2.LINE_4):
        self.image = img
        #add rectangles
        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(threshz)
        ######### PLAY AROUND WITH THE RECTANGLE SIZE TO ENSURE THE RIGHT THINGS ARE MARKED
        #rect_min_size = 5 #15 self.settings['rect_min']
        #rect_max_size = 7 #25 self.settings['rect_max']
        
        for i in range(1, n_labels):
            if stats[i, cv2.CC_STAT_AREA] >= rect_min_size <= rect_max_size:
                # print(stats[i, cv2.CC_STAT_AREA])
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                cv2.rectangle(self.image, (x, y), (x + w+5, y + h+5), (0, 255, 0), thickness=1)
                if marker:
                    #draw crossharis on center of rectangle.
                    #line_color = (0, 255, 0)
                    #line_type = cv2.LINE_4
                    #marker_color = (255, 255, 0)
                    #marker_type = cv2.MARKER_CROSS
                    center_x = x + int(w/2)
                    center_y = y + int(h/2)
                    cv2.drawMarker(self.image, (center_x, center_y), color=marker_color, markerType=marker_type, markerSize=25, thickness=2)
                
        self.frame_markup = self.image.copy()
        img = self.image
        cv2.imwrite(f"./info_screenshots/cows_markered_infunction" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.image)
        return img

    #obtain the distance to the nearest marker found. we would use it to take decisions if we should bounce-off it or not
    def targets_ordered_by_distance(self, targets):
        IGNORE_RADIUS = 50
        # our character is always in the center of the screen
        my_pos = (0,0) #self._screen.convert_abs_to_monitor((0, 0))
        # searched "python order points by distance from point"
        # simply uses the pythagorean theorem
        # https://stackoverflow.com/a/30636138/4655368
        def pythagorean_distance(pos):
            return math.sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)

        # print(my_pos)
        # print(targets)
        # for t in targets:
        #    print(pythagorean_distance(t))

        # ignore targets at are too close to our character (within 130 pixels) to avoid 
        # re-clicking a deposit we just mined
        targets = [t for t in targets if pythagorean_distance(t) > self.IGNORE_RADIUS]

        return targets

    #to bring us backwards to the previous positions - not yet customized for botty
    def click_backtrack(self):
        # pop the top item off the clicked points stack. this will be the click that
        # brought us to our current location.
        last_click = self.click_history.pop()
        # to undo this click, we must mirror it across the center point. so if our
        # character is at the middle of the screen at ex. (100, 100), and our last
        # click was at (120, 120), then to undo this we must now click at (80, 80).
        # our character is always in the center of the screen
        my_pos = (self.window_w / 2, self.window_h / 2)
        mirrored_click_x = my_pos[0] - (last_click[0] - my_pos[0])
        mirrored_click_y = my_pos[1] - (last_click[1] - my_pos[1])
        # convert this screenshot position to a screen position
        screen_x, screen_y = self.get_screen_position((mirrored_click_x, mirrored_click_y))
        print('Backtracking to x:{} y:{}'.format(screen_x, screen_y))
        mouse.move(x=screen_x, y=screen_y)
        # short pause to let the mouse movement complete
        wait(0.500)
        mouse.click("right")

    # this function kills cows
    def _cows(self) -> bool:
        logger.info('\033[93m' + "Cows: Entering Portal"+ '\033[0m')
        if not self._char.select_by_template(["COW_STONY_FIELD_PORTAL_1"], threshold=0.63, time_out=4,telekinesis=True): return False
        #train neuronal network to search for heads and feet of cows that are not dead as positive according to this tutorial: https://www.youtube.com/watch?v=XrCAvs9AePM&list=PL1m2M8LQlzfKtkKq2lK5xko4X-8EZzFPI&index=8
        #train it with images from dead cows and from empty cow levels as negative
        #search for template head or feet, cast attack rotation & pickit, repeat until?
        return True

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Secret Cow Level")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Cows requires teleport")
        logger.info("Checking if we have the Wirt's Leg already")
        """
        if not self._legcheck():
            logger.info("We dont have the Leg, let's grab it! Opening WP & moving to Stony Field")
            if not self._town_manager.open_wp(start_loc):
                return False
            wait(0.4)
            self._ui_manager.use_wp(1, 2)
            return Location.A1_STONY_FIELD_WP
        else:
            self._open_cow_portal()
        """
        if not self._town_manager.open_wp(start_loc): return False
        wait(0.4)
        self._ui_manager.use_wp(1, 2)
        return Location.A1_STONY_FIELD_WP
    

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        """
        if do_pre_buff: self._char.pre_buff()   
        """
        self._picked_up_items = False
        self.used_tps = 0
        start_time = time.time()
        stuck_count = 0
        
        #########################################################################################################
        # APPLY FILTERS # need to transfer the code in a function, the one above does not work yet :(
        wait(1)
        keyboard.send(self._config.char["minimap"]) #turn on minimap       
        self.image = self._screen.grab()        
        
        #HUD removal
        _hud_mask = cv2.imread(f"d:/documents/GitHub/botty-diablo/assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
        self.image = cv2.bitwise_and(self.image, self.image, mask=_hud_mask)

        #brighten image
        self.image = self._screen.grab() 
        self.image = self.bright_contrast(self.image, 17, 116)
        #HSV filtering
        lower = np.array([0, 0, 0])
        upper = np.array([35, 13, 30])
        self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        cont_mask = cv2.inRange(self.hsv, lower, upper)
        self.image = cv2.bitwise_and(self.image, self.image, mask=cont_mask)
        #Threshold
        self.image = cv2.threshold(self.image, 25, 255, cv2.THRESH_BINARY)[1]
        threshz = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, threshz = cv2.threshold(threshz, 25, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        img = self.image
        #write screenshot to debug
        cv2.imwrite(f"./info_screenshots/cows_fil_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        #########################################################################################################
        # ADD REACTANGLES & MARKERS # need to transfer the code in a function, the one above does not work yet :(
        self.image = img
        marker = True
        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(threshz)
        rect_min_size = 5 #15 self.settings['rect_min']
        rect_max_size = 7 #25 self.settings['rect_max']
        
        targets = []

        for i in range(1, n_labels):
        # for i in range(1, 5):
            if stats[i, cv2.CC_STAT_AREA] >= rect_min_size <= rect_max_size:
                # print(stats[i, cv2.CC_STAT_AREA])
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                #cv2.rectangle(self.image, (x, y), (x + w+5, y + h+5), (0, 255, 0), thickness=0)
                if marker:
                    #draw crossharis on center of rectangle.
                    line_color = (0, 255, 0)
                    line_type = cv2.LINE_4
                    marker_color = (255, 255, 0)
                    marker_type = cv2.MARKER_CROSS
                    center_x = x + int(w/2)
                    center_y = y + int(h/2)
                    cv2.drawMarker(self.image, (center_x, center_y), color=marker_color, markerType=marker_type, markerSize=10, thickness=1)
                    target = [center_x, center_y]
                
        self.frame_markup = self.image.copy()
        
        #HUD removal
        _hud_mask = cv2.imread(f"d:/documents/GitHub/botty-diablo/assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
        self.image = cv2.bitwise_and(self.image, self.image, mask=_hud_mask)
        img = self.image
        cv2.imwrite(f"./info_screenshots/cows_fil_mar" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)     
        
        #########################################################################################################
        #img, threshz = self.apply_filter(img, mask_char=False, erode=0, dilate=0, blur=0, lh=0, ls=0, lv=24, uh=35, us=13, uv=30, bright=17, contrast=116, thresh=25, invert=0)
        #cv2.imwrite(f"./info_screenshots/cows_filtered" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        #img = self.add_markers(img, threshz, rect_min_size=5, rect_max_size=5, marker=True, marker_color=(0, 255, 255), marker_type=cv2.MARKER_CROSS, line_color=(0, 255,0), line_type=cv2.LINE_4)
        #cv2.imwrite(f"./info_screenshots/cows_filtered_marker" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        print("took screenshots with filters")
        print("Done with Screenshots")
        template = "COW_WALL_MARKER"
        wall = False
        input = self.image
        while not wall:
            print("No Wall Found")            
            wall = self._template_finder.search_and_wait_filtered(input, template, best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False, roi=Config.ui_roi["wallcheck_topright"], take_ss=False).valid 
        print("Found Wall in Topright ROI")
        #########################################################################################################
        return False
        # find old tristram portal in stony field
        found = False
        keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
        self._scout(1, -100, 100, -200, -300, stuck_count, 0, 3, 2, 2, 0, found) #scout top     
        
        # lets evaluate how long we scouted
        scout_duration = (time.time() - start_time)
        #time.strftime("%H:%M:%S", time.gmtime(scout_duration))
        Logger.info ("Scouting Duration [s]: " + str(round(scout_duration)))
        
        #get the leg & TP to town
        if not self._tristram(): return False
        Logger.info ("I arrived back in town")
        wait(3)

        #check if we have the leg.
        if not self._legcheck(): return False #if no leg is found, stop the run.
        
        #get stuff from stash & akara
        if not self._open_cow_portal(): return False
    
        # go through TP & kill cows
        if not self._cows(): return False

        return (Location.A1_COW_END, self._picked_up_items)

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

    #pre, during_1, during_2, diffed = self._map_capture()
    #self.map_diff(pre, during_1, during_2)
    print("hello")