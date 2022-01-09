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
        pickit: PickIt
    ):
        self._config = Config()
        self._screen = screen
        self._pather = pather
        self._town_manager = town_manager
        self._ui_manager = ui_manager
        self._char = char
        self._pickit = pickit
        # memory reading
        self._api = MapAssistApi()
        self._pather_v2 = PatherV2(screen, self._api)

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

    def _go_to_area(self, poi: Union[tuple[int, int], str], end_loc: str):
        start = time.time()
        while time.time() - start < 20:
            data = self._api.get_data()
            if data is not None:
                pos_monitor = None
                if type(poi) == str:
                    for p in data["poi"]:
                        if p["label"].startswith(poi):
                            # find the gradient for the grid position and move one back
                            ap = p["position"] - data["area_origin"]
                            if data["map"][ap[1] - 1][ap[0]] == 1:
                                ap = [p["position"][0], p["position"][1] + 2]
                            elif data["map"][ap[1] + 1][ap[0]] == 1:
                                ap = [p["position"][0], p["position"][1] - 2]
                            elif data["map"][ap[1]][ap[0] - 1] == 1:
                                ap = [p["position"][0] + 2, p["position"][1]]
                            elif data["map"][ap[1]][ap[0] + 1] == 1:
                                ap = [p["position"][0] - 2, p["position"][1]]
                            else:
                                ap = p["position"]
                            pos_monitor = self._api.world_to_abs_screen(ap)
                            if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                                pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)
                            else:
                                pos_monitor = None
                else:
                    pos_monitor = self._api.world_to_abs_screen(poi)
                    if -640 < pos_monitor[0] < 640 and -360 < pos_monitor[1] < 360:
                        pos_monitor = self._screen.convert_abs_to_monitor(pos_monitor)
                    else:
                        pos_monitor = None
                if pos_monitor is not None:
                    mouse.move(*pos_monitor)
                    time.sleep(0.1)
                    mouse.click("left")
                if data["current_area"] == end_loc:
                    return True
        return False

    def _wait_for_monsters(self, monster_filter = None):
        Logger.info(f"Wait for Wave: {monster_filter}")
        throne_area = [70, 0, 50, 85]
        while 1:
            data = self._api.get_data()
            if data is not None:
                 for m in data["monsters"]:
                    area_pos = m["position"] - data["area_origin"]
                    proceed = True
                    if monster_filter is not None:
                        proceed = any(m["name"].startswith(startstr) for startstr in monster_filter)
                    if is_in_roi(throne_area, area_pos) and proceed:
                        Logger.info("Found wave, attack")
                        return
            time.sleep(0.2)

    def battle(self, do_pre_buff: bool) -> Union[bool, tuple[Location, bool]]:
        if not self._pather_v2.wait_for_location("TheWorldStoneKeepLevel2"): return False
        if do_pre_buff:
            self._char.pre_buff()
        if not self._pather_v2.traverse("Worldstone Keep Level 3", self._char): return False
        if not self._go_to_area("Worldstone Keep Level 3", "TheWorldStoneKeepLevel3"): return False
        if not self._pather_v2.traverse("Throne of Destruction", self._char): return False
        if not self._go_to_area("Throne of Destruction", "ThroneOfDestruction"): return False
        # Attacks start: Clear room
        if not self._pather_v2.traverse((95, 55), self._char): return False
        if not self._char.clear_throne(self._api, self._pather_v2, full=True): return False
        if not self._pather_v2.traverse((95, 45), self._char): return False
        # Wave 1
        wave1 = ["fallen", "fallenshaman"]
        self._wait_for_monsters(monster_filter=wave1)
        if not self._char.clear_throne(self._api, self._pather_v2, monster_filter=wave1): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        if not self._pather_v2.traverse((95, 45), self._char): return False
        # Wave 2
        wave2 = ["unraveler", "skmage"]
        self._wait_for_monsters(monster_filter=wave2)
        if not self._char.clear_throne(self._api, self._pather_v2, monster_filter=wave2): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        if not self._pather_v2.traverse((95, 45), self._char): return False
        # Wave 3
        wave3 = ["baalhighpriest"]
        self._wait_for_monsters(monster_filter=wave3)
        if not self._char.clear_throne(self._api, self._pather_v2, monster_filter=wave3): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        if not self._pather_v2.traverse((95, 45), self._char): return False
        # one more pre buff
        self._char.pre_buff()
        # Wave 4
        wave4 = ["venomlord"]
        self._wait_for_monsters(monster_filter=wave4)
        if not self._char.clear_throne(self._api, self._pather_v2, monster_filter=wave4): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        if not self._pather_v2.traverse((95, 45), self._char): return False
        # Wave 5
        wave5 = ["baalminion"]
        self._wait_for_monsters(monster_filter=wave5)
        if not self._char.clear_throne(self._api, self._pather_v2, monster_filter=wave5): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        # Pick items
        if not self._pather_v2.traverse((95, 39), self._char): return False
        picked_up_items = self._pickit.pick_up_items(self._char)
        # Move to baal room
        if not self._pather_v2.traverse((91, 15), self._char): return False
        if not self._go_to_area((15089, 5006), "TheWorldstoneChamber"): return False
        self._char.pre_move()
        if not self._pather_v2.traverse((136, 176), self._char): return False
        self._char.kill_baal(self._api, self._pather_v2)
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
    self._go_to_area((15089, 5006), "TheWorldstoneChamber")
    # self._char.kill_baal(self._api, self._pather_v2)
    # self._char.clear_throne(self._api, self._pather_v2, full=True)
    # while 1:
    #     data = self._api.get_data()
    #     if data is not None:
    #         print(data["player_pos_area"])
    #     print("-----")
    #     time.sleep(0.5)
