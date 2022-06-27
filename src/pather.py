import math
import keyboard
import time
import os
import random
import cv2
import numpy as np
from utils.custom_mouse import mouse
from utils.misc import wait # for stash/shrine tele cancel detection in traverse node
from utils.misc import is_in_roi
from config import Config
from logger import Logger
from screen import convert_screen_to_monitor, convert_abs_to_screen, convert_abs_to_monitor, convert_screen_to_abs, grab, stop_detecting_window
import template_finder
from char import IChar
from ui_manager import detect_screen_object, ScreenObjects, is_visible, select_screen_object_match, get_closest_non_hud_pixel

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
    A4_JAMELLA = "a4_jamella"
    A4_HALBU = "a4_halbu"
    # A3 Town
    A3_TOWN_START = "a3_town_start"
    A3_ORMUS = "a3_ormus"
    A3_STASH_WP = "a3_stash_wp"
    A3_ASHEARA = "a3_asheara"
    # A2 Town
    A2_TOWN_START = "a2_town_start"
    A2_WP = "a2_wp"
    A2_TP = "a2_tp"
    A2_FARA_STASH = "a2_fara_stash"
    A2_LYSANDER = "a2_lysander"
    A2_DROGNAN = "a2_drognan"
    # A1 Town
    A1_TOWN_START = "a1_town_start"
    A1_STASH = "a1_stash"
    A1_WP_NORTH = "a1_wp_north"
    A1_WP_SOUTH = "a1_wp_south"
    A1_KASHYA_CAIN = "a1_kashya_cain"
    A1_AKARA = "a1_akara"
    A1_CHARSI = "a1_charsi"
    A1_TOWN_TP = "a1_town_tp"
    # Trav
    A3_TRAV_START = "a3_trav_start"
    A3_TRAV_CENTER_STAIRS = "a3_trav_center_stairs"
    # Nihalatk
    A5_NIHLATHAK_START = "a5_nihlathak_lvl1_start"
    A5_NIHLATHAK_END = "a5_nihlathak_lvl2_end"
    # Arcane
    A2_ARC_START = "a2_arc_start"
    A2_ARC_CHECKPOINT = "a2_arc_checkpoint"
    A2_ARC_END = "a2_arc_end"
    # Chaos Sanctuary (a = vizier, b = deseis, c = infector)
    A4_DIABLO_WP = "a4_diablo_wp"
    A4_DIABLO_START = "a4_diablo_start"
    A4_DIABLO_ENTRANCE = "a4_diablo_entrance"
    A4_DIABLO_PENTAGRAM = "a4_diablo_pentagram"
    A4_DIABLO_A_LAYOUTCHECK = "a4_diablo_a_layoutcheck"
    A4_DIABLO_B_LAYOUTCHECK = "a4_diablo_b_layoutcheck"
    A4_DIABLO_C_LAYOUTCHECK = "a4_diablo_c_layoutcheck"
    A4_DIABLO_END = "a4_diablo_end"

