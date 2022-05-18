from char import IChar
from town.i_act import IAct
from screen import grab
from npc_manager import Npc, open_npc_menu, press_npc_btn
from pather import Pather, Location
from typing import Union
import template_finder
from utils.misc import wait
from ui_manager import ScreenObjects, is_visible


class A4(IAct):
    def __init__(self, pather: Pather, char: IChar):
        self._pather = pather
        self._char = char

    def get_wp_location(self) -> Location: return Location.A4_WP
    def can_resurrect(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_gamble(self) -> bool: return True
    def can_heal(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_TYRAEL_STASH), self._char, force_move=True):
            return False
        if open_npc_menu(Npc.TYRAEL):
            press_npc_btn(Npc.TYRAEL, "resurrect")
            return Location.A4_TYRAEL_STASH
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_WP), self._char, force_move=True): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: is_visible(ScreenObjects.WaypointLabel)
        # decreased threshold because we sometimes walk "over" it during pathing
        return self._char.select_by_template(["A4_WP", "A4_WP_2"], found_wp_func, threshold=0.62, telekinesis=False)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = template_finder.search_and_wait(["A4_TOWN_4", "A4_TOWN_5", "A4_TOWN_6"], timeout=20).valid
        if success:
            return Location.A4_TOWN_START
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_TYRAEL_STASH), self._char, force_move=True): return False
        if open_npc_menu(Npc.CAIN):
            press_npc_btn(Npc.CAIN, "identify")
            return Location.A4_TYRAEL_STASH
        return False

    def gamble (self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_JAMELLA), self._char, force_move=True): return False
        if open_npc_menu(Npc.JAMELLA):
            press_npc_btn(Npc.JAMELLA, "gamble")
            return Location.A4_JAMELLA
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_JAMELLA), self._char, force_move=True): return False
        if open_npc_menu(Npc.JAMELLA):
            press_npc_btn(Npc.JAMELLA, "trade")
            return Location.A4_JAMELLA
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_TYRAEL_STASH), self._char, force_move=True):
            return False
        wait(0.5, 0.6)
        def stash_is_open_func():
            img = grab()
            found = is_visible(ScreenObjects.GoldBtnInventory, img)
            found |= is_visible(ScreenObjects.GoldBtnStash, img)
            return found
        if not self._char.select_by_template(["A4_TOWN_2"], stash_is_open_func, telekinesis=True):
            return False
        return Location.A4_TYRAEL_STASH

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_JAMELLA), self._char, force_move=True): return False
        if open_npc_menu(Npc.JAMELLA):
            return Location.A4_JAMELLA
        return False

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A4_HALBU), self._char, force_move=True): return False
        if open_npc_menu(Npc.HALBU):
            press_npc_btn(Npc.HALBU, "trade_repair")
            return Location.A4_HALBU
        return False
