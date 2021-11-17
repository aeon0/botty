import time
import random
from utils.custom_mouse import mouse
import keyboard
from config import Config
from logger import Logger
from screen import Screen
from template_finder import TemplateFinder
import numpy as np
from typing import Tuple, List
from utils.misc import wait

class BeltManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._screen = screen
        self._config = Config()
        self._template_finder = template_finder
        self.potions_remaining = [0, 0, 0, 0]
        self.belt_height = 0

    def filter_list_pots(self, img: np.ndarray, item_list: List) -> List:
        ignorepotion_types=[]
        for x in range(4):
            #Logger.debug(f"slot:{x},type:{self._config.char['belt_slots'][x]},remain:{self.potions_remaining[x]}")

            # Exclude rule 1: if in slot x is empty then the empty potion column type(s) NOT OF THE SAME TYPE to the right of it cannot be picked up (overridden by below conditions)
            if (self.potions_remaining[x] == 0) and x<3:
                for n in range(x+1,4):
                    if (self._config.char['belt_slots'][n] not in ignorepotion_types) and (self._config.char['belt_slots'][n] != self._config.char['belt_slots'][x]):
                        ignorepotion_types.append(self._config.char['belt_slots'][n])
                        #Logger.debug(f"Excl 1: {self._config.char['belt_slots'][n]}")

            # Keep rule 1: if the potions remaining in slot 0 is <max then that type can be picked up
            if ((self.potions_remaining[x] < self.belt_height) and x == 0) and self._config.char['belt_slots'][x] in ignorepotion_types:
                ignorepotion_types.remove(self._config.char['belt_slots'][x])
                #Logger.debug(f"Keep 1: keep {self._config.char['belt_slots'][x]}")

            # Keep rule 2: if the potions remaining in slot x is >0 and <max it can be picked up
            if ((0 < self.potions_remaining[x] < self.belt_height)) and self._config.char['belt_slots'][x] in ignorepotion_types:
                ignorepotion_types.remove(self._config.char['belt_slots'][x])
                #Logger.debug(f"Keep 1: {self._config.char['belt_slots'][x]}")

            # Keep rule 3: if the potions remaining in slot x is <max and remaining potions to the left of it are max then it can be picked up
            if (self.potions_remaining[x] < self.belt_height) and (np.sum(self.potions_remaining[0:(x-1)]) == self.belt_height*(x)) and self._config.char['belt_slots'][x] in ignorepotion_types:
                ignorepotion_types.remove(self._config.char['belt_slots'][x])
                #Logger.debug(f"Keep 3: {self._config.char['belt_slots'][x]}")


        # Exclude rule 2: if all the columns of potion type have remaining pots equal to belt height then ignore type
        for potion_type in list(set(self._config.char['belt_slots'])):
            indices = [i for i, x in enumerate(self._config.char['belt_slots']) if x == potion_type]
            #Logger.debug(f"potion_type: {potion_type}; indices: {indices}")
            if (np.sum([self.potions_remaining[i] for i in indices ]) == self.belt_height*len(indices)) and (potion_type not in ignorepotion_types):
                ignorepotion_types.append(potion_type)
                #Logger.debug(f"Excl 2: {potion_type}")

        #Logger.debug(f"_ignore_potion_types ignorepotion_types: {ignorepotion_types}")
        #Logger.debug(f"filter_list_pots item_list: {item_list}")

        filteredList =  [x for x in item_list if not x.name.endswith(tuple(ignorepotion_types))]

        #Logger.debug(f"filter_list_pots item_list: {filteredList}")
        return filteredList

    def predict_pot_col(self, item_name: str) -> int:
        # find first column that matches itemName and has < belt_height pots
        col=-1
        for x in range(4):
            if self._config.char['belt_slots'][x] in item_name and self.potions_remaining[x] < self.belt_height:
                col=x
                #Logger.debug(f"Put {item_name} in slot {col}")
                break
        return col

    def get_belt_contents(self, img: np.ndarray, readAll: bool, toggleBelt: bool) -> Tuple[np.ndarray,int]:
        # args: img=screen grab; readAll=1 read entire belt, 0 for just bottom row; toogleBelt: whether to toggle full belt view or not
        self.potions_remaining = [0,0,0,0]
        belt_contents = np.full((4,4),'no_match',dtype='object')
        if toggleBelt:
            wait(0.2,0.3)
            keyboard.send(self._config.char["show_belt"]) #toggle belt on
            wait(0.2,0.3)
        if readAll:
            rows=range(4)
        else:
            rows=[3]
        for row in rows:
            top=int(round(self._config.ui_pos["potion1_y"] + row*self._config.ui_pos["potion_height"]))
            for col in range(4):
                left=int(round(self._config.ui_pos["potion1_x"] + col*self._config.ui_pos["potion_width"]))
                slot_roi=[left,top,self._config.ui_pos["potion_width"],self._config.ui_pos["potion_height"]]
                #Logger.debug(f"slot_roi {col},{row}: {slot_roi}")
                for potion_type in ["healing_potion","mana_potion","rejuvenation_potion","full_rejuvenation_potion","empty"]:
                    #Logger.debug(f"potion_type: {potion_type}")
                    if "healing" in potion_type or "mana" in potion_type:
                        search_potion_type=("belt_super_"+potion_type).upper()
                    else:
                        search_potion_type=("belt_"+potion_type).upper()
                    #Logger.debug(f"search_potion_type: {search_potion_type}")
                    found,_= self._template_finder.search(search_potion_type, img, roi=slot_roi, threshold=0.8)
                    if found:
                        #Logger.debug(f"search_potion_type: {search_potion_type} found in {col},{row}")
                        if "full" in potion_type:
                            belt_contents[col][row]="rejuvenation_potion" # override full_rejuv for now
                        else:
                            belt_contents[col][row]=potion_type
                        break
                    else:
                        belt_contents[col][row]="no_match"
                    #else:
                        #Logger.debug(f"search_potion_type: {search_potion_type} NOT found in {col},{row}")
        keepRows=[]
        for i in range(4):
            if np.all(belt_contents[:,i] != "no_match"):
                keepRows.append(i)
        if toggleBelt:
            wait(0.2,0.3)
            keyboard.send(self._config.char["show_belt"]) #toggle belt off
            wait(0.2,0.3)
        #Logger.debug(f"belt_contents:{belt_contents}, belt_height:{belt_contents[:,keepRows].shape[1]}")
        return belt_contents, belt_contents[:,keepRows].shape[1]

    def drop_wrong_belt_pots(self, belt_contents: np.ndarray, toggleBelt: bool):
        #iterate through every belt position from top to bottom
        if toggleBelt:
            wait(0.2,0.3)
            keyboard.send(self._config.char["show_belt"]) #toggle belt on
            wait(0.2,0.3)
        #Logger.debug(f"{belt_slots}")
        for y in range(belt_contents.shape[1]):
            y_center=int(round(self._config.ui_pos["potion1_y"] + y*self._config.ui_pos["potion_height"] + self._config.ui_pos["potion_height"]/2,1))
            for x in range(4):
                x_center=int(round(self._config.ui_pos["potion1_x"] + x*self._config.ui_pos["potion_width"] + self._config.ui_pos["potion_width"]/2,1))
                detected=belt_contents[x][y]
                expected=self._config.char['belt_slots'][x]
                # if detected potion type not empty, no_match, or expected then drop unless detected type is "full_rejuvenation_potion" AND expected is "rejuvenation_potion"
                if (detected not in ("empty", "no_match", expected)) and (not (detected == "full_rejuvenation_potion" and expected == "rejuvenation_potion")):
                    Logger.debug(f"Belt slot({x},{y}) detected {detected} but expected {expected}, drop")
                    mouse.move(x_center, y_center, randomize=[2, 2], delay_factor=[1, 1.5])
                    wait(0.2, 0.3)
                    mouse.click(button="left")
                    wait(0.2, 0.3)
                    mouse.move(1920/2*self._config.res["scale"], 1080/2*self._config.res["scale"], randomize=[5, 5], delay_factor=[1,1.5]) #NEED TO FIX THIS LINE SO NOT HARD CODED
                    wait(0.2, 0.3)
                    mouse.click(button="left")
                    wait(0.2, 0.3)
                # if potion is equal to expected or detected type is "full_rejuvenation_potion" AND expected is "rejuvenation_potion"
                elif (detected == expected) or (detected == "full_rejuvenation_potion" and expected == "rejuvenation_potion"):
                    #add to _potions_remaining count
                    self.potions_remaining[x] = self.potions_remaining[x] +1

        if toggleBelt:
            wait(0.2,0.3)
            keyboard.send(self._config.char["show_belt"]) #toggle belt off
            wait(0.2,0.3)

                #if belt_contents[x][y] is not self._config.char

    def fill_up_belt_from_inventory(self):
        """
        Fill up your belt with pots from the inventory e.g. after death. It will open and close invetory by itself!
        Updated 11/2021 to respect assigned potion columns
        :param num_loot_columns: Number of columns used for loot from left
        """
        inv_left = self._config.ui_pos["inventory_top_left_slot_x"]
        inv_top = self._config.ui_pos["inventory_top_left_slot_y"]
        inv_width = self._config.ui_pos["slot_width"]*self._config.char["num_loot_columns"]
        inv_height = self._config.ui_pos["slot_height"]*4
        num_loot_columns=self._config.char["num_loot_columns"]
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.7, 1.0)
        keyboard.press("shift")
        wait(0.1, 0.15)
        for potion_slot in range(4):
            potion_type=self._config.char["belt_slots"][potion_slot]
            if "healing" in potion_type or "mana" in potion_type:
                potion_template_key=("inv_super_"+potion_type).upper()
            elif "rejuvenation" in potion_type:
                potion_template_key=[("inv_"+potion_type).upper(),("inv_full_"+potion_type).upper()]
            #Logger.debug(f"potion_slot: {potion_slot} potion_type: {potion_type} potion_template_key: {potion_template_key}")
            while (self.potions_remaining[potion_slot] < self.belt_height):
                #self._template_finder.search_and_wait(potion_template_key, img, roi=[inv_left, inv_top, inv_width, inv_height], threshold=0.9,time_out=0.75) TypeError: search_and_wait() got multiple values for argument 'roi'
                img = self._screen.grab()
                found, pos = self._template_finder.search(potion_template_key, img, roi=[inv_left, inv_top, inv_width, inv_height], threshold=0.9)
                if found:
                    #Logger.debug("found")
                    x, y = self._screen.convert_screen_to_monitor(pos)
                    mouse.move(x, y, randomize=1)
                    wait(0.1, 0.2)
                    mouse.press(button="left")
                    wait(0.2, 0.3)
                    mouse.release(button="left")
                    self.potions_remaining[potion_slot] = self.potions_remaining[potion_slot] +1
                else:
                    #Logger.debug("not found")
                    break
                wait(0.1, 0.2)
        wait(0.5, 0.65)
        keyboard.release("shift")
        keyboard.send(self._config.char["inventory_screen"])


if __name__ == "__main__":
    keyboard.wait("f11")
    #idk what this does