from typing import Union
from item import ItemFinder
from template_finder import TemplateFinder
from config import Config
from pather import Location
from logger import Logger
from ui import UiManager
from town import IAct, A3, A4, A5
from utils.misc import wait


class TownManager:
    def __init__(self, template_finder: TemplateFinder, ui_manager: UiManager, item_finder: ItemFinder, a3: A3, a4: A4, a5: A5):
        self._config = Config()
        self._template_finder = template_finder
        self._ui_manager = ui_manager
        self._item_finder = item_finder
        self._acts: dict[Location, IAct] = {
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
        return location

    def wait_for_town_spawn(self, time_out: float = None) -> Location:
        """Wait for the char to spawn in town after starting a new game
        :param time_out: Optional float value for time out in seconds, defaults to None
        :return: Location of the town (e.g. Location.A4_TOWN_START) or None if nothing was found within time_out time
        """
        template_match = self._template_finder.search_and_wait([
            "A5_TOWN_0", "A5_TOWN_1",
            "A4_TOWN_4", "A4_TOWN_5",
            "A3_TOWN_0", "A3_TOWN_1"
        ], best_match=True, time_out=time_out)
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
        if act_idx == 3: act = Location.A3_TOWN_START
        elif act_idx == 4: act = Location.A4_TOWN_START
        elif act_idx == 5: act = Location.A5_TOWN_START
        else:
            Logger.error(f"Act {act_idx} is not supported")
            return False
        if curr_act == act:
            return curr_loc
        # if not, move to the desired act via waypoint
        if not self._acts[curr_act].open_wp(curr_loc): return False
        self._ui_manager.use_wp(act_idx, 0)
        return self._acts[act].get_wp_location()

    def heal(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can heal in current act
        if self._acts[curr_act].can_heal():
            return self._acts[curr_act].heal(curr_loc)
        Logger.warning(f"Could not heal in {curr_act}. Continue without healing")
        return curr_loc

    def resurrect(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can resurrect in current act
        if self._acts[curr_act].can_resurrect():
            return self._acts[curr_act].resurrect(curr_loc)
        new_loc = self.go_to_act(4, curr_loc)
        if not new_loc: return False
        return self._acts[Location.A4_TOWN_START].resurrect(new_loc)

    def stash(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can stash in current act
        if self._acts[curr_act].can_stash():
            new_loc = self._acts[curr_act].open_stash(curr_loc)
            if not new_loc: return False
            wait(1.0)
            self._ui_manager.stash_all_items(self._config.char["num_loot_columns"], self._item_finder)
            return new_loc
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False
        new_loc = self._acts[Location.A5_TOWN_START].open_stash(new_loc)
        if not new_loc: return False
        wait(1.0)
        self._ui_manager.stash_all_items(self._config.char["num_loot_columns"], self._item_finder)
        return new_loc

    def repair_and_fill_tps(self, curr_loc: Location) -> Union[Location, bool]:
        curr_act = TownManager.get_act_from_location(curr_loc)
        if curr_act is None: return False
        # check if we can rapair in current act
        if self._acts[curr_act].can_trade_and_repair():
            new_loc = self._acts[curr_act].open_trade_and_repair_menu(curr_loc)
            if not new_loc: return False
            if self._ui_manager.repair_and_fill_up_tp():
                wait(0.1, 0.2)
                self._ui_manager.close_vendor_screen()
                return new_loc
        new_loc = self.go_to_act(5, curr_loc)
        if not new_loc: return False
        new_loc = self._acts[Location.A5_TOWN_START].open_trade_and_repair_menu(new_loc)
        if not new_loc: return False
        if self._ui_manager.repair_and_fill_up_tp():
            wait(0.1, 0.2)
            self._ui_manager.close_vendor_screen()
            return new_loc
        return False


# Test: Move to desired location in d2r and run any town action you want to test from there
if __name__ == "__main__":
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")
    from char.hammerdin import Hammerdin
    from item import ItemFinder
    from pather import Pather
    from screen import Screen
    from npc_manager import NpcManager
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    npc_manager = NpcManager(screen, template_finder)
    pather = Pather(screen, template_finder)
    ui_manager = UiManager(screen, template_finder)
    item_finder = ItemFinder(config)
    char = Hammerdin(config.hammerdin, config.char, screen, template_finder, ui_manager, pather)
    a5 = A5(screen, template_finder, pather, char, npc_manager)
    a4 = A4(screen, template_finder, pather, char, npc_manager)
    a3 = A3(screen, template_finder, pather, char, npc_manager)
    town_manager = TownManager(template_finder, ui_manager, item_finder, a3, a4, a5)
    print(town_manager.stash(Location.A5_STASH))
