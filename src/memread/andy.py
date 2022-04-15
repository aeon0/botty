from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from memread.mem_pather import MemPather
from town.town_manager import TownManager
from utils.misc import wait
from ui import waypoint
import time


class Andy:
    def __init__(
        self,
        pather: Pather,
        town_manager: TownManager,
        char: IChar,
        pickit: PickIt
    ):
        self._pather = pather
        self._town_manager = town_manager
        self._char = char
        self._pickit = pickit

    def approach(self, start_loc: Location) -> Union[bool, Location, bool]:
        Logger.info("Run Andy")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Andy requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if waypoint.use_wp("Catacombs Level 2"):
            return Location.A1_ANDY_START
        return False

    # "Catacombs Level 3"
    # CatacombsLevel1
    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not MemPather().wait_for_location("CatacombsLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()
        if not MemPather().traverse("Catacombs Level 3", self._char): return False
        if not MemPather().go_to_area("Catacombs Level 3", "CatacombsLevel3", entrance_in_wall=False): return False
        if not MemPather().traverse("Catacombs Level 4", self._char): return False
        if not MemPather().go_to_area("Catacombs Level 4", "CatacombsLevel4", entrance_in_wall=False): return False
        if not MemPather().traverse((63, 88), self._char): return False
        self._char.kill_andy()
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A1_ANDY_END, picked_up_items)


if __name__ == "__main__":
    from memread.mapassist import MapAssistApi
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    config = Config()
    game_stats = GameStats()
    bot = Bot(game_stats)
    self = bot._andy
    while 1:
        data = MapAssistApi().get_data()
        if data is not None:
            print(data["player_pos_area"])
        print("-----")
        time.sleep(0.5)
