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


class Andy:
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
        Logger.info("Run Andy")
        if not self._char.can_teleport():
            raise ValueError("Andy requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        if self._ui_manager.use_wp(1, 8):
            return Location.A1_ANDY_START
        return False

    # "Catacombs Level 3"
    # CatacombsLevel1
    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather_v2.wait_for_location("CatacombsLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()
        if not self._pather_v2.traverse("Catacombs Level 3", self._char): return False
        if not self._pather_v2.go_to_area("Catacombs Level 3", "CatacombsLevel3", entrance_in_wall=False): return False
        if not self._pather_v2.traverse("Catacombs Level 4", self._char): return False
        if not self._pather_v2.go_to_area("Catacombs Level 4", "CatacombsLevel4", entrance_in_wall=False): return False
        if not self._pather_v2.traverse((64, 84), self._char): return False
        self._char.kill_andy(self._api, self._pather_v2)
        picked_up_items = self._pickit.pick_up_items(self._char)
        return (Location.A1_ANDY_END, picked_up_items)


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
    self = bot._andy
    while 1:
        data = self._api.get_data()
        if data is not None:
            print(data["player_pos_area"])
        print("-----")
        time.sleep(0.5)
