"""
Has to be used alongside this mapassist branch: https://github.com/aeon0/MapAssist/tree/feat/api
"""
import requests
import time
from requests.exceptions import ConnectionError
import cv2
import numpy as np
import pyastar2d
from copy import deepcopy
import math


def translation_matrix(tx, ty):
    return np.transpose(np.array([
        [1.0, 0.0,  tx],
        [0.0, 1.0,  ty],
        [0.0, 0.0, 1.0]
    ]))

def rotation_matrix(a):
    return np.transpose(np.array([
        [np.cos(a), -np.sin(a), 0.0],
        [np.sin(a),  np.cos(a), 0.0],
        [      0.0,        0.0, 1.0]
    ]))

def scaling_matrix(sx, sy):
    return np.transpose(np.array([
        [ sx, 0.0, 0.0],
        [0.0,  sy, 0.0],
        [0.0, 0.0, 1.0]
    ]))

class MapAssistApi:
    def __init__(self):
        self._transform_matrix = None

    def update_transform_matrix(self, player_pos):
        angle = np.deg2rad(45)
        tm_p = translation_matrix(-player_pos[0], -player_pos[1])
        rm = rotation_matrix(angle)
        scalem = scaling_matrix(27, 13.5)
        self._transform_matrix = tm_p @ rm @ scalem
        self._transform_matrix = np.transpose(self._transform_matrix)
        self._inv_transform_matrix = np.linalg.inv(self._transform_matrix)

    def world_to_abs_screen(self, world_pos):
        cp = np.array([world_pos[0], world_pos[1], 1.0])
        res = self._transform_matrix @ cp
        res = np.transpose(res)
        res = np.array([int(res[0] / res[2]), int(res[1] / res[2])])
        return res

    def abs_screen_to_world(self, abs_screen_pos):
        cp = np.array([abs_screen_pos[0], abs_screen_pos[1], 1.0])
        res = self._inv_transform_matrix @ cp
        res = np.transpose(res)
        res = np.array([int(res[0] / res[2]), int(res[1] / res[2])])
        return res

    def get_data(self) -> dict:
        try:
            botty_data = {
                "monsters": [],
                "poi": [],
                "map": None,
                "player_pos_world": None,
                "area_origin": None,
            }
            resp = requests.post("http://localhost:1111/get_data")
            data = resp.json()
            if data["success"] == True:
                botty_data["map"] = np.array(data["collision_grid"])
                botty_data["map"][botty_data["map"] == 1] = 0
                botty_data["map"] += 1
                botty_data["area_origin"] = np.array([int(data["area_origin"]["X"]), int(data["area_origin"]["Y"])])
                botty_data["player_pos_world"] = np.array([data["player_pos"]["X"], data["player_pos"]["Y"]])
                botty_data["player_pos_area"] = botty_data["player_pos_world"] - botty_data["area_origin"]
                self.update_transform_matrix(botty_data["player_pos_world"])
                for monster in data["monsters"]:
                    world_pos = np.array([monster["position"]["X"], monster["position"]["Y"]])
                    abs_pos = self.world_to_abs_screen(world_pos)
                    monster["position"] = abs_pos
                    botty_data["monsters"].append(monster)
                for p in data["points_of_interest"]:
                    p["position"] = np.array([int(p["position"]["X"]), int(p["position"]["Y"])])
                    botty_data["poi"].append(p)
            return botty_data
        except ConnectionError as e:
            return None


if __name__ == "__main__":
    from screen import Screen
    screen = Screen(1)
    api = MapAssistApi()
    while 1:
        img = screen.grab().copy()
        data = api.get_data()
        map_img = None
        if data is not None:
            for monster in data["monsters"]:
                screen_pos = screen.convert_abs_to_screen(monster["position"])
                top_left = (int(screen_pos[0] - 30), int(screen_pos[1] - 100))
                bottom_right = (int(screen_pos[0] + 30), int(screen_pos[1]))
                cv2.circle(img, (int(screen_pos[0]), int(screen_pos[1])), 4, (0, 255, 0), 2)
                cv2.rectangle(img, top_left, bottom_right, (0, 0, 255), 2)

            if data["map"] is not None:
                map_img = deepcopy(data["map"])
                map_img[map_img == 1] = 255
                map_img = map_img.astype(np.uint8)
                map_img = cv2.cvtColor(map_img, cv2.COLOR_GRAY2BGR)
                player_pos_area = np.array((int(data["player_pos_area"][0]), int(data["player_pos_area"][1])))
                cv2.circle(map_img, player_pos_area, 3, (0, 255, 0), 2)
                # viewport area of screen
                top_left = api.abs_screen_to_world([-630, -360]) - data["area_origin"]
                top_right = api.abs_screen_to_world([630, -360]) - data["area_origin"]
                bottom_right = api.abs_screen_to_world([630, 260]) - data["area_origin"]
                bottom_left = api.abs_screen_to_world([-630, 260]) - data["area_origin"]
                cv2.line(map_img, top_left, top_right, (0, 0, 255), 1)
                cv2.line(map_img, top_right, bottom_right, (0, 0, 255), 1)
                cv2.line(map_img, bottom_right, bottom_left, (0, 0, 255), 1)
                cv2.line(map_img, bottom_left, top_left, (0, 0, 255), 1)
                d1 = math.dist(player_pos_area, top_left)
                d2 = math.dist(player_pos_area, top_right)
                d3 = math.dist(player_pos_area, bottom_right)
                d4 = math.dist(player_pos_area, bottom_left)
                # Get worldstone keep area 3 entrance
                for p in data["poi"]:
                    if p["label"].startswith("Worldstone Keep Level 3"):
                        map_pos = p["position"] - data["area_origin"]
                        cv2.circle(map_img, map_pos, 3, (255, 0, 0), 2)
                        # Calc route from player to entrance
                        start = time.time()
                        weighted_map = deepcopy(data["map"])
                        weighted_map = weighted_map.astype(np.float32)
                        weighted_map[weighted_map == 0] = np.inf
                        weighted_map[weighted_map == 1] = 1
                        start_pos = np.array([player_pos_area[1], player_pos_area[0]])
                        end_pos = np.array([map_pos[1], map_pos[0] + 1])
                        x1 = weighted_map[start_pos[0]][start_pos[1]]
                        x2 = weighted_map[end_pos[0]][end_pos[1]]
                        route = pyastar2d.astar_path(weighted_map, start_pos, end_pos, allow_diagonal=False)
                        if route is not None:
                            for r in route:
                                map_img[int(r[0])][int(r[1])] = (244, 0, 255)
                            for r in reversed(route):
                                dist = math.dist([r[1], r[0]], player_pos_area)
                                if dist < 29:
                                    # check if it is in screen
                                    world_r = np.array([r[1], r[0]]) + data["area_origin"]
                                    sc = api.world_to_abs_screen(world_r)
                                    if -630 < sc[0] < 630 and -360 < sc[1] < 260:
                                        cv2.circle(map_img, (r[1], r[0]), 3, (255, 190, 0), 2)
                                        cv2.circle(img, (sc[0] + 640, sc[1] + 360), 5, (255, 190, 0), 3)
                                        break
                        print(time.time() - start)
        time.sleep(0.05)
        cv2.imshow("t", img)
        if map_img is not None:
            cv2.imshow("map", map_img)
        cv2.waitKey(1)
