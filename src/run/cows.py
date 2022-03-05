import random
from cv2 import LINE_4
import keyboard
import math
import numpy as np

import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager, A1
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import convert_abs_to_monitor, grab, convert_screen_to_monitor, convert_monitor_to_screen, convert_screen_to_abs, convert_abs_to_screen
from ui import skills, loading, waypoint
from ui_manager import detect_screen_object, wait_for_screen_object, ScreenObjects

import npc_manager
from npc_manager import Npc, open_npc_menu, press_npc_btn


class Cows:
    def __init__(
        self,
        pather: Pather,
        town_manager: TownManager,
        char: IChar,
        pickit: PickIt,        
    ):
        self._pather = pather
        self._town_manager = town_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0
        self._curr_loc: Union[bool, Location] = Location.A1_TOWN_START
        

    #TAKE A SCREENSHOT, CHECK FOR MARKERS, RETURN TRUE IF FOUND
    def _marker_check(self, ignore_radius:int=5, debug:bool=False, roi: list[float] = None,)-> bool:
       
        img = grab()
       
        if roi is None:
            # if no roi is provided roi = full img
            roi = [0, 0, img.shape[1], img.shape[0]]
        rx, ry, rw, rh = roi
        img = img[ry:ry + rh, rx:rx + rw]

        #filterimage, threshz = TemplateFinder().apply_filter(img, mask_char=False, mask_hud=True, info_ss=False, erode=0, dilate=2, blur=3, lh=35, ls=0, lv=0, uh=88, us=255, uv=255, bright=255, contrast=254, invert=0, thresh=0) # add HSV filter for walls (few  markers)
        filterimage, threshz = TemplateFinder().apply_filter(img, mask_char=False, mask_hud=False, info_ss=False, erode=0, dilate=4, blur=0, lh=0, ls=0, lv=95, uh=25, us=28, uv=125, bright=170, contrast=125, invert=0, thresh=98) # add HSV filter for walls (many markers)
        pos_marker = [] #define variables as empty array
        pos_rectangle = []  #define variables as empty array
        filterimage, pos_rectangle, pos_marker = TemplateFinder().add_markers(filterimage, threshz, info_ss=False, rect_min_size=40, rect_max_size=50, marker=True) # add markers to our filtered image & return the x,y coordinates for each marker and x,y,w,h for each rectangle
        if not pos_marker:
            if debug: Logger.debug("No Marker found")
            return False
        nearest_marker = TemplateFinder().get_targets_ordered_by_distance(pos_marker, ignore_radius) # returns the distance of the closest marker.
        if not nearest_marker[0]:
            if debug: Logger.debug("No nearest Marker found")
        else:
            if debug: Logger.debug (nearest_marker[0])
            pos_m = convert_abs_to_monitor(nearest_marker[0])
            pt1 = nearest_marker[0]
            check_directions = convert_screen_to_abs(pt1)
            x, y = check_directions
            if debug: 
                Logger.debug (f'\033[91m' + "Marker found at: ("+str(pos_m[0])+","+str(pos_m[1])+")" + '\033[0m')
                pt2 = (640,360)
                x1, y1 = nearest_marker[0]
                pt1 = (int(x1),int(y1))
                img = np.ascontiguousarray(img)
                cv2.arrowedLine(img, pt1, pt2, line_type=LINE_4, thickness=2, tipLength=0.3, color=(255, 0, 255))
                cv2.imwrite(f"./info_screenshots/info_add_line" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        #wait(5)
        return True , x , y


    #this function randomly teleports around until we either get stuck or find the exit we search for
    def _scout(self, corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)-> bool:
        templates_scout = ["COW_STONY_FIELD_YELLOW"] #the template we scout for on the minimap, either an exit (purple) or portal (yellow)
        templates_avoid = ["COW_COLD_PLAINS0"] #in case our scout can bring us to other locations, we add the "Entering ..." message here, so we know when we accidently leave the area
        avoid = TemplateFinder().search_and_wait(templates_avoid, best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False, suppress_debug=True, take_ss=False).valid # boolean of avoid template
        #lets make sure our minimap is on
        Logger.info('\033[93m' + "Scout: Starting to explore map" + '\033[0m')
        if not TemplateFinder().search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False, take_ss=False, suppress_debug=True).valid: #check if the minimap is already on
            keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
            keyboard.send(Config().char["minimap"]) #turn on minimap
            Logger.info('\033[93m' + "Scout: Opening Minimap" + '\033[0m')
        found = TemplateFinder().search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False).valid
        #so lets loop teleporting around until we find our templates
        while not found and not avoid:
                found = TemplateFinder().search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False).valid #boolean, if we found it
                founder = TemplateFinder().search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False, suppress_debug=True) #template
                avoid = TemplateFinder().search_and_wait(templates_avoid, best_match=True, threshold=0.8, time_out=0.1, use_grayscale=False, take_ss=False, suppress_debug=True).valid #have to repeat it from above, so its defined in the loop
                #we check if we exited our scouting location and take measures if this is the case
                if avoid:
                    Logger.info('\033[93m' + "Scout: Ended up in Cold Plains, stopping to move" + '\033[0m')
                    if corner_picker == 8:
                        corner_picker = corner_exclude
                        exclude1 = corner_picker - 1
                        exclude2 = 1
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    elif corner_picker == 1:
                        corner_picker = corner_exclude
                        exclude1 = 8
                        exclude2 = corner_picker - 1
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    else:
                        corner_picker = corner_exclude
                        exclude1 = corner_picker - 1
                        exclude2 = corner_picker + 1
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    #we might have to teleport backwards 3 times & change corners.
                    found=False
                    avoid=False
                    return avoid, found
                # we break the loop if the template is found & return its x, y position to pos_m
                if founder.valid:
                    pos_m = convert_screen_to_monitor(founder.center)
                    Logger.info('\033[93m' + "Scout: target template is at position:" + str(pos_m) + '\033[0m')
                    break
                #teleporting part
                pos_m = convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m))) # randomize our position
                t0 = grab() # take screenshot before teleport
                self._char.move(pos_m, force_tp=True, force_move=True) # first of two teleports to randomized position
                t1 = grab() # take screenshot after teleport
                # check by making a diff of the screenshots, if we moved between the teleports
                diff = cv2.absdiff(t0, t1)
                diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
                score = (float(np.sum(mask)) / mask.size) * (1/255.0) #score to check how much difference there is between screenshots (high = movement, low = stuck)
                #Logger.debug("Scout: " + str(score) + ": is our current score")
                pos_m = convert_abs_to_monitor((random.uniform(x1_m, x2_m), random.uniform(y1_m, y2_m))) # randomize our position
                self._char.move(pos_m, force_tp=True, force_move=True) # second of two teleports to randomized position
                ######## WALLCHECK #########
                #check if a wall is close by
                marker_check, x, y = self._marker_check(15, debug=True, roi=Config().ui_roi["wallcheck_roi"])
                if marker_check or score < .10:
                #lets change scouting direction:
                    score = round(score,2)
                    Logger.info('\033[93m' + "Scout: score was too low ("+str(score)+" or a Marker for a Wall was found close-by (marker_check="+str(marker_check)+"), we seem stuck, changing direction from corner: " + str(corner_picker) + '\033[0m')
                    #print(x)
                    #print(y)
                    """
                    if x < 0 and y < 0: # marker found: left top | pick: 2r, 4b, 7br, 5tr, 8bl  ex: 1l, 3t, 6tl,
                        pick_list = [2,4,7,5,8]
                        exclude_list = [1,3,6]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    if x < 0 and y > 0: # marker found: left bottom | pick: 2r, 3t, 7br, 5tr, 6tl,  ex: 1l, 4b, 8bl
                        pick_list = [2,3,7,5,6]
                        exclude_list = [1,4,8]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    if x > 0 and y < 0: # marker found: right top | pick: 1l, 4b, 8bl, 5tr  ex: 5tr, 2r, 3t,
                        pick_list = [1,4,6,7, 8]
                        exclude_list = [2,3,5]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    if x > 0 and y > 0: # marker found: right bottom | pick: 1l, 3t, 8bl, 5tr  ex: 2r,7br,4b
                        pick_list = [1,3,5,6,8]
                        exclude_list = [2,3,5]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    """
                    #new order, clockwise, top starting as 1
                    if x < 0 and y < 0: # marker found: left top (8)
                        pick_list = [2,3,4,5,6]
                        exclude_list = [7,8,1]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at Top Left ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    if x < 0 and y > 0: # marker found: left bottom (6)
                        pick_list = [8,1,2,3,4]
                        exclude_list = [5,6,7]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at Bottom Left ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    if x > 0 and y < 0: # marker found: right top (2)
                        pick_list = [4,5,6,7,8]
                        exclude_list = [1,2,3]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at Top Right ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    if x > 0 and y > 0: # marker found: right bottom (4)
                        pick_list = [1,2,6,7,8]
                        exclude_list = [3,4,5]
                        corner_picker = random.choice(pick_list)
                        corner_exclude = random.choice(exclude_list)
                        Logger.info('\033[92m' + "Scout: Marker at Bottom Right ("+str(x)+","+str(y)+"), picking corner: " +str(corner_picker)+", excluding corner: "+str(corner_exclude) + '\033[0m')
                        self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
                    #this exlude & picker has to be based on the x,y coordinate direction.
                    #corner_exclude = corner_picker
                    #self._corner_roller(corner_picker, x1_m, x2_m, y1_m, y2_m, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found)
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
            Logger.info('\033[93m' + "Scout (found TRUE): Found our Template, trying to click the exit template, calling exitclicker()" + '\033[0m')
            found = TemplateFinder().search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False).valid #boolean, if we found it
            founder = TemplateFinder().search_and_wait(templates_scout, best_match=True, threshold=0.9, time_out=0.1, use_grayscale=False, take_ss=False, suppress_debug=True) #template
            pos_m = convert_screen_to_monitor(founder.center)
            Logger.info('\033[93m' + "Scout (found TRUE): target template is at position:" + str(pos_m) + '\033[0m')
            self._exitclicker(pos_m)
            return True


    # this function is called when we are stuck and teleports backwards to get us unstuck
    def stuck(self, corner_picker, x2_m, y2_m, stuck_count, super_stuck)-> bool:
        tele_math = random.randint(1, 3) #lets roll a 3-sided dice to decide in which direction we should go now.
        if math.fmod(tele_math, 3) == 0:
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck (telemath: "+ str(tele_math) +"), let's go reverse 2 x 3, first x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            # we go opposite of our last direction
            pos_m = convert_abs_to_monitor((x2_m * -1, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            # and now we change direction along Y
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3, second x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = convert_abs_to_monitor((x2_m * -1, y2_m))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            stuck_count += 1
            super_stuck += 1
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": stuck_count: "+str(stuck_count)+", super_stuck count: "+str(super_stuck)+ '\033[0m')
        else:
            # we go opposite of our last direction
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck (telemath: "+ str(tele_math) +"), let's go reverse 2 x 3, first x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = convert_abs_to_monitor((x2_m * -1, y2_m * -1))
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            self._char.move(pos_m, force_tp=True)
            # and now we change direction along X
            Logger.info('\033[94m' + "Stuck: " + str(corner_picker) + ": Seems we are stuck, let's go reverse 2 x 3, second x3 to: ("+str(x2_m)+","+str(y2_m)+")" + '\033[0m')
            pos_m = convert_abs_to_monitor((x2_m, y2_m * -1))
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
                """
                if corner_picker == 1:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 1 = left" + '\033[0m')
                    self._scout(1, -250, -525, 0, -0, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # left
                elif corner_picker == 2:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 2 = right" + '\033[0m')
                    self._scout(2, 525, 250, 0, -0, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # right
                elif corner_picker == 3:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 3 = top " + '\033[0m')
                    self._scout(3, 0, -0, -250, -325, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # top
                elif corner_picker == 4:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 4 = bottom" + '\033[0m')
                    self._scout(4, 0, -0, 225, 150, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottom
                # commenting: maybe having less corners & wall detection speeds up things.
                elif corner_picker == 5:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 5 = top right" + '\033[0m')
                    self._scout(5, 280, 278, -220, -218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # topright
                elif corner_picker == 6:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 6 = top left " + '\033[0m')
                    self._scout(6, -280, -278, -220, -218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # topleft
                elif corner_picker == 7:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 7 = bottom right" + '\033[0m')
                    self._scout(7, 280, 278, 220, 218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottomright
                elif corner_picker == 8:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 8 = bottom left" + '\033[0m')
                    self._scout(8, -280, -278, 220, 218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottomleft    
                """
                #new order, clockwise, top starting as 1
                if corner_picker == 1:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 1 = top " + '\033[0m')
                    self._scout(3, 0, -0, -250, -325, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # top
                elif corner_picker == 2:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 2 = top right" + '\033[0m')
                    self._scout(5, 280, 278, -220, -218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # topright
                elif corner_picker == 3:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 3 = right" + '\033[0m')
                    self._scout(2, 525, 250, 0, -0, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # right
                elif corner_picker == 4:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 4 = bottom right" + '\033[0m')
                    self._scout(7, 280, 278, 220, 218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottomright
                elif corner_picker == 5:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 5 = bottom" + '\033[0m')
                    self._scout(4, 0, -0, 225, 150, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottom
                elif corner_picker == 6:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 6 = bottom left" + '\033[0m')
                    self._scout(8, -280, -278, 220, 218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # bottomleft    
                elif corner_picker == 7:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 7 = left" + '\033[0m')
                    self._scout(1, -250, -525, 0, -0, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # left
                elif corner_picker == 8:
                    Logger.info('\033[92m' + "Cornerpicker: Picked Corner 8 = top left " + '\033[0m')
                    self._scout(6, -280, -278, -220, -218, stuck_count, super_stuck, corner_exclude, exclude1, exclude2, keepernumber, found) # topleft
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
            mapcheck = TemplateFinder().search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False, take_ss=False)
            template_match = TemplateFinder().search_and_wait(templates_exit, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False, take_ss=False)
            if template_match.valid and mapcheck.valid:
                pos_m = convert_screen_to_monitor(template_match.center)
                if TemplateFinder().search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
                    Logger.info('\033[92m' + "Exit_Clicker: Step2: Minimap Scout Template Found, Minimap off" + '\033[0m')
                    keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                    keyboard.send(Config().char["minimap"]) #turn off minimap
            
            while not closetoexit:    
                closetoexit = TemplateFinder().search_and_wait(templates_exit, best_match=True, threshold=0.7,  time_out=0.1, use_grayscale=False, take_ss=False).valid
                template_match = TemplateFinder().search_and_wait(templates_scout, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False)
                if closetoexit == True or template_match == True:
                    if TemplateFinder().search_and_wait(templates_mapcheck, best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False).valid:
                        keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                        keyboard.send(Config().char["minimap"]) #turn on minimap
                        Logger.info('\033[92m' + "Exit_Clicker: Step3a: Minimap off to identify Exit Templates" + '\033[0m')
                        if TemplateFinder().search_and_wait(templates_exit, best_match=True, threshold=0.9,  time_out=0.1, use_grayscale=False, take_ss=False) == True:
                            pos_m = convert_screen_to_monitor(template_match.center)
                            pos_m = template_match.center                   
                            Logger.info('\033[92m' + "Exit_Clicker: Step3b (in while): Found Exit Template, clicking on it" + '\033[0m')
                t0 = grab()
                self._char.move(pos_m, force_tp=True, force_move=True)
                t1 = grab()
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
            found_loading_screen_func = lambda: loading.wait_for_loading_screen(2.0)
            if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                # do a random tele jump and try again
                Logger.info('\033[92m' + "Exit_Clicker: Step4b: Found Exit, but didn't manage to click it, moving left and right and top" + '\033[0m')
                pos_m = convert_abs_to_monitor((315, -150))
                self._char.move(pos_m, force_move=True)
                if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                    self._char.move(pos_m, force_move=True)
                    if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4, telekinesis=True):
                        pos_m = convert_abs_to_monitor((-315, -100))
                        self._char.move(pos_m, force_move=True)
                        Logger.info('\033[92m' + "Exit_Clicker: Step4c: Found Exit, but cannot click it, retry" + '\033[0m')
                        if not self._char.select_by_template(templates_exit, found_loading_screen_func, threshold=0.7, time_out=4,telekinesis=True):
                            Logger.info('\033[92m' + "Exit_Clicker: Step4d: Found Exit, but didn't manage to click it repeatedly, aborting run" + '\033[0m')
                            return False

            if not TemplateFinder().search_and_wait(templates_nextlevel, threshold=0.8, time_out=.5, take_ss=False).valid:
                if not TemplateFinder().search_and_wait(templates_nextlevel, threshold=0.8, time_out=1, take_ss=False).valid:
                    Logger.info('\033[92m' + "Exit_Clicker: Step5: CANNOT confirm to be at the right new location, starting again to scout()" + '\033[0m')
                    self._scout(4, -250, -400, 200, 300, 0, 0, 4, 2, 2, 4, False) # bottom - left
            else:
                Logger.info('\033[92m' + "Exit_Clicker: Step5: Confirmed to be at the right new location, switching off minimap, stopping to scout()" + '\033[0m')
                wait(1)
                keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                keyboard.send(Config().char["minimap"]) #turn off minimap
                wait(1)
            return True
            #self._tristram()

    
    #this function helps us to unstuck ourselves, when we already found our exit tile, but got stuck entering the exit.
    def exit_stuck(self, pos_m, stuck_count, super_stuck, closetoexit)-> bool:
        x, y = pos_m
        pos_m2 = x, y
        coordlog = x, y
        Logger.info(coordlog)
        x, y = convert_monitor_to_screen(pos_m2)
        pos_m2 = x, y
        x, y = convert_screen_to_abs(pos_m2)                        
        pos_m2 = x, y
        coordlog = x, y
        Logger.info(coordlog)
        # x, y = convert_abs_to_monitor((pos_m2))
        #########################
        if x < 0 and y < 0 and not closetoexit: # -, - Corner 1 Top Left
            Logger.info('\033[91m' + "Exit_stuck: corner one stuck" + '\033[0m')
            t0 = grab()                      
            pos_m2 = convert_abs_to_monitor((-600, -300))
            self._char.move(pos_m2, force_move=True)
            t1 = grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = convert_abs_to_monitor((600, -300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y < 0 and not closetoexit: #corner 2
            Logger.info('\033[91m' + "Exit_stuck: corner two stuck" + '\033[0m')
            t0 = grab()                      
            pos_m2 = convert_abs_to_monitor((600, -300))
            self._char.move(pos_m2, force_move=True)
            t1 = grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = convert_abs_to_monitor((600, 300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y > 0 and not closetoexit: #corner 3
            Logger.info('\033[91m' + "Exit_stuck: corner three stuck" + '\033[0m')
            t0 = grab()                      
            pos_m2 = convert_abs_to_monitor((600, 300))
            self._char.move(pos_m2, force_move=True)
            t1 = grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = convert_abs_to_monitor((-600, 300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x < 0 and y > 0 and not closetoexit: #corner 4
            Logger.info('\033[91m' + "Exit_stuck: corner four stuck" + '\033[0m')
            t0 = grab()                      
            pos_m2 = convert_abs_to_monitor((-600, 350))
            self._char.move(pos_m2, force_move=True)
            t1 = grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score < .15:
                pos_m2 = convert_abs_to_monitor((-600, 300))
                self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0


     #this function is called when we get stuck whilst clicking the exit after our template was found
    def exit_super_stuck(self, pos_m, stuck_count, super_stuck, closetoexit)-> bool:
        x, y = pos_m
        pos_m2 = x, y
        coordlog = x, y
        Logger.info(coordlog)
        x, y = convert_monitor_to_screen(pos_m2)
        pos_m2 = x, y
        x, y = convert_screen_to_abs(pos_m2)                        
        pos_m2 = x, y
        coordlog = x, y
        Logger.info('\033[93m' + "Exit_Super_stuck: " + str(coordlog) + '\033[0m')
        if x < 0 and y < 0: # -, - Corner 1 Top Left
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 1 Top Left" + '\033[0m')
            pos_m2 = convert_abs_to_monitor((600, 350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = convert_abs_to_monitor((-20, -300))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y < 0 and not closetoexit: #corner 2
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 2 Top Right" + '\033[0m')
            pos_m2 = convert_abs_to_monitor((-600, 350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = convert_abs_to_monitor((20, -300))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x > 0 and y > 0 and not closetoexit: #corner 3
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 3 Bottom Right" + '\033[0m')
            pos_m2 = convert_abs_to_monitor((-600, -350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = convert_abs_to_monitor((-35, 250))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        if x < 0 and y > 0 and not closetoexit: #corner 4
            Logger.info('\033[93m' + "Exit_Super_stuck: Corner 4 Bottom Left" + '\033[0m')
            pos_m2 = convert_abs_to_monitor((600, -350))
            self._char.move(pos_m2, force_tp=True)
            pos_m2 = convert_abs_to_monitor((-35, 250))
            self._char.move(pos_m2, force_tp=True)
            super_stuck += 1
            stuck_count = 0
        template_match = TemplateFinder().search_and_wait(["COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False)
        if template_match.valid: 
            template_match = TemplateFinder().search_and_wait(["COW_STONY_FIELD_YELLOW"], best_match=True, threshold=0.9,  time_out=0.5, use_grayscale=False, take_ss=False)
            pos_m = convert_screen_to_monitor(template_match.center)
            if TemplateFinder().search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.7, time_out=0.1, use_grayscale=False, take_ss=False).valid:
                keyboard.send(self._char._skill_hotkeys["teleport"])
                keyboard.send(Config().char["minimap"])
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
        if TemplateFinder().search_and_wait(["MAP_CHECK"], best_match=True, threshold=0.5, time_out=0.1, use_grayscale=False, take_ss=False).valid: #check if the minimap is already on
            keyboard.send(Config().char["minimap"]) #turn off minimap
            Logger.info('\033[95m' + "Old Tristram: Closing Minimap" + '\033[0m')
        #Calibrate at WP
        Logger.info('\033[95m' + "Old Tristram: Entering Old Tristram to get the leg" + '\033[0m')
        Logger.info('\033[95m' + "Old Tristram: Calibrating at Entrance TP" + '\033[0m')
        if not self._pather.traverse_nodes([1000], self._char, time_out=5): return False
        #Static path to Wirt
        Logger.info('\033[95m' + "Old Tristram: Static Path to Corpse" + '\033[0m')
        self._pather.traverse_nodes_fixed("cow_trist_tp_leg", self._char)
        #Calibrate at Wirt
        Logger.info('\033[95m' + "Old Tristram: Calibrating at Corpse" + '\033[0m')
        if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
        #Loot Wirt
        Logger.info('\033[95m' + "Old Tristram: Looting the leg the Corpse" + '\033[0m')
        if not self._char.select_by_template(["COW_WIRT_CLOSED"], threshold=0.63, time_out=4,telekinesis=True):
            # do a random tele jump and try again
            pos_m = convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            #and recalibrate at wirt
            if not self._pather.traverse_nodes([1001], self._char, time_out=5): return False
            if not self._char.select_by_template(["COW_WIRT_CLOSED"], threshold=0.63, time_out=4, telekinesis=True):
                Logger.info('\033[95m' + "Old Tristram: Unable to interact with the wirt" + '\033[0m')
                return False
        #Loot Leg
        Logger.info('\033[95m' + "Old Tristram: Grabbing the leg" + '\033[0m')
        self._picked_up_items |= self._pickit.pick_up_items(self._char) #grab the leg
        pos_m = convert_abs_to_monitor((0, 0))
        self._char.kill_cows(pos_m) #clear some trash to make sure, we can access the TP w/o getting interrupted
        self._picked_up_items |= self._pickit.pick_up_items(self._char)
        #TP Home
        Logger.info('\033[95m' + "Old Tristram: Making TP to go home" + '\033[0m')
        if not skills.has_tps():
            Logger.warning('\033[95m' + "Old Tristram: Open TP failed. Aborting run." + '\033[0m')
            self.used_tps += 20
            return False
        mouse.click(button="right")
        self.used_tps += 1
        if not self._char.select_by_template(["BLUE_PORTAL"], threshold=0.7, time_out=4,telekinesis=True):
            # do a random tele jump and try again
            pos_m = convert_abs_to_monitor((random.randint(-70, 70), random.randint(-70, 70)))
            self._char.move(pos_m, force_move=True)
            if not self._char.select_by_template(["BLUE_PORTAL"], threshold=0.7, time_out=4,telekinesis=True): Logger.info('\033[93m' + "Tristram: didnt make it through Portal :/" + '\033[0m')
            wait(1)
            #we need to return location!
        if not self._pather.traverse_nodes((Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN), self._char, force_move=True): return False #go back to the center after TP
        return Location.A1_KASHYA_CAIN


    #this function checks for the leg in inventory, stash & cube.
    def _legcheck(self) -> bool:
        #open inventory, search for leg
        Logger.info('\033[96m' + "Legcheck: Checking Inventory for Leg" + '\033[0m')  
        keyboard.send(Config().char["inventory_screen"]) 
        legfound = TemplateFinder().search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.8,  time_out=0.5, use_grayscale=False, take_ss=False).valid
        keyboard.send(Config().char["inventory_screen"])
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
            if TemplateFinder().search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.8,  time_out=0.5, use_grayscale=False, take_ss=False).valid: 
                Logger.info('\033[96m' + "Legcheck: Checking Stash for Leg: found, moving it to inventory" + '\033[0m')
                leg = TemplateFinder().search_and_wait("LEG_INVENTORY", Config().ui_roi["left_inventory"], time_out=3, normalize_monitor=True, take_ss=False, threshold=0.8) 
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
                self.open_cube()
                if TemplateFinder().search_and_wait(["LEG_INVENTORY"], best_match=True, threshold=0.8,  time_out=0.5, use_grayscale=False, take_ss=False).valid: 
                    Logger.info('\033[96m' + "Legcheck: Checking Cube for Leg: found, moving it to inventory" + '\033[0m')
                    leg = TemplateFinder().search_and_wait("LEG_INVENTORY", roi=Config().ui_roi["cube_area_roi"], time_out=3, normalize_monitor=True, take_ss=False, threshold=0.8) 
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

    def open_cube(self):
        #move_to_stash_tab(0)
        match = detect_screen_object(ScreenObjects.CubeInventory)
        if match.valid:
            x, y = convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            wait(0.2, 0.3)
            mouse.click("right")
            wait(0.2, 0.3)
        else:
            Logger.error(f"Can't find cube: {match.score}")

    def transmute(self):
        match = detect_screen_object(ScreenObjects.CubeOpened)
        if match.valid:
            x, y = convert_screen_to_monitor(match.center)
            mouse.move(x, y)
            wait(0.2, 0.3)
            mouse.click("left")
            wait(0.2, 0.3)


    #this function opens the cow portal
    def _open_cow_portal(self)-> bool:
        #go to Akara, get a Tome of TP
        Logger.info('\033[91m' + "Open_Cow_Portal: TP to Akara - buy Tome" + '\033[0m')
        if not self._pather.traverse_nodes((Location.A1_KASHYA_CAIN, Location.A1_AKARA), self._char, force_move=True): return False #walk to Akara
        npc_manager.open_npc_menu(Npc.AKARA)
        npc_manager.press_npc_btn(Npc.AKARA, "trade")
        #check if there is a tome for sale & buy it
        tp_tome = TemplateFinder().search_and_wait("TP_TOME", roi=Config().ui_roi["left_inventory"], time_out=3, normalize_monitor=True, take_ss=False) 
        if not tp_tome.valid: return False
        keyboard.send('ctrl', do_release=False)
        mouse.move(*tp_tome.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15) 
        mouse.click(button="right")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        keyboard.send("esc") #close vendor menu
        Logger.info('\033[91m' + "Open_Cow_Portal: Akara to Stash - get Cube"+ '\033[0m')
        if not self._pather.traverse_nodes((Location.A1_AKARA, Location.A1_STASH), self._char, force_move=True): return False #walk to Akara #Akara to Stash
        #moving to the LEFT of the stash so the Cow Portal does not block the Stash
        pos_m2 = convert_abs_to_monitor((-150, 0))
        self._char.move(pos_m2, force_tp=True)
        if not self._town_manager.open_stash(Location.A1_TOWN_START):
            Logger.info('\033[91m' + "Open_Cow_Portal: Stash not open, trying again after waiting a bit"+ '\033[0m')
            wait(0.5)
            if not self._pather.traverse_nodes([700], self._char, force_move=True): return False #walk to Town Center
            self._town_manager.open_stash(Location.A1_TOWN_START)
        Logger.info('\033[91m' + "Open_Cow_Portal: Opening Cube"+ '\033[0m')
        self.open_cube()
        tp_tome = TemplateFinder().search_and_wait("TP_TOME", roi=Config().ui_roi["4loot_columns"], time_out=3, normalize_monitor=True, take_ss=False) #we must search for the tome in our loot columns. I run with loot columns=4, so we take an ROI of 4x 40px = 160x160 from the left inventory.
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
        legmove = TemplateFinder().search_and_wait("LEG_INVENTORY", roi=Config().ui_roi["right_inventory"], time_out=3, normalize_monitor=True, take_ss=False, threshold=0.8)
        if not legmove.valid:
            Logger.info('\033[91m' + "Open_Cow_Portal: Did not find LEG to transmute, aborting run"+ '\033[0m')
            return False
        keyboard.send('ctrl', do_release=False)
        mouse.move(*legmove.center, randomize=8, delay_factor=[1.0, 1.5])
        wait(0.1, 0.15)
        mouse.click(button="left")
        wait(0.1, 0.15)
        keyboard.send('ctrl', do_press=False)
        Logger.info('\033[91m' + "Open_Cow_Portal: Transmuting"+ '\033[0m')
        self.transmute()
        wait(0.2, 0.3)
        keyboard.send("esc") #cube
        wait(0.2, 0.3)
        keyboard.send("esc") #stash & inv
        return True


    # this function kills cows
    def _cows(self) -> bool:
        Logger.info('\033[93m' + "Cows: Entering Portal"+ '\033[0m')
        wait(0.5)
        if not self._char.select_by_template(["COW_STONY_FIELD_PORTAL_1"], threshold=0.5, time_out=1, telekinesis=True): return False
        return True

    def _cull_cows(self) -> bool:
        #train neuronal network to search for heads and feet of cows that are not dead as positive according to this tutorial: https://www.youtube.com/watch?v=XrCAvs9AePM&list=PL1m2M8LQlzfKtkKq2lK5xko4X-8EZzFPI&index=8
        #train it with images from dead cows and from empty cow levels as negative
        #search for template head or feet, cast attack rotation & pickit, repeat until?
        start_time = time.time()
        cow_duration = (time.time() - start_time)
        keyboard.send(Config().char["minimap"]) #turn off minimap
        Logger.info("Minimap on, moving up 1")
        pos_m0 = (0,-400)
        pos_m = convert_abs_to_monitor(pos_m0)
        keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
        self._char.move(pos_m, force_tp=True)
        Logger.info("Minimap on, moving up 2")
        self._char.move(pos_m, force_tp=True)
        Logger.info("Minimap on, moving up 3")
        self._char.move(pos_m, force_tp=True)
        while cow_duration < 360: #we farm cows for this amount of seconds            
            #if mobfound, attack, else scout. also we could use a param for holy freeze or conviction for changing the filter depending on merc type
            self.image = grab()
            input = self.image
            cv2.imwrite(f"./info_screenshots/info_cows_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.image)
            #filterimage, threshz = TemplateFinder().apply_filter(self.image, mask_char=True, mask_hud=True, info_ss=False, erode=0, dilate=2, blur=3, lh=35, ls=0, lv=0, uh=88, us=255, uv=255, bright=255, contrast=254, thresh=0, invert=0) # add HSV filter for cows #conviction
            #holy freeze
            filterimage, threshz = TemplateFinder().apply_filter(self.image, mask_char=True, mask_hud=True, info_ss=False, erode=0, dilate=0, blur=5, lh=95, ls=109, lv=21, uh=123, us=255, uv=255, bright=255, contrast=128, thresh=117, invert=0) # add HSV filter for cows #holy freeze
            pos_marker = []
            pos_rectangle = []
            filterimage, pos_rectangle, pos_marker = TemplateFinder().add_markers(filterimage, threshz, info_ss=False, rect_min_size=100, rect_max_size=200, marker=True)
            cv2.imwrite(f"./info_screenshots/info_cows_filtered" + time.strftime("%Y%m%d_%H%M%S") + ".png", filterimage)
            order = TemplateFinder().get_targets_ordered_by_distance(pos_marker, 150)
            if not order:
                x_m = random(-600, 600)
                y_m = random(-350, 270)
                pos_m = convert_abs_to_monitor((x_m, y_m))
                #check for walls
                marker_check, x, y = self._marker_check(15, debug=True)
                if not marker_check: #if no wall, teleport where you wanted to go
                    self._char.move(pos_m, force_tp=True)
                else:
                    if x < 0 and y < 0: # marker found: left top (8)
                        Logger.info('\033[92m' + "Cull_cows: Found Wall at ("+str(x)+","+str(y)+"), - Therefore now avoiding Top and Left" + '\033[0m')
                        x_m = random(0, 525)
                        y_m = random(0, 270)
                        pos_m = convert_abs_to_monitor((x_m, y_m))
                        self._char.move(pos_m, force_tp=True)
                    if x < 0 and y > 0: # marker found: left bottom (6)
                        Logger.info('\033[92m' + "Cull_cows: Found Wall at ("+str(x)+","+str(y)+"), - Therefore now avoiding Bottom and Left" + '\033[0m')
                        x_m = random(0, 525)
                        y_m = random(0, -270)
                        pos_m = convert_abs_to_monitor((x_m, y_m))
                        self._char.move(pos_m, force_tp=True)
                    if x > 0 and y < 0: # marker found: right top (2)
                        Logger.info('\033[92m' + "Cull_cows: Found Wall at ("+str(x)+","+str(y)+"), - Therefore now avoiding Top and Right" + '\033[0m')
                        x_m = random(0, -525)
                        y_m = random(0, 270)
                        pos_m = convert_abs_to_monitor((x_m, y_m))
                        self._char.move(pos_m, force_tp=True)
                    if x > 0 and y > 0: # marker found: right bottom (4)
                        Logger.info('\033[92m' + "Cull_cows: Found Wall at ("+str(x)+","+str(y)+"), - Therefore now avoiding Bottom and Right" + '\033[0m')
                        x_m = random(0, -525)
                        y_m = random(0, -270)
                        pos_m = convert_abs_to_monitor((x_m, y_m))
                        self._char.move(pos_m, force_tp=True)                   
                keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                cow_duration = round(cow_duration, 0)
                Logger.info('\033[93m' + "Scouting for cows for " + str(cow_duration) +" seconds, moving to " + str(pos_m) + '\033[0m')
            else:
                pos_m = convert_screen_to_abs(order[0]) #nearest marker
                pos_m = convert_abs_to_monitor(pos_m)
                Logger.debug('\033[92m' + "Found cow at: " + str(pos_m) + " attacking now!" + '\033[0m')
                pt2 = (640,360)
                x1, y1 = order[0]
                pt1 = (int(x1),int(y1))
                input = np.ascontiguousarray(input)
                cv2.arrowedLine(input, pt2, pt1, line_type=LINE_4, thickness=2, tipLength=0.3, color=(255, 0, 255))
                cv2.imwrite(f"./info_screenshots/info_cow_add_line" + time.strftime("%Y%m%d_%H%M%S") + ".png", input)
                #cv2.imwrite(f"./info_screenshots/info_cowfound_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.image)
                #cv2.imwrite(f"./info_screenshots/info_cowfound_marker_" + time.strftime("%Y%m%d_%H%M%S") + ".png", filterimage)
                keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
                self._char.move(pos_m, force_tp=True)
                self._char.kill_cows(pos_m)
            cow_duration = (time.time() - start_time)
            #if cow_duration => 120: do self pre buff (renew CTA)
        Logger.info("Completed Cow Level")
        return True

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Secret Cow Level")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Cows requires teleport")
        return Location.A1_TOWN_START
    

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        #walls          {"erode": 0, "dilate": 0, "blur": 0, "lh": 000, "ls": 0, "lv": 24, "uh": 35, "us": 13, "uv": 30, "bright": 17, "contrast": 116, "invert": 0, "thresh": 25}
        #path           {"erode": 0, "dilate": 4, "blur": 4, "lh": 015, "ls": 255, "lv": 255, "uh": 255, "us": 255, "uv": 255, "bright": 255, "contrast": 224, "invert": 0, "thresh": 85}
        #path2          {"erode": 0, "dilate": 5, "blur": 2, "lh": 007, "ls": 225, "lv": 225, "uh": 80, "us": 255, "uv": 250, "bright": 219, "contrast": 224, "invert": 0, "thresh": 115}
        #yellow portal  {"erode": 0, "dilate": 0, "blur": 0, "lh": 000, "ls": 255, "lv": 0, "uh": 83, "us": 255, "uv": 255, "bright": 210, "contrast": 165, "invert": 0, "thresh": 236}
        #cave exit      {"erode": 0, "dilate": 3, "blur": 0, "lh": 118, "ls": 0, "lv": 135, "uh": 245, "us": 255, "uv": 255, "bright": 165, "contrast": 197, "invert": 0, "thresh": 85}
        
        start_loc = Location.A1_TOWN_START

        Logger.info("Checking if we have the Wirt's Leg already")
        if not self._legcheck():
            Logger.info("We dont have the Leg, let's grab it! Opening WP & moving to Stony Field")
            if not self._town_manager.open_wp(start_loc): return False
            wait(0.4)
            waypoint.use_wp("Stony Field")
            if do_pre_buff: self._char.pre_buff()   
            self._picked_up_items = False
            self.used_tps = 0
            # find old tristram portal in stony field
            stuck_count = 0
            start_time = time.time()
            found = False
            keyboard.send(self._char._skill_hotkeys["teleport"]) #switch active skill to teleport
            self._scout(1, -100, 100, -200, -300, stuck_count, 0, 3, 2, 2, 0, found) #scout top     
            scout_duration = (time.time() - start_time) # lets evaluate how long we scouted
            Logger.info ("Scouting Duration [s]: " + str(round(scout_duration)))
            #get the leg & TP to town
            if not self._tristram(): return False
            Logger.info ("I arrived back in town")     
            #check if we have the leg.
            if not self._legcheck(): return False #if no leg is found, stop the run.
                
        #get stuff from stash & akara
        if not self._open_cow_portal(): return False
        # go through TP & kill cows
        if not self._cows(): return False
        if do_pre_buff: self._char.pre_buff()
        if not self._cull_cows(): return False
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
    from town import TownManager
    from npc_manager import NpcManager
    from template_finder import TemplateFinder
    config = Config()
    game_stats = GameStats()
    templatefinder = TemplateFinder
    bot = Bot(game_stats, templatefinder, False)
