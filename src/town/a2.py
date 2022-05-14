from char import IChar
from town.i_act import IAct
from screen import grab
from npc_manager import Npc, open_npc_menu, press_npc_btn
from pather import Pather, Location
from typing import Union
import template_finder
from utils.misc import wait
from ui_manager import ScreenObjects, is_visible

class A2(IAct):
    def __init__(self, pather: Pather, char: IChar):
        self._pather = pather
        self._char = char

    def get_wp_location(self) -> Location: return Location.A2_WP
    def can_stash(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return False
        if open_npc_menu(Npc.FARA):
            return Location.A2_FARA_STASH
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True):
            return False
        wait(0.3)
        def stash_is_open_func():
            img = grab()
            found = is_visible(ScreenObjects.GoldBtnInventory, img)
            found |= is_visible(ScreenObjects.GoldBtnStash, img)
            return found
        if not self._char.select_by_template(["A2_STASH_LIGHT", "A2_STASH_DARK"], stash_is_open_func, telekinesis=True):
            return False
        return Location.A2_FARA_STASH

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return False
        if open_npc_menu(Npc.CAIN):
            press_npc_btn(Npc.CAIN, "identify")
            return Location.A2_FARA_STASH
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A2_DROGNAN), self._char, force_move=True): return False
        if open_npc_menu(Npc.DROGNAN):
            press_npc_btn(Npc.DROGNAN, "trade")
            return Location.A2_DROGNAN
        return False

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A2_FARA_STASH), self._char, force_move=True): return
        if open_npc_menu(Npc.FARA):
            press_npc_btn(Npc.FARA, "trade_repair")
            return Location.A2_FARA_STASH
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A2_WP), self._char, force_move=True): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: is_visible(ScreenObjects.WaypointLabel)
        return self._char.select_by_template(["A2_WP_LIGHT", "A2_WP_DARK"], found_wp_func, telekinesis=True)

    def wait_for_tp(self) -> Union[Location, bool]:
        template_match = template_finder.search_and_wait(["A2_TOWN_21", "A2_TOWN_22", "A2_TOWN_20", "A2_TOWN_19"], timeout=20)
        if template_match.valid:
            self._pather.traverse_nodes((Location.A2_TP, Location.A2_FARA_STASH), self._char, force_move=True)
            return Location.A2_FARA_STASH
        return False
