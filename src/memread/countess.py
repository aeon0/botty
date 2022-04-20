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


class Countess:
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
        Logger.info("Run Countess")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Countess requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if waypoint.use_wp("Black Marsh"):
          Logger.debug("Waipont taken to countess")
          return Location.A1_COUNTESS_START
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not MemPather().wait_for_location("BlackMarsh"): return False
        if do_pre_buff:
            self._char.pre_buff()
        if not MemPather().traverse("Forgotten Tower", self._char): return False
        if not MemPather().go_to_area("Forgotten Tower", "ForgottenTower", entrance_in_wall=False): return False
        # if not MemPather().traverse("Tower Cellar Level 1 (75)", self._char): return False
        if not MemPather().go_to_area("Tower Cellar Level 1", "TowerCellarLevel1", entrance_in_wall=True): return False
        if not MemPather().traverse("Tower Cellar Level 2", self._char): return False
        if not MemPather().go_to_area("Tower Cellar Level 2", "TowerCellarLevel2", entrance_in_wall=False): return False
        if not MemPather().traverse("Tower Cellar Level 3", self._char): return False
        if not MemPather().go_to_area("Tower Cellar Level 3", "TowerCellarLevel3", entrance_in_wall=False): return False
        if not MemPather().traverse("Tower Cellar Level 4", self._char): return False
        if not MemPather().go_to_area("Tower Cellar Level 4", "TowerCellarLevel4", entrance_in_wall=False): return False
        if not MemPather().traverse("Tower Cellar Level 5", self._char): return False
        if not MemPather().go_to_area("Tower Cellar Level 5", "TowerCellarLevel5", entrance_in_wall=False): return False
        if not MemPather().traverse("GoodChest",self._char): return False
        if not self._char.kill_countess(): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A1_COUNTESS_END, picked_up_items)

if __name__ == "__main__":
    from memread.mapassist import MapAssistApi
    import keyboard
    import os
    from char.capabilities import CharacterCapabilities
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from bot import Bot
    from config import Config
    from game_stats import GameStats
    config = Config()
    game_stats = GameStats()
    bot = Bot(game_stats)
    self = bot._countess
    bot._char.capabilities = CharacterCapabilities(can_teleport_natively=True, can_teleport_with_charges=False)
    self.battle(True)
    while 1:
        data = MapAssistApi().get_data()
        if data is not None:
            print(data["player_pos_area"])
        print("-----")
        time.sleep(0.5)
