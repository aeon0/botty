"""
Has to be used alongside this mapassist branch: https://github.com/aeon0/MapAssist/tree/feat/api
"""
import requests
import time
from requests.exceptions import ConnectionError
import cv2
import numpy as np


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
                "map": None,
                "player_pos_world": None,
                "area_origin": None,
            }
            resp = requests.post("http://localhost:1111/get_data")
            data = resp.json()
            if data["success"] == True:
                botty_data["map"] = np.array(data["collision_grid"])
                botty_data["area_origin"] = np.array([int(data["area_origin"]["X"]), int(data["area_origin"]["Y"])])
                botty_data["player_pos_world"] = np.array([data["player_pos"]["X"], data["player_pos"]["Y"]])
                botty_data["player_pos_area"] = botty_data["player_pos_world"] - botty_data["area_origin"]
                self.update_transform_matrix(botty_data["player_pos_world"])
                for monster in data["monsters"]:
                    world_pos = np.array([monster["position"]["X"], monster["position"]["Y"]])
                    abs_pos = self.world_to_abs_screen(world_pos)
                    monster["position"] = abs_pos
                    botty_data["monsters"].append(monster)
            return botty_data
        except ConnectionError as e:
            return None


if __name__ == "__main__":
    from screen import Screen
    screen = Screen(1)
    api = MapAssistApi()
    while 1:
        print("-")
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
                print(data["player_pos_area"])
                map_img = data["map"][:,:]
                map_img[map_img == -1] = 255
                map_img = map_img.astype(np.uint8)
                map_img = cv2.cvtColor(map_img, cv2.COLOR_GRAY2BGR)
                p = (int(data["player_pos_area"][0]), int(data["player_pos_area"][1]))
                cv2.circle(map_img, p, 3, (0, 255, 0), 2)
                # viewport area of screen
                top_left = api.abs_screen_to_world([-640, -360]) - data["area_origin"]
                top_right = api.abs_screen_to_world([640, -360]) - data["area_origin"]
                bottom_right = api.abs_screen_to_world([640, 360]) - data["area_origin"]
                bottom_left = api.abs_screen_to_world([-640, 360]) - data["area_origin"]
                cv2.line(map_img, top_left, top_right, (0, 0, 255), 2)
                cv2.line(map_img, top_right, bottom_right, (0, 0, 255), 2)
                cv2.line(map_img, bottom_right, bottom_left, (0, 0, 255), 2)
                cv2.line(map_img, bottom_left, top_left, (0, 0, 255), 2)

        time.sleep(0.1)
        cv2.imshow("t", img)
        if map_img is not None:
            cv2.imshow("map", map_img)
        cv2.waitKey(1)
