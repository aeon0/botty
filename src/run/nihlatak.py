from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui_manager import UiManager
from utils.misc import wait


class Nihlatak:
    def __init__(
        self,
        template_finder: TemplateFinder,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt
    ):
        self._config = Config()
        self._template_finder = template_finder
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Nihlatak")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(5, 4) # use Halls of Pain Waypoint (5th in A5)
        #return Location.A5_Nilatak_START # I dont think I need this.

    def battle(self, do_nihlatak: bool, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if do_pre_buff: # we buff first, to get that out of the way of the whole logic that is to follow for finding the right way
            self._char.pre_buff()        
        template_match = self._template_finder.search_and_wait(["NI1_A", "NI1_B", "NI1_C"], threshold=0.65, time_out=20) # So let's check which layout ("NI1_A = bottom exit" , "NI1_B = large room", "NI1_C = small room") of Level1 we have.
        if not template_match.valid:# check if any of these templates was found
            return False
        self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) # depending on what template is found we do static pathing to the stairs on level1. It expects that the static routes to be defined in game.ini named: "ni_a", "ni_b", "ni_c"
        self._char.select_by_template(["NI1_STAIRS"]) # So the static path brought me safely to the stairs leading to HALLS OF PAIN LEVEL2 - Now, I just have to click the stairs template "NI1_STAIRS" to enter level2
        return Location.A5_NIHLATAK_LVL2_START # and here we are, level2
        
        #example block
        #pather.traverse_nodes(Location.A5_NIHLATAK_LVL2_C, Location.A5_NIHLATAK_LVL2_D, char) #brings us from eye check C to eye check D
        #template_match = self._template_finder.search_and_wait(["NI2_D", threshold=0.65, time_out=20) # look for the eye at location D
        #    if not template_match.valid:
        #        return False # I didnt find the eye at location D, i should go back to level1 & tp home
        #    self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) #path to nihlatak in position D
        #end example block


        pather.traverse_nodes(Location.A5_NIHLATAK_LVL2_START, Location.A5_NIHLATAK_LVL2_A, char) # So now we traverse from stairs to the first location to check for eyes: brings us from stairs to eye check A
        template_match = self._template_finder.search_and_wait(["NI2_A"], threshold=0.65, time_out=20)  # look for the eye at location A
        if template_match.valid: 
            self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) # I found the eye and now moving on to nihlatak. 
        elif #did not find the eye in position A, so lets move on
            pather.traverse_nodes(Location.A5_NIHLATAK_LVL2_A, Location.A5_NIHLATAK_LVL2_B, char) #brings us from eye check A to eye check B
            template_match = self._template_finder.search_and_wait(["NI2_B"], threshold=0.65, time_out=20)  # look for the eye at location B
            self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) #path to nihlatak in position B
        elif #did not find the eye in position B, so lets move on
            pather.traverse_nodes(Location.A5_NIHLATAK_LVL2_B, Location.A5_NIHLATAK_LVL2_C, char) #brings us from eye check B to eye check C
            template_match = self._template_finder.search_and_wait(["NI2_C"], threshold=0.65, time_out=20)  # look for the eye at location C
            self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) #path to nihlatak in position C
        elif #did not find the eye in position C, so lets move on
            pather.traverse_nodes(Location.A5_NIHLATAK_LVL2_C, Location.A5_NIHLATAK_LVL2_D, char) #brings us from eye check C to eye check D
            template_match = self._template_finder.search_and_wait(["NI2_D"], threshold=0.65, time_out=20)  # look for the eye at location D
            self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char) #path to nihlatak in position D
        else #did not find the eye in position D, so lets move on
            pather.traverse_nodes(Location.A5_NIHLATAK_LVL2_D, Location.A5_NIHLATAK_LVL2_END, char) #brings us from eye check D back to the stairs - if I end up here, then I didnt find an eye and can go back to Level1 for save TP home.
            self._char.select_by_template(["NI2_SEARCH_0"]) #obviously, I did not find what I was looking for, so better click on the stairs "NI2_SEARCH_0" here to go back to level1
            return False # here should be a line to TP back to town & start the next run
            
        self._char.kill_nihlatak()
        loc = Location.A5_NIHLATAK_END
        wait(0.2, 0.3)
        picked_up_items = self._pickit.pick_up_items(self._char)     

        return (loc, picked_up_items)