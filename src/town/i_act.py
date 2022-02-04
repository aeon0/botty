from typing import Union
from pather import Location


class IAct:
    # Open waypoint menu
    def open_wp(self, curr_loc: Location) -> bool: return False
    # Get Location that is closest to waypoint to continue pathing from there
    def get_wp_location(self) -> Location: pass
    # Wait until we arrive in town after using town portal (by searching for templates close it)
    def wait_for_tp(self) -> Union[Location, bool]: return False

    # Is buying pots implemented for this Town?
    def can_buy_pots(self) -> bool: return False
    # Is healing implemented for this Town?
    def can_heal(self) -> bool: return False
    # Is merc resurrection implemented for this Town?
    def can_resurrect(self) -> bool: return False
    # Is stashing implemented in this Town?
    def can_stash(self) -> bool: return False
    # Is trade/repair implemented in this Town?
    def can_trade_and_repair(self) -> bool: return False
    # Is merc resurrection implemented for this Town?
    def can_identify(self) -> bool: return False    
    def can_gamble (self) -> bool: return False
    # If any of the above functions return True for the Town, the respective method must be implemented
    def open_trade_menu(self, curr_loc: Location) -> Union[Location, bool]: return False
    def heal(self, curr_loc: Location) -> Union[Location, bool]: return False
    def resurrect(self, curr_loc: Location) -> Union[Location, bool]: return False
    def open_stash(self, curr_loc: Location) -> Union[Location, bool]: return False
    def open_trade_and_repair_menu(self, curr_loc: Location) -> Union[Location, bool]: return False
    def identify(self, curr_loc: Location) -> Union[Location, bool]: return False
    def gamble (self, curr_loc: Location) -> Union[Location, bool]: return False
