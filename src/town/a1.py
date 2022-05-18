from char import IChar
from town.i_act import IAct
from screen import grab
from config import Config
from npc_manager import Npc, open_npc_menu, press_npc_btn
from pather import Pather, Location
from typing import Union
import template_finder
from ui_manager import ScreenObjects, is_visible
from utils.misc import wait


class A1(IAct):
    def __init__(self, pather: Pather, char: IChar):
        self._pather = pather
        self._char = char

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
        if open_npc_menu(Npc.KASHYA):
            press_npc_btn(Npc.KASHYA, "resurrect")
            return Location.A1_KASHYA_CAIN
        return False

    def open_wp(self, curr_loc: Location) -> bool:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_WP_SOUTH), self._char, force_move=True): return False
        wait(0.5, 0.7)
        if not template_finder.search("A1_WP", grab()).valid:
            curr_loc = Location.A1_WP_SOUTH
            if not self._pather.traverse_nodes((curr_loc, Location.A1_WP_NORTH), self._char, force_move=True): return False
            wait(0.5, 0.7)
        found_wp_func = lambda: is_visible(ScreenObjects.WaypointLabel)
        # decreased threshold because we sometimes walk "over" it during pathing
        return self._char.select_by_template(["A1_WP"], found_wp_func, threshold=0.62)

    def wait_for_tp(self) -> Union[Location, bool]:
        success = template_finder.search_and_wait(["A1_TOWN_7", "A1_TOWN_9"], timeout=20).valid
        if not self._pather.traverse_nodes([Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN], self._char, force_move=True): return False
        if success:
            return Location.A1_KASHYA_CAIN
        return False

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_KASHYA_CAIN), self._char, force_move=True): return False
        if open_npc_menu(Npc.CAIN):
            press_npc_btn(Npc.CAIN, "identify")
            return Location.A1_KASHYA_CAIN
        return False

    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_AKARA), self._char, force_move=True): return False
        open_npc_menu(Npc.AKARA)
        press_npc_btn(Npc.AKARA, "trade")
        return Location.A1_AKARA

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_STASH), self._char, force_move=True):
            return False
        wait(0.5, 0.6)
        def stash_is_open_func():
            img = grab()
            found = is_visible(ScreenObjects.GoldBtnInventory, img)
            found |= is_visible(ScreenObjects.GoldBtnStash, img)
            return found
        if not self._char.select_by_template(["A1_TOWN_0"], stash_is_open_func):
            return False
        return Location.A1_STASH

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_AKARA), self._char, force_move=True): return False
        open_npc_menu(Npc.AKARA)
        return Location.A1_AKARA

    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]:
        if not self._pather.traverse_nodes((curr_loc, Location.A1_CHARSI), self._char, force_move=True): return False
        open_npc_menu(Npc.CHARSI)
        press_npc_btn(Npc.CHARSI, "trade_repair")
        return Location.A1_CHARSI
