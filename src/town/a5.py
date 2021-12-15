from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pather import Pather, Location
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait


class A5(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, pather: Pather, char: IChar, npc_manager: NpcManager):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._char = char
        self._npc_manager = npc_manager
        self._template_finder = template_finder

    def get_wp_location(self) -> Location: return Location.A5_WP

    def can_heal(self) -> bool: return True
    def can_resurrect(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_MALAH), self._char, force_move=True): return False
        self._npc_manager.open_npc_menu(Npc.MALAH)
        if not self._pather.traverse_nodes((Location.A5_MALAH, Location.A5_TOWN_START), self._char, force_move=True): return False
        return Location.A5_TOWN_START

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_QUAL_KEHK), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.QUAL_KEHK):
            self._npc_manager.press_npc_btn(Npc.QUAL_KEHK, "resurrect")
            return Location.A5_QUAL_KEHK
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_STASH), self._char):
            return False
        wait(0.5, 0.6)
        def stash_is_open_func():
            img = self._screen.grab()
            found = self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn"]).valid
            found |= self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn_stash"]).valid
            return found
        if not self._char.select_by_template(["A5_STASH", "A5_STASH_2"], stash_is_open_func):
            return False
        return Location.A5_STASH

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_LARZUK), self._char): return
        self._npc_manager.open_npc_menu(Npc.LARZUK)
        self._npc_manager.press_npc_btn(Npc.LARZUK, "trade_repair")
        return Location.A5_LARZUK

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_WP), self._char): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
        return self._char.select_by_template("A5_WP", found_wp_func)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = self._template_finder.search_and_wait(["A5_TOWN_1", "A5_TOWN_0"], time_out=20).valid
        if success:
            return Location.A5_TOWN_START
        return False
