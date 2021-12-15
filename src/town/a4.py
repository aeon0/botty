from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pather import Pather, Location
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait


class A4(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, pather: Pather, char: IChar, npc_manager: NpcManager):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._char = char
        self._npc_manager = npc_manager
        self._template_finder = template_finder

    def get_wp_location(self) -> Location: return Location.A4_WP
    def can_resurrect(self) -> bool: return True

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_TYRAEL_STASH), self._char, force_move=True):
            return False
        if self._npc_manager.open_npc_menu(Npc.TYRAEL):
            self._npc_manager.press_npc_btn(Npc.TYRAEL, "resurrect")
            return Location.A4_TYRAEL_STASH
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_WP), self._char): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
        # decreased threshold because we sometimes walk "over" it during pathing
        return self._char.select_by_template(["A4_WP", "A4_WP_2"], found_wp_func, threshold=0.62)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = self._template_finder.search_and_wait(["A4_TOWN_4", "A4_TOWN_5", "A4_TOWN_6"], time_out=20).valid
        if success:
            return Location.A4_TOWN_START
        return False