class Pather:
    """
    Traverses 'dynamic' pathes with reference templates and relative coordinates or statically recorded pathes.
    Check utils/node_recorder.py to generate templates/refpoints and relative coordinates to nodes. Once you have refpoints and
    nodes you can specify in which order this nodes should be traversed in self._paths.
    """

    def __init__(self):
        self._range_x = [-Config().ui_pos["center_x"] + 7, Config().ui_pos["center_x"] - 7]
        self._range_y = [-Config().ui_pos["center_y"] + 7, Config().ui_pos["center_y"] - Config().ui_pos["skill_bar_height"] - 33]
        self._nodes = {
            # A5 town
            0: {'A5_TOWN_0': (27, 249), 'A5_TOWN_1': (-92, -137), 'A5_TOWN_11': (-313, -177)},
            1: {'A5_TOWN_0': (-311, 191), 'A5_TOWN_1': (-429, -194), 'A5_TOWN_0.5': (478, 233), 'A5_TOWN_11': (-651, -231)},
            2: {'A5_TOWN_0': (-368, -39), 'A5_TOWN_0.5': (423, 7)},
            3: {'A5_TOWN_1': (-276, 94), 'A5_TOWN_2': (485, -60), 'A5_TOWN_11': (-500, 56)},
            4: {'A5_TOWN_1': (-467, 267), 'A5_TOWN_2': (293, 113), 'A5_TOWN_3': (-267, -139), 'A5_TOWN_4': (162, -163)},
            5: {'A5_TOWN_2': (303+60, 219+40), 'A5_TOWN_3': (-257+60, -33+40), 'A5_TOWN_4': (172+60, -57+40)},
            6: {'A5_TOWN_3': (-583+80, 175+60), 'A5_TOWN_4': (-155+80, 151+60), 'A5_TOWN_5': (-13+80, -240+60), 'A5_TOWN_6': (307+80, 61+60)},
            8: {'A5_TOWN_6': (127, 293), 'A5_TOWN_5': (-195, -5), 'A5_RED_PORTAL': (598, -87)},
            9: {'A5_TOWN_5': (-407, 167), 'A5_RED_PORTAL': (386, 85)},
            10: {'A5_TOWN_4': (-472, 58), 'A5_TOWN_6': (-11, -32), 'A5_TOWN_8': (321, 131)},
            11: {'A5_TOWN_6': (-299, -215), 'A5_TOWN_8': (33, -52), 'A5_TOWN_9': (7, 231)},
            12: {'A5_TOWN_8': (-139, -196), 'A5_TOWN_9': (-165, 87)},
            13: {'A5_TOWN_3': (120, 120), 'A5_TOWN_10': (-533, 221), 'A5_TOWN_4': (548, 97)},
            14: {'A5_TOWN_3': (447, 173), 'A5_TOWN_10': (-200, 280)},
            15: {'A5_TOWN_9': (310, -38), 'A5_TOWN_2': (-327, -118), 'A5_TOWN_12': (-267, 204)},
            16: {'A5_TOWN_0.5': (65, 155), 'A5_TOWN_12': (-25, -107)},
            # Pindle
            100: {'PINDLE_7': (384, -92), 'PINDLE_0': (-97, -40), 'PINDLE_1': (-13, 223), 'PINDLE_2': (-366, 85)},
            101: {'PINDLE_1': (371, -45), 'PINDLE_2': (18, -184), 'PINDLE_3': (-123, 261)},
            102: {'PINDLE_3': (223, 88), 'PINDLE_4': (95, 215)},
            103: {'PINDLE_3': (395, -75), 'PINDLE_4': (267, 52)},
            104: {'PINDLE_4': (717, -117), 'PINDLE_3': (843, -244), 'PINDLE_5': (-187, 237), 'PINDLE_6': (-467, 89)},
            # Eldritch
            120: {'ELDRITCH_0': (293, 24), 'ELDRITCH_0_V2': (293, 24), 'ELDRITCH_0_V3': (293, 24), 'ELDRITCH_1': (-307, 76), 'ELDRITCH_1_V2': (-307, 76), 'ELDRITCH_5': (27, -164), 'ELDRITCH_6': (400, -50)},
            121: {'ELDRITCH_6': (360, -244), 'ELDRITCH_1': (-329, -103), 'ELDRITCH_1_V2': (-329, -103), 'ELDRITCH_2': (411, 171), 'ELDRITCH_2_V2': (411, 171), 'ELDRITCH_3': (-91, 198), 'ELDRITCH_7': (409, 180), 'ELDRITCH_7_V2': (409, 180), 'ELDRITCH_8': (465, 345), 'ELDRITCH_8_V2': (465, 345)},
            122: {'ELDRITCH_2': (353, -145), 'ELDRITCH_2_V2': (353, -145), 'ELDRITCH_3': (-149, -119), 'ELDRITCH_9': (-253, -118), 'ELDRITCH_7': (352, -134), 'ELDRITCH_7_V2': (352, -134), 'ELDRITCH_8': (404, 29), 'ELDRITCH_8_V2': (404, 29)},
            123: {'ELDRITCH_3': (-99, -252), 'ELDRITCH_2': (403, -279), 'ELDRITCH_2_V2': (403, -279), 'ELDRITCH_4': (-62, -109), 'ELDRITCH_9': (-204, -254), 'ELDRITCH_8': (454, -104),  'ELDRITCH_8_V2': (454, -104)},
            # Shenk
            141: {'SHENK_0': (-129, 44), 'SHENK_1': (464, 107), 'SHENK_2': (-167, -34), 'SHENK_17': (-520, 528), 'SHENK_15': (77, 293), 'SHENK_18': (518, 512)},
            142: {'SHENK_1': (584, 376), 'SHENK_4': (-443, -103), 'SHENK_2': (-52, 235), 'SHENK_3': (357, -129),
                "ELDRITCH_2_V2": (516, 195), 'ELDRITCH_1': (-233, -77), "ELDRITCH_0_V2": (360, -140), "ELDRITCH_3": (20, 219)
            },
            143: {'SHENK_4': (-251, 165), 'SHENK_2': (141, 505), 'SHENK_3': (549, 139), 'SHENK_6': (-339, -69),
                'ELDRITCH_1': (10, 204), 'SHENK_7': (264, -37), 'ELDRITCH_0_V2': (591, 141), 'ELDRITCH_3': (252, 500)
            },
            144: {'SHENK_6': (-108, 123), 'SHENK_7': (481, 151)},
            145: {'SHENK_7': (803, 372), 'SHENK_12': (97, -133), 'SHENK_6': (209, 347), 'SHENK_8': (-245, 18)},
            146: {'SHENK_12': (272, 111), 'SHENK_9': (-331, -144), 'SHENK_8': (-72, 258), 'SHENK_19': (-120, -221)},
            147: {'SHENK_16': (317, -18), 'SHENK_9': (-67, 139), 'SHENK_10': (-431, 67), 'SHENK_19': (468, 144), 'SHENK_20': (-61, -278)},
            148: {'SHENK_16': (682, 103), 'SHENK_9': (301, 263), 'SHENK_10': (-65, 188), 'SHENK_11': (-306, 139), 'SHENK_19': (108, 25), 'SHENK_20': (308, -154)},
            149: {'SHENK_11': (261, 395), 'SHENK_10': (495, 421), 'SHENK_13': (393, -9)},
            150: {"SHENK_V2_6": (-80, -6), "SHENK_V2_3": (-89, 5), "SHENK_V2_4": (-16, -138), "SHENK_V2_7": (-15, -144), "SHENK_V2_8": (-193, -160), 'SHENK_20': (461, 9)},
            151: {"SHENK_V2_8": (109, 88), "SHENK_V2_7": (287, 104), "SHENK_V2_4": (286, 110), "SHENK_V2_6": (222, 242), "SHENK_V2_3": (213, 253)},
            # A4 town
            160: {"A4_TOWN_4": (-100, -83), "A4_TOWN_3": (-117, 288), "A4_TOWN_0": (-364, 201), "A4_TOWN_6": (24, -375), "A4_TOWN_5": (-347, -227)},
            161: {"A4_TOWN_3": (-289, 156), "A4_TOWN_4": (-272, -215), "A4_TOWN_2": (385, -92), "A4_TOWN_6": (-148, -507), "A4_TOWN_0": (-536, 69)},
            162: {"A4_TOWN_4": (74, 66), "A4_TOWN_5": (-173, -78), "A4_TOWN_6": (198, -226), "A4_TOWN_0": (-190, 350), "A4_TOWN_7": (-101, -455)},
            163: {"A4_TOWN_5": (-92, 143), "A4_TOWN_7": (-19, -233), "A4_TOWN_6": (280, -4), "A4_TOWN_4": (156, 288), "A4_TOWN_8": (-598, 5)},
            164: {"A4_TOWN_7": (235, 39), "A4_TOWN_8": (-344, 277), "A4_TOWN_5": (163, 415), "A4_TOWN_6": (534, 268), "A4_TOWN_4": (409, 559), "A4_TOWN_9": (80, -329)},
            165: {"A4_TOWN_8": (80, 200), "A4_TOWN_7": (661, -38)},
            # A3 town
            180: {"A3_TOWN_0": (-144, 170), "A3_TOWN_1": (-417, 59), "A3_TOWN_2": (-716, -161)},
            181: {"A3_TOWN_1": (-113, 155), "A3_TOWN_0": (160, 266), "A3_TOWN_2": (-412, -65), "A3_TOWN_3": (-867, 133)},
            182: {"A3_TOWN_2": (-101, -135), "A3_TOWN_1": (198, 85), "A3_TOWN_0": (471, 196), "A3_TOWN_3": (-556, 63), "A3_TOWN_12": (-500, 717)},
            183: {"A3_TOWN_3": (-287, -80), "A3_TOWN_2": (168, -279), "A3_TOWN_1": (467, -58), "A3_TOWN_4": (-587, 86), "A3_TOWN_12": (-231, 574)},
            184: {"A3_TOWN_4": (-109, -146), "A3_TOWN_5": (-81, 206), "A3_TOWN_3": (191, -311), "A3_TOWN_12": (247, 342), "A3_TOWN_13": (-323, 530)},
            185: {"A3_TOWN_5": (223, 40), "A3_TOWN_13": (-19, 364), "A3_TOWN_4": (195, -312), "A3_TOWN_12": (551, 176), "A3_TOWN_20": (-549, 184)},
            186: {"A3_TOWN_7": (-195, -118), "A3_TOWN_20": (-130, 237), "A3_TOWN_8": (-269, 308), "A3_TOWN_13": (400, 417), "A3_TOWN_5": (642, 93)},
            187: {"A3_TOWN_8": (161, 107), "A3_TOWN_9": (-108, 165), "A3_TOWN_7": (236, -319), "A3_TOWN_20": (300, 36), "A3_TOWN_11": (-618, 50)},
            188: {"A3_TOWN_9": (173, 57), "A3_TOWN_11": (-337, -58), "A3_TOWN_8": (442, -1), "A3_TOWN_20": (581, -72), "A3_TOWN_7": (517, -227)},
            #187: {"A3_TOWN_8": (161, 207), "A3_TOWN_9": (-108, 265), "A3_TOWN_7": (236, -219), "A3_TOWN_20": (300, 136), "A3_TOWN_11": (-618, 150)},
            #188: {"A3_TOWN_9": (173, 157), "A3_TOWN_11": (-337, 42), "A3_TOWN_8": (442, 99), "A3_TOWN_20": (581, 28), "A3_TOWN_7": (517, -327)},
            189: {"A3_TOWN_5": (10, -182), "A3_TOWN_13": (-232, 142), "A3_TOWN_14": (-7, 337), "A3_TOWN_12": (338, -46), "A3_TOWN_15": (722, 143)},
            190: {"A3_TOWN_12": (27, -198), "A3_TOWN_16": (831, 258), "A3_TOWN_14": (-318, 185), "A3_TOWN_15": (411, -9), "A3_TOWN_5": (-301, -334), "A3_TOWN_13": (-543, -10), "A3_TOWN_17": (707, 541)},
            191: {"A3_TOWN_15": (-79, -256), "A3_TOWN_16": (341, 11), "A3_TOWN_17": (217, 294), "A3_TOWN_18": (542, 408), "A3_TOWN_19": (779, 171)},
            192: {"A3_TOWN_17": (-187, 78), "A3_TOWN_16": (-63, -205), "A3_TOWN_18": (138, 192), "A3_TOWN_19": (375, -45)},
            # Trav
            220: {"TRAV_0": (445, 384), "TRAV_20": (-259, 267), "TRAV_1": (-248, -139), "TRAV_2": (-682, 21), "TRAV_21": (25, 180)},
            221: {"TRAV_2": (-153, -101), "TRAV_3": (-125, 201), "TRAV_20": (270, 145), "TRAV_1": (281, -261), "TRAV_4": (-459, 122)},
            222: {"TRAV_5": (-218, 106), "TRAV_4": (120, 230), "TRAV_2": (426, 7), "TRAV_7": (-719, -166), "TRAV_7_V2": (-719, -166), "TRAV_1": (862, -153)},
            223: {"TRAV_5": (344, 123), 'TRAV_4': (682, 247), "TRAV_8": (-353, -31), "TRAV_7": (-157, -149), "TRAV_7_V2": (-157, -149), "TRAV_22": (-368, -222), "TRAV_22_V2": (-368, -222), "TRAV_23": (-579, 116)},
            224: {'TRAV_7': (411, -129), 'TRAV_7_V2': (411, -129), 'TRAV_27': (-363, 163), "TRAV_8": (214, -11), "TRAV_23": (-11, 136), "TRAV_10": (-130, -187), "TRAV_10_V2": (-130, -187), "TRAV_24": (-274, 15), "TRAV_22": (200, -202), "TRAV_22_V2": (200, -202)},
            225: {'TRAV_27': (96, 359), 'TRAV_8': (670, 187), 'TRAV_7': (867, 69), 'TRAV_7_V2': (867, 69), "TRAV_11": (10, 214), "TRAV_19": (-298, 539), "TRAV_24": (181, 213), "TRAV_12": (-408, -73), "TRAV_25": (-538, 132), 'TRAV_225_V3_0': (549, -147), 'TRAV_225_V3_1': (555, 125), 'TRAV_225_V3_3': (-149, -229), 'TRAV_225_V3_7': (-242, 13), 'TRAV_V2_2': (-27, 103), 'TRAV_225_V3_2': (31, 135)},
            226: {"TRAV_12": (-75, -172), "TRAV_25": (-205, 33), "TRAV_13": (-252, 195), "TRAV_11": (343, 115), "TRAV_18": (-514, 373), "TRAV_19": (35, 440), "TRAV_17": (-231, 242), "TRAV_27": (428, 263), "TRAV_29": (-929, 334), "TRAV_28": (-614, 338)},
            227: {"TRAV_11": (65, -42), "TRAV_24": (236, -43), "TRAV_19": (-243, 283), 'TRAV_18': (-792, 216), "TRAV_12": (-356, -330), "TRAV_25": (-483, -124), 'TRAV_27': (154, 104)},
            228: {"TRAV_13": (8, 9), "TRAV_17": (29, 56), "TRAV_25": (58, -152), "TRAV_16": (-198, -110), "TRAV_18": (-251, 188)},
            229: {"TRAV_18": (-250, 58), "TRAV_25": (59, -282), "TRAV_17": (30, -74), "TRAV_13": (9, -121), "TRAV_16": (-138, -241)},
            230: {"TRAV_19": (157, 39), "TRAV_18": (-392, -28), "TRAV_17": (-112, -160), "TRAV_13": (-133, -207), "TRAV_25": (-83, -368)},
            300: {"TRAV_V3_4": (-101, 134), "TRAV_V3_5": (72, 220), "TRAV_V3_1": (237, -24), "TRAV_V3_3": (-318, 224), "TRAV_V3_11": (472, 39),
                "TRAV_16": (129, -86), "TRAV_V2_0": (472, 65), "TRAV_17": (357, 84), "TRAV_12": (512, -333),
            },
            301: {"TRAV_V3_7": (178, -33), "TRAV_V3_6": (170, 157), "TRAV_V3_0": (88, -235), "TRAV_V3_5": (-335, -95), "TRAV_V3_8": (444, -108)},
            302: {"TRAV_V3_0": (-18, 6), "TRAV_V3_7": (73, 208), "TRAV_V3_8": (339, 133), "TRAV_V3_6": (65, 398), "TRAV_V3_5": (-440, 146)},
            304: {"TRAV_V2_4": (125, -148), "TRAV_V2_3": (-187, 55), "TRAV_V2_1": (-207, 59), "TRAV_V2_2": (267, 183), "TRAV_V2_0": (-159, 403)},
            # A2 town
            400: {"A2_TOWN_2": (-169, 160), "A2_TOWN_0": (290, -114), "A2_TOWN_3": (-348, 225), "A2_TOWN_1": (-345, -374)},
            401: {"A2_TOWN_3": (45, -202), "A2_TOWN_7": (-40, 266), "A2_TOWN_2": (224, -267), "A2_TOWN_6": (-505, 26), "A2_TOWN_5": (116, 203)},
            402: {"A2_TOWN_8": (182, 121), "A2_TOWN_6": (103, -348), "A2_TOWN_11": (128, 357), "A2_TOWN_9": (-324, 223), "A2_TOWN_12": (-213, 500)},
            403: {"A2_TOWN_11": (161, -18), "A2_TOWN_12": (-180, 125), "A2_TOWN_9": (-291, -152), "A2_TOWN_8": (215, -254), "A2_TOWN_13": (149, 392)},
            404: {"A2_TOWN_14": (79, 190), "A2_TOWN_15": (244, -12), "A2_TOWN_13": (-270, 123), "A2_TOWN_11": (-258, -287), "A2_TOWN_12": (-599, -143)},
            405: {"A2_TOWN_10": (65, -175), "A2_TOWN_17": (-108, 164), "A2_TOWN_16": (-304, -11), "A2_TOWN_9": (319, -68), "A2_TOWN_18": (-415, -284)},
            406: {"A2_TOWN_18": (108, -143), "A2_TOWN_16": (219, 129), "A2_TOWN_19": (-293, 21), "A2_TOWN_17": (415, 304), "A2_TOWN_10": (588, -34)},
            408: {"A2_TOWN_20": (-26, -109), "A2_TOWN_25": (-82, 278), "A2_TOWN_19": (344, 38), "A2_TOWN_18": (745, -125), "A2_TOWN_26": (-831, -73)},
            409: {"A2_TOWN_14": (477, 294), "A2_TOWN_13": (128, 226), "A2_TOWN_11": (140, -182), "A2_TOWN_12": (-201, -40)},
            410: {"A2_TOWN_13": (416, 82), "A2_TOWN_12": (87, -184), "A2_TOWN_21": (-211, 10), "A2_TOWN_22": (-178, 269)},
            411: {"A2_TOWN_22": (298, 0), "A2_TOWN_23": (0, 190), "A2_TOWN_21": (265, -260), "A2_TOWN_24": (-150, -185)},
            # Arcane
            450: {"ARC_START": (49, 62)},
            453: {"ARC_START": (-259, 62)},
            456: {"ARC_START": (145, 264)},
            459: {"ARC_START": (-356, 258)},
            461: {"ARC_ALTAR": (60, 120), "ARC_ALTAR3": (-272, 200), "ARC_CENTER_2": (67, 41), "ARC_END_STAIRS": (76, -344), "ARC_END_STAIRS_2": (60, -160)},
            462: {"ARC_PLATFORM_1": (0, -100), "ARC_PLATFORM_2": (50, -100), "ARC_PLATFORM_3": (70, 0)},
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

            ########################
            # Diablo Chaos Sanctuary
            ########################
            600: {"DIABLO_1": (-127, -11), "DIABLO_0": (310, -121),}, #waypoint
            601: {"DIABLO_CS_ENTRANCE_3": (5, -130), "DIABLO_CS_ENTRANCE_0": (145, 128), "DIABLO_CS_ENTRANCE_2": (-305, -30), }, # entrance to cs -> rebuild with new templates
            # PENTRAGRAM
            602: {"DIA_NEW_PENT_TP": (-275, 193), "DIA_NEW_PENT_5": (-6, -31), "DIA_NEW_PENT_0": (5, -181), "DIA_NEW_PENT_2": (133, 370), "DIA_NEW_PENT_1": (439, 16), "DIA_NEW_PENT_3": (-509, 240), "DIA_NEW_PENT_6": (-534, 205), },
            #Trash Entrance Calibration Node
            603: {"DIA_CS_ENTRANCE_603": (121-111, 100-267),"DIA_CS_ENTRANCE_603_2": (121-111+700, 100-267-103),"DIA_CS_ENTRANCE_1": (121, 100), "DIA_CS_ENTRANCE_3": (42, 321), "DIA_CS_ENTRANCE_0": (-314, -85), "DIA_CS_ENTRANCE_4": (-318, 193), "DIA_CS_ENTRANCE_5": (-372, 73), "DIA_CS_ENTRANCE_7": (-36, 443), "DIA_CS_ENTRANCE_6": (-317, 341), }, # outside cs entrance
            604: {"DIA_CS_ENTRANCE_6": (284, -38), "DIA_CS_ENTRANCE_4": (282, -186), "DIA_CS_ENTRANCE_5": (228, -306), "DIA_CS_ENTRANCE_7": (564, 64), "DIA_CS_ENTRANCE_3": (642, -58), "DIA_CS_ENTRANCE_1": (721, -279), }, # inside cs entrance (677)
            605: {"DIABLO_ENTRANCE_50": (550, -220),"DIABLO_ENTRANCE_51": (-240, -228), "DIABLO_ENTRANCE_52": (70, 15), "DIABLO_ENTRANCE_53": (280, -142), "DIABLO_ENTRANCE_54": (-130, -80), "DIABLO_ENTRANCE_55": (35, -145), "DIABLO_ENTRANCE2_50": (525, -10),"DIABLO_ENTRANCE2_51": (-435, 208),"DIABLO_ENTRANCE2_52": (-540, -250), "DIABLO_ENTRANCE2_53": (342, -12),"DIABLO_ENTRANCE2_54": (185, 10),"DIABLO_ENTRANCE2_55": (522, 229), "DIABLO_ENTRANCE2_56": (370, 230),}, #LC Hall1
            #Trash Pent - Seal Calibration Nodes (currently not used)
            606: {"DIA_TRASH_A_6": (146, -35), "DIA_TRASH_A_1": (104, 136), "DIA_TRASH_A_2": (-262, -36), "DIA_TRASH_A_0": (294, 48), "DIA_TRASH_A_3": (-368, 70), "DIA_TRASH_A_7": (446, 22), "DIA_TRASH_A_9": (-280, 391), "DIA_TRASH_A_10": (262, -484), }, #Trash Pent A
            607: {'DIA_TRASH_B_6': (325, 7), 'DIA_TRASH_B_9': (325, 13), 'DIA_TRASH_B_15': (-182, 108), 'DIA_TRASH_B_19': (-260, -165), 'DIA_TRASH_B_10': (-189, 107), 'DIA_TRASH_B_18': (653, -254), 'DIA_TRASH_B_5': (323, 13), 'DIA_TRASH_B_11': (582, -55), 'DIA_TRASH_B_21': (676, 313), 'DIA_TRASH_B_2': (326, 11), 'DIA_TRASH_B_7': (320, 11), 'DIA_TRASH_B_20': (796, 243), 'DIA_TRASH_B_13': (-190, 107), 'DIA_TRASH_B_17': (-196, 103), 'DIA_TRASH_B_14': (-190, 108), 'DIA_TRASH_B_22': (-678, -150), 'DIA_TRASH_B_16': (-184, 109), 'DIA_TRASH_B_12': (-184, 110), 'DIA_TRASH_B_3': (333, 19), 'DIA_TRASH_B_1': (327, 18), 'DIA_TRASH_B_8': (329, 17), 'DIA_TRASH_B_4': (326, 15), 'DIA_TRASH_B_24': (343, -220)}, #trash pent b
            608: {'DIA_TRASH_C_4': (395, 242), 'DIA_TRASH_C_5': (325, 121), 'DIA_TRASH_C_6': (317, 110), 'DIA_TRASH_C_12': (-37, -173), 'DIA_TRASH_C_1': (-215, 227), 'DIA_TRASH_C_3': (105, 301), 'DIA_TRASH_C_7': (-211, 220), 'DIA_TRASH_C_0': (656, 458), 'DIA_TRASH_C_10': (317, 118), 'DIA_TRASH_C_2': (-213, 225), 'DIA_TRASH_C_13': (-33, -172), 'DIA_TRASH_C_8': (604, -187), 'DIA_TRASH_C_11': (-32, -170), 'DIA_TRASH_C_19': (27, -462), 'DIA_TRASH_C_9': (600, -190), 'DIA_TRASH_C_14': (-36, -172), 'DIA_TRASH_C_15': (-34, -170), 'DIA_TRASH_C_18': (-36, -172), 'DIA_TRASH_C_16': (-36, -171)}, #Trash Pent C
            # Entrance 1 Hall3
            609: {"DIABLO_ENTRANCE2_HALL3_3": (375+28,-5+50), "DIABLO_ENTRANCE2_HALL3_4": (50+51,-170+10), "DIABLO_ENTRANCE2_HALL3_5": (150+53,-170+16), "DIABLO_ENTRANCE2_HALL3_6": (160+127,264+11),}, #Entrance 2 Hall3

            #CALIBRATION SPOTS FOR LAYOUT CHECKS
            610620: {"DIA_A2Y4_0": (43, 131), "DIA_A2Y4_16": (44, 152),"DIA_A1L_CAL_7": (-76, -213), "DIA_A1L_CAL_2": (220, -114), "DIA_A1L_CAL_1": (232, 102), "DIA_A1L_CAL_3": (-259, 166), "DIA_A1L_CAL_5": (-357, -174), "DIA_A1L_CAL_10": (-170, 379), "DIA_A1L_CAL_8": (-308, 282), "DIA_A1L_CAL_12": (-395, -218),},
            630640: {"DIA_B1S2_6": (253, -156), "DIA_B1S2_7": (78, -233), "DIA_B1S2_20": (8, 303),"DIA_B1S2_24_OPEN": (-345, -57),"DIA_B1S2_24_CLOSED": (-345, -57),"DIA_B1S2_24_MOUSEOVER": (-345, -57),"DIA_B1S2_25": (278, 121),  "DIA_B1S2_26": (120, 7),"DIA_B2U_CAL_9": (-102, -96), "DIA_B2U_CAL_10": (79, -191), "DIA_B2U_CAL_5": (-153, 164), "DIA_B2U_CAL_13": (94, -207), "DIA_B2U_CAL_4": (32, 243), "DIA_B2U_CAL_8": (-262, -66), "DIA_B2U_CAL_6": (-285, 141), "DIA_B2U_CAL_1": (347, 33),}, #not used anymore.
            650660: {"DIA_C1F7_48": (-61, 13), "DIA_C1F7_39": (71, 101), "DIA_C1F7_44": (129, -56), "DIA_C1F7_49": (-139, -76), "DIA_C1F7_52": (141, -82), "DIA_C1F7_51": (147, 119), "DIA_C1F7_36": (146, 271), "DIA_C1F7_35": (276, 194), "DIA_C2G_CAL_0": (-247, -56), "DIA_C2G_CAL_1": (-379, -64), "DIA_C2G_CAL_2": (134, -158), "DIA_C2G_CAL_3": (52, 157), "DIA_C2G_CAL_4": (269, 196), "DIA_C2G_CAL_6": (200, -22), "DIA_C2G_CAL_7": (166, -83), "DIA_C2G_CAL_8": (248, -151), "DIA_C2G_CAL_9": (-87, 55), "DIA_C2G_CAL_10": (377, -220), "DIA_C2G_CAL_11": (46, -30), "DIA_C2G_CAL_12": (172, -34), "DIA_C2G_CAL_13": (118, -177), "DIA_C2G_CAL_14": (130, -290), "DIA_C2G_CAL_15": (290, -341), "DIA_C2G_CAL_16": (-218, -148), "DIA_C2G_CAL_17": (40, 66), "DIA_C2G_CAL_18": (745, 70), "DIA_C2G_CAL_19": (666, 231),},

            # SEAL A1L Vizier
            610: {'DIA_A1L2_24': (-329, 18),'DIA_A1L2_20': (-423, 160),'DIA_A1L2_21': (-214, -247),'DIA_A1L2_22': (-123, 143), 'DIA_A1L2_23': (134, -105), "DIA_A1L2_8": (-99, 161), "DIA_A1L2_4": (299, -13), "DIA_A1L2_1": (49, 300), "DIA_A1L2_7": (160, 389), "DIA_A1L2_2": (-60, 480), "DIA_A1L2_3": (212, 447), "DIA_A1L2_18": (340, 460), "DIA_A1L2_0": (571, -107), "DIA_A1L2_6": (358, 467), }, #approach1
            611: {'DIA_A1L2_22': (-338, 41),'DIA_A1L2_23': (-80, -212), "DIA_A1L2_4": (85, -120), "DIA_A1L2_1": (-165, 193), "DIA_A1L2_7": (-53, 282), "DIA_A1L2_8": (-313, 54), "DIA_A1L2_3": (-2, 339), "DIA_A1L2_18": (126, 353), "DIA_A1L2_9": (140, 350), "DIA_A1L2_6": (144, 360), "DIA_A1L2_0": (357, -214), },#safe-dist
            612: {"DIA_A1L2_9": (-126, 171), "DIA_A1L2_6": (-122, 181), "DIA_A1L2_18": (-140, 174), "DIA_A1L2_3": (-268, 160), "DIA_A1L2_7": (-319, 103), "DIA_A1L2_4": (-181, -299), "DIA_A1L2_5_OPEN": (335, 110), "DIA_A1L2_5_CLOSED": (335, 110), "DIA_A1L2_5_MOUSEOVER": (335, 110), "DIA_A1L2_0": (91, -393), "DIA_A1L2_1": (-431, 14), }, # seal boss far
            613: {"DIA_A1L2_6": (62, -157), "DIA_A1L2_18": (44, -164), "DIA_A1L2_9": (58, -167), "DIA_A1L2_13": (-170, -52), "DIA_A1L2_3": (-84, -178), "DIA_A1L2_7": (-136, -235), "DIA_A1L2_14_OPEN": (-251, 155), "DIA_A1L2_14_CLOSED": (-251, 155), "DIA_A1L2_14_MOUSEOVER": (-251, 155), "DIA_A1L2_2": (-356, -144), "DIA_A1L2_19": (344, 198), },# seal fake far
            614: {"DIA_A1L2_14_OPEN": (-109, 10), "DIA_A1L2_14_CLOSED": (-109, 10), "DIA_A1L2_14_MOUSEOVER": (-109, 10), "DIA_A1L2_14_CLOSED_DARK": (-109, 10),"DIA_A1L2_13": (-28, -196), "DIA_A1L2_3": (58, -322), "DIA_A1L2_2": (-214, -289), "DIA_A1L2_18": (186, -308), "DIA_A1L2_6": (204, -302), "DIA_A1L2_9": (200, -312), "DIA_A1L2_7": (6, -380), "DIA_A1L2_1": (-105, -469), }, # seal fake close
            615: {"DIA_A1L2_10": (314, -49), "DIA_A1L2_18": (-354, 39), "DIA_A1L2_19": (-53, 396), "DIA_A1L2_3": (-481, 25), "DIA_A1L2_7": (-533, -33), "DIA_A1L2_0": (-122, -528), "DIA_A1L2_4": (-394, -434), "DIA_A1L2_13": (-567, 151), "DIA_A1L2_1": (-644, -121), }, # seal boss close
            619: {"DIA_A2Y4_0": (43, 131), "DIA_A2Y4_16": (44, 152), "DIA_A1L_CAL_7": (-76, -213), "DIA_A1L_CAL_2": (220, -114), "DIA_A1L_CAL_1": (232, 102), "DIA_A1L_CAL_3": (-259, 166), "DIA_A1L_CAL_5": (-357, -174), "DIA_A1L_CAL_10": (-170, 379), "DIA_A1L_CAL_8": (-308, 282), "DIA_A1L_CAL_12": (-395, -218), }, # calibration point for layout check MERGED  619 and  620 templates from both seals to have a "common node" for calibration before layout check

            # SEAL A2Y Vizier
            620: {"DIA_A2Y4_0": (43, 131), "DIA_A2Y4_16": (44, 152),}, #approach
            621: {"DIA_A2Y4_1": (-13, 92), "DIA_A2Y4_5": (76, 81), "DIA_A2Y4_3": (-5, -255), "DIA_A2Y4_10": (231, 173), "DIA_A2Y4_25": (237, 175), "DIA_A2Y4_0": (319, -5), "DIA_A2Y4_16": (320, 16), }, #approach
            622: {"DIA_A2Y4_12": (23, -165), "DIA_A2Y4_41": (-99, 182), "DIA_A2Y4_36_OPEN": (320, 466), "DIA_A2Y4_15": (-116, 180), "DIA_A2Y4_10": (260, -81), "DIA_A2Y4_25": (267, -79), "DIA_A2Y4_14": (-348, 68), "DIA_A2Y4_13": (-342, 136), "DIA_A2Y4_20": (-269, 269), "DIA_A2Y4_2": (-164, -375), }, #safe-dist
            623: {"DIA_A2Y4_43": (486, -350), "DIA_A2Y4_25": (38, -210), "DIA_A2Y4_10": (31, -212), "DIA_A2Y4_20": (-500, 146), "DIA_A2Y4_18": (192, -173), "DIA_A2Y4_26": (190, -178), "DIA_A2Y4_21": (157, 217), "DIA_A2Y4_41": (-329, 52), "DIA_A2Y4_15": (-345, 51), "DIA_A2Y4_11": (248, -253), "DIA_A2Y4_12": (-206, -294), "DIA_A2Y4_16": (121, -369), "DIA_A2Y4_0": (121+1, -369-24),}, #center
            624: {"DIA_A2Y4_29_CLOSED": (440, 135), "DIA_A2Y4_29_OPEN": (440, 135), "DIA_A2Y4_29_MOUSEOVER": (440, 135),"DIA_A2Y4_43": (43, -218), "DIA_A2Y4_24": (23, -115), "DIA_A2Y4_4": (56, -127), "DIA_A2Y4_20": (-934, 274), "DIA_A2Y4_15": (-780, 186), "DIA_A2Y4_13": (-1000, 140), "DIA_A2Y4_27": (-33, 182), "DIA_A2Y4_23": (-32, 187), "DIA_A2Y4_11": (-187, -121), "DIA_A2Y4_22": (73, 226), "DIA_A2Y4_26": (-245, -45), "DIA_A2Y4_30": (253, -56), "DIA_A2Y4_16": (-319, -238),"DIA_A2Y4_0": (-319+1, -238-24),}, #left far fake
            625: {"DIA_A2Y4_29_CLOSED": (150, -28), "DIA_A2Y4_29_OPEN": (150, -28), "DIA_A2Y4_29_MOUSEOVER": (150, -28), "DIA_A2Y4_43": (-245, -380), "DIA_A2Y4_22": (-217, 65), "DIA_A2Y4_23": (-322, 26), "DIA_A2Y4_30": (-37, -218), "DIA_A2Y4_32": (235, -142),"DIA_A2Y4_33": (336, -62), "DIA_A2Y4_16": (-604, -400),"DIA_A2Y4_0": (-604+1, -400-24),}, #left close fake
            626: {"DIA_A2Y4_35": (296, 68), "DIA_A2Y4_36_OPEN": (-115, 70), "DIA_A2Y4_36_CLOSED": (-115, 70), "DIA_A2Y4_36B_CLOSED": (-115, 70), "DIA_A2Y4_36B_CLOSED": (-115, 70), "DIA_A2Y4_36_MOUSEOVER": (-115, 70), "DIA_A2Y4_37": (-486, 76), },# right close boss
            627: {"DIA_A2Y4_13": (-472, -187),"DIA_A2Y4_15": (-246, -143), "DIA_A2Y4_20": (-399, -54), "DIA_A2Y4_36_OPEN": (205, 197), "DIA_A2Y4_36_CLOSED": (205, 197),"DIA_A2Y4_36_MOUSEOVER": (205, 197),"DIA_A2Y4_37": (-166, 203), "DIA_A2Y4_38": (-288, 83), "DIA_A2Y4_39": (-291, 89), "DIA_A2Y4_40": (-256, 89), "DIA_A2Y4_41": (-229, -143), }, # right far boss

            # SEAL B1S De Seis
            630: {"DIA_B1S3_1": (201, -191), "DIA_B1S3_6": (369, 38), "DIA_B1S3_0": (494, -45), "DIA_B1S3_3": (489, -172), "DIA_B1S3_4": (723, -39),}, #cross river
            631: {"DIA_B1S2_2": (-232, -78), "DIA_B1S2_3": (169, -361), "DIA_B1S2_5": (-225, -86), "DIA_B1S2_12": (-29, 199), "DIA_B1S2_13": (-358, 52), "DIA_B1S2_15": (-42, 210), "DIA_B1S2_16": (168, 124), "DIA_B1S2_18": (-197, 117), }, #corner left
            632: {"DIA_B1S2_2": (87, -224), "DIA_B1S2_8": (-330, -95), "DIA_B1S2_11": (-120, -306), "DIA_B1S2_12": (290, 53), "DIA_B1S2_13": (-38, -93), "DIA_B1S2_15": (277, 64), "DIA_B1S2_17": (-200, 25), "DIA_B1S2_18": (122, -29), "DIA_B1S2_19": (-174, 287), "DIA_B1S2_21": (-307, -67), }, #corner
            633: {"DIA_B1S2_2": (99, 278), "DIA_B1S2_6": (37, -391), "DIA_B1S2_8": (-285, -280), "DIA_B1S2_13": (352, -100), "DIA_B1S2_19": (216, 279), "DIA_B1S2_20": (-208, 69), "DIA_B1S2_21": (83, -75), "DIA_B1S2_25": (62, -114), "DIA_B1S2_26": (-96, -228), }, #corner right
            634: {"DIA_B1S2_6": (253, -156), "DIA_B1S2_7": (78, -233), "DIA_B1S2_20": (8, 303),"DIA_B1S2_24_OPEN": (-345, -57),"DIA_B1S2_24_CLOSED": (-345, -57),"DIA_B1S2_24_MOUSEOVER": (-345, -57),"DIA_B1S2_25": (278, 121),  "DIA_B1S2_26": (120, 7),}, #seal close
            635: {"DIA_B1S2_7": (315, -167), "DIA_B1S2_8": (169, 21), "DIA_B1S2_24_OPEN": (-108, 9), "DIA_B1S2_24_CLOSED": (-108, 9),"DIA_B1S2_24_MOUSEOVER": (-108, 9),"DIA_B1S2_26": (357, 73), "DIA_B1S2_27": (-94, -146),"DIA_B1S2_29": (-325, -6),  "DIA_B1S2_30": (143, 21),}, # seal far
            636: {"DIA_B1S2_4": (383, -111), "DIA_B1S2_5": (187, 256), "DIA_B1S2_6": (-252, 100), "DIA_B1S2_7": (-427, 23), "DIA_B1S2_11": (-20, 177),  "DIA_B1S2_25": (-228, 377), }, #cross river
            637: {"DIA_B1S2_2": (-210, 122), "DIA_B1S2_4": (-20, -251), "DIA_B1S2_5": (-216, 116), "DIA_B1S2_6": (-663, -35), "DIA_B1S2_7": (-838, -112), "DIA_B1S2_11": (-430, 42), "DIA_B1S2_26": (-796, 127), }, #close circle

            # SEAL B2U De Seis
            640: {"DIA_B2U2_14": (-183, -53), "DIA_B2U2_0": (-20, 196), "DIA_B2U2_1": (-177, -96), "DIA_B2U2_2": (-299, 40), "DIA_B2U2_5": (-414, 168), "DIA_B2U2_8": (-431, 166), "DIA_B2U2_4": (-278, 371), "DIA_B2U2_6": (-462, -232), "DIA_B2U2_3": (-431, 310), "DIA_B2U2_13": (-540, -182), }, #approach
            641: {"DIA_B2U2_2": (-11, -111), "DIA_B2U2_5": (-126, 17), "DIA_B2U2_8": (-142, 15), "DIA_B2U2_3": (-143, 159), "DIA_B2U2_4": (11, 220), "DIA_B2U2_14": (105, -204), "DIA_B2U2_1": (111, -247), "DIA_B2U2_0": (268, 45), "DIA_B2U2_7": (-308, -148), "DIA_B2U2_13": (-252, -334), },#  approach
            642: {"DIA_B2U2_10": (-96, 90), "DIA_B2U2_7": (122, -107), "DIA_B2U2_17": (-65, 216), "DIA_B2U2_5": (304, 58), "DIA_B2U2_13": (178, -293), "DIA_B2U2_3": (287, 200), "DIA_B2U2_15": (50, 366), "DIA_B2U2_2": (419, -70), "DIA_B2U2_6": (256, -342), "DIA_B2U2_20": (-406, 151), }, #safe-dist
            643: {"DIA_B2U2_3": (75, -82), "DIA_B2U2_4": (229, -21), "DIA_B2U2_5": (92, -224), "DIA_B2U2_6": (-122, 246), "DIA_B2U2_13": (-201, 296), "DIA_B2U2_10": (-308, -192), "DIA_B2U2_1": (163, 382), "DIA_B2U2_17": (-407, 105), "DIA_B2U2_15": (-292, 255) }, #boss seal far
            644: {"DIA_B2U2_15": (50, 6),  "DIA_B2U2_13": (141, 47), "DIA_B2U2_17": (-65, -144), "DIA_B2U2_6": (220, -3), "DIA_B2U2_7": (85, 233), "DIA_B2U2_16_OPEN": (-308, -18), "DIA_B2U2_16_CLOSED": (-308, -18), "DIA_B2U2_16_MOUSEOVER": (-308, -18), "DIA_B2U2_22": (-334, 149), "DIA_B2U2_19": (-344, 270), "DIA_B2U2_10": (34, -441), }, # boss seal close
            645: {"DIA_B2U2_16_CLOSED": (81, 34), "DIA_B2U2_16_OPEN": (81, 34), "DIA_B2U2_16_MOUSEOVER": (81, 34),"DIA_B2U2_20": (-18, -157), "DIA_B2U2_18": (-185, 98), "DIA_B2U2_19": (44, 322), "DIA_B2U2_17": (323, -92), "DIA_B2U2_12": (-123, 377),  "DIA_B2U2_13": (530, 99), "DIA_B2U2_15": (439, 58),}, # boss seal far
            646: {"DIA_B2U2_1": (37, 203), "DIA_B2U2_14": (31, 246), "DIA_B2U2_6": (-248, 67), "DIA_B2U2_13": (-327, 117), }, #safe-dist2
            647: {"DIA_B2U_CAL_9": (-102, -96), "DIA_B2U_CAL_10": (79, -191), "DIA_B2U_CAL_5": (-153, 164), "DIA_B2U_CAL_13": (94, -207), "DIA_B2U_CAL_4": (32, 243), "DIA_B2U_CAL_8": (-262, -66), "DIA_B2U_CAL_6": (-285, 141), "DIA_B2U_CAL_1": (347, 33), }, #calibdation node
            648: {"DIA_B2U_CAL_14": (19, -193), "DIA_B2U_CAL_13": (-218, -46), "DIA_B2U_CAL_17": (266, 49), "DIA_B2U_CAL_18": (217, 222), "DIA_B2U_CAL_16": (377, 79), "DIA_B2U_CAL_15": (524, 85), "DIA_B2U_CAL_8": (-574, 95), "DIA_B2U_CAL_19": (698, -131), },#approach calibration node 2
            649: {"DIA_B2U_CAL_17": (-59, 210), "DIA_B2U_CAL_16": (52, 240), "DIA_B2U_CAL_14": (-306, -32), "DIA_B2U_CAL_15": (199, 246), "DIA_B2U_CAL_19": (373, 30), "DIA_B2U_CAL_18": (-108, 383), "DIA_B2U_CAL_13": (-543, 115), "DIA_B2U_CAL_8": (-899, 256), }, #approach calibration node1 (close to river)

            #SEAL C1F_NEW Infector
            650: {"DIA_C1F7_5": (-37, 150), "DIA_C1F7_2": (91, -130), "DIA_C1F7_4": (-184, 91), "DIA_C1F7_7": (168, -183), "DIA_C1F7_8": (-332, 109), "DIA_C1F7_20": (-43, -347), "DIA_C1F7_26": (-45, -351), "DIA_C1F7_17": (-42, -353), }, #approach
            651: {"DIA_C1F7_20": (-22, -106), "DIA_C1F7_26": (-24, -111), "DIA_C1F7_17": (-21, -113), "DIA_C1F7_2": (112, 110), "DIA_C1F7_7": (189, 57), "DIA_C1F7_16": (188, -207), "DIA_C1F7_14": (-21, -301), "DIA_C1F7_15": (-169, -256), },#seal boss far
            652: {"DIA_C1F7_21": (-41, -121), "DIA_C1F7_15": (-14, -130), "DIA_C1F7_26": (130, 14), "DIA_C1F7_27": (-91, -98), "DIA_C1F7_20": (133, 19), "DIA_C1F7_17": (134, 13), "DIA_C1F7_14": (134, -175), "DIA_C1F7_13": (-251, 4), },# seal boss close
            653: {"DIA_C1F7_41": (5, -124), "DIA_C1F7_37": (100, -86), "DIA_C1F7_13": (112, -70), "DIA_C1F7_23": (-53, -134), "DIA_C1F7_32": (-81, -157), "DIA_C1F7_38": (-100, 204), "DIA_C1F7_31": (-29, 229), "DIA_C1F7_42": (-155, -179), },#center & safe_dist
            654: {"DIA_C1F7_704_SUPPORT1": (715, -130),"DIA_C1F7_704_SUPPORT2": (515, -65), "DIA_C1F7_704_SUPPORT3": (318, -155),"DIA_C1F7_704_SUPPORT4": (185, -108), "DIA_C1F7_43": (106, -155), "DIA_C1F7_28": (59, 215), "DIA_C1F7_47": (169, -150), "DIA_C1F7_42": (267, -82), "DIA_C1F7_33": (-233, 191), "DIA_C1F7_29": (-26, 310), "DIA_C1F7_50": (-325, 52), "DIA_C1F7_35": (-330, 46), },#seal fake far
            655: {"DIA_C1F7_33": (-106, 28), "DIA_C1F7_34": (-19, 170), "DIA_C1F7_29": (101, 147), "DIA_C1F7_28": (186, 52), "DIA_C1F7_50": (-197, -110), "DIA_C1F7_35": (-202, -116), "DIA_C1F7_36": (-332, -39), "DIA_C1F7_51": (-331, -191), },#seal fake close
            656: {"DIA_C1F7_48": (-61, 13), "DIA_C1F7_39": (71, 101), "DIA_C1F7_44": (129, -56), "DIA_C1F7_49": (-139, -76), "DIA_C1F7_52": (141, -82), "DIA_C1F7_51": (147, 119), "DIA_C1F7_36": (146, 271), "DIA_C1F7_35": (276, 194), },#layoutcheck

            #SEAL C2G_new Infector
            660: {"DIA_C2G2_2": (-182, 71), "DIA_C2G2_3": (-258, 115), "DIA_C2G2_18": (151, -250), "DIA_C2G2_6": (-310, -9), "DIA_C2G2_15": (430, -74), "DIA_C2G2_11": (-272, -406), }, # approach
            661: {"DIA_C2G2_14": (33, 153), "DIA_C2G2_5": (20, 226), "DIA_C2G2_11": (322, -90), "DIA_C2G2_6": (284, 307), "DIA_C2G2_17": (-420, 110), "DIA_C2G2_10": (-429, 146), "DIA_C2G2_8": (-407, 277),  "DIA_C2G2_22": (56, 514), },# seal boss close
            662: {"DIA_C2G2_15": (-54, -160), "DIA_C2G2_12": (271, -138), "DIA_C2G2_17": (-137, 280), "DIA_C2G2_10": (-146, 316), "DIA_C2G2_9": (-251, 354), "DIA_C2G2_7_CLOSED": (433, 88), "DIA_C2G2_7_OPEN": (433, 88),"DIA_C2G2_7_MOUSEOVER": (433, 88),"DIA_C2G2_14": (315, 323), "DIA_C2G2_8": (-124, 447), }, # seal boss far
            663: {"DIA_C2G2_9": (94, 181), "DIA_C2G2_17": (207, 107), "DIA_C2G2_10": (198, 143), "DIA_C2G2_21_OPEN": (16, 297), "DIA_C2G2_21_CLOSED": (16, 297),"DIA_C2G2_21_MOUSEOVER": (16, 297),"DIA_C2G2_8": (221, 274), "DIA_C2G2_15": (290, -333), "DIA_C2G2_20": (-435, 93), "DIA_C2G2_19": (-504, 24), }, # safe dist
            664: {"DIA_C2G2_20": (-214, -66), "DIA_C2G2_21_OPEN": (237, 137), "DIA_C2G2_21_CLOSED": (237, 137),"DIA_C2G2_21_MOUSEOVER": (237, 137),"DIA_C2G2_19": (-284, -135), "DIA_C2G2_9": (315, 22), "DIA_C2G2_10": (419, -16), "DIA_C2G2_17": (428, -52), "DIA_C2G2_8": (442, 115), "DIA_C2G2_5": (868, 63), }, # seal fake far
            665: {"DIA_C2G2_8": (43, -27), "DIA_C2G2_9": (-85, -121), "DIA_C2G2_10": (19, -158), "DIA_C2G2_21_OPEN": (-163, -6), "DIA_C2G2_21_CLOSED": (-163, -6),"DIA_C2G2_21_MOUSEOVER": (-163, -6),"DIA_C2G2_17": (28, -194),  "DIA_C2G2_5": (468, -80), "DIA_C2G2_14": (480, -153), "DIA_C2G2_22": (503, 208), "DIA_C2G2_20": (-614, -208), }, # seal boss close

            #DIABLO ENTRANCE STYLE 1 (clear_trash=1)
            670: {"DIABLO_ENTRANCE_1": (1200, 260),"DIABLO_ENTRANCE_2": (233, -174),"DIABLO_ENTRANCE_3": (-77, -182),"DIABLO_ENTRANCE_4": (-363, 372), "DIABLO_ENTRANCE_5": (-612, -76),  "DIABLO_ENTRANCE_6": (869, 86),"DIABLO_ENTRANCE_7": (593, 579),"DIABLO_ENTRANCE_8": (1105, 301),"DIABLO_ENTRANCE_9": (236, 418),  "DIABLO_ENTRANCE_10": (233, 386), "DIABLO_ENTRANCE_11": (73, -216), "DIABLO_ENTRANCE_12": (-569, 611), "DIABLO_ENTRANCE_31": (376, -100), "DIABLO_ENTRANCE_32": (506, -133), "DIABLO_ENTRANCE_33": (187, -150), "DIABLO_ENTRANCE_34": (-8, -152), "DIABLO_ENTRANCE_35": (-167, -202), "DIABLO_ENTRANCE_36": (-310, -90), "DIABLO_ENTRANCE_37": (-444, -40), "DIABLO_ENTRANCE_38": (1, 282), "DIABLO_ENTRANCE_39": (-275, 163),},# Hall 1 center
            671: {"DIABLO_ENTRANCE_1": (621, 60),"DIABLO_ENTRANCE_2": (-144, -318), "DIABLO_ENTRANCE_3": (-454, -327), "DIABLO_ENTRANCE_4": (-740, 230), "DIABLO_ENTRANCE_5": (-989, -218),  "DIABLO_ENTRANCE_6": (492, -56), "DIABLO_ENTRANCE_7": (216, 437), "DIABLO_ENTRANCE_8": (728, 159), "DIABLO_ENTRANCE_9": (-140, 276), "DIABLO_ENTRANCE_10": (-143, 245),  "DIABLO_ENTRANCE_11": (-304, -360), "DIABLO_ENTRANCE_12": (-964, 469), "DIABLO_ENTRANCE_31": (-1, -242), "DIABLO_ENTRANCE_32": (129, -275), "DIABLO_ENTRANCE_33": (-190, -292), "DIABLO_ENTRANCE_34": (-385, -294), "DIABLO_ENTRANCE_35": (-544, -344), "DIABLO_ENTRANCE_36": (-687, -232), "DIABLO_ENTRANCE_37": (-821, -182), "DIABLO_ENTRANCE_38": (-376, 140), "DIABLO_ENTRANCE_39": (-652, 21),}, #hall1 right
            672: {"DIABLO_ENTRANCE_1": (327, -118), "DIABLO_ENTRANCE_2": (-438, -496), "DIABLO_ENTRANCE_6": (198, -234), "DIABLO_ENTRANCE_7": (-78, 259),  "DIABLO_ENTRANCE_8": (434, -19),  "DIABLO_ENTRANCE_9": (-434, 98),  "DIABLO_ENTRANCE_10": (-437, 66),  "DIABLO_ENTRANCE_11": (-598, -538),  },#hall1 left not used
            673: {"DIABLO_ENTRANCE_12": (-129, -152), "DIABLO_ENTRANCE_15": (-273, -108), "DIABLO_ENTRANCE_13": (211, 241), "DIABLO_ENTRANCE_17": (-19, 386), "DIABLO_ENTRANCE_16": (-522, -174), "DIABLO_ENTRANCE_18": (-730, 239), },
            674: {"DIABLO_ENTRANCE_18": (13, 235), "DIABLO_ENTRANCE_19": (-150, 201), "DIABLO_ENTRANCE_16": (221, -178), "DIABLO_ENTRANCE_15": (470, -112), "DIABLO_ENTRANCE_23": (-718, 214), "DIABLO_ENTRANCE_26": (-551, 564), "DIABLO_ENTRANCE_17": (724, 382), },
            675: {"DIABLO_ENTRANCE_23": (-279, 181), "DIABLO_ENTRANCE_19": (289, 167), "DIABLO_ENTRANCE_18": (452, 202), "DIABLO_ENTRANCE_26": (-112, 531), "DIABLO_ENTRANCE_22": (-197, 523), "DIABLO_ENTRANCE_24": (-117, 587), "DIABLO_ENTRANCE_21": (-564, 399), "DIABLO_ENTRANCE_16": (660, -211), },
            676: {"DIABLO_ENTRANCE_21": (142, -273), "DIABLO_ENTRANCE_25": (-268, -357), "DIABLO_ENTRANCE_22": (509, -149), "DIABLO_ENTRANCE_24": (589, -85), "DIABLO_ENTRANCE_26": (594, -141), "DIABLO_ENTRANCE_23": (481, -499), },

            #DIABLO ENTRANCE STYLE 2  (clear_trash=1)
            677: {"DIABLO_ENTRANCE2_2": (31, -146), "DIABLO_ENTRANCE2_46": (480, -2), "DIABLO_ENTRANCE2_3": (-500, 4), },
            678: {"DIABLO_ENTRANCE2_5": (58, -224), "DIABLO_ENTRANCE2_4": (-150, -227), "DIABLO_ENTRANCE2_17": (-277, 151), "DIABLO_ENTRANCE2_9": (-178, 300), "DIABLO_ENTRANCE2_10": (-178, 335), "DIABLO_ENTRANCE2_15": (-261, 317), "DIABLO_ENTRANCE2_12": (-329, -296), "DIABLO_ENTRANCE2_7": (452, 48), },
            679: {"DIABLO_ENTRANCE2_7": (252, -152), "DIABLO_ENTRANCE2_9": (-378, 100), "DIABLO_ENTRANCE2_8": (389, -48), "DIABLO_ENTRANCE2_10": (-378, 135), "DIABLO_ENTRANCE2_11": (501, 20), },
            680: {"DIABLO_ENTRANCE2_12": (101, -199), "DIABLO_ENTRANCE2_41": (-290, 13), "DIABLO_ENTRANCE2_17": (151, 256), "DIABLO_ENTRANCE2_4": (280, -130), "DIABLO_ENTRANCE2_35": (-291, 114), "DIABLO_ENTRANCE2_29": (-293, 113), "DIABLO_ENTRANCE2_27": (-342, 229), "DIABLO_ENTRANCE2_36": (-341, 244), },
            681: {"DIABLO_ENTRANCE2_18": (358, -56), "DIABLO_ENTRANCE2_19": (-291, 267), "DIABLO_ENTRANCE2_20": (-287, 278), "DIABLO_ENTRANCE2_15": (-492, -142), "DIABLO_ENTRANCE2_17": (-508, -307), "DIABLO_ENTRANCE2_43": (-517, 419), },
            682: {"DIABLO_ENTRANCE2_41": (-42, -13), "DIABLO_ENTRANCE2_35": (-43, 88), "DIABLO_ENTRANCE2_29": (-45, 87), "DIABLO_ENTRANCE2_15": (394, 40), "DIABLO_ENTRANCE2_17": (378, -126), "DIABLO_ENTRANCE2_32": (-472, 315), "DIABLO_ENTRANCE2_21": (-471, 355), "DIABLO_ENTRANCE2_23": (-471, 356), },
            683: {"DIABLO_ENTRANCE2_43": (356, 259), "DIABLO_ENTRANCE2_23": (-483, 14), "DIABLO_ENTRANCE2_21": (-484, 13), "DIABLO_ENTRANCE2_24": (-484, 24), "DIABLO_ENTRANCE2_32": (-485, -27), "DIABLO_ENTRANCE2_25": (-489, 45), "DIABLO_ENTRANCE2_27": (-645, 493), "DIABLO_ENTRANCE2_36": (-644, 508), },
            684: {"DIABLO_ENTRANCE2_25": (-203, -242), "DIABLO_ENTRANCE2_23": (-197, -273), "DIABLO_ENTRANCE2_27": (-359, 206), "DIABLO_ENTRANCE2_36": (-358, 221), "DIABLO_ENTRANCE2_31": (-536, 429), "DIABLO_ENTRANCE2_39": (-876, 120), },
            685: {"DIABLO_ENTRANCE2_42": (15, -383), "DIABLO_ENTRANCE2_39": (205, -363), "DIABLO_ENTRANCE2_31": (545, -54), "DIABLO_ENTRANCE2_41": (-474, -502), "DIABLO_ENTRANCE2_35": (-473, -507), "DIABLO_ENTRANCE2_28": (-474, -508), "DIABLO_ENTRANCE2_29": (-475, -508), },
            686: {"DIABLO_ENTRANCE2_35": (-127, -314), "DIABLO_ENTRANCE2_28": (-128, -315), "DIABLO_ENTRANCE2_42": (361, -191), "DIABLO_ENTRANCE2_39": (551, -171),}, #replaced by 609
            ########################
            # DIABLO END
            ########################

            # A1 town
            #kashya_cain
            700: {"A1_TOWN_3": (174, -40), "A1_TOWN_4": (202, 52), "A1_TOWN_0": (226, 196), "A1_TOWN_1": (385, 293), "A1_TOWN_6": (290, 653), "A1_TOWN_5": (439, 610), },
            #stash
            701: {"A1_TOWN_4": (56, -71), "A1_TOWN_0": (80, 73), "A1_TOWN_3": (28, -163), "A1_TOWN_1": (239, 170), "A1_TOWN_6": (104, 530), "A1_TOWN_5": (293, 487), },
            #wp check (north)
            702: {"A1_TOWN_0": (279, -83), "A1_TOWN_4": (255, -227), "A1_TOWN_3": (227, -319), "A1_TOWN_1": (438, 14), "A1_TOWN_6": (303, 374), "A1_TOWN_5": (492, 331), },
            703: {"A1_TOWN_6": (-36, 161), "A1_TOWN_5": (153, 118), "A1_TOWN_1": (99, -199), "A1_TOWN_0": (-60, -296), "A1_TOWN_4": (-84, -440), "A1_TOWN_3": (-112, -532), },
            #charsi
            704: {"A1_TOWN_5": (-104, 108), "A1_TOWN_1": (-158, -209), "A1_TOWN_6": (-293, 151), "A1_TOWN_0": (-317, -306), "A1_TOWN_4": (-341, -450), "A1_TOWN_3": (-369, -542), },
            #wp check (south)
            705: {"A1_TOWN_3": (457, -29), "A1_TOWN_4": (485, 63), "A1_TOWN_0": (509, 207), "A1_TOWN_7": (-608, -188), "A1_TOWN_1": (668, 304), },
            706: {"A1_TOWN_7": (-79, -33), "A1_TOWN_8": (-666, 21), "A1_TOWN_3": (986, 126), "A1_TOWN_4": (1014, 218), },
            #akara
            707: {"A1_TOWN_8": (-230, 93), "A1_TOWN_7": (357, 39), },
            708: {"A1_TOWN_3": (-32, 200), "A1_TOWN_7": (533, -103), "A1_TOWN_9": (505, -298)},

            #extra necro walking waypoints
            900: {"NECRO_TRAV_1": (-102, 46), },
            901: {"NECRO_TRAV_4": (-37, -69), "NECRO_TRAV_0": (354, 28), "NECRO_TRAV_6": (-339, 117), "NECRO_TRAV_5": (426, 140), "NECRO_TRAV_3": (433, -269), "NECRO_TRAV_2": (775, -176), },
            902: {"NECRO_TRAV_6": (271, 358), "NECRO_TRAV_4": (573, 172), },
            903: {"NECRO_TRAV_12": (-20, -155), "NECRO_TRAV_9": (-250, 37), "NECRO_TRAV_7": (146, 235), "NECRO_TRAV_8": (-155, 361), "NECRO_TRAV_16": (-725, -197), },
            904: {"NECRO_TRAV_16": (-185, 82), "NECRO_TRAV_9": (290, 316), "NECRO_TRAV_12": (520, 124), },
            905: {"NECRO_TRAV_14": (-284, -28), "NECRO_TRAV_11": (-166, 314), "NECRO_TRAV_15": (-558, 115), "NECRO_TRAV_17": (-421, 387), "NECRO_TRAV_13": (597, -64), "NECRO_TRAV_18": (-747, 292), "NECRO_TRAV_19": (-777, 328), },
            906: {"NECRO_TRAV_14": (27, -177), "NECRO_TRAV_13": (908, -213), },
            907: {"NECRO_TRAV_19": (-28, -66), "NECRO_TRAV_18": (2, -102), "NECRO_TRAV_17": (328, -7), "NECRO_TRAV_15": (191, -279), "NECRO_TRAV_11": (583, -80), "NECRO_TRAV_21": (-486, 380), "NECRO_TRAV_22": (-685, 244), },
            908: {"NECRO_TRAV_19": (264, 51), "NECRO_TRAV_18": (244, -211), "NECRO_TRAV_21": (-244, 271), "NECRO_TRAV_22": (-443, 135), "NECRO_TRAV_17": (570, -116), },
            909: {"NECRO_TRAV_21": (-38, 101), "NECRO_TRAV_22": (-237, -35), "NECRO_TRAV_18": (450, -381), "NECRO_TRAV_17": (776, -286), },
            910: {"NECRO_TRAV_22": (287, 133), "NECRO_TRAV_21": (486, 269), },
            911: {"NECRO_TRAV_22": (13, 171), "NECRO_TRAV_21": (212, 307), },
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
            (Location.A5_MALAH, Location.A5_QUAL_KEHK): [16, 15, 12],
            (Location.A5_MALAH, Location.A5_STASH): [1, 0, 3, 4, 5],
            (Location.A5_MALAH, Location.A5_LARZUK): [1, 0, 3, 4, 5, 13, 14],
            (Location.A5_MALAH, Location.A5_WP): [1, 0, 3, 4],
            (Location.A5_MALAH, Location.A5_NIHLATHAK_PORTAL): [16, 15, 12, 11, 10, 6, 8, 9],
            (Location.A5_STASH, Location.A5_NIHLATHAK_PORTAL): [6, 8, 9],
            (Location.A5_STASH, Location.A5_QUAL_KEHK): [5, 6, 10, 11, 12],
            (Location.A5_STASH, Location.A5_LARZUK): [13, 14],
            (Location.A5_STASH, Location.A5_WP): [],
            (Location.A5_STASH, Location.A5_MALAH): [4, 3, 0, 1, 2],
            (Location.A5_WP, Location.A5_STASH): [],
            (Location.A5_WP, Location.A5_LARZUK): [13, 14],
            (Location.A5_WP, Location.A5_NIHLATHAK_PORTAL): [6, 8, 9],
            (Location.A5_WP, Location.A5_QUAL_KEHK): [6, 10, 11, 12],
            (Location.A5_WP, Location.A5_MALAH): [4, 3, 0, 1, 2],
            (Location.A5_QUAL_KEHK, Location.A5_NIHLATHAK_PORTAL): [12, 11, 10, 6, 8, 9],
            (Location.A5_QUAL_KEHK, Location.A5_WP): [12, 11, 10, 6],
            (Location.A5_QUAL_KEHK, Location.A5_STASH): [12, 11, 10, 6, 5],
            (Location.A5_QUAL_KEHK, Location.A5_LARZUK): [12, 11, 10, 6, 5, 13, 14],
            (Location.A5_QUAL_KEHK, Location.A5_MALAH): [15, 16, 2],
            (Location.A5_LARZUK, Location.A5_QUAL_KEHK): [13, 14, 5, 6, 10, 11, 12],
            (Location.A5_LARZUK, Location.A5_NIHLATHAK_PORTAL): [14, 13, 5, 6, 8, 9],
            (Location.A5_LARZUK, Location.A5_WP): [14, 13, 5],
            (Location.A5_LARZUK, Location.A5_STASH): [14, 13, 5],
            (Location.A5_LARZUK, Location.A5_MALAH): [14, 13, 5, 4, 3, 1, 2],
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
            (Location.A4_TOWN_START, Location.A4_WP): [162],
            (Location.A4_TOWN_START, Location.A4_TYRAEL_STASH): [160, 161],
            (Location.A4_TOWN_START, Location.A4_JAMELLA): [163, 164],
            (Location.A4_TOWN_START, Location.A4_HALBU): [163, 164, 165],
            (Location.A4_WP, Location.A4_TYRAEL_STASH): [160, 161],
            (Location.A4_WP, Location.A4_JAMELLA): [162, 163, 164],
            (Location.A4_WP, Location.A4_HALBU): [162, 163, 164, 165],
            (Location.A4_TYRAEL_STASH, Location.A4_WP): [161, 160],
            (Location.A4_TYRAEL_STASH, Location.A4_JAMELLA): [161, 160, 162, 163, 164],
            (Location.A4_TYRAEL_STASH, Location.A4_HALBU): [161, 160, 162, 163, 164, 165],
            (Location.A4_JAMELLA, Location.A4_WP): [164, 163, 162],
            (Location.A4_JAMELLA, Location.A4_TYRAEL_STASH): [164, 163, 162, 160, 161],
            (Location.A4_JAMELLA, Location.A4_HALBU): [165],
            (Location.A4_HALBU, Location.A4_WP): [164, 163, 162],
            (Location.A4_HALBU, Location.A4_TYRAEL_STASH): [164, 163, 162, 160, 161],
            (Location.A4_HALBU, Location.A4_JAMELLA): [164],
            # A3 Town
            (Location.A3_TOWN_START, Location.A3_STASH_WP): [180, 181, 182, 183, 184, 185, 186, 187, 188],
            (Location.A3_TOWN_START, Location.A3_ORMUS): [180, 181, 182, 183, 184, 185],
            (Location.A3_ORMUS, Location.A3_STASH_WP): [186, 187, 188],
            (Location.A3_ORMUS, Location.A3_ASHEARA): [189, 190, 191, 192],
            (Location.A3_ASHEARA, Location.A3_STASH_WP): [191, 190, 189, 185, 186, 187, 188],
            (Location.A3_STASH_WP, Location.A3_STASH_WP): [188],
            (Location.A3_STASH_WP, Location.A3_ORMUS): [187, 186, 185],
            # A2 Town
            (Location.A2_TOWN_START, Location.A2_WP): [400, 401, 402, 403, 404],
            (Location.A2_TOWN_START, Location.A2_FARA_STASH): [400, 401, 402, 405],
            (Location.A2_TOWN_START, Location.A2_LYSANDER): [400, 401, 402],
            (Location.A2_TOWN_START, Location.A2_DROGNAN): [400, 401, 402, 403, 409, 410, 411],
            (Location.A2_FARA_STASH, Location.A2_WP): [403, 404],
            (Location.A2_FARA_STASH, Location.A2_LYSANDER): [403, 402],
            (Location.A2_FARA_STASH, Location.A2_DROGNAN): [403, 409, 410, 411],
            (Location.A2_TP, Location.A2_FARA_STASH): [408, 406, 405],
            (Location.A2_TP, Location.A2_DROGNAN): [408, 406, 405, 403, 409, 410, 411],
            (Location.A2_TP, Location.A2_LYSANDER): [408, 406, 405, 402],
            (Location.A2_WP, Location.A2_FARA_STASH): [404, 403, 405],
            (Location.A2_WP, Location.A2_DROGNAN): [404, 409, 410, 411],
            (Location.A2_WP, Location.A2_LYSANDER): [404, 403, 402],
            (Location.A2_LYSANDER, Location.A2_FARA_STASH): [402, 405],
            (Location.A2_LYSANDER, Location.A2_TP): [402, 405, 406, 408],
            (Location.A2_LYSANDER, Location.A2_WP): [403, 404],
            (Location.A2_LYSANDER, Location.A2_DROGNAN): [403, 409, 410, 411],
            (Location.A2_DROGNAN, Location.A2_LYSANDER): [411, 410, 409, 403, 402],
            (Location.A2_DROGNAN, Location.A2_WP): [411, 410, 409, 404],
            (Location.A2_DROGNAN, Location.A2_FARA_STASH): [411, 410, 409, 403, 405],
            # A1 Town
            #spawned in where do we go?
            (Location.A1_TOWN_START, Location.A1_STASH): [],
            (Location.A1_TOWN_START, Location.A1_KASHYA_CAIN): [],
            (Location.A1_TOWN_START, Location.A1_CHARSI): [702, 703, 704],
            (Location.A1_TOWN_START, Location.A1_AKARA): [705, 706, 707],
            (Location.A1_TOWN_START, Location.A1_WP_NORTH): [702],
            (Location.A1_TOWN_START, Location.A1_WP_SOUTH): [705],
            #from the stash to where?
            (Location.A1_STASH, Location.A1_KASHYA_CAIN): [700],
            (Location.A1_STASH, Location.A1_CHARSI): [701, 702, 703, 704],
            (Location.A1_STASH, Location.A1_AKARA): [701, 705, 706, 707],
            (Location.A1_STASH, Location.A1_WP_NORTH): [701, 702],
            (Location.A1_STASH, Location.A1_WP_SOUTH): [701, 705],
            #from the Kashya/Cain to where?
            (Location.A1_KASHYA_CAIN, Location.A1_STASH): [700],
            (Location.A1_KASHYA_CAIN, Location.A1_CHARSI): [700, 702, 703, 704],
            (Location.A1_KASHYA_CAIN, Location.A1_AKARA): [700, 705, 706, 707],
            (Location.A1_KASHYA_CAIN, Location.A1_WP_NORTH): [700, 702],
            (Location.A1_KASHYA_CAIN, Location.A1_WP_SOUTH): [700, 705],
            #from the Charsi to where?
            (Location.A1_CHARSI, Location.A1_STASH): [704, 703, 702, 700],
            (Location.A1_CHARSI, Location.A1_KASHYA_CAIN): [704, 703, 702, 700],
            (Location.A1_CHARSI, Location.A1_AKARA): [704, 703, 702, 705, 706, 707],
            (Location.A1_CHARSI, Location.A1_WP_NORTH): [704, 703, 702],
            (Location.A1_CHARSI, Location.A1_WP_SOUTH): [704, 703, 702, 705],
            #from the Akara to where?
            (Location.A1_AKARA, Location.A1_STASH): [707, 706, 705, 700],
            (Location.A1_AKARA, Location.A1_KASHYA_CAIN): [707, 706, 705, 700],
            (Location.A1_AKARA, Location.A1_CHARSI): [707, 706, 705, 702, 703, 704],
            (Location.A1_AKARA, Location.A1_WP_NORTH): [707, 706, 705, 702],
            (Location.A1_AKARA, Location.A1_WP_SOUTH): [707, 706, 706],
            (Location.A1_WP_SOUTH, Location.A1_WP_NORTH): [702],
            #from town portal
            (Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN): [708, 700],
            # Trav
            (Location.A3_TRAV_START, Location.A3_TRAV_CENTER_STAIRS): [220, 221, 222, 223, 224, 225, 226],
        }

    def adapt_path(self,key: tuple[Location, Location], new_node_sequence: list[int]):
        self._paths[key] = new_node_sequence

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
    def _convert_rel_to_abs(rel_loc: tuple[float, float], pos_abs: tuple[float, float]) -> tuple[float, float]:
        return (rel_loc[0] + pos_abs[0], rel_loc[1] + pos_abs[1])

    def traverse_nodes_fixed(self, key: str | list[tuple[float, float]], char: IChar) -> bool:
        if not char.capabilities.can_teleport_natively:
            error_msg = "Teleport is required for static pathing"
            Logger.error(error_msg)
            raise ValueError(error_msg)
        char.pre_move()
        if type(key) == str:
            path = Config().path[key]
        else:
            path = key
        i = 0
        stuck_count = 0
        while i < len(path):
            x_m, y_m = convert_screen_to_monitor(path[i])
            x_m += int(random.random() * 6 - 3)
            y_m += int(random.random() * 6 - 3)
            t0 = grab(force_new=True)
            char.move((x_m, y_m))
            t1 = grab(force_new=True)
            # check difference between the two frames to determine if tele was good or not
            diff = cv2.absdiff(t0, t1)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(diff, 13, 255, cv2.THRESH_BINARY)
            score = (float(np.sum(mask)) / mask.size) * (1/255.0)
            if score > 0.15:
                i += 1
            else:
                stuck_count += 1
                Logger.debug(f"Teleport cancel detected. Try same teleport action again. ({score:.4f})")
                if stuck_count >= 5:
                    return False
        # if type(key) == str and ("_save_dist" in key or "_end" in key):
        #     cv2.imwrite(f"./log/screenshots/info/nil_path_{key}_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        return True


    def find_abs_node_pos(self, node_idx: int, img: np.ndarray, threshold: float = 0.68) -> tuple[float, float]:
        node = self._nodes[node_idx]
        template_match = template_finder.search(
            [*node],
            img,
            best_match=False,
            threshold=threshold,
            roi=Config().ui_roi["cut_skill_bar"],
            use_grayscale=True
        )
        if template_match.valid:
            # Get reference position of template in abs coordinates
            ref_pos_abs = convert_screen_to_abs(template_match.center)
            # Calc the abs node position with the relative coordinates (relative to ref)
            node_pos_rel = self._get_node(node_idx, template_match.name)
            node_pos_abs = self._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
            node_pos_abs = get_closest_non_hud_pixel(pos = node_pos_abs, pos_type="abs")
            return node_pos_abs
        return None

    def traverse_nodes(
        self,
        path: tuple[Location, Location] | list[int],
        char: IChar,
        timeout: float = 5,
        force_tp: bool = False,
        do_pre_move: bool = True,
        force_move: bool = False,
        threshold: float = 0.68,
        use_tp_charge: bool = False
    ) -> bool:
        """Traverse from one location to another
        :param path: Either a list of node indices or a tuple with (start_location, end_location)
        :param char: Char that is traversing the nodes
        :param timeout: Timeout in second. If no more move was found in that time it will cancel traverse
        :param force_move: Bool value if force move should be used for pathing
        :return: Bool if traversed successful or False if it got stuck
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

        if use_tp_charge and char.select_tp():
            # this means we want to use tele charge and we were able to select it
            pass
        elif do_pre_move:
            # we either want to tele charge but have no charges or don't wanna use the charge falling back to default pre_move handling
            char.pre_move()

        last_direction = None
        for i, node_idx in enumerate(path):
            continue_to_next_node = False
            last_move = time.time()
            did_force_move = False
            teleport_count = 0
            while not continue_to_next_node:
                img = grab(force_new=True)
                # Handle timeout
                if (time.time() - last_move) > timeout:
                    if is_visible(ScreenObjects.WaypointLabel, img):
                        # sometimes bot opens waypoint menu, close it to find templates again
                        Logger.debug("Opened wp, closing it again")
                        keyboard.send("esc")
                        last_move = time.time()
                    else:
                        # This is a bit hacky, but for moving into a boss location we set timeout usually quite low
                        # because of all the spells and monsters it often can not determine the final template
                        # Don't want to spam the log with errors in this case because it most likely worked out just fine
                        if timeout > 3.1:
                            if Config().general["info_screenshots"]:
                                cv2.imwrite("./log/screenshots/info/info_pather_got_stuck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                            Logger.error("Got stuck exit pather")
                        return False

                # Sometimes we get stuck at rocks and stuff, after a few seconds force a move into the last known direction
                if not did_force_move and time.time() - last_move > 3.1:
                    if last_direction is not None:
                        pos_abs = last_direction
                    else:
                        angle = random.random() * math.pi * 2
                        pos_abs = (round(math.cos(angle) * 150), round(math.sin(angle) * 150))
                    pos_abs = get_closest_non_hud_pixel(pos = pos_abs, pos_type="abs")
                    Logger.debug(f"Pather: taking a random guess towards " + str(pos_abs))
                    x_m, y_m = convert_abs_to_monitor(pos_abs)
                    char.move((x_m, y_m), force_move=True)
                    did_force_move = True
                    last_move = time.time()

                # Sometimes we get stuck at a Shrine or Stash, after a few seconds check if the screen was different, if force a left click.
                if (teleport_count + 1) % 30 == 0:
                    if (match := detect_screen_object(ScreenObjects.ShrineArea, img)).valid:
                        if Config().general["info_screenshots"]:
                            cv2.imwrite(f"./log/screenshots/info_shrine_check_before" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                        Logger.debug(f"Shrine found, activating it")
                        select_screen_object_match(match)
                        if Config().general["info_screenshots"]:
                            cv2.imwrite(f"./log/screenshots/info/info_shrine_check_after" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                    teleport_count = 0
                    break
                teleport_count += 1

                # Find any template and calc node position from it
                node_pos_abs = self.find_abs_node_pos(node_idx, img, threshold=threshold)
                if node_pos_abs is not None:
                    dist = math.dist(node_pos_abs, (0, 0))
                    if dist < Config().ui_pos["reached_node_dist"]:
                        continue_to_next_node = True
                    else:
                        # Move the char
                        x_m, y_m = convert_abs_to_monitor(node_pos_abs)
                        char.move((x_m, y_m), force_tp=force_tp, force_move=force_move)
                        last_direction = node_pos_abs
                        last_move = time.time()

        return True


# Testing: Move char to whatever Location to start and run
if __name__ == "__main__":
    # debug method to display all nodes

    def display_all_nodes(pather: Pather, filters: list | str = None):
        start = time.time()
        while 1:
            img = grab()
            display_img = img.copy()
            template_map = {}
            template_scores = {}
            for template_type in template_finder.stored_templates().keys():
                if type(filters) != list:
                    filters = [filters]
                for filter in filters:
                    if filter is None or filter in template_type:
                        template_match = template_finder.search(template_type, img, use_grayscale=True, threshold=0.78)
                        if template_match.valid:
                            template_map[template_type] = template_match.center
                            template_scores[template_type] = round(template_match.score, 3)
            #print(f"{template_scores:0.2f}")
            print(f"Matching template scores: {template_scores}")
            # print(template_map)
            for node_idx in pather._nodes:
                for template_type in pather._nodes[node_idx]:
                    if template_type in template_map:
                        ref_pos_screen = template_map[template_type]
                        # Get reference position of template in abs coordinates
                        ref_pos_abs = convert_screen_to_abs(ref_pos_screen)
                        # Calc the abs node position with the relative coordinates (relative to ref)
                        node_pos_rel = pather._get_node(node_idx, template_type)
                        node_pos_abs = pather._convert_rel_to_abs(node_pos_rel, ref_pos_abs)
                        node_pos_abs = get_closest_non_hud_pixel(pos = node_pos_abs, pos_type="abs")
                        x, y = convert_abs_to_screen(node_pos_abs)
                        print(f"Draw circle for node {node_idx} at abs coordinates: {node_pos_abs}")
                        cv2.circle(display_img, (x, y), 5, (255, 0, 0), 3)
                        cv2.putText(display_img, str(node_idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        x, y = convert_abs_to_screen(ref_pos_abs)
                        cv2.circle(display_img, (x, y), 5, (0, 255, 0), 3)
                        cv2.putText(display_img, template_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        wrt_origin = (-ref_pos_abs[0], -ref_pos_abs[1])
                        print(f'Found template "{template_type}" at abs coordinates: {ref_pos_abs}')
                        # print(f'Template: "{template_type}", coordinates with respect to origin: {wrt_origin}')
            # display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5)
            # if round(time.time() - start) % 3 == 0:
            #     cv2.imwrite("./log/screenshots/info/pather_" + time.strftime("%Y%m%d_%H%M%S") + ".png", display_img)
            cv2.imshow("debug", display_img)
            cv2.waitKey(1)

    import keyboard
    from screen import start_detecting_window, stop_detecting_window, grab
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    start_detecting_window()
    from config import Config
    from char.sorceress import LightSorc
    from char.paladin.hammerdin import Hammerdin
    from item.pickit import PickIt
    pather = Pather()

    #char = Hammerdin(Config().hammerdin, pather, PickIt) #Config().char,
    #char.discover_capabilities()

    display_all_nodes(pather, ["ELD", "SHENK_"])
    #pather.traverse_nodes([120, 121, 122, 123, 122, 121, 120], char) #works!
    #pather.traverse_nodes_fixed("dia_trash_c", char)
    #display_all_nodes(pather, "SHENK")
    #pather.traverse_nodes([141,142,143], char)
    #stop_detecting_window()
