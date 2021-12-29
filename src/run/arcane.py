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
from chest import Chest

class Arcane:
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
        self._chest = Chest(self._char, self._template_finder, 'arcane')
    
    def approach(self, start_loc: Location) -> Union[bool, Location]:
        Logger.info("Run Arcane")
        if not self._char.can_teleport():
            raise ValueError("Arcane requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(2, 7)
        return Location.A2_ARC_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
    
        def enter_portal():
            # Get to act 4 via canyon in case of summoner
            template_match = self._template_finder.search_and_wait(["ARC_ALTAR", "ARC_ALTAR2", "ARC_ALTAR3"], threshold=0.70, time_out=1)
            if template_match.valid:
                def go_act4():
                    wait(0.5)
                    self._ui_manager.use_wp(4, 0)
                    return True
                def wait_for_canyon():
                    wait(0.5)
                    self._template_finder.search_and_wait(["CANYON"], threshold=0.70, time_out=2)
                    self._pather.traverse_nodes_fixed([[665,10]], self._char)
                    if self._chest.open_up_chest(threshold=0.8) > 0.8:
                        self._pickit.pick_up_items(self._char)
                    if not self._char.select_by_template(["CANYON"], go_act4, telekinesis=True):
                        Logger.debug("Did not find altar")
                        return False
                    return True
                def go_canyon():
                    template_match = self._template_finder.search_and_wait(["ARC_SPEECH"], threshold=0.70, time_out=2)
                    if not template_match.valid:
                        return False
                    # dismiss altar speech
                    self._pather.traverse_nodes_fixed([[625,360]], self._char)
                    wait(1)
                    template_match = self._template_finder.search_and_wait(["ARC_RED_PORTAL"], threshold=0.70, time_out=1)
                    if template_match.valid:
                        if not self._char.select_by_template(["ARC_RED_PORTAL"], wait_for_canyon, time_out=2, telekinesis=True):
                            Logger.debug("Did not find red portal")
                            return False
                        return True
                    return False
                self._pather.traverse_nodes([461], self._char, time_out=0.7, force_move=True)
                if not self._char.select_by_template(["ARC_ALTAR", "ARC_ALTAR2"], go_canyon, time_out=3, threshold=0.70, telekinesis=True):
                    # teleport and try again
                    self._pather.traverse_nodes_fixed([[625,370]], self._char)
                    if not self._char.select_by_template(["ARC_ALTAR", "ARC_ALTAR2"], go_canyon, time_out=3, threshold=0.60, telekinesis=True):
                        Logger.debug("could not reach altar")
                return True
                
        def move_center(transverse=[]) -> bool:
            def find_center() -> bool:
                template_match = self._template_finder.search_and_wait(["ARC_PLATFORM_1", "ARC_PLATFORM_2", "ARC_PLATFORM_3", "ARC_CENTER"], threshold=0.50, time_out=0.5)
                if template_match.valid:
                    self._pather.traverse_nodes([451], self._char, time_out=0.7, force_move=True)
                    return True
                else:
                    self._pather.traverse_nodes_fixed(transverse, self._char)
                    template_match = self._template_finder.search_and_wait(["ARC_ALTAR", "ARC_ALTAR2"], threshold=0.70, time_out=0.5)
                    if template_match.valid:
                        self._pather.traverse_nodes([461], self._char, time_out=0.7, force_move=True)
                        return True
                return False
            if not find_center():
                self._char.kill_summoner()
                chest_loot()
                # move and try again
                self._pather.traverse_nodes_fixed([[700,500]], self._char)
                if not find_center():
                    Logger.debug("Could not find the way back")
                    return False    
            return True
                
        def chest_loot() -> bool:
            wait(0.5)
            self._chest.open_up_chests(threshold=0.8)
            return self._pickit.pick_up_items(self._char)
            
        def return_wp(path: str, traverse = []) -> bool:
            Logger.debug("Returning to wp")
            self._pather.traverse_nodes_fixed(path, self._char)
            self._pather.traverse_nodes_fixed([traverse], self._char)
            template_match = self._template_finder.search_and_wait(["ARC_START"], threshold=0.70, time_out=2)
            if not template_match.valid:
                return False
            return True
                
        def get_in_position(path: float) -> bool:
            Logger.debug("Get in position")
            template_match = self._template_finder.search_and_wait(["ARC_PLATFORM_1", "ARC_PLATFORM_2", "ARC_CENTER", "ARC_END_1", "ARC_END_2"], threshold=0.50, time_out=1)
            if not template_match.valid:
                Logger.debug("Failed to set position to return")
                return False
            self._pather.traverse_nodes(([path]), self._char, force_move=True)
            template_match = self._template_finder.search_and_wait(["ARC_PLATFORM_1", "ARC_PLATFORM_2", "ARC_CENTER"], threshold=0.50, time_out=2)
            return template_match.valid
    
        picked_up_items = False
    
        if do_pre_buff:
            self._char.pre_buff()

        # Run top right
        self._pather.traverse_nodes(([450]), self._char, force_move=True)
        self._pather.traverse_nodes_fixed('arc_top_right', self._char)
        
        if not move_center([[500,40]]):
            return (Location.A2_ARC_END, picked_up_items)
            
        self._char.kill_summoner()

        picked_up_items = picked_up_items or chest_loot()
        
        if enter_portal():
            return (Location.A2_ARC_END, picked_up_items)
           
        if not get_in_position(452):
            return (Location.A2_ARC_END, picked_up_items)

        if not return_wp('arc_bottom_left', [20,360]):
            return (Location.A2_ARC_END, picked_up_items)
  
        # Run top left
        self._pather.traverse_nodes(([453]), self._char, force_move=True)
        self._pather.traverse_nodes_fixed([[20,20]], self._char)
        self._pather.traverse_nodes_fixed('arc_top_left', self._char)
        
        move_center([[500,40]])
        
        self._char.kill_summoner()

        picked_up_items = picked_up_items or chest_loot()
        
        if enter_portal():
            return (Location.A2_ARC_END, picked_up_items)
            
        if not get_in_position(454):
            return (Location.A2_ARC_END, picked_up_items)
               
        if not return_wp('arc_bottom_right', [1250,700]):
            return (Location.A2_ARC_END, picked_up_items)
      
        # Run bottom right
        if do_pre_buff:
            self._char.pre_buff()
        
        self._pather.traverse_nodes(([456]), self._char, force_move=True)
        self._pather.traverse_nodes_fixed([[1250,700]], self._char)
        self._pather.traverse_nodes_fixed('arc_bottom_right', self._char)
        
        move_center([[500,40]])

        self._char.kill_summoner()

        picked_up_items = picked_up_items or chest_loot()
        
        if enter_portal():
            return (Location.A2_ARC_END, picked_up_items)
            
        if not get_in_position(457):
            return (Location.A2_ARC_END, picked_up_items)
       
        if not return_wp('arc_top_left', [20,20]):
            return (Location.A2_ARC_END, picked_up_items)

        # Run bottom left
        self._pather.traverse_nodes(([459]), self._char, force_move=True)
        self._pather.traverse_nodes_fixed([[20,700]], self._char)
        self._pather.traverse_nodes_fixed('arc_bottom_left', self._char)
        
        move_center([[500,20], [700,100]])

        self._char.kill_summoner()

        picked_up_items = picked_up_items or chest_loot()
        
        if enter_portal():
            return (Location.A2_ARC_END, picked_up_items)
        
        return (Location.A2_ARC_END, picked_up_items)