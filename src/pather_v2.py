import cv2
import numpy as np
import pyastar2d
from copy import deepcopy
import math
import time
from typing import Union
import random

from api.mapassist import MapAssistApi
from char import IChar
from screen import Screen
from config import Config
from utils.misc import is_in_roi
from utils.custom_mouse import mouse
from logger import Logger


class PatherV2:
    def __init__(self, screen: Screen, api: MapAssistApi):
        self._api = api
        self._screen = screen
        self._config = Config()
        self._range_x = [-self._config.ui_pos["center_x"] + 7, self._config.ui_pos["center_x"] - 7]
        self._range_y = [-self._config.ui_pos["center_y"] + 7, self._config.ui_pos["center_y"] - self._config.ui_pos["skill_bar_height"] - 33]

    def _adjust_abs_range_to_screen(self, abs_pos: tuple[float, float]) -> tuple[float, float]:
        """
        Adjust an absolute coordinate so it will not go out of screen or click on any ui which will not move the char
        :param abs_pos: Absolute position of the desired position to move to
        :return: Absolute position of a valid position that can be clicked on
        """
        f = 1.0
        # Check for x-range
        if abs_pos[0] > self._range_x[1]:
            f = min(f, abs(self._range_x[1] / float(abs_pos[0])))
        elif abs_pos[0] < self._range_x[0]:
            f = min(f, abs(self._range_x[0] / float(abs_pos[0])))
        # Check y-range
        if abs_pos[1] > self._range_y[1]:
            f = min(f, abs(self._range_y[1] / float(abs_pos[1])))
        if abs_pos[1] < self._range_y[0]:
            f = min(f, abs(self._range_y[0] / float(abs_pos[1])))
        # Scale the position by the factor f
        if f < 1.0:
            abs_pos = (int(abs_pos[0] * f), int(abs_pos[1] * f))
        # Check if adjusted position is "inside globe"
        screen_pos = self._screen.convert_abs_to_screen(abs_pos)
        if is_in_roi(self._config.ui_roi["mana_globe"], screen_pos) or is_in_roi(self._config.ui_roi["health_globe"], screen_pos):
            # convert any of health or mana roi top coordinate to abs (x-coordinate is just a dummy 0 value)
            new_range_y_bottom = self._screen.convert_screen_to_abs((0, self._config.ui_roi["mana_globe"][1]))[1]
            f = abs(new_range_y_bottom / float(abs_pos[1]))
            abs_pos = (int(abs_pos[0] * f), int(abs_pos[1] * f))
        # Check if clicking on merc img
        screen_pos = self._screen.convert_abs_to_screen(abs_pos)
        if is_in_roi(self._config.ui_roi["merc_icon"], screen_pos):
            width = self._config.ui_roi["merc_icon"][2]
            height = self._config.ui_roi["merc_icon"][3]
            w_abs, h_abs = self._screen.convert_screen_to_abs((width, height))
            fw = abs(w_abs / float(abs_pos[0]))
            fh = abs(h_abs / float(abs_pos[1]))
            f = max(fw, fh)
            abs_pos = (int(abs_pos[0] * f), int(abs_pos[1] * f))
        return abs_pos

    def go_to_area(self, poi: Union[tuple[int, int], str], end_loc: str, entrance_in_wall: bool = True) -> bool:
        start = time.time()
        while time.time() - start < 20:
            data = self._api.get_data()
            if data is not None:
                pos_monitor = None
                if type(poi) == str:
                    for p in data["poi"]:
                        if p["label"].startswith(poi):
                            # find the gradient for the grid position and move one back
                            if entrance_in_wall:
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

    # end can be any of:
    # Worldstone Keep Level 3
    # Throne of Destruction
    # Worldstone Chamber
    def traverse(self, end: Union[str, tuple[int, int]], char: IChar, randomize: int = 0):
        Logger.debug(f"Traverse to {end}")
        char.pre_move()
        tmp_duration = char._cast_duration
        char._cast_duration = 0.2
        last_pos = None
        repeated_pos_count = 0
        reached_destination = 2
        while 1:
            data = self._api.get_data()
            if data is not None and "map" in data and data["map"] is not None:
                player_pos_area = np.array((int(data["player_pos_area"][0]), int(data["player_pos_area"][1])))
                if last_pos is not None and np.array_equal(player_pos_area, last_pos):
                    repeated_pos_count += 1
                    if repeated_pos_count == 2:
                        Logger.debug("Increasing end point reached range")
                        reached_destination += 5
                    elif repeated_pos_count > 4:
                        Logger.warning("Got stuck during pathing")
                        return False
                last_pos = player_pos_area
                # Get worldstone keep area 3 entrance
                map_pos = None
                if type(end) is str:
                    for p in data["poi"]:
                        if p["label"].startswith(end):
                            map_pos = p["position"] - data["area_origin"]
                else:
                    map_pos = end
                if map_pos is None:
                    Logger.warning(f"Couldnt find endpoint: {end}")
                    char._cast_duration = tmp_duration
                    return False
                # Check if we are alredy close to our position
                diff = player_pos_area - map_pos
                if abs(diff[0]) <= reached_destination and abs(diff[1]) <= reached_destination:
                    char._cast_duration = tmp_duration
                    return True
                # Calc route from player to entrance
                weighted_map = deepcopy(data["map"])
                weighted_map = weighted_map.astype(np.float32)
                weighted_map[weighted_map == 0] = np.inf
                weighted_map[weighted_map == 1] = 1
                start_pos = np.array([player_pos_area[1], player_pos_area[0]])
                end_pos = np.array([map_pos[1], map_pos[0]])
                weighted_map[end_pos[0]][end_pos[1]] = 1
                route = pyastar2d.astar_path(weighted_map, start_pos, end_pos, allow_diagonal=False)
                if route is None:
                    Logger.warning("Could not calculate route")
                    char._cast_duration = tmp_duration
                    return False
                for r in reversed(route):
                    dist = math.dist([r[1], r[0]], player_pos_area)
                    if dist < 29:
                        # check if it is in screen
                        world_r = np.array([r[1], r[0]]) + data["area_origin"]
                        sc = self._api.world_to_abs_screen(world_r)
                        if -630 < sc[0] < 630 and -360 < sc[1] < 360:
                            sc = self._adjust_abs_range_to_screen(sc)
                            move_to = self._screen.convert_abs_to_monitor(sc)
                            move_to = (move_to[0] + random.randint(-randomize, +randomize), move_to[1] + random.randint(-randomize, +randomize))
                            char.move(move_to)
                            break
            time.sleep(0.05)

    def wait_for_location(self, name) -> bool:
        start = time.time()
        while time.time() - start < 20:
            data = self._api.get_data()
            if data is not None and data["current_area"] == name:
                return True
            time.sleep(0.2)
        return False


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
    
    api = MapAssistApi()
    pather_v2 = PatherV2(screen, api)
    pather_v2.traverse("Worldstone Keep Level 3", bot._char)
    # print(pather_v2.wait_for_location("TheWorldStoneKeepLevel2"))
