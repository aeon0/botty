import math
import keyboard
import time
import os
import random
from typing import Tuple, Union, List
import cv2
import numpy as np

from utils.misc import is_in_roi
from config import Config
from logger import Logger
from screen import Screen
from template_finder import TemplateFinder
from char import IChar


class Location:
    # A5 Town
    A5_TOWN_START = "a5_town_start"
    A5_STASH = "a5_stash"
    A5_WP = "a5_wp"
    A5_QUAL_KEHK = "a5_qual_kehk"
    A5_MALAH = "a5_malah"
    A5_NIHLATHAK_PORTAL = "a5_nihlathak_portal"
    A5_LARZUK = "a5_larzuk"
    # Pindle
    A5_PINDLE_START = "a5_pindle_start"
    A5_PINDLE_SAFE_DIST = "a5_pindle_safe_dist"
    A5_PINDLE_END = "a5_pindle_end"
    # Eldritch
    A5_ELDRITCH_START = "a5_eldritch_start"
    A5_ELDRITCH_SAFE_DIST = "a5_eldritch_safe_dist"
    A5_ELDRITCH_END = "a5_eldritch_end"
    # Shenk
    A5_SHENK_START = "a5_shenk_start"
    A5_SHENK_SAFE_DIST = "a5_shenk_safe_dist"
    A5_SHENK_END = "a5_shenk_end"
    # A4 Town
    A4_TOWN_START = "a4_town_start"
    A4_WP = "a4_town_wp"
    A4_TYRAEL_STASH = "a4_tyrael_stash"
    A4_VENDOR = "a4_vendor"
    # A3 Town
    A3_TOWN_START = "a3_town_start"
    A3_ORMUS = "a3_ormus"
    A3_STASH_WP = "a3_stash_wp"
    A3_ASHEARA = "a3_asheara"
    # Trav
    A3_TRAV_START = "a3_trav_start"
    A3_TRAV_CENTER_STAIRS = "a3_trav_center_stairs"
    # Nihalatk
    A5_NIHLATAK_START = "a5_nihlatak_lvl1_start"
    A5_NIHLATAK_END = "a5_nihlatak_lvl2_end"


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
        self._range_x = [-self._config.ui_pos["center_x"] + 7, self._config.ui_pos["center_x"] - 7]
        self._range_y = [-self._config.ui_pos["center_y"] + 7, self._config.ui_pos["center_y"] - self._config.ui_pos["skill_bar_height"] - 33]
        self._nodes = {
            # A5 town
            0: {'A5_TOWN_0': (27, 249), 'A5_TOWN_1': (-92, -137)}, 
            1: {'A5_TOWN_0': (-311, 191), 'A5_TOWN_1': (-429, -194), 'A5_TOWN_0.5': (478, 233)}, 
            2: {'A5_TOWN_0': (-368, -39), 'A5_TOWN_0.5': (423, 7)}, 
            3: {'A5_TOWN_1': (-276, 94), 'A5_TOWN_2': (485, -60)}, 
            4: {'A5_TOWN_1': (-467, 267), 'A5_TOWN_2': (293, 113), 'A5_TOWN_3': (-267, -139), 'A5_TOWN_4': (162, -163)}, 
            5: {'A5_TOWN_2': (303+60, 219+40), 'A5_TOWN_3': (-257+60, -33+40), 'A5_TOWN_4': (172+60, -57+40)}, 
            6: {'A5_TOWN_3': (-583+80, 175+60), 'A5_TOWN_4': (-155+80, 151+60), 'A5_TOWN_5': (-13+80, -240+60), 'A5_TOWN_6': (307+80, 61+60)}, 
            8: {'A5_TOWN_6': (127, 293), 'A5_TOWN_5': (-195, -5), 'A5_TOWN_7': (598, -87)}, 
            9: {'A5_TOWN_5': (-407, 167), 'A5_TOWN_7': (386, 85)}, 
            10: {'A5_TOWN_4': (-472, 58), 'A5_TOWN_6': (-11, -32), 'A5_TOWN_8': (321, 131)}, 
            11: {'A5_TOWN_6': (-299, -215), 'A5_TOWN_8': (33, -52), 'A5_TOWN_9': (7, 231)}, 
            12: {'A5_TOWN_8': (-139, -196), 'A5_TOWN_9': (-165, 87)}, 
            13: {'A5_TOWN_3': (120, 120), 'A5_TOWN_10': (-533, 221), 'A5_TOWN_4': (548, 97)}, 
            14: {'A5_TOWN_3': (447, 173), 'A5_TOWN_10': (-200, 280)},
            # Pindle
            100: {'PINDLE_7': (384, -92), 'PINDLE_0': (-97, -40), 'PINDLE_1': (-13, 223), 'PINDLE_2': (-366, 85)}, 
            101: {'PINDLE_1': (371, -45), 'PINDLE_2': (18, -184), 'PINDLE_3': (-123, 261)}, 
            102: {'PINDLE_3': (223, 88), 'PINDLE_4': (95, 215)}, 
            103: {'PINDLE_3': (395, -75), 'PINDLE_4': (267, 52)}, 
            104: {'PINDLE_4': (717, -117), 'PINDLE_3': (843, -244), 'PINDLE_5': (-187, 237), 'PINDLE_6': (-467, 89)}, 
            # Eldritch
            120: {'ELDRITCH_0': (293, 24), 'ELDRITCH_1': (-307, 76), 'ELDRITCH_5': (27, -164), 'ELDRITCH_6': (400, -50)},
            121: {'ELDRITCH_6': (360, -244), 'ELDRITCH_1': (-329, -103), 'ELDRITCH_2': (411, 171), 'ELDRITCH_3': (-91, 198), 'ELDRITCH_7': (409, 180), 'ELDRITCH_8': (465, 345)},
            122: {'ELDRITCH_2': (353, -145), 'ELDRITCH_3': (-149, -119), 'ELDRITCH_9': (-253, -118), 'ELDRITCH_7': (352, -134), 'ELDRITCH_8': (404, 29)},
            123: {'ELDRITCH_3': (-99, -252), 'ELDRITCH_2': (403, -279), 'ELDRITCH_4': (-62, -109), 'ELDRITCH_9': (-204, -254), 'ELDRITCH_8': (400, -267), 'ELDRITCH_8': (454, -104)},
            # Shenk
            141: {'SHENK_0': (-129, 44), 'SHENK_1': (464, 107), 'SHENK_2': (-167, -34), 'SHENK_17': (-520, 528), 'SHENK_15': (77, 293), 'SHENK_18': (518, 512)},
            142: {'SHENK_1': (584, 376), 'SHENK_4': (-443, -103), 'SHENK_2': (-52, 235), 'SHENK_3': (357, -129)},
            143: {'SHENK_4': (-251, 165), 'SHENK_2': (141, 505), 'SHENK_3': (549, 139), 'SHENK_6': (-339, -69)},
            144: {'SHENK_6': (-108, 123), 'SHENK_7': (481, 151)},
            145: {'SHENK_7': (803, 372), 'SHENK_12': (97, -133), 'SHENK_6': (209, 347), 'SHENK_8': (-245, 18)},
            146: {'SHENK_12': (272, 111), 'SHENK_9': (-331, -144), 'SHENK_8': (-72, 258)},
            147: {'SHENK_16': (317, -18), 'SHENK_9': (-67, 139), 'SHENK_10': (-431, 67)},
            148: {'SHENK_16': (682, 103), 'SHENK_9': (301, 263), 'SHENK_10': (-65, 188), 'SHENK_11': (-306, 139)},
            149: {'SHENK_11': (261, 395), 'SHENK_10': (495, 421), 'SHENK_13': (393, -9)},
            # A4 town
            160: {"A4_TOWN_4": (-100, -133), "A4_TOWN_3": (-117, 238), "A4_TOWN_0": (-364, 151), "A4_TOWN_6": (24, -425), "A4_TOWN_5": (-347, -277)},
            161: {"A4_TOWN_3": (-289, 156), "A4_TOWN_4": (-272, -215), "A4_TOWN_2": (385, -92), "A4_TOWN_6": (-148, -507), "A4_TOWN_0": (-536, 69)},
            162: {"A4_TOWN_4": (74, 66), "A4_TOWN_5": (-173, -78), "A4_TOWN_6": (198, -226), "A4_TOWN_0": (-190, 350), "A4_TOWN_7": (-101, -455)},
            163: {"A4_TOWN_5": (-92, 143), "A4_TOWN_7": (-19, -233), "A4_TOWN_6": (280, -4), "A4_TOWN_4": (156, 288), "A4_TOWN_8": (-598, 5)},
            164: {"A4_TOWN_7": (235, 39), "A4_TOWN_8": (-344, 277), "A4_TOWN_5": (163, 415), "A4_TOWN_6": (534, 268), "A4_TOWN_4": (409, 559)},
            # A3 town
            180: {"A3_TOWN_0": (-144, 170), "A3_TOWN_1": (-417, 59), "A3_TOWN_2": (-716, -161)},
            181: {"A3_TOWN_1": (-113, 155), "A3_TOWN_0": (160, 266), "A3_TOWN_2": (-412, -65), "A3_TOWN_3": (-867, 133)},
            182: {"A3_TOWN_2": (-101, -135), "A3_TOWN_1": (198, 85), "A3_TOWN_0": (471, 196), "A3_TOWN_3": (-556, 63), "A3_TOWN_12": (-500, 717)},
            183: {"A3_TOWN_3": (-287, -80), "A3_TOWN_2": (168, -279), "A3_TOWN_1": (467, -58), "A3_TOWN_4": (-587, 86), "A3_TOWN_12": (-231, 574)},
            184: {"A3_TOWN_4": (-109, -146), "A3_TOWN_5": (-81, 206), "A3_TOWN_3": (191, -311), "A3_TOWN_12": (247, 342), "A3_TOWN_13": (-323, 530)},
            185: {"A3_TOWN_5": (223, 40), "A3_TOWN_13": (-19, 364), "A3_TOWN_4": (195, -312), "A3_TOWN_12": (551, 176), "A3_TOWN_20": (-549, 184)},
            186: {"A3_TOWN_7": (-195, -118), "A3_TOWN_20": (-130, 237), "A3_TOWN_8": (-269, 308), "A3_TOWN_13": (400, 417), "A3_TOWN_5": (642, 93)},
            187: {"A3_TOWN_8": (161, 207), "A3_TOWN_9": (-108, 265), "A3_TOWN_7": (236, -219), "A3_TOWN_20": (300, 136), "A3_TOWN_11": (-618, 150)},
            188: {"A3_TOWN_9": (173, 157), "A3_TOWN_11": (-337, 42), "A3_TOWN_8": (442, 99), "A3_TOWN_20": (581, 28), "A3_TOWN_7": (517, -327)},
            189: {"A3_TOWN_5": (10, -182), "A3_TOWN_13": (-232, 142), "A3_TOWN_14": (-7, 337), "A3_TOWN_12": (338, -46), "A3_TOWN_15": (722, 143)},
            190: {"A3_TOWN_12": (27, -198), "A3_TOWN_16": (831, 258), "A3_TOWN_14": (-318, 185), "A3_TOWN_15": (411, -9), "A3_TOWN_5": (-301, -334), "A3_TOWN_13": (-543, -10), "A3_TOWN_17": (707, 541)},
            191: {"A3_TOWN_15": (-79, -256), "A3_TOWN_16": (341, 11), "A3_TOWN_17": (217, 294), "A3_TOWN_18": (542, 408), "A3_TOWN_19": (779, 171)},
            192: {"A3_TOWN_17": (-187, 78), "A3_TOWN_16": (-63, -205), "A3_TOWN_18": (138, 192), "A3_TOWN_19": (375, -45)},
            # Trav
            220: {"TRAV_0": (445, 384), "TRAV_20": (-259, 267), "TRAV_1": (-248, -139), "TRAV_2": (-682, 21), "TRAV_21": (25, 180)},
            221: {"TRAV_2": (-153, -101), "TRAV_3": (-125, 201), "TRAV_20": (270, 145), "TRAV_1": (281, -261), "TRAV_4": (-459, 122)},
            222: {"TRAV_5": (-218, 106), "TRAV_4": (120, 230), "TRAV_2": (426, 7), "TRAV_7": (-719, -166), "TRAV_1": (862, -153)},
            223: {"TRAV_5": (344, 123), 'TRAV_4': (682, 247), "TRAV_8": (-353, -31), "TRAV_7": (-157, -149), "TRAV_22": (-368, -222), "TRAV_23": (-579, 116)},
            224: {'TRAV_7': (411, -129), 'TRAV_27': (-363, 163), "TRAV_8": (214, -11), "TRAV_23": (-11, 136), "TRAV_10": (-130, -187), "TRAV_24": (-274, 15), "TRAV_22": (200, -202)},
            225: {'TRAV_27': (96, 359), 'TRAV_8': (670, 187), 'TRAV_7': (867, 69), "TRAV_11": (10, 214), "TRAV_19": (-298, 539), "TRAV_24": (181, 213), "TRAV_12": (-408, -73), "TRAV_25": (-538, 132)},
            226: {"TRAV_12": (-75, -172), "TRAV_25": (-205, 33), "TRAV_13": (-252, 195), "TRAV_11": (343, 115), "TRAV_18": (-514, 373), "TRAV_19": (35, 440), "TRAV_17": (-231, 242), "TRAV_27": (428, 263)},
            227: {"TRAV_11": (65, -42), "TRAV_24": (236, -43), "TRAV_19": (-243, 283), 'TRAV_18': (-792, 216), "TRAV_12": (-356, -330), "TRAV_25": (-483, -124), 'TRAV_27': (154, 104)},
            228: {"TRAV_13": (8, 9), "TRAV_17": (29, 56), "TRAV_25": (58, -152), "TRAV_16": (-198, -110), "TRAV_18": (-251, 188)},
            229: {"TRAV_18": (-250, 58), "TRAV_25": (59, -282), "TRAV_17": (30, -74), "TRAV_13": (9, -121), "TRAV_16": (-138, -241)},
            230: {"TRAV_19": (157, 39), "TRAV_18": (-392, -28), "TRAV_17": (-112, -160), "TRAV_13": (-133, -207), "TRAV_25": (-83, -368)},
            # Nil - End of Arm A
            500: {"NIL2A_0": (-200, 1), "NIL2A_2": (-181, -102), "NIL2A_1": (329, 146), "NIL2A_4": (835, 24), "NIL2A_5": (-384, -20), "NIL2A_6": (-600, 410)},
            501: {"NIL2A_4": (270+20, 259-50), "NIL2A_1": (-236+20, 381-50), "NIL2A_2": (-746+20, 133-50), "NIL2A_0": (-765+20, 236-50)},
            # Nil - End of Arm B
            505: {"NIL2B_1": (-97, 161), "NIL2B_2": (226, -16), "NIL2B_0": (402, -60), "NIL2B_3": (-790, 7)},
            506: {"NIL2B_3": (-245, 260), "NIL2B_5": (-385, 182), "NIL2B_1": (448, 415), "NIL2B_2": (771, 237)},
            # Nil - End of Arm C
            510: {"NIL2C_0": (-206, 67), "NIL2C_2": (131, 178), "NIL2C_1": (-300, -127), "NIL2C_4": (-183, 373), "NIL2C_3": (-20, 433), "NIL2C_6": (310, -320)},
            511: {"NIL2C_4": (417, 49), "NIL2C_0": (394, -257), "NIL2C_1": (300, -451), "NIL2C_3": (580, 109), "NIL2C_5": (-435, 204), "NIL2C_2": (731, -146)},
            # Nil - End of Arm D
            515: {"NIL2D_2": (66, -12), "NIL2D_0": (-141, 245), "NIL2D_1": (329, -167), "NIL2D_4": (219, 392), "NIL2D_3": (-773, 91)},
            516: {"NIL2D_2": (-80, -143), "NIL2D_4": (73, 261), "NIL2D_0": (-287, 114), "NIL2D_3": (-343, 248)},
            517: {"NIL2D_5": (423, 139), "NIL2D_4": (-444, 127), "NIL2D_2": (-598, -277), "NIL2D_0": (-804, -20), "NIL2D_3": (-860, 114)},
        }
        self._paths = {
            # A5 Town
            (Location.A5_TOWN_START, Location.A5_NIHLATHAK_PORTAL): [3, 4, 5, 6, 8, 9],
            (Location.A5_TOWN_START, Location.A5_STASH): [3, 4, 5],
            (Location.A5_TOWN_START, Location.A5_WP): [3, 4],
            (Location.A5_TOWN_START, Location.A5_QUAL_KEHK): [3, 4, 5, 6, 10, 11, 12],
            (Location.A5_TOWN_START, Location.A5_MALAH): [1, 2],
            (Location.A5_TOWN_START, Location.A5_LARZUK): [3, 4, 5, 13, 14],
            (Location.A5_MALAH, Location.A5_TOWN_START): [1, 0],
            (Location.A5_STASH, Location.A5_NIHLATHAK_PORTAL): [6, 8, 9],
            (Location.A5_STASH, Location.A5_QUAL_KEHK): [5, 6, 10, 11, 12],
            (Location.A5_STASH, Location.A5_LARZUK): [13, 14],
            (Location.A5_STASH, Location.A5_WP): [],
            (Location.A5_WP, Location.A5_STASH): [],
            (Location.A5_WP, Location.A5_LARZUK): [13, 14],
            (Location.A5_WP, Location.A5_NIHLATHAK_PORTAL): [6, 8, 9],
            (Location.A5_QUAL_KEHK, Location.A5_NIHLATHAK_PORTAL): [12, 11, 10, 6, 8, 9],
            (Location.A5_QUAL_KEHK, Location.A5_WP): [12, 11, 10, 6],
            (Location.A5_LARZUK, Location.A5_QUAL_KEHK): [13, 14, 5, 6, 10, 11, 12],
            (Location.A5_LARZUK, Location.A5_NIHLATHAK_PORTAL): [14, 13, 5, 6, 8, 9],
            (Location.A5_LARZUK, Location.A5_WP): [14, 13, 5],
            # Pindle
            (Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST): [100, 101, 102, 103],
            (Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END): [104],
            # Eldritch
            (Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAFE_DIST): [120, 121, 122],
            (Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END): [123],
            # Shenk
            (Location.A5_SHENK_START, Location.A5_SHENK_SAFE_DIST): [141, 142, 143, 144, 145, 146, 147, 148],
            (Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END): [149],
            # A4 Town
            (Location.A4_WP, Location.A4_TYRAEL_STASH): [160, 161],
            (Location.A4_TYRAEL_STASH, Location.A4_WP): [161, 160],
            (Location.A4_TOWN_START, Location.A4_WP): [162],
            (Location.A4_TOWN_START, Location.A4_TYRAEL_STASH): [160, 161],
            # A3 Town
            (Location.A3_TOWN_START, Location.A3_STASH_WP): [180, 181, 182, 183, 184, 185, 186, 187, 188],
            (Location.A3_TOWN_START, Location.A3_ORMUS): [180, 181, 182, 183, 184, 185],
            (Location.A3_ORMUS, Location.A3_STASH_WP): [186, 187, 188],
            (Location.A3_ORMUS, Location.A3_ASHEARA): [189, 190, 191, 192],
            (Location.A3_ASHEARA, Location.A3_STASH_WP): [191, 190, 189, 185, 186, 187, 188],
            (Location.A3_STASH_WP, Location.A3_STASH_WP): [188],
            (Location.A3_STASH_WP, Location.A3_ORMUS): [187, 186, 185],
            # Trav
            (Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS): [220, 221, 222, 223, 224, 225, 226],
        }

    def offset_node(self, node_idx: int, offset: tuple[int, int]):
        """Will offset any node. e.g. can be used in char files to change final attacking positions
        :param node_idx: Index of node to be changed
        :param offset: Offset [x, y] the node will get. +x will move node to the right, +y more to the bottom
        """
        for k in self._nodes[node_idx]:
            self._nodes[node_idx][k] = (
                self._nodes[node_idx][k][0] + offset[0],
                self._nodes[node_idx][k][1] + offset[1]
            )

    def _get_node(self, key: int, template: str):
        return (
            self._nodes[key][template][0],
            self._nodes[key][template][1]
        )

    @staticmethod
    def _convert_rel_to_abs(rel_loc: Tuple[float, float], pos_abs: Tuple[float, float]) -> Tuple[float, float]:
        return (rel_loc[0] + pos_abs[0], rel_loc[1] + pos_abs[1])

    def traverse_nodes_fixed(self, key: Union[str, List[Tuple[float, float]]], char: IChar):
        if not char.can_teleport():
            error_msg = "Teleport is requiered for static pathing"
            Logger.error(error_msg)
            raise ValueError(error_msg)
        char.pre_move()
        if type(key) == str:
            path = self._config.path[key]
        else:
            path = key
        i = 0
        while i < len(path):
            x_m, y_m = self._screen.convert_screen_to_monitor(path[i])
            x_m += int(random.random() * 6 - 3)
            y_m += int(random.random() * 6 - 3)
            t0 = self._screen.grab()
            char.move((x_m, y_m))
            t1 = self._screen.grab()
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score > 0.15:
                i += 1
            else:
                Logger.debug(f"Teleport cancel detected. Try same teleport action again. ({score:.4f})")
        # if type(key) == str and ("_save_dist" in key or "_end" in key):
        #     cv2.imwrite(f"./info_screenshots/nil_path_{key}_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())

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
        template_match = self._template_finder.search([*node], img, best_match=False, roi=self._config.ui_roi["cut_skill_bar"], use_grayscale=True)
        if template_match.valid:
            # Get reference position of template in abs coordinates
            ref_pos_abs = self._screen.convert_screen_to_abs(template_match.position)
            # Calc the abs node position with the relative coordinates (relative to ref)
            node_pos_rel = self._get_node(node_idx, template_match.name)
            node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
            node_pos_abs = self._adjust_abs_range_to_screen(node_pos_abs)
            return node_pos_abs
        return None

    def traverse_nodes(
        self,
        path: Union[tuple[Location, Location], list[int]],
        char: IChar,
        time_out: float = 5,
        force_tp: bool = False,
        do_pre_move: bool = True,
        force_move: bool = False
    ) -> bool:
        """Traverse from one location to another
        :param path: Either a list of node indices or a tuple with (start_location, end_location)
        :param char: Char that is traversing the nodes
        :param time_out: Timeout in second. If no more move was found in that time it will cancel traverse
        :param force_move: Bool value if force move should be used for pathing
        :return: Bool if traversed succesfull or False if it got stuck
        """
        if len(path) == 0:
            Logger.error("Path must be a list of integers or a tuple with start and end location!")
            return False
        if type(path[0]) != int:
            start_location = path[0]
            end_location = path[1]
            Logger.debug(f"Traverse from {start_location} to {end_location}")
            try:
                path = self._paths[(start_location, end_location)]
            except KeyError:
                if start_location == end_location:
                    return True
                Logger.error(f"Don't know how to traverse from {start_location} to {end_location}")
                return False
        else:
            Logger.debug(f"Traverse: {path}")
        if do_pre_move:
            char.pre_move()
        last_direction = None
        for i, node_idx in enumerate(path):
            continue_to_next_node = False
            last_move = time.time()
            did_force_move = False
            while not continue_to_next_node:
                img = self._screen.grab()
                # Handle timeout
                if (time.time() - last_move) > time_out:
                    success = self._template_finder.search("WAYPOINT_MENU", img).valid
                    if success:
                        # sometimes bot opens waypoint menu, close it to find templates again
                        Logger.debug("Opened wp, closing it again")
                        keyboard.send("esc")
                        last_move = time.time()
                    else:
                        # This is a bit hacky, but for moving into a boss location we set time_out usually quite low
                        # because of all the spells and monsters it often can not determine the final template
                        # Don't want to spam the log with errors in this case because it most likely worked out just fine
                        if time_out > 3.1:
                            if self._config.general["info_screenshots"]:
                                cv2.imwrite("./info_screenshots/info_pather_got_stuck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                            Logger.error("Got stuck exit pather")
                        return False

                # Sometimes we get stuck at rocks and stuff, after 2.5 seconds force a move into the last know direction
                if not did_force_move and time.time() - last_move > 3.1:
                    pos_abs = (0, 150)
                    if last_direction is not None:
                        pos_abs = last_direction
                    Logger.debug(f"Pather: taking a random guess for next position")
                    x_m, y_m = self._screen.convert_abs_to_monitor(pos_abs)
                    char.move((x_m, y_m), force_move=True)
                    did_force_move = True
                    last_move = time.time()

                # Find any template and calc node position from it
                node_pos_abs = self.find_abs_node_pos(node_idx, img)
                if node_pos_abs is not None:
                    dist = math.dist(node_pos_abs, (0, 0))
                    if dist < self._config.ui_pos["reached_node_dist"]:
                        continue_to_next_node = True
                    else:
                        # Move the char
                        x_m, y_m = self._screen.convert_abs_to_monitor(node_pos_abs)
                        char.move((x_m, y_m), force_tp=force_tp, force_move=force_move)
                        last_direction = node_pos_abs
                        last_move = time.time()
        return True


# Testing: Move char to whatever Location to start and run
if __name__ == "__main__":
    # debug method to display all nodes
    def display_all_nodes(pather: Pather, filter: str = None):
        while 1:
            img = pather._screen.grab()
            display_img = img.copy()
            template_map = {}
            template_scores = {}
            for template_type in pather._template_finder._templates:
                if filter is None or filter in template_type:
                    template_match = pather._template_finder.search(template_type, img, use_grayscale=True)
                    if template_match.valid:
                        template_map[template_type] = template_match.position
                        template_scores[template_type] = template_match.score
            print(template_scores)
            for node_idx in pather._nodes:
                for template_type in pather._nodes[node_idx]:
                    if template_type in template_map:
                        ref_pos_screen = template_map[template_type]
                        # Get reference position of template in abs coordinates
                        ref_pos_abs = pather._screen.convert_screen_to_abs(ref_pos_screen)
                        # Calc the abs node position with the relative coordinates (relative to ref)
                        node_pos_rel = pather._get_node(node_idx, template_type)
                        node_pos_abs = pather._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                        node_pos_abs = pather._adjust_abs_range_to_screen(node_pos_abs)
                        x, y = pather._screen.convert_abs_to_screen(node_pos_abs)
                        cv2.circle(display_img, (x, y), 5, (255, 0, 0), 3)
                        cv2.putText(display_img, str(node_idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        x, y = pather._screen.convert_abs_to_screen(ref_pos_abs)
                        cv2.circle(display_img, (x, y), 5, (0, 255, 0), 3)
                        cv2.putText(display_img, template_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5)
            cv2.imshow("debug", display_img)
            cv2.waitKey(1)

    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char.sorceress import Sorceress
    from char.hammerdin import Hammerdin
    from ui import UiManager
    config = Config()
    screen = Screen(config.general["monitor"])
    t_finder = TemplateFinder(screen)
    pather = Pather(screen, t_finder)

    display_all_nodes(pather, "ELD")

    # # changing node pos and generating new code
    # code = ""
    # node_idx = 226
    # offset = [0, 0]
    # for k in pather._nodes[node_idx]:
    #     pather._nodes[node_idx][k][0] += offset[0]
    #     pather._nodes[node_idx][k][1] += offset[1]
    #     code += (f'"{k}": {pather._nodes[node_idx][k]}, ')
    # print(code)

    # ui_manager = UiManager(screen, t_finder)
    # char = Hammerdin(config.hammerdin, config.char, screen, t_finder, ui_manager, pather)
    # pather.traverse_nodes_fixed("trav_safe_dist", char)
    # print("-----")
    # pather.traverse_nodes([226, 228, 229], char)
