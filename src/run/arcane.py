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
from screen import Screen
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
    
        if do_pre_buff:
            self._char.pre_buff()
    
        # move to checkpoint to determine layout
        self._pather.traverse_nodes((Location.A2_ARC_START, Location.A2_ARC_CHECKPOINT), self._char, force_move=True)
        
        # check layout
        template_match = self._template_finder.search_and_wait(["ARC_FLAT", "ARC_STAIRS", "ARC_PORTALS", "ARC_MAZE"], threshold=0.65, time_out=20)
        if not template_match.valid:
            return False
   
        # Depending on what template is found we do static pathing to the end.
        #self._pather.traverse_nodes_fixed(template_match.name.lower(), self._char)
        self._pather.traverse_nodes_fixed('arc_top_right', self._char)
        
        # Attack
        self._char.kill_summoner()

        # Chests & Pick items
        self._chest.open_up_chests()
        picked_up_items = self._pickit.pick_up_items(self._char)
        
        return (Location.A2_ARC_END, picked_up_items)
