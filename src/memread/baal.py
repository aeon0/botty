from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from memread.mem_pather import MemPather
from town.town_manager import TownManager
from ui import waypoint
from utils.misc import wait
import time


class Baal:
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
        Logger.info("Run Baal")
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Baal requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if waypoint.use_wp("Worldstone Keep Level 2"):
            return Location.A5_BAAL_WORLDSTONE_KEEP_LVL2
        return False

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not MemPather().wait_for_location("TheWorldStoneKeepLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()
        if not MemPather().traverse("Worldstone Keep Level 3", self._char): return False
        if not MemPather().go_to_area("Worldstone Keep Level 3", "TheWorldStoneKeepLevel3"): return False
        if not MemPather().traverse("Throne of Destruction", self._char): return False
        if not MemPather().go_to_area("Throne of Destruction", "ThroneOfDestruction"): return False
        # Attacks start: Clear room
        if not MemPather().traverse((95, 55), self._char): return False
        for _ in range(4):
            if not self._char.clear_throne(full=True): return False
            if not MemPather().traverse((95, 45), self._char): return False
        start_time = time.time()
        picked_up_items = self._pickit.pick_up_items(self._char)

        wave_monsters = [
            "WarpedFallen", "WarpedShaman",
            "BaalSubjectMummy", "BaalColdMage",
            "CouncilMember",
            "VenomLord",
            "BaalsMinion"
        ]
        for wave_nr in range(5):
            wave_nr += 1
            Logger.info(f"Baal Wave: {wave_nr}")
            success, found_monsters = self._char.baal_idle(monster_filter=wave_monsters, start_time=start_time)
            if not success: return False
            if not self._char.clear_throne(monster_filter=wave_monsters): return False
            self._char.clear_throne()
            start_time = time.time()
            if wave_nr == 2 or wave_nr == 5:
                picked_up_items |= self._pickit.pick_up_items(self._char)
            elif wave_nr == 3:
                if not MemPather().traverse((95, 42), self._char): return False
                self._char.pre_buff()
            if "BaalsMinion" in found_monsters:
                Logger.debug("Finished last baal wave, go to throne")
                break

        # Pick items
        if not MemPather().traverse((95, 26), self._char): return False
        picked_up_items |= self._pickit.pick_up_items(self._char)
        # Move to baal room
        if not MemPather().traverse((91, 15), self._char): return False
        if not MemPather().go_to_area((15089, 5006), "TheWorldstoneChamber"): return False
        self._char.select_skill("teleport")
        if not MemPather().traverse((136, 176), self._char, do_pre_move=False): return False
        self._char.kill_baal()
        picked_up_items |= self._pickit.pick_up_items(self._char)
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
    game_stats = GameStats()
    bot = Bot(game_stats)
    self = bot._baal
    # self._go_to_area((15089, 5006), "TheWorldstoneChamber")
    # self._char.kill_baal()
    self._char.clear_throne(monster_filter=["BaalSubjectMummy", "BaalColdMage"])
    # while 1:
    #     data = self._api.get_data()
    #     if data is not None:
    #         print(data["player_pos_area"])
    #     print("-----")
    #     time.sleep(0.5)
