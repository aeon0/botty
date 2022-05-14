from char import IChar
from town.i_act import IAct
from screen import grab
from npc_manager import Npc, open_npc_menu, press_npc_btn
from pather import Pather, Location
from typing import Union
import template_finder
from utils.misc import wait
from ui_manager import ScreenObjects, is_visible


class A5(IAct):
    def __init__(self, pather: Pather, char: IChar):
        self._pather = pather
        self._char = char

    def get_wp_location(self) -> Location: return Location.A5_WP
    def can_heal(self) -> bool: return True
    def can_buy_pots(self) -> bool: return True
    def can_resurrect(self) -> bool: return True
    def can_identify(self) -> bool: return True
    def can_stash(self) -> bool: return True
    def can_trade_and_repair(self) -> bool: return True

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_MALAH), self._char, force_move=True): return False
        if not open_npc_menu(Npc.MALAH): return False
        if not self._pather.traverse_nodes((Location.A5_MALAH, Location.A5_TOWN_START), self._char, force_move=True): return False
        return Location.A5_TOWN_START

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_MALAH), self._char, force_move=True): return False
        if open_npc_menu(Npc.MALAH):
            press_npc_btn(Npc.MALAH, "trade")
            return Location.A5_MALAH
        return False

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_QUAL_KEHK), self._char, force_move=True): return False
        if open_npc_menu(Npc.QUAL_KEHK):
            press_npc_btn(Npc.QUAL_KEHK, "resurrect")
            return Location.A5_QUAL_KEHK
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_QUAL_KEHK), self._char, force_move=True): return False
        if open_npc_menu(Npc.CAIN):
            press_npc_btn(Npc.CAIN, "identify")
            return Location.A5_QUAL_KEHK
        return False

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_STASH), self._char, force_move=True):
            return False
        wait(0.5, 0.6)
        def stash_is_open_func():
            img = grab()
            found = is_visible(ScreenObjects.GoldBtnInventory, img)
            found |= is_visible(ScreenObjects.GoldBtnStash, img)
            return found
        if not self._char.select_by_template(["A5_STASH", "A5_STASH_2"], stash_is_open_func, telekinesis=True):
            return False
        return Location.A5_STASH

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_LARZUK), self._char, force_move=True): return False
        open_npc_menu(Npc.LARZUK)
        press_npc_btn(Npc.LARZUK, "trade_repair")
        return Location.A5_LARZUK

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A5_WP), self._char, force_move=True): return False
        wait(0.5, 0.7)
        found_wp_func = lambda: is_visible(ScreenObjects.WaypointLabel)
        return self._char.select_by_template("A5_WP", found_wp_func, telekinesis=True)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = template_finder.search_and_wait(["A5_TOWN_1", "A5_TOWN_0"], timeout=20).valid
        if success:
            return Location.A5_TOWN_START
        return False
