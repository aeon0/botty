from typing import Union
import template_finder
from config import Config
from pather import Location
from logger import Logger
from town import IAct, A1, A2, A3, A4, A5
from utils.misc import wait
from screen import grab
from ui import waypoint, view
from inventory import consumables, personal, vendor, common

TOWN_MARKERS = [
            "A5_TOWN_0", "A5_TOWN_1",
            "A4_TOWN_4", "A4_TOWN_5",
            "A3_TOWN_0", "A3_TOWN_1",
            "A2_TOWN_0", "A2_TOWN_1", "A2_TOWN_10",
            "A1_TOWN_1", "A1_TOWN_3"
        ]

class TownManager:

    def __init__(self, a1: A1, a2: A2, a3: A3, a4: A4, a5: A5):
        self._acts: dict[Location, IAct] = {
            Location.A1_TOWN_START: a1,
            Location.A2_TOWN_START: a2,
            Location.A3_TOWN_START: a3,
            Location.A4_TOWN_START: a4,
            Location.A5_TOWN_START: a5
        }

    @staticmethod
    def get_act_from_location(loc: Location) -> Location:
        location = None
        if loc.upper().startswith("A5_"):
            location = Location.A5_TOWN_START
        elif loc.upper().startswith("A4_"):
            location = Location.A4_TOWN_START
        elif loc.upper().startswith("A3_"):
            location = Location.A3_TOWN_START
        elif loc.upper().startswith("A2_"):
            location = Location.A2_TOWN_START
        elif loc.upper().startswith("A1_"):
            location = Location.A1_TOWN_START
        return location

    def wait_for_town_spawn(self, timeout: float = 30) -> Location:
        """Wait for the char to spawn in town after starting a new game
        :param timeout: Optional float value for time out in seconds, defaults to None
        :return: Location of the town (e.g. Location.A4_TOWN_START) or None if nothing was found within timeout time
        """
        template_match = template_finder.search_and_wait(TOWN_MARKERS, best_match=True, timeout=timeout)
        if template_match.valid:
            return TownManager.get_act_from_location(template_match.name)
        return None

    def wait_for_tp(self, curr_loc: Location):
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        return self._acts[curr_act].wait_for_tp()

    def open_wp(self, curr_loc: Location):
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        return self._acts[curr_act].open_wp(curr_loc)

    def go_to_act(self, act_idx: int, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we already are in the desired act
        if act_idx == 1: act = Location.A1_TOWN_START
        elif act_idx == 2: act = Location.A2_TOWN_START
        elif act_idx == 3: act = Location.A3_TOWN_START
        elif act_idx == 4: act = Location.A4_TOWN_START
        elif act_idx == 5: act = Location.A5_TOWN_START
        else:
            Logger.error(f"Act {act_idx} is not supported")
            return False
        if curr_act == act:
            return curr_loc
        # if not, move to the desired act via waypoint
        if not self._acts[curr_act].open_wp(curr_loc): return False
        waypoint.use_wp(act = act_idx, idx = 0)
        return self._acts[act].get_wp_location()

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can heal in current act
        if self._acts[curr_act].can_heal():
            return self._acts[curr_act].heal(curr_loc)
        Logger.warning(f"Could not heal in {curr_act}. Continue without healing")
        return curr_loc

    def buy_consumables(self, curr_loc: Location, items: list = None):
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False, items
        # check if we can buy pots in current act
        if self._acts[curr_act].can_buy_pots():
            new_loc = self._acts[curr_act].open_trade_menu(curr_loc)
            if not (new_loc and common.wait_for_left_inventory()): return False, items
            common.select_tab(3)
            img=grab()
            # Buy HP pots
            if consumables.get_needs("health") > 0:
                can_shift_click = not sum([ x > 0 for x in [consumables.get_needs("health"), consumables.get_needs("mana"), consumables.get_needs("rejuv")]]) > 1
                if vendor.buy_item(template_name = "SUPER_HEALING_POTION", quantity = consumables.get_needs("health"), shift_click = can_shift_click, img=img):
                    consumables.set_needs("health", 0)
                else:
                    if vendor.buy_item(template_name="GREATER_HEALING_POTION", quantity = consumables.get_needs("health"), shift_click = can_shift_click, img=img):
                        consumables.set_needs("health", 0)
                    else:
                        Logger.error("buy_consumables: Error purchasing health potions")
            # Buy mana pots
            if consumables.get_needs("mana") > 0:
                can_shift_click = not sum([ x > 0 for x in [consumables.get_needs("health"), consumables.get_needs("mana"), consumables.get_needs("rejuv")]]) > 1
                if vendor.buy_item(template_name="SUPER_MANA_POTION", quantity = consumables.get_needs("mana"), shift_click = can_shift_click, img=img):
                    consumables.set_needs("mana", 0)
                else:
                    if vendor.buy_item(template_name="GREATER_MANA_POTION", quantity = consumables.get_needs("mana"), shift_click = can_shift_click, img=img):
                        consumables.set_needs("mana", 0)
                    else:
                        Logger.error("buy_consumables: Error purchasing mana potions")
            # Buy TP scrolls
            if consumables.get_needs("tp") > 0:
                if vendor.buy_item(template_name="INV_SCROLL_TP", shift_click = True, img=img):
                    consumables.set_needs("tp", 0)
                else:
                    Logger.error("buy_consumables: Error purchasing teleport scrolls")
            # Buy ID scrolls
            if consumables.get_needs("id") > 0:
                if vendor.buy_item(template_name="INV_SCROLL_ID", shift_click = True, img=img):
                    consumables.set_needs("id", 0)
                else:
                    Logger.error("buy_consumables: Error purchasing ID scrolls")
            # Buy keys
            if consumables.get_needs("key") > 0:
                if vendor.buy_item(template_name="INV_KEY", shift_click = True, img=img):
                    consumables.set_needs("key", 0)
                else:
                    Logger.error("buy_consumables: Error purchasing keys")
            # Sell items, if any
            if items:
                items = personal.transfer_items(items, action = "sell")
            common.close()
            return new_loc, items
        Logger.warning(f"Could not buy consumables in {curr_act}. Continue.")
        return curr_loc, items

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can resurrect in current act
        if self._acts[curr_act].can_resurrect():
            return self._acts[curr_act].resurrect(curr_loc)
        new_loc = self.go_to_act(4, curr_loc)
        if not new_loc: return False
        return self._acts[Location.A4_TOWN_START].resurrect(new_loc)

    def identify(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can Identify in current act
        if self._acts[curr_act].can_identify():
            success = self._acts[curr_act].identify(curr_loc)
            view.return_to_play()
            return success
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False
        success = self._acts[Location.A5_TOWN_START].identify(new_loc)
        view.return_to_play()
        return success

    def open_stash(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        new_loc = curr_loc

        if not self._acts[curr_act].can_stash():
            new_loc = self.go_to_act(5, curr_loc)
            if not new_loc: return False
            curr_act = Location.A5_TOWN_START

        new_loc = self._acts[curr_act].open_stash(new_loc)
        if not new_loc: return False
        return new_loc

    def gamble(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can Identify in current act
        if self._acts[curr_act].can_gamble():
            return self._acts[curr_act].gamble(curr_loc)
        new_loc = self.go_to_act(4, curr_loc)
        if not new_loc: return False
        return self._acts[Location.A4_TOWN_START].gamble(new_loc)

    def stash(self, curr_loc: Location, items: list = None):
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False, False
        # check if we can stash in current act
        if self._acts[curr_act].can_stash():
            new_loc = self._acts[curr_act].open_stash(curr_loc)
            if not new_loc: return False, False
            wait(1.0)
            items = personal.stash_all_items(items)
            return new_loc, items
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False, False
        new_loc = self._acts[Location.A5_TOWN_START].open_stash(new_loc)
        if not new_loc: return False, False
        wait(1.0)
        items = personal.stash_all_items(items)
        return new_loc, items

    def repair(self, curr_loc: Location, items: list = None):
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False, False
        # check if we can rapair in current act
        if self._acts[curr_act].can_trade_and_repair():
            new_loc = self._acts[curr_act].open_trade_and_repair_menu(curr_loc)
            if not new_loc: return False, False
            if items:
                items = personal.transfer_items(items, "sell")
            vendor.repair()
            wait(0.1, 0.2)
            common.close()
            return new_loc, items
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False, False
        new_loc = self._acts[Location.A5_TOWN_START].open_trade_and_repair_menu(new_loc)
        if not new_loc: return False, False
        if items:
            items = personal.transfer_items(items, "sell")
        vendor.repair()
        wait(0.1, 0.2)
        common.close()
        return new_loc, items

# Test: Move to desired location in d2r and run any town action you want to test from there
if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")
    from char.hammerdin import Hammerdin
    from pather import Pather
    pather = Pather()
    char = Hammerdin(Config().hammerdin, Config().char, pather)
    a5 = A5(pather, char)
    a4 = A4(pather, char)
    a3 = A3(pather, char)
    a2 = A2(pather, char)
    a1 = A1(pather, char)
    town_manager = TownManager(a1, a2, a3, a4, a5)
    print(town_manager.identify(Location.A3_TOWN_START))
