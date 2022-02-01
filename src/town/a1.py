from char import IChar
from town.i_act import IAct
from screen import Screen
from config import Config
from npc_manager import NpcManager, Npc
from pather import Pather, Location
from typing import Union
from template_finder import TemplateFinder
from utils.misc import wait


class A1(IAct):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, pather: Pather, char: IChar, npc_manager: NpcManager):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._char = char
        self._npc_manager = npc_manager
        self._template_finder = template_finder

    def get_wp_location(self) -> Location: return Location.A1_WP_NORTH
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char, force_move=True):
            return False
        if self._npc_manager.open_npc_menu(Npc.KASHYA):
            self._npc_manager.press_npc_btn(Npc.KASHYA, "resurrect")
            return Location.A1_KASHYA_CAIN
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_WP_SOUTH), self._char): return False
        wait(0.5, 0.7)
        if not self._char._template_finder.search("A1_WP", self._screen.grab()).valid:
            curr_loc = Location.A1_WP_SOUTH
            if not self._pather.traverse_nodes((curr_loc, Location.A1_WP_NORTH), self._char): return False
            wait(0.5, 0.7)
        found_wp_func = lambda: self._template_finder.search("WAYPOINT_MENU", self._screen.grab()).valid
        # decreased threshold because we sometimes walk "over" it during pathing
        return self._char.select_by_template(["A1_WP"], found_wp_func, threshold=0.62)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = self._template_finder.search_and_wait(["A1_TOWN_7", "A1_TOWN_9"], time_out=20).valid
        if not self._pather.traverse_nodes([Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN], self._char, force_move=True): return False
        if success:
            return Location.A1_KASHYA_CAIN
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char): return False
        if self._npc_manager.open_npc_menu(Npc.CAIN):
            self._npc_manager.press_npc_btn(Npc.CAIN, "identify")
            return Location.A1_KASHYA_CAIN
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_AKARA), self._char, force_move=True): return False
        self._npc_manager.open_npc_menu(Npc.AKARA)
        self._npc_manager.press_npc_btn(Npc.AKARA, "trade")
        return Location.A1_AKARA

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_STASH), self._char):
            return False
        wait(0.5, 0.6)
        def stash_is_open_func():
            img = self._screen.grab()
            found = self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn"]).valid
            found |= self._template_finder.search("INVENTORY_GOLD_BTN", img, roi=self._config.ui_roi["gold_btn_stash"]).valid
            return found
        if not self._char.select_by_template(["A1_TOWN_0"], stash_is_open_func):
            return False
        return Location.A1_STASH

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_AKARA), self._char, force_move=True): return False
        self._npc_manager.open_npc_menu(Npc.AKARA)
        return Location.A1_AKARA

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_CHARSI), self._char): return False
        self._npc_manager.open_npc_menu(Npc.CHARSI)
        self._npc_manager.press_npc_btn(Npc.CHARSI, "trade_repair")
        return Location.A1_CHARSI
