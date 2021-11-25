from char.i_char import IChar
from screen import Screen
from template_finder import TemplateFinder
from logger import Logger
from char.i_char import IChar
import math
import keyboard
import time
import os
import random
from typing import Tuple, List
import cv2
from config import Config
from utils.misc import wait, is_in_roi
import numpy as np


class Location:
    # A5 Town
    A5_TOWN_START = "a5_town_start"
    A5_STASH = "a5_stash"
    A5_WP = "a5_wp"
    QUAL_KEHK = "qual_kehk"
    MALAH = "malah"
    NIHLATHAK_PORTAL = "nihlathak_portal"
    LARZUK = "larzuk"
    # Pindle
    PINDLE_START = "pindle_start"
    PINDLE_SAVE_DIST = "pindle_save_dist"
    PINDLE_END = "pindle_end"
    # Eldritch
    ELDRITCH_START = "eldritch_start"
    ELDRITCH_SAVE_DIST = "eldritch_save_dist"
    ELDRITCH_END = "eldritch_end"
    # Shenk
    SHENK_START = "shenk_start"
    SHENK_SAVE_DIST = "shenk_save_dist"
    SHENK_END = "shenk_end"


class Pather:
    """
    Traverses 'dynamic' pathes with reference templates and relative coordinates or statically recorded pathes.
    Check utils/node_recorder.py to generate templates/refpoints and relative coordinates to nodes. Once you have refpoints and
    nodes you can specify in which order this nodes should be traversed in self._paths.
    """

    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._range_x = [-self._config.ui_pos["center_x"] + 10, self._config.ui_pos["center_x"] - 10]
        self._range_y = [-self._config.ui_pos["center_y"] + 10, self._config.ui_pos["center_y"] - self._config.ui_pos["skill_bar_height"] - 50]
        self._nodes = {
            # A5 town
            0: {"A5_TOWN_0": (110-70, 373), "A5_TOWN_1": (-68-70, -205)},
            1: {"A5_TOWN_0": (-466, 287), "A5_TOWN_1": (-644, -291), "A5_TOWN_0.5": (717, 349)},
            2: {"A5_TOWN_0": (-552, 42-100), "A5_TOWN_0.5": (659-25, 90+20-100)},
            3: {"A5_TOWN_1": (-414, 141), "A5_TOWN_2": (728, -90)},
            4: {"A5_TOWN_1": (-701, 400), "A5_TOWN_2": (440, 169), "A5_TOWN_3": (-400, -208), "A5_TOWN_4": (243, -244)},
            5: {"A5_TOWN_2": (555-100, 429-100), "A5_TOWN_3": (-285-100, 51-100), "A5_TOWN_4": (358-100, 15-100)},
            6: {"A5_TOWN_3": (-775-100, 382-120), "A5_TOWN_4": (-132-100, 346-120), "A5_TOWN_5": (80-100, -240-120), "A5_TOWN_6": (560-100, 211-120)},
            8: {"A5_TOWN_6": (190, 440), "A5_TOWN_5": (-323+30, 192-200), "A5_TOWN_7": (867+30, 69-200)},
            9: {"A5_TOWN_5": (-611, 250), "A5_TOWN_7": (579, 127)},
            10: {"A5_TOWN_4": (-708, 87), "A5_TOWN_6": (-16, -48), "A5_TOWN_8": (482, 196)},
            11: {"A5_TOWN_6": (-448, -322), "A5_TOWN_8": (50, -78), "A5_TOWN_9": (11, 346)},
            12: {"A5_TOWN_8": (-209, -294), "A5_TOWN_9": (-248, 130)},
            13: {"A5_TOWN_3": (180, 180),"A5_TOWN_10": (-800, 332), "A5_TOWN_4": (822, 146)},
            14: {"A5_TOWN_3": (670, 260), "A5_TOWN_10": (-300, 420)},
            # Pindle
            100: {"PINDLE_7": (576, -138), "PINDLE_0": (-146, -60), "PINDLE_1": (-19, 335), "PINDLE_2": (-549, 127)},
            101: {"PINDLE_1": (557, -68), "PINDLE_2": (27, -276), "PINDLE_3": (-185, 391)},
            102: {"PINDLE_3": (334, 132), "PINDLE_4": (142, 323)},
            103: {"PINDLE_3": (593, -113), "PINDLE_4": (401, 78)},
            104: {"PINDLE_4": (1076, -176), "PINDLE_3": (1264, -366), "PINDLE_5": (-280, 356), "PINDLE_6": (-700, 133)},
            # Eldritch
            120: {"ELDRITCH_0": (439, 36), "ELDRITCH_1": (-461, 114)},
            121: {"ELDRITCH_1": (-493, -155), "ELDRITCH_2": (616, 257), "ELDRITCH_3": (-137, 297)},
            122: {"ELDRITCH_2": (530, -218), "ELDRITCH_3": (-223, -178)},
            123: {"ELDRITCH_3": (-148, -498), "ELDRITCH_2": (604, -538), "ELDRITCH_4": (-163, -283)},
            # Shenk
            140: {"SHENK_0": (-224, -340), "SHENK_17": (-750, 353), "SHENK_15": (120, 20), "SHENK_1": (667, -242)},
            141: {"SHENK_0": (-194, 66), "SHENK_17": (-780, 792), "SHENK_15": (116, 440), "SHENK_1": (696, 161), "SHENK_2": (-251, -51)},
            142: {"SHENK_1": (876, 564), "SHENK_2": (-78, 352), "SHENK_3": (535, -194), "SHENK_4": (-665, -155)},
            143: {"SHENK_2": (212, 758),"SHENK_3": (823, 209), "SHENK_4": (-377, 248), "SHENK_6": (-508, -103)},
            144: {"SHENK_6": (-162, 185), "SHENK_7": (721, 226)},
            145: {"SHENK_12": (146, -200), "SHENK_7": (1204, 558), "SHENK_6": (314, 520), "SHENK_8": (-367, 27)},
            146: {"SHENK_12": (408, 166), "SHENK_9": (-497, -216), "SHENK_8": (-108, 387)},
            147: {"SHENK_16": (290, -150), "SHENK_9": (-100, 208), "SHENK_10": (-646, 100)},
            148: {"SHENK_16": (967, 95), "SHENK_9": (451, 395), "SHENK_10": (-97, 282), "SHENK_11": (-459, 208)},
            149: {"SHENK_11": (532, 602), "SHENK_10": (882, 682), "SHENK_13": (730, 36)},

        }
        self._paths = {
            # A5 Town
            (Location.A5_TOWN_START, Location.NIHLATHAK_PORTAL): [3, 4, 5, 6, 8, 9],
            (Location.A5_TOWN_START, Location.A5_STASH): [3, 4, 5],
            (Location.A5_TOWN_START, Location.A5_WP): [3, 4],
            (Location.A5_TOWN_START, Location.QUAL_KEHK): [3, 4, 5, 6, 10, 11, 12],
            (Location.A5_TOWN_START, Location.MALAH): [1, 2],
            (Location.A5_TOWN_START, Location.LARZUK): [3, 4, 5, 13, 14],
            (Location.MALAH, Location.A5_TOWN_START): [1, 0],
            (Location.A5_STASH, Location.NIHLATHAK_PORTAL): [6, 8, 9],
            (Location.A5_STASH, Location.QUAL_KEHK): [5, 6, 10, 11, 12],
            (Location.A5_STASH, Location.LARZUK): [13, 14],
            (Location.A5_STASH, Location.A5_WP): [],
            (Location.QUAL_KEHK, Location.NIHLATHAK_PORTAL): [12, 11, 10, 6, 8, 9],
            (Location.QUAL_KEHK, Location.A5_WP): [12, 11, 10, 6],
            (Location.LARZUK, Location.QUAL_KEHK): [13, 14, 5, 6, 10, 11, 12],
            (Location.LARZUK, Location.NIHLATHAK_PORTAL): [14, 13, 5, 6, 8, 9],
            (Location.LARZUK, Location.A5_WP): [14, 13, 5],
            # Pindle
            (Location.PINDLE_START, Location.PINDLE_SAVE_DIST): [100, 101, 102, 103],
            (Location.PINDLE_SAVE_DIST, Location.PINDLE_END): [104],
            # Eldritch
            (Location.ELDRITCH_START, Location.ELDRITCH_SAVE_DIST): [120, 121, 122],
            (Location.ELDRITCH_SAVE_DIST, Location.ELDRITCH_END): [123],
            # Shenk
            (Location.SHENK_START, Location.SHENK_SAVE_DIST): [140, 141, 142, 143, 144, 145, 146, 147, 148],
            (Location.SHENK_SAVE_DIST, Location.SHENK_END): [149],
        }

    def _get_scaled_node(self, key: int, template: str):
        return (
            int(self._nodes[key][template][0] * self._config.scale),
            int(self._nodes[key][template][1] * self._config.scale)
        )

    def _display_all_nodes_debug(self, filter: str = None):
        while 1:
            img = self._screen.grab()
            display_img = img.copy()
            template_map = {}
            for node_idx in self._nodes:
                for template_type in self._nodes[node_idx]:
                        if filter is None or filter in template_type:
                            if template_type in template_map:
                                success = True
                                ref_pos_screen = template_map[template_type]
                            else:
                                success, ref_pos_screen = self._template_finder.search(template_type, img)
                            if success:
                                template_map[template_type] = ref_pos_screen
                                # Get reference position of template in abs coordinates
                                ref_pos_abs = self._screen.convert_screen_to_abs(ref_pos_screen)
                                # Calc the abs node position with the relative coordinates (relative to ref)
                                node_pos_rel = self._get_scaled_node(node_idx, template_type)
                                node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                                node_pos_abs = self._adjust_abs_range_to_screen(node_pos_abs)
                                x, y = self._screen.convert_abs_to_screen(node_pos_abs)
                                cv2.circle(display_img, (x, y), 5, (255, 0, 0), 3)
                                cv2.putText(display_img, str(node_idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                                x, y = self._screen.convert_abs_to_screen(ref_pos_abs)
                                cv2.circle(display_img, (x, y), 5, (0, 255, 0), 3)
                                cv2.putText(display_img, template_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5)
            cv2.imshow("debug", display_img)
            cv2.waitKey(1)

    @staticmethod
    def _convert_rel_to_abs(rel_loc: Tuple[float, float], pos_abs: Tuple[float, float]) -> Tuple[float, float]:
        return (rel_loc[0] + pos_abs[0], rel_loc[1] + pos_abs[1])

    def traverse_nodes_fixed(self, key: str, char):
        path = self._config.path[key]
        for pos in path:
            x_m, y_m = self._screen.convert_screen_to_monitor(pos)
            x_m += int(random.random() * 6 - 3)
            y_m += int(random.random() * 6 - 3)
            char.move((x_m, y_m))

    def _adjust_abs_range_to_screen(self, abs_pos: Tuple[float, float]) -> Tuple[float, float]:
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
        return abs_pos

    def find_abs_node_pos(self, node_idx: int, img: np.ndarray) -> Tuple[float, float]:
        node = self._nodes[node_idx]
        for template_type in node:
            success, ref_pos_screen = self._template_finder.search(template_type, img)
            if success:
                # Get reference position of template in abs coordinates
                ref_pos_abs = self._screen.convert_screen_to_abs(ref_pos_screen)
                # Calc the abs node position with the relative coordinates (relative to ref)
                node_pos_rel = self._get_scaled_node(node_idx, template_type)
                node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                node_pos_abs = self._adjust_abs_range_to_screen(node_pos_abs)
                return node_pos_abs
        return None

    def traverse_nodes(self, start_location: Location, end_location: Location, char: IChar, time_out: float = 7, force_tp: bool = False) -> bool:
        """
        Traverse from one location to another
        :param start_location: Location the char is starting at
        :param end_location: Location the char is supposed to end up
        :param char: Char that is traversing the nodes
        :param time_out: Timeout in second. If no more move was found in that time it will cancel traverse
        :return: Bool if traversed succesfull or False if it got stuck
        """
        Logger.debug(f"Traverse from {start_location} to {end_location}")
        path = self._paths[(start_location, end_location)]
        for i, node_idx in enumerate(path):
            continue_to_next_node = False
            last_move = time.time()
            while not continue_to_next_node:
                img = self._screen.grab()
                if (time.time() - last_move) > time_out:
                    success, _ = self._template_finder.search("WAYPOINT_MENU", img)
                    if success:
                        # sometimes bot opens waypoint menu, close it to find templates again
                        Logger.debug("Opened wp, closing it again")
                        keyboard.send("esc")
                        last_move = time.time()
                    else:
                        # This is a bit hacky, but for moving into a boss location we set time_out usually quite low
                        # because of all the spells and monsters it often can not determine the final template
                        # Don't want to spam the log with errors in this case because it most likely worked out just fine
                        if time_out > 1.5:
                            if self._config.general["info_screenshots"]:
                                cv2.imwrite("./info_screenshots/info_pather_got_stuck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                            Logger.error("Got stuck exit pather")
                        return False
                node_pos_abs = self.find_abs_node_pos(node_idx, img)
                if node_pos_abs is not None:
                    dist = math.dist(node_pos_abs, (0, 0))
                    if dist < self._config.ui_pos["reached_node_dist"]:
                        continue_to_next_node = True
                    else:
                        # Move the char
                        x_m, y_m = self._screen.convert_abs_to_monitor(node_pos_abs)
                        char.move((x_m, y_m), force_tp=force_tp)
                        last_move = time.time()
        return True


# Testing: Move char to whatever Location to start and run
if __name__ == "__main__":
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char.sorceress import Sorceress
    from ui_manager import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)
    ui_manager = UiManager(screen, t_finder)
    char = Sorceress(config.sorceress, config.char, screen, t_finder, ui_manager, pather)
    # pather.traverse_nodes_fixed("pindle_save_dist", char)
    # pather.traverse_nodes(Location.SHENK_START, Location.SHENK_SAVE_DIST, char)
    pather._display_all_nodes_debug(filter="SHENK_17")
