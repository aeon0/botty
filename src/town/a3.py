from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pather import Pather, Location
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait



class A3(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, pather: Pather, char: IChar, npc_manager: NpcManager):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._char = char
        self._npc_manager = npc_manager
        self._template_finder = template_finder

    def get_wp_location(self) -> Location: return Location.A3_STASH_WP
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_stash(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A3_ORMUS), self._char, force_move=True): return False
        self._npc_manager.open_npc_menu(Npc.ORMUS)
        return Location.A3_ORMUS

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A3_ORMUS), self._char, force_move=True): return False
        if self._npc_manager.open_npc_menu(Npc.ORMUS):
            self._npc_manager.press_npc_btn(Npc.ORMUS, "trade")
            return Location.A3_ORMUS
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A3_STASH_WP), self._char, force_move=True):
            return False
        wait(0.3)
        def stash_is_open_func():
            img = self._screen.grab()
            found = self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn"]).valid
            found |= self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn_stash"]).valid
            return found
        if not self._char.select_by_template("A3_STASH", stash_is_open_func, telekinesis=True):
            return False
        return Location.A3_STASH_WP

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A3_STASH_WP), self._char, force_move=True): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: self._template_finder.search(ref="LABEL_WAYPOINT", roi=self._config.ui_roi["left_panel_label"], inp_img=self._screen.grab()).valid
        return self._char.select_by_template("A3_WP", found_wp_func, telekinesis=True)

    def wait_for_tp(self) -> Union[Location, bool]:
        template_match = self._template_finder.search_and_wait("A3_TOWN_10", time_out=20)
        if template_match.valid:
            self._pather.traverse_nodes((Location.A3_STASH_WP, Location.A3_STASH_WP), self._char, force_move=True)
            return Location.A3_STASH_WP
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A3_STASH_WP), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A3_STASH_WP
        return False
