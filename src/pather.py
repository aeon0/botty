from screen import Screen
from template_finder import TemplateFinder
from logger import Logger
from char.i_char import IChar
import math
import keyboard
import time
import os
import random
from typing import Tuple
import cv2


class Location:
    A5_TOWN_START = "a5_town_start"
    A5_STASH = "a5_stash"
    A5_WP = "a5_wp"
    QUAL_KEHK = "qual_kehk"
    MALAH = "malah"
    NIHLATHAK_PORTAL = "nihlathak_portal"


class Pather:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._screen = screen
        self._template_finder = template_finder
        # TODO: params based on 1920x1080 (in rel coordinates to ref point)
        self._range_x = [-950, 950]
        self._range_y = [-530, 440]
        self._nodes = {
            # A5 town
            0: {"A5_TOWN_0": (110-70, 373), "A5_TOWN_1": (-68-70, -205)},
            1: {"A5_TOWN_0": (-466, 287), "A5_TOWN_1": (-644, -291), "A5_TOWN_0.5": (717, 349)},
            2: {"A5_TOWN_0": (-552, 42), "A5_TOWN_0.5": (659-25, 90+20)},
            3: {"A5_TOWN_1": (-414, 141), "A5_TOWN_2": (728, -90)},
            4: {"A5_TOWN_1": (-701, 400), "A5_TOWN_2": (440, 169), "A5_TOWN_3": (-400, -208), "A5_TOWN_4": (243, -244)},
            5: {"A5_TOWN_2": (555-100, 429-100), "A5_TOWN_3": (-285-100, 51-100), "A5_TOWN_4": (358-100, 15-100)},
            6: {"A5_TOWN_3": (-775-100, 382-120), "A5_TOWN_4": (-132-100, 346-120), "A5_TOWN_5": (80-100, -240-120), "A5_TOWN_6": (560-100, 211-120)},
            8: {"A5_TOWN_5": (-323+30, 192-200), "A5_TOWN_7": (867+30, 69-200)},
            9: {"A5_TOWN_5": (-611, 250), "A5_TOWN_7": (579, 127)},
            10: {"A5_TOWN_4": (-708, 87), "A5_TOWN_6": (-16, -48), "A5_TOWN_8": (482, 196)},
            11: {"A5_TOWN_6": (-448, -322), "A5_TOWN_8": (50, -78), "A5_TOWN_9": (11, 346)},
            12: {"A5_TOWN_8": (-209, -294), "A5_TOWN_9": (-248, 130)},
            13: {"A5_TOWN_3": (262, 210)},
            14: {"A5_TOWN_3": (694, 282)},
        }
        self._paths = {
            (Location.A5_TOWN_START, Location.NIHLATHAK_PORTAL): [3, 4, 5, 6, 8, 9],
            (Location.A5_TOWN_START, Location.A5_STASH): [3, 4, 5],
            (Location.A5_TOWN_START, Location.A5_WP): [3, 4],
            (Location.A5_TOWN_START, Location.QUAL_KEHK): [3, 4, 5, 6, 10, 11, 12],
            (Location.A5_TOWN_START, Location.MALAH): [1, 2],
            (Location.MALAH, Location.A5_TOWN_START): [1, 0],
            (Location.A5_STASH, Location.NIHLATHAK_PORTAL): [6, 8, 9],
            (Location.A5_STASH, Location.QUAL_KEHK): [5, 6, 10, 11, 12],
            (Location.A5_STASH, Location.A5_WP): [],
            (Location.QUAL_KEHK, Location.NIHLATHAK_PORTAL): [12, 11, 10, 6, 8, 9],
            (Location.QUAL_KEHK, Location.A5_WP): [12, 11, 10, 6],
        }
        self._fixed_tele_path = {
            # 0: path to boss, 1: location of boss
            "PINDLE": ([(1382, 53), (1685, 105), (1429, 122)], (1533, 327)),
            "PINDLE_END": ([(1800, 400)], None),
            "ELDRITCH": ([(978, 95), (845, 109)], (1012, 42)),
            "SHENK": ([(798, 869), (1112, 882), (1220, 860), (1330, 869), (1502, 836), (1247, 887), (1258, 901), (1463, 814), (1351, 778)], [1815, 772])
        }

    def get_fixed_path(self, key: str):
        return self._fixed_tele_path[key]

    def _draw_debug(self, img, node_pos_abs_list, ref_pos_abs_list):
        for node_pos_abs in node_pos_abs_list:
            pos_screen = self._screen.convert_abs_to_screen(node_pos_abs)
            cv2.circle(img, pos_screen, 10, (255, 0, 0), 10)
        for ref_pos_screen in ref_pos_abs_list:
            pos_screen = self._screen.convert_abs_to_screen(ref_pos_screen)
            cv2.circle(img, pos_screen, 10, (0, 255, 0), 10)
        img = cv2.resize(img, None, fx=0.5, fy=0.5)
        cv2.namedWindow("x")
        cv2.moveWindow("x", 2000, 30)
        cv2.imshow("x", img)
        cv2.waitKey(1)

    def _display_all_nodes(self):
        while 1:
            img = self._screen.grab()
            for node_idx in self._nodes:
                for template_type in self._nodes[node_idx]:
                        success, ref_pos_screen = self._template_finder.search(template_type, img)
                        if success:
                            # Get reference position of template in abs coordinates
                            ref_pos_abs = self._screen.convert_screen_to_abs(ref_pos_screen)
                            # Calc the abs node position with the relative coordinates (relative to ref)
                            node_pos_rel = self._nodes[node_idx][template_type]
                            node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                            if self._check_abs_range_to_screen(node_pos_abs):
                                x, y = self._screen.convert_abs_to_screen(node_pos_abs)
                                cv2.circle(img, (x, y), 5, (255, 0, 0), 3)
                                cv2.putText(img, str(node_idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                                x, y = self._screen.convert_abs_to_monitor(ref_pos_abs)
                                cv2.circle(img, (x, y), 5, (0, 255, 0), 3)
            img = cv2.resize(img, None, fx=0.5, fy=0.5)
            cv2.imshow("debug", img)
            cv2.waitKey(1)

    @staticmethod 
    def _convert_rel_to_abs(rel_loc, pos_abs):
        return (rel_loc[0] + pos_abs[0], rel_loc[1] + pos_abs[1])

    def _check_abs_range_to_screen(self, pos_abs: Tuple[float, float]) -> Tuple[float, float]:
        is_in_x_range = self._range_x[0] < pos_abs[0] < self._range_x[1]
        is_in_y_range = self._range_y[0] < pos_abs[1] < self._range_y[1]
        return is_in_x_range and is_in_y_range

    def traverse_nodes_fixed(self, key: str, char: IChar):
        path = self._fixed_tele_path[key][0]
        for pos in path:
            x_m, y_m = self._screen.convert_screen_to_monitor(pos)
            x_m += int(random.random() * 6 - 3)
            y_m += int(random.random() * 6 - 3)
            char.move((x_m, y_m))

    def traverse_nodes(self, start_location: Location, end_location: Location, char: IChar, debug: bool = False) -> bool:
        Logger.debug(f"Traverse from {start_location} to {end_location}")
        path = self._paths[(start_location, end_location)]
        for i, node_idx in enumerate(path):
            continue_to_next_node = False
            last_move = time.time()
            while not continue_to_next_node:
                img = self._screen.grab()
                if (time.time() - last_move) > 7:
                    success, _ = self._template_finder.search("WAYPOINT_MENU", img)
                    if success:
                        # sometimes bot opens waypoint menu, close it to find templates again
                        Logger.debug("Opened wp, closing it again")
                        keyboard.send("esc")
                        last_move = time.time()
                    else:
                        cv2.imwrite("info_pather_got_stuck.png", img)
                        Logger.error("Got stuck exit")
                        return False
                _debug_node_pos_abs_list = []
                _debug_ref_pos_abs_list = []
                node = self._nodes[node_idx]
                for template_type in node:
                    success, ref_pos_screen = self._template_finder.search(template_type, img)
                    if success:
                        # Get reference position of template in abs coordinates
                        ref_pos_abs = self._screen.convert_screen_to_abs(ref_pos_screen)
                        _debug_ref_pos_abs_list.append(ref_pos_abs)
                        # Calc the abs node position with the relative coordinates (relative to ref)
                        node_pos_rel = node[template_type]
                        node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                        _debug_node_pos_abs_list.append(node_pos_abs)
                        if debug:
                            self._draw_debug(img, _debug_node_pos_abs_list, _debug_ref_pos_abs_list)
                        if self._check_abs_range_to_screen(node_pos_abs):
                            dist = math.dist(node_pos_abs, (0, 0))
                            # TODO: param based on 1920x1080
                            if dist < 150:
                                continue_to_next_node = True
                            else:
                                # Move the char
                                x_m, y_m = self._screen.convert_abs_to_monitor(node_pos_abs)
                                char.move((x_m, y_m))
                                last_move = time.time()
                            break
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
    char = Sorceress(config.sorceress, config.char, screen, t_finder, None, ui_manager)
    # pather.traverse_nodes_fixed("PINDLE", char)
    # pather.traverse_nodes(Location.QUAL_KEHK, Location.NIHLATHAK_PORTAL, char, debug=True)
    pather._display_all_nodes()
