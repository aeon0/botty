from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from api.mapassist import MapAssistApi
from pather_v2 import PatherV2
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait, is_in_roi
from utils.custom_mouse import mouse
from screen import Screen
import time


class Baal:
    def __init__(
        self,
        screen: Screen,
        pather: Pather,
        town_manager: TownManager,
        ui_manager: UiManager,
        char: IChar,
        pickit: PickIt,
        api: MapAssistApi,
        pather_v2: PatherV2,
    ):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        self._api = api
        self._pather_v2 = pather_v2

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Baal")
        if not self._char.can_teleport():
            raise ValueError("Baal requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(5, 8): # use Halls of Pain Waypoint (5th in A5)
            return Location.A5_BAAL_WORLDSTONE_KEEP_LVL2
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather_v2.wait_for_location("TheWorldStoneKeepLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()
        if not self._pather_v2.traverse("Worldstone Keep Level 3", self._char): return False
        if not self._pather_v2.go_to_area("Worldstone Keep Level 3", "TheWorldStoneKeepLevel3"): return False
        if not self._pather_v2.traverse("Throne of Destruction", self._char): return False
        if not self._pather_v2.go_to_area("Throne of Destruction", "ThroneOfDestruction"): return False
        # Attacks start: Clear room
        if not self._pather_v2.traverse((95, 55), self._char): return False
        for _ in range(4):
            if not self._char.clear_throne(full=True): return False
            if not self._pather_v2.traverse((95, 45), self._char): return False
        start_time = time.time()
        picked_up_items = self._pickit.pick_up_items(self._char)
        # Wave 1
        wave1 = ["WarpedFallen", "WarpedShaman"]
        self._char.baal_idle(monster_filter=wave1, start_time=start_time)
        if not self._char.clear_throne(monster_filter=wave1): return False
        self._char.clear_throne()
        start_time = time.time()
        # Wave 2
        wave2 = ["BaalSubjectMummy", "BaalColdMage"]
        self._char.baal_idle(monster_filter=wave2, start_time=start_time)
        if not self._char.clear_throne(monster_filter=wave2): return False
        self._char.clear_throne()
        start_time = time.time()
        picked_up_items = self._pickit.pick_up_items(self._char)
        # Wave 3
        wave3 = ["CouncilMember"]
        self._char.baal_idle(monster_filter=wave3, start_time=start_time)
        if not self._char.clear_throne(monster_filter=wave3): return False
        self._char.clear_throne()
        start_time = time.time()
        # one more pre buff
        if not self._pather_v2.traverse((95, 38), self._char): return False
        self._char.pre_buff()
        # Wave 4
        wave4 = ["VenomLord"]
        self._char.baal_idle(monster_filter=wave4, start_time=start_time)
        if not self._char.clear_throne(monster_filter=wave4): return False
        self._char.clear_throne()
        start_time = time.time()
        # Wave 5
        wave5 = ["BaalsMinion"]
        self._char.baal_idle(monster_filter=wave5, start_time=start_time)
        if not self._char.clear_throne(monster_filter=wave5): return False
        self._char.clear_throne()
        picked_up_items = self._pickit.pick_up_items(self._char)
        # Pick items
        if not self._pather_v2.traverse((95, 26), self._char): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        # Move to baal room
        if not self._pather_v2.traverse((91, 15), self._char): return False
        if not self._pather_v2.go_to_area((15089, 5006), "TheWorldstoneChamber"): return False
        self._char.select_skill("teleport")
        if not self._pather_v2.traverse((136, 176), self._char, do_pre_move=False): return False
        self._char.kill_baal()
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A5_BAAL_WORLDSTONE_CHAMBER, picked_up_items)


if __name__ == "__main__":
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    config = Config()
    screen = Screen(config.general["monitor"])
    game_stats = GameStats()
    bot = Bot(screen, game_stats)
    self = bot._baal
    # self._go_to_area((15089, 5006), "TheWorldstoneChamber")
    # self._char.kill_baal()
    self._char.clear_throne(monster_filter=["unraveler", "skmage"])
    # while 1:
    #     data = self._api.get_data()
    #     if data is not None:
    #         print(data["player_pos_area"])
    #     print("-----")
    #     time.sleep(0.5)
