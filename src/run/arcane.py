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
        #if not self._char.can_teleport():
        #    raise ValueError("Arcane requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        self._ui_manager.use_wp(2, 7)
        return Location.A2_ARC_START

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
    
        def enter_portal():
            # Get to act 4 via canyon in case of summoner
            template_match = self._template_finder.search_and_wait(["ARC_ALTAR", "ARC_ALTAR2"], threshold=0.70, time_out=1)
            if template_match.valid:
                def go_act4():
                    wait(0.5)
                    self._ui_manager.use_wp(4, 0)
                    return True
                def wait_for_canyon():
                    wait(0.5)
                    self._template_finder.search_and_wait(["CANYON"], threshold=0.70, time_out=2)
                    self._pather.traverse_nodes_fixed([[665,10]], self._char)
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
                if not self._char.select_by_template(["ARC_ALTAR", "ARC_ALTAR2"], go_canyon, time_out=3, threshold=0.75, telekinesis=True):
                    # teleport and try again
                    self._pather.traverse_nodes_fixed([[625,370]], self._char)
                    if not self._char.select_by_template(["ARC_ALTAR", "ARC_ALTAR2"], go_canyon, time_out=3, threshold=0.75, telekinesis=True):
                        Logger.debug("could not reach altar")
                        return False
                return True
    
        if do_pre_buff:
            self._char.pre_buff()
    
        # Move to checkpoint to determine layout
        self._pather.traverse_nodes((Location.A2_ARC_START, Location.A2_ARC_CHECKPOINT), self._char, force_move=True)
        
        """
        # Check layout
        template_match = self._template_finder.search_and_wait(["ARC_FLAT", "ARC_STAIRS", "ARC_PORTALS", "ARC_MAZE"], threshold=0.65, time_out=20)
        if not template_match.valid:
            return False
            
        # Depending on what template is found we do static pathing to the end.
        #self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char)
        """

        # Run top right
        self._pather.traverse_nodes_fixed('arc_top_right', self._char)
        
        # Move to center
        template_match = self._template_finder.search_and_wait(["ARC_ALTAR", "ARC_ALTAR2"], threshold=0.70, time_out=0.5)
        if not template_match.valid:
            self._pather.traverse_nodes([451], self._char, time_out=0.8, force_move=True)
        else:
            self._pather.traverse_nodes_fixed([[500,40]], self._char)
        
        # Attack
        self._char.kill_summoner()

        # Chests & Pick items
        wait(0.5)
        self._chest.open_up_chests(threshold=0.8)
        picked_up_items = self._pickit.pick_up_items(self._char)
        
        if enter_portal():
            return (Location.A2_ARC_END, picked_up_items)
        
        # Get in position to return
        self._pather.traverse_nodes(([452]), self._char, force_move=True)
        template_match = self._template_finder.search_and_wait(["ARC_END_1"], roi=[730,60,170,130], threshold=0.80, time_out=2)
        if not template_match.valid:
            return (Location.A2_ARC_END, picked_up_items)
        
        # Return to wp
        self._pather.traverse_nodes_fixed('arc_top_right_return', self._char)
        template_match = self._template_finder.search_and_wait(["ARC_START"], threshold=0.70, time_out=2)
        if not template_match.valid:
            return (Location.A2_ARC_END, picked_up_items)
        if do_pre_buff:
            self._char.pre_buff()    

        # Run top left
        self._pather.traverse_nodes(([453]), self._char, force_move=True)
        self._pather.traverse_nodes_fixed('arc_top_left', self._char)
        
        # Move to center
        template_match = self._template_finder.search_and_wait(["ARC_ALTAR", "ARC_ALTAR2"], threshold=0.70, time_out=0.5)
        if not template_match.valid:
            self._pather.traverse_nodes([454], self._char, time_out=0.8, force_move=True)
        else:
            self._pather.traverse_nodes_fixed([[500,40]], self._char)
        
        # Attack
        self._char.kill_summoner()

        # Chests & Pick items
        wait(0.5)
        self._chest.open_up_chests(threshold=0.8)
        picked_up_items = self._pickit.pick_up_items(self._char)
        
        if enter_portal():
            return (Location.A2_ARC_END, picked_up_items)
        
        return (Location.A2_ARC_END, picked_up_items)
