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
from automap_finder import toggle_automap
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
    A5_ANYA = "a5_anya"
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
    A1_WP ="a1_wp"
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
            1000: {'A5_TOWN_AUTOMAP': (-118, -38)},
            1001: {'A5_TOWN_AUTOMAP': (-178, -52)},
            1003: {'A5_TOWN_AUTOMAP': (-140, -12)},
            1004: {'A5_TOWN_AUTOMAP': (-170, 12)},
            1005: {'A5_TOWN_AUTOMAP': (-152, 36)},
            1006: {'A5_TOWN_AUTOMAP': (-204, 66)},
            1007: {'A5_TOWN_AUTOMAP': (-112, 10)},
            1008: {'A5_TOWN_AUTOMAP': (-222, 84)},
            1009: {'A5_TOWN_AUTOMAP': (-264, 104)},
            1010: {'A5_TOWN_AUTOMAP': (-256, 40)},
            1011: {'A5_TOWN_AUTOMAP': (-222, 46)},
            1012: {'A5_TOWN_AUTOMAP': (-300, 2)},
            1014: {'A5_TOWN_AUTOMAP': (-82, 34)},
            1016: {'A5_TOWN_AUTOMAP': (-222, -50)},
            1017: {'A5_TOWN_AUTOMAP': (-360, 66)},
            1018: {'A5_TOWN_AUTOMAP': (-330, 88)},
            1019: {'A5_TOWN_AUTOMAP': (-288, 102)},
            # Pindle
            1103: {'PINDLE_AM_1': (118, -81)},#,'PINDLE_AM_1': (118, -81),'PINDLE_AM_3': (-76, 38),PINDLE_AM_2': (310, -276)
            1104: {'PINDLE_AM_1': (172, -100)},#'PINDLE_AM_2': (68, -18),'PINDLE_AM_3': (-22, 20),
            100: {'PINDLE_7': (384, -92), 'PINDLE_0': (-97, -40), 'PINDLE_1': (-13, 223), 'PINDLE_2': (-366, 85)},
            101: {'PINDLE_1': (371, -45), 'PINDLE_2': (18, -184), 'PINDLE_3': (-123, 261)},
            102: {'PINDLE_3': (223, 88), 'PINDLE_4': (95, 215)},
            103: {'PINDLE_3': (395, -75), 'PINDLE_4': (267, 52)},
            104: {'PINDLE_4': (717, -117), 'PINDLE_3': (843, -244), 'PINDLE_5': (-187, 237), 'PINDLE_6': (-467, 89)},
            # Eldritch
            1120: {'SHENK_WP_AUTOMAP': (2, -12),'SHENK_ROCK_AUTOMAP': (60, -2)},
            1121: {'SHENK_WP_AUTOMAP': (-3, -36),'SHENK_ROCK_AUTOMAP': (55, -26)},
            1122: {'SHENK_WP_AUTOMAP': (-7, -74),'SHENK_ROCK_AUTOMAP': (51, -64)}, # A5_ELDRITCH_SAFE_DIST
            1123: {'SHENK_WP_AUTOMAP': (-3, -90),'SHENK_ROCK_AUTOMAP': (55, -80)}, # A5_ELDRITCH_END
            120: {'ELDRITCH_0': (293, 24), 'ELDRITCH_0_V2': (293, 24), 'ELDRITCH_0_V3': (293, 24), 'ELDRITCH_1': (-307, 76), 'ELDRITCH_1_V2': (-307, 76), 'ELDRITCH_5': (27, -164), 'ELDRITCH_6': (400, -50)},
            121: {'ELDRITCH_6': (360, -244), 'ELDRITCH_1': (-329, -103), 'ELDRITCH_1_V2': (-329, -103), 'ELDRITCH_2': (411, 171), 'ELDRITCH_2_V2': (411, 171), 'ELDRITCH_3': (-91, 198), 'ELDRITCH_7': (409, 180), 'ELDRITCH_7_V2': (409, 180), 'ELDRITCH_8': (465, 345), 'ELDRITCH_8_V2': (465, 345)},
            122: {'ELDRITCH_2': (353, -145), 'ELDRITCH_2_V2': (353, -145), 'ELDRITCH_3': (-149, -119), 'ELDRITCH_9': (-253, -118), 'ELDRITCH_7': (352, -134), 'ELDRITCH_7_V2': (352, -134), 'ELDRITCH_8': (404, 29), 'ELDRITCH_8_V2': (404, 29)},
            123: {'ELDRITCH_3': (-99, -252), 'ELDRITCH_2': (403, -279), 'ELDRITCH_2_V2': (403, -279), 'ELDRITCH_4': (-62, -109), 'ELDRITCH_9': (-204, -254), 'ELDRITCH_8': (454, -104),  'ELDRITCH_8_V2': (454, -104)},
            # Shenk
            1146: {'SHENK_WP_AUTOMAP': (66, 28), 'SHENK_ROCK_AUTOMAP': (124, 38)},
            1147: {'SHENK_WP_AUTOMAP': (137, 108), 'SHENK_ROCK_AUTOMAP': (195, 118)},
            1148: {'SHENK_WP_AUTOMAP': (213, 138), 'SHENK_ROCK_AUTOMAP': (271, 148)}, # A5_SHENK_SAFE_DIST
            1149: {'SHENK_WP_AUTOMAP': (293, 172),'SHENK_ROCK_AUTOMAP': (351, 182)}, # kill shenk telestomp
            1150: {'SHENK_WP_AUTOMAP': (233, 154),'SHENK_ROCK_AUTOMAP': (291, 164)}, # tp outside of fire
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
            1160: {'A4_TOWN_AUTOMAP': (130, -4)},
            1161: {'A4_TOWN_AUTOMAP': (106, -18)},
            1162: {'A4_TOWN_AUTOMAP': (154, 20)},
            1163: {'A4_TOWN_AUTOMAP': (160, 42)},
            1164: {'A4_TOWN_AUTOMAP': (196, 82)},
            1165: {'A4_TOWN_AUTOMAP': (250, 66)},
            # A3 town
            1180: {'A3_TOWN_AUTOMAP': (38, 34)},
            1181: {'A3_TOWN_AUTOMAP': (72, 43)},
            1182: {'A3_TOWN_AUTOMAP': (116, 29)},
            1183: {'A3_TOWN_AUTOMAP': (146, 13)},
            1184: {'A3_TOWN_AUTOMAP': (206, -17)},
            1185: {'A3_TOWN_AUTOMAP': (246, -37)},
            1186: {'A3_TOWN_AUTOMAP': (296, -23)},
            1187: {'A3_TOWN_AUTOMAP': (346, -53)},
            1188: {'A3_TOWN_AUTOMAP': (386, -70)},
            1189: {'A3_TOWN_AUTOMAP': (206, -65)},
            1190: {'A3_TOWN_AUTOMAP': (164, -85)},
            1191: {'A3_TOWN_AUTOMAP': (108, -113)},
            1192: {'A3_TOWN_AUTOMAP': (56, -140)},
            # Trav
            1220: {'TRAV_AUTOMAP': (32, 26)},
            1221: {'TRAV_AUTOMAP': (86, 5)},    
            1222: {'TRAV_AUTOMAP': (166, 20)},
            1223: {'TRAV_AUTOMAP': (244, 20)},
            1224: {'TRAV_AUTOMAP': (318, 24)},
            1225: {'TRAV_AUTOMAP': (352, 44)},
            1226: {'TRAV_AUTOMAP': (404, 28)},
            1227: {'TRAV_AUTOMAP': (358, 14)},
            1228: {'TRAV_AUTOMAP': (430, 10)},
            1229: {'TRAV_AUTOMAP': (442, -8)},
            1230: {'TRAV_AUTOMAP': (406, -25)},
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
            #extra necro walking waypoints
            900: {"NECRO_TRAV_1": (-102, 46)},
            901: {"NECRO_TRAV_4": (-37, -69), "NECRO_TRAV_0": (354, 28), "NECRO_TRAV_6": (-339, 117), "NECRO_TRAV_5": (426, 140), "NECRO_TRAV_3": (433, -269), "NECRO_TRAV_2": (775, -176)},
            902: {"NECRO_TRAV_6": (271, 358), "NECRO_TRAV_4": (573, 172)},
            903: {"NECRO_TRAV_12": (-20, -155), "NECRO_TRAV_9": (-250, 37), "NECRO_TRAV_7": (146, 235), "NECRO_TRAV_8": (-155, 361), "NECRO_TRAV_16": (-725, -197)},
            904: {"NECRO_TRAV_16": (-185, 82), "NECRO_TRAV_9": (290, 316), "NECRO_TRAV_12": (520, 124)},
            905: {"NECRO_TRAV_14": (-284, -28), "NECRO_TRAV_11": (-166, 314), "NECRO_TRAV_15": (-558, 115), "NECRO_TRAV_17": (-421, 387), "NECRO_TRAV_13": (597, -64), "NECRO_TRAV_18": (-747, 292), "NECRO_TRAV_19": (-777, 328)},
            906: {"NECRO_TRAV_14": (27, -177), "NECRO_TRAV_13": (908, -213)},
            907: {"NECRO_TRAV_19": (-28, -66), "NECRO_TRAV_18": (2, -102), "NECRO_TRAV_17": (328, -7), "NECRO_TRAV_15": (191, -279), "NECRO_TRAV_11": (583, -80), "NECRO_TRAV_21": (-486, 380), "NECRO_TRAV_22": (-685, 244)},
            908: {"NECRO_TRAV_19": (264, 51), "NECRO_TRAV_18": (244, -211), "NECRO_TRAV_21": (-244, 271), "NECRO_TRAV_22": (-443, 135), "NECRO_TRAV_17": (570, -116)},
            909: {"NECRO_TRAV_21": (-38, 101), "NECRO_TRAV_22": (-237, -35), "NECRO_TRAV_18": (450, -381), "NECRO_TRAV_17": (776, -286)},
            910: {"NECRO_TRAV_22": (287, 133), "NECRO_TRAV_21": (486, 269)},
            911: {"NECRO_TRAV_22": (13, 171), "NECRO_TRAV_21": (212, 307)},
            # A2 town
            1400: {'A2_TOWN_AUTOMAP': (-518, 56)},
            1401: {'A2_TOWN_AUTOMAP': (-462, -1)},
            1402: {'A2_TOWN_AUTOMAP': (-392, -45)},
            1403: {'A2_TOWN_AUTOMAP': (-390, -93)},
            1404: {'A2_TOWN_AUTOMAP': (-448, -126)},
            1405: {'A2_TOWN_AUTOMAP': (-324, -75)},
            1406: {'A2_TOWN_AUTOMAP': (-240, -60)},
            1408: {'A2_TOWN_AUTOMAP': (-158, -57)},
            1409: {'A2_TOWN_AUTOMAP': (-384, -108)},
            1410: {'A2_TOWN_AUTOMAP': (-348, -135)},
            1411: {'A2_TOWN_AUTOMAP': (-290, -166)},
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

            ### WALKING CS PATHS FOR KILLING TRASH ###

            #outside CS
            1500: {'DIA_AM_CS': (-66, 61)},    # outside CS
            1501: {'DIA_AM_CS': (-24, 37)},    # outside cs stars bottom

            # CS Aisle
            1502: {'DIA_AM_CS': (19, 13)},     # inside cs, aisle 1/4
            1503: {'DIA_AM_CS': (63, -11)},    # inside cs, aisle 2/4
            1504: {'DIA_AM_CS': (106, -35)},   # inside cs, aisle 3/4
            1505: {'DIA_AM_CS': (150, -59)},   # inside cs, aisle 4/4
            
            # CS Hall1
            1506: {'DIA_AM_CS': (192, -83)},   # cs hall1 center approach
            1507: {'DIA_AM_CS': (247, -62)},   # cs hall1 lower
            1508: {'DIA_AM_CS': (306, -77)},   # cs hall1 lower forward
            1509: {'DIA_AM_CS': (228, -97)},   # cs hall1 center departure
            1510: {'DIA_AM_CS': (154, -115)},  # cs hall1 upper approach
            1511: {'DIA_AM_CS': (190, -140)},  # cs hall1 / hall2 traverse 1
            1512: {'DIA_AM_CS': (240, -163)},  # cs hall1 / hall2 traverse 2
            1513: {'DIA_AM_CS': (291, -185)},  # cs hall1 / hall2 traverse 3 approach hall2 center
            
            # CS Hall2
            1514: {'DIA_AM_CS': (358, -157)},  # cs hall2 center, LC
            1515: {'DIA_AM_CS': (414, -131)},  # cs hall2 lower
            1516: {'DIA_AM_CS': (471, -158)},  # cs hall2 lower approach 1/2
            1517: {'DIA_AM_CS': (534, -188)},  # cs hall2 lower approach offensive 2/2
            # here we must traverse back (1717, 1716, 1715, 1714)
            1518: {'DIA_AM_CS': (351, -220)},  # cs hall2 upper -> hall3 traverse 1/n
            1519: {'DIA_AM_E_A': (144, -96), 'DIA_AM_E_B': (144, -96)},#cs hall2 upper -> hall3 traverse 2/n #'['DIA_AM_CS']': (0, 0), #masekd by HUD
            1520: {'DIA_AM_E_A': (192, -116), 'DIA_AM_E_B': (192, -116)},#cs hall2 -> hall3 traverse 3/n
            
            # CS Hall3
            1521: {'DIA_AM_CS': (540, -257)},  # cs hall 3 center #'DIA_AM_E_B': (286, -110), 'DIA_AM_E_A': (286, -110),
            1522: {'DIA_AM_CS': (591, -254), 'DIA_AM_E_A': (340, -102), 'DIA_AM_E_B': (340, -102)},  # cs hall3 lower 
            1523: {'DIA_AM_E_A': (406, -116), 'DIA_AM_E_B': (406, -116)}, # cs hall3 lower -> reveal cr4 template
            1524: {'DIA_AM_CR4': (-55, -62), 'DIA_AM_E_A': (372, -146),'DIA_AM_E_B': (372, -146)},  # cs hall3 center almost reveal pent - 
            1525: {'DIA_AM_CS': (582, -326), 'DIA_AM_CR1_2': (70, 10), 'DIA_AM_PENT': (-96, 4)}, # cs hall3 center almost reveal CR1 template #'DIA_AM_CR4': (-111, -97),
            
            # CS Trash A (1529, 1627, 1620)
            1526: {'DIA_AM_CR1_2': (70, -30)},    # pent - trash A center
            1527: {'DIA_AM_CR1_2': (28, -50)},    # pent - trash A center 2
            1528: {'DIA_AM_CR1_2': (-14, -60)},   # pent - trash A center 3
            1529: {'DIA_AM_CR1_2': (-56, -68)},   # pent - trash A center 4
            
            # CS Trash B
            1530: {'DIA_AM_CR1_2': (238, -24)},   # pent - trash B center # reveals CR2
            1531: {'DIA_AM_PENT': (72, -66)},   # pent - trash B upper 
            1532: {'DIA_AM_PENT': (138, -58)},  # pent - trash B center 2 forward
            1533: {'DIA_AM_PENT': (104, -12)},  # pent - trash B center lower - reveals cr3 
        
            # CS Trash C
            1534: {'DIA_AM_PENT': (96, 34)},    # pent - trash C center to pent
            1535: {'DIA_AM_PENT': (156, 50)},   # pent - trash C upper forward 
            1536: {'DIA_AM_PENT': (164, 88)},   # pent - trash C center  forward 
            1537: {'DIA_AM_PENT': (84, 78)},    # pent - trash C lower  back 

            # ROF & CS
            1600: {'DIA_AM_WP': (28, -13),'DIA_AM_TYRAEL': (-94, 46)},   # Waypoint -66  33
            1601: {'DIA_AM_WP': (129, -49),'DIA_AM_TYRAEL': (-10, -2)},  # Dodge Tyrael
            1602: {'DIA_AM_WP': (268, -133),'DIA_AM_TYRAEL': (146, -74)}, # ROF FIRST TELE
            1603: {'DIA_AM_WP': (558, -276)}, # ROF SECOND TELE            
            1604: {}, #not used - there is no visible template for Last Tele :(
            1605: {'DIA_AM_CS': (96, -35)}, # CS Entrance Calibration node
            1606: {}, #not used
            1607: {}, #not used
            1608: {}, #not used
            1609: {}, #not used

            # PENT
            1610: {'DIA_AM_PENT':   (0, -6),'DIA_AM_CR1':(154, 20)}, # PENTAGRAM
            1611: {}, #not used
            1612: {}, #not used
            1613: {}, #not used
            1614: {}, #not used
            1615: {}, #not used
            1616: {}, #not used
            1617: {}, #not used
            1618: {}, #not used
            1619: {}, #not used

            # SEAL A (1529, 1627, 1620) 
            1620: {'DIA_AM_CR1_2': (-186, -128),'DIA_AM_PENT': (-352, -134)},# Calibration & Departure Node Seal A (Boss Seal A1L, Fake Seal A2Y)
            1621: {'DIA_AM_CR1_2': (-122, -180),'DIA_AM_PENT':(-288, -186)}, # A1L FAKE SEAL for SEALDANCE
            1622: {'DIA_AM_CR1_2': (-218, -134),'DIA_AM_PENT': (-384, -136)}, # A1L BOSS SEAL for SEALDANCE
            1623: {'DIA_AM_CR1_2': (-140, -118),'DIA_AM_PENT': (-306, -124)}, # A1L KILL VIZIER
            1624: {'DIA_AM_CR1_2': (-216, -134),'DIA_AM_PENT': (-382, -140)}, # A2Y Fake Seal
            1625: {'DIA_AM_CR1_2': (-122, -182),'DIA_AM_PENT': (-288, -188)}, # A2Y BOSS SEAL Calibration Node (Should also work for A1L - gotta test that )
            1627: {'DIA_AM_CR1_2': (-126, -108),'DIA_AM_PENT': (-292, -114)}, # A2Y KILL VIZIER -  Not existent for A1L)
            1628: {}, #not used
            1629: {}, #not used

            # SEAL B (xxxx 1637  xxx 1638)
            1630: {'DIA_AM_CR1_2': (530, -140), 'DIA_AM_PENT': (364, -146)}, # Calibration & Departure Node Seal B
            1631: {'DIA_AM_CR1_2': (550, -134), 'DIA_AM_PENT': (384, -140)}, # B1S BOSS SEAL Calibration Node
            1632: {'DIA_AM_PENT': (252, -130),'DIA_AM_CR1_2': (418, -124)}, # B1S KILL DESEIS 
            1633: {'DIA_AM_PENT': (236, -56),'DIA_AM_CR1_2': (402, -50)}, # B1S approach 1
            1634: {}, #not used
            1635: {'DIA_AM_CR1_2': (450, -184),'DIA_AM_PENT': (284, -190)}, # B2U BOSS SEAL Calibration Node
            1636: {'DIA_AM_PENT': (144, -88),'DIA_AM_CR1_2': (310, -82)},  # B2U DESEIS
            1637: {'DIA_AM_PENT': (144, -128),'DIA_AM_CR1_2': (310, -122)}, # B2U approach 1
            #1637-1: {'DIA_AM_PENT': (208, -140), 'DIA_AM_PENT1': (215, -143), 'DIA_AM_PENT2': (208, -140)}, // Causes conflict with other chars.
            1638: {'DIA_AM_PENT': (308, -86),'DIA_AM_CR1_2': (474, -80)}, # B2U approach 2
            1639: {}, #not used

            # SEAL C 
            1640: {'DIA_AM_PENT': (320, 158), 'DIA_AM_CR1_2': (486, 164)}, # Calibration & Departure Node Seal C , 'DIA_AM_CR3': (156, 170) #'DIA_AM_CR4': (317, 59)
            1641: {'DIA_AM_CR1_2': (504, 130),'DIA_AM_PENT': (338, 124)}, # C1F FAKE SEAL
            1642: {'DIA_AM_CR1_2': (360, 148),'DIA_AM_PENT': (194, 140)}, # C1F BOSS SEAL
            1643: {'DIA_AM_PENT': (252, 154),'DIA_AM_CR1_2': (418, 160)}, # Fight Infector C1F
            1644: {'DIA_AM_PENT': (228, 106),'DIA_AM_CR1_2': (394, 112)}, # C1F ACCESS (used for walking traverse)
            1645: {'DIA_AM_CR1_2': (504, 132),'DIA_AM_PENT': (338, 126)}, # C2G FAKE SEAL
            1646: {'DIA_AM_CR1_2': (406, 180),'DIA_AM_PENT': (240, 174)}, # C2G BOSS SEAL
            1647: {'DIA_AM_PENT': (312, 160),'DIA_AM_CR1_2': (478, 166)}, # C2G Fight Infector - a bit more in center
            1648: {'DIA_AM_PENT': (270, 110),'DIA_AM_CR1_2': (436, 116)},# C2G ACCESS (used for walking traverse) #DOES NOT WORK FOR C1F
            1649: {}, #not used


            1997: {'DIA_AM_PENT2': (-186, -76),'DIA_AM_CR1_2': (-20, -70)}, # new LC A
            1998: {'DIA_AM_PENT2': (-186, -76),'DIA_AM_CR1_2': (-20, -70)}, # new LC B
            1999: {'DIA_AM_PENT2': (-186, -76),'DIA_AM_CR1_2': (-20, -70)}, # new LC B

            ########################
            # DIABLO END
            ########################

            # A1 town
            #kashya_cain
            1700: {'A1_TOWN_AUTOMAP_AKARA': (-194, -6),'A1_TOWN_AUTOMAP_GHEED': (218, 24),'A1_TOWN_AUTOMAP_CHARSI': (52, 104)},
            1701: {'A1_TOWN_AUTOMAP_AKARA': (-215, -26),'A1_TOWN_AUTOMAP_GHEED': (196, 4),'A1_TOWN_AUTOMAP_CHARSI': (31, 84)},
            1702: {'A1_TOWN_AUTOMAP_AKARA': (-184, -42),'A1_TOWN_AUTOMAP_GHEED': (228, -12),'A1_TOWN_AUTOMAP_CHARSI': (62, 68)},
            1703: {'A1_TOWN_AUTOMAP_AKARA': (-236, -72),'A1_TOWN_AUTOMAP_GHEED': (176, -42),'A1_TOWN_AUTOMAP_CHARSI': (10, 38)},
            1704: {'A1_TOWN_AUTOMAP_AKARA': (-275, -68),'A1_TOWN_AUTOMAP_GHEED': (136, -38),'A1_TOWN_AUTOMAP_CHARSI': (-29, 42)},
            1705: {'A1_TOWN_AUTOMAP_AKARA': (-148, -2),'A1_TOWN_AUTOMAP_GHEED': (264, 28),'A1_TOWN_AUTOMAP_CHARSI': (98, 108)},
            1706: {'A1_TOWN_AUTOMAP_AKARA': (-83, 16),'A1_TOWN_AUTOMAP_GHEED': (328, 46),'A1_TOWN_AUTOMAP_CHARSI': (163, 126)},
            1707: {'A1_TOWN_AUTOMAP_AKARA': (-26, 25),'A1_TOWN_AUTOMAP_GHEED': (386, 56),'A1_TOWN_AUTOMAP_CHARSI': (220, 135)},
            1708: {'A1_TOWN_AUTOMAP_GHEED': (398, 36),'A1_TOWN_AUTOMAP_CHARSI': (232, 116)},#'['A1_TOWN_AUTOMAP_AKARA']': (0, 0) < blocked by player marker
            1709: {'A1_TOWN_AUTOMAP_WP': (-2,24)}, #WP
        }
        self._paths_automap = {
            # A5 Town
            (Location.A5_TOWN_START, Location.A5_NIHLATHAK_PORTAL): [1003, 1006, 1008, 1009],
            (Location.A5_TOWN_START, Location.A5_ANYA): [1003, 1006, 1008, 1009, 1019],
            (Location.A5_TOWN_START, Location.A5_STASH): [1003, 1004],
            (Location.A5_TOWN_START, Location.A5_WP): [1003, 1004],
            (Location.A5_TOWN_START, Location.A5_QUAL_KEHK): [1003, 1004, 1006, 1010, 1012],
            (Location.A5_TOWN_START, Location.A5_MALAH): [1001],
            (Location.A5_TOWN_START, Location.A5_LARZUK): [1003, 1007, 1014],
            (Location.A5_MALAH, Location.A5_TOWN_START): [1001, 1000],
            (Location.A5_MALAH, Location.A5_QUAL_KEHK): [1016, 1012],
            (Location.A5_MALAH, Location.A5_STASH): [1001, 1000, 1003, 1004],
            (Location.A5_MALAH, Location.A5_LARZUK): [1001, 1000, 1003, 1007, 1014],
            (Location.A5_MALAH, Location.A5_WP): [1001, 1000, 1003, 1004],
            (Location.A5_MALAH, Location.A5_NIHLATHAK_PORTAL): [1016, 1012, 1018],
            (Location.A5_MALAH, Location.A5_ANYA): [1016, 1012, 1018],
            (Location.A5_STASH, Location.A5_NIHLATHAK_PORTAL): [1006, 1008, 1009],
            (Location.A5_STASH, Location.A5_ANYA): [1006, 1008, 1009, 1019],
            (Location.A5_STASH, Location.A5_QUAL_KEHK): [1006, 1010, 1012],
            (Location.A5_STASH, Location.A5_LARZUK): [1014],
            (Location.A5_STASH, Location.A5_WP): [],
            (Location.A5_STASH, Location.A5_MALAH): [1004, 1003, 1000, 1001],
            (Location.A5_WP, Location.A5_STASH): [],
            (Location.A5_WP, Location.A5_LARZUK): [1005, 1014],
            (Location.A5_WP, Location.A5_NIHLATHAK_PORTAL): [1006, 1008, 1009],
            (Location.A5_WP, Location.A5_ANYA): [1006, 1008, 1009, 1019],
            (Location.A5_WP, Location.A5_QUAL_KEHK): [1006, 1010, 1012],
            (Location.A5_WP, Location.A5_MALAH): [1004, 1003, 1000, 1001],
            (Location.A5_QUAL_KEHK, Location.A5_NIHLATHAK_PORTAL): [1012, 1018],
            (Location.A5_QUAL_KEHK, Location.A5_ANYA): [1012, 1018],
            (Location.A5_QUAL_KEHK, Location.A5_WP): [1012, 1010, 1011],
            (Location.A5_QUAL_KEHK, Location.A5_STASH): [1012, 1010, 1006, 1005],
            (Location.A5_QUAL_KEHK, Location.A5_LARZUK): [1012, 1010, 1006, 1005, 1014],
            (Location.A5_QUAL_KEHK, Location.A5_MALAH): [1012, 1016],
            (Location.A5_LARZUK, Location.A5_QUAL_KEHK): [1014, 1006, 1010, 1012],
            (Location.A5_LARZUK, Location.A5_NIHLATHAK_PORTAL): [1014, 1008, 1009],
            (Location.A5_LARZUK, Location.A5_ANYA): [1014, 1008, 1009, 1019],
            (Location.A5_LARZUK, Location.A5_WP): [1014, 1005],
            (Location.A5_LARZUK, Location.A5_STASH): [1014, 1005],
            (Location.A5_LARZUK, Location.A5_MALAH): [1014, 1007, 1003, 1000, 1001],
            (Location.A5_NIHLATHAK_PORTAL, Location.A5_STASH): [1009, 1008, 1006, 1005],
            (Location.A5_NIHLATHAK_PORTAL, Location.A5_WP): [1009, 1008, 1006],
            # Pindle
            (Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST): [1103],
            (Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END): [1104],
            # Eldritch
            (Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAFE_DIST): [1122],
            (Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END): [1123],
            # Shenk
            (Location.A5_SHENK_START, Location.A5_SHENK_SAFE_DIST): [1146, 1147, 1148],
            (Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END): [1149],
            # A4 Town
            (Location.A4_TOWN_START, Location.A4_WP): [1162],
            (Location.A4_TOWN_START, Location.A4_TYRAEL_STASH): [1160, 1161],
            (Location.A4_TOWN_START, Location.A4_JAMELLA): [1163, 1164],
            (Location.A4_TOWN_START, Location.A4_HALBU): [1163, 1164, 1165],
            (Location.A4_WP, Location.A4_TYRAEL_STASH): [1160, 1161],
            (Location.A4_WP, Location.A4_JAMELLA): [1162, 1163, 1164],
            (Location.A4_WP, Location.A4_HALBU): [1162, 1163, 1164, 1165],
            (Location.A4_TYRAEL_STASH, Location.A4_WP): [1161, 1160],
            (Location.A4_TYRAEL_STASH, Location.A4_JAMELLA): [1161, 1160, 1162, 1163, 1164],
            (Location.A4_TYRAEL_STASH, Location.A4_HALBU): [1161, 1160, 1162, 1163, 1164, 1165],
            (Location.A4_JAMELLA, Location.A4_WP): [1164, 1163, 1162],
            (Location.A4_JAMELLA, Location.A4_TYRAEL_STASH): [1164, 1163, 1162, 1160, 1161],
            (Location.A4_JAMELLA, Location.A4_HALBU): [1165],
            (Location.A4_HALBU, Location.A4_WP): [1164, 1163, 1162],
            (Location.A4_HALBU, Location.A4_TYRAEL_STASH): [1164, 1163, 1162, 1160, 1161],
            (Location.A4_HALBU, Location.A4_JAMELLA): [1164],
            # A3 Town
            (Location.A3_TOWN_START, Location.A3_STASH_WP): [1180, 1181, 1182, 1183, 1184, 1185, 1186, 1187, 1188],
            (Location.A3_TOWN_START, Location.A3_ORMUS): [1180, 1181, 1182, 1183, 1184, 1185],
            (Location.A3_ORMUS, Location.A3_STASH_WP): [1186, 1187, 1188],
            (Location.A3_ORMUS, Location.A3_ASHEARA): [1189, 1190, 1191, 1192],
            (Location.A3_ASHEARA, Location.A3_STASH_WP): [1191, 1190, 1189, 1185, 1186, 1187, 1188],
            (Location.A3_STASH_WP, Location.A3_STASH_WP): [1188],
            (Location.A3_STASH_WP, Location.A3_ORMUS): [1187, 1186, 1185],
            # A2 Town
            (Location.A2_TOWN_START, Location.A2_WP): [1400, 1401, 1402, 1403, 1404],
            (Location.A2_TOWN_START, Location.A2_FARA_STASH): [1400, 1401, 1402, 1405],
            (Location.A2_TOWN_START, Location.A2_LYSANDER): [1400, 1401, 1402],
            (Location.A2_TOWN_START, Location.A2_DROGNAN): [1400, 1401, 1402, 1403, 1409, 1410, 1411],
            (Location.A2_FARA_STASH, Location.A2_WP): [1403, 1404],
            (Location.A2_FARA_STASH, Location.A2_LYSANDER): [1403, 1402],
            (Location.A2_FARA_STASH, Location.A2_DROGNAN): [1403, 1409, 1410, 1411],
            (Location.A2_TP, Location.A2_FARA_STASH): [1408, 1406, 1405],
            (Location.A2_TP, Location.A2_DROGNAN): [1408, 1406, 1405, 1403, 1409, 1410, 1411],
            (Location.A2_TP, Location.A2_LYSANDER): [1408, 1406, 1405, 1402],
            (Location.A2_WP, Location.A2_FARA_STASH): [1404, 1403, 1405],
            (Location.A2_WP, Location.A2_DROGNAN): [1404, 1409, 1410, 1411],
            (Location.A2_WP, Location.A2_LYSANDER): [1404, 1403, 1402],
            (Location.A2_LYSANDER, Location.A2_FARA_STASH): [1402, 1405],
            (Location.A2_LYSANDER, Location.A2_TP): [1402, 1405, 1406, 1408],
            (Location.A2_LYSANDER, Location.A2_WP): [1403, 1404],
            (Location.A2_LYSANDER, Location.A2_DROGNAN): [1403, 1409, 1410, 1411],
            (Location.A2_DROGNAN, Location.A2_LYSANDER): [1411, 1410, 1409, 1403, 1402],
            (Location.A2_DROGNAN, Location.A2_WP): [1411, 1410, 1409, 1404],
            (Location.A2_DROGNAN, Location.A2_FARA_STASH): [1411, 1410, 1409, 1403, 1405],
            # A1 Town
            #spawned in where do we go?
            (Location.A1_TOWN_START, Location.A1_STASH): [],
            (Location.A1_TOWN_START, Location.A1_KASHYA_CAIN): [],
            (Location.A1_TOWN_START, Location.A1_CHARSI): [1702, 1703, 1704],
            (Location.A1_TOWN_START, Location.A1_AKARA): [1705, 1706, 1707],
            (Location.A1_TOWN_START, Location.A1_WP_NORTH): [1702],
            (Location.A1_TOWN_START, Location.A1_WP_SOUTH): [1705],
            (Location.A1_TOWN_START, Location.A1_WP): [1709],
            #from the stash to where?
            (Location.A1_STASH, Location.A1_KASHYA_CAIN): [1700],
            (Location.A1_STASH, Location.A1_CHARSI): [1701, 1702, 1703, 1704],
            (Location.A1_STASH, Location.A1_AKARA): [1701, 1705, 1706, 1707],
            (Location.A1_STASH, Location.A1_WP_NORTH): [1701, 1702],
            (Location.A1_STASH, Location.A1_WP_SOUTH): [1701, 1705],
            (Location.A1_STASH, Location.A1_WP): [1701, 1709],
            #from the Kashya/Cain to where?
            (Location.A1_KASHYA_CAIN, Location.A1_STASH): [1700],
            (Location.A1_KASHYA_CAIN, Location.A1_CHARSI): [1700, 1702, 1703, 1704],
            (Location.A1_KASHYA_CAIN, Location.A1_AKARA): [1700, 1705, 1706, 1707],
            (Location.A1_KASHYA_CAIN, Location.A1_WP_NORTH): [1700, 1702],
            (Location.A1_KASHYA_CAIN, Location.A1_WP_SOUTH): [1700, 1705],
            (Location.A1_KASHYA_CAIN, Location.A1_WP): [1700, 1709],
            #from the Charsi to where?
            (Location.A1_CHARSI, Location.A1_STASH): [1704, 1703, 1702, 1700],
            (Location.A1_CHARSI, Location.A1_KASHYA_CAIN): [1704, 1703, 1702, 1700],
            (Location.A1_CHARSI, Location.A1_AKARA): [1704, 1703, 1702, 1705, 1706, 1707],
            (Location.A1_CHARSI, Location.A1_WP_NORTH): [1704, 1703, 1702],
            (Location.A1_CHARSI, Location.A1_WP_SOUTH): [1704, 1703, 1702, 1705],
            (Location.A1_CHARSI, Location.A1_WP): [1704, 1703, 1702, 1701, 1709],
            #from the Akara to where?
            (Location.A1_AKARA, Location.A1_STASH): [1707, 1706, 1705, 1700],
            (Location.A1_AKARA, Location.A1_KASHYA_CAIN): [1707, 1706, 1705, 1700],
            (Location.A1_AKARA, Location.A1_CHARSI): [1707, 1706, 1705, 1702, 1703, 1704],
            (Location.A1_AKARA, Location.A1_WP_NORTH): [1707, 1706, 1705, 1702],
            (Location.A1_AKARA, Location.A1_WP_SOUTH): [1707, 1706, 1706],
            (Location.A1_AKARA, Location.A1_WP): [1707, 1706, 1701, 1709],
            (Location.A1_WP_SOUTH, Location.A1_WP_NORTH): [1702],
            #from town portal
            (Location.A1_TOWN_TP, Location.A1_KASHYA_CAIN): [1708, 1700],
        }
        self._paths = {
            # Pindle
            (Location.A5_PINDLE_START, Location.A5_PINDLE_SAFE_DIST): [100, 101, 102, 103],
            (Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END): [104],
            # Eldritch
            (Location.A5_ELDRITCH_START, Location.A5_ELDRITCH_SAFE_DIST): [120, 121, 122],
            (Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END): [123],
            # Shenk
            (Location.A5_SHENK_START, Location.A5_SHENK_SAFE_DIST): [141, 142, 143, 144, 145, 146, 147, 148],
            (Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END): [149],
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
        if not (char.capabilities.can_teleport_natively or char.capabilities.can_teleport_with_charges):
            error_msg = "Teleport is required for static pathing"
            Logger.error(error_msg)
            raise ValueError(error_msg)
        char.select_tp()
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


    def find_abs_node_pos(self, node_idx: int, img: np.ndarray, threshold: float = 0.68, grayscale = True) -> tuple[float, float]:
        node = self._nodes[node_idx]
        template_match = template_finder.search(
            [*node],
            img,
            best_match=not grayscale,
            threshold=threshold,
            roi=Config().ui_roi["cut_skill_bar"],
            use_grayscale=grayscale
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
                        x_m, y_m = convert_abs_to_monitor(node_pos_abs, avoid_hud=True)
                        char.move((x_m, y_m), force_tp=force_tp, force_move=force_move)
                        last_direction = node_pos_abs
                        last_move = time.time()

        return True

    def traverse_nodes_automap(
        self,
        path: tuple[Location, Location] | list[int],
        char: IChar,
        timeout: float = 5,
        do_pre_move: bool = True,
        force_move: bool = False,
        threshold: float = 0.75, #down from 0.78 to allow proper traverse in A1 town
        toggle_map: bool = True,
        force_tp: bool = False,
        use_tp_charge: bool = False
    ) -> bool:

        if len(path) == 0:
            Logger.error("Path must be a list of integers or a tuple with start and end location!")
            return False
        if type(path[0]) != int:
            start_location = path[0]
            end_location = path[1]
            Logger.debug(f"Traverse from {start_location} to {end_location}")
            try:
                path = self._paths_automap[(start_location, end_location)]
            except KeyError:
                if start_location == end_location:
                    return True
                Logger.error(f"Don't know how to traverse from {start_location} to {end_location}")
                return False
        else:
            Logger.debug(f"Traverse automap: {path}")

        if toggle_map:
            toggle_automap()
            time.sleep(0.04)
        if (force_tp or use_tp_charge) and char.select_tp():
            # this means we want to use tele charge and we were able to select it
            pass
        elif do_pre_move:
            # we either want to tele charge but have no charges or don't wanna use the charge falling back to default pre_move handling
            char.pre_move()

        if Config().char["type"] == "fohdin": # Walking FOHdin will want to have conviction on so that in case he force moves on mobs, he also kills them.
            if char.capabilities.can_teleport_with_charges:
                keyboard.send(Config().fohdin["conviction"])
                wait(0.15)

        last_direction = None
        for i, node_idx in enumerate(path):
            continue_to_next_node = False
            last_move = time.time()
            did_force_move = False
            stuck_cnt = 0
            last_node_pos_abs = (0, 0)
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
                            if Config().general["info_screenshots"]: cv2.imwrite("./log/screenshots/info/info_pather_automap_got_stuck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                            toggle_automap(True)
                            if Config().general["info_screenshots"]: cv2.imwrite("./log/screenshots/info/info_pather_automap_got_stuck_" + time.strftime("%Y%m%d_%H%M%S") + "_automap.png", img)
                            Logger.error("Got stuck exit pather")
                            # actually, typically pather gets stuck with automap if the automap is off whilst a traverse is performed, would be clever to just switch the map on and retry the traverse
                        if toggle_map:
                            Logger.debug("Got stuck, switching Automap:"+ '\033[91m' + " OFF" + '\033[0m')
                            toggle_automap(False)
                            if Config().general["info_screenshots"]: cv2.imwrite("./log/screenshots/info/info_pather_automap_got_stuck_AM_off" + time.strftime("%Y%m%d_%H%M%S") + "_automap.png", img)
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

                # Find any template and calc node position from it
                node_pos_abs = self.find_abs_node_pos(node_idx, img, threshold=threshold, grayscale=False)
                if node_pos_abs is not None:
                    if node_pos_abs == last_node_pos_abs:
                        stuck_cnt += 1
                        # Sometimes we get stuck at a Shrine or Stash.
                        # Check for shrine after a few failed moves, then force a left click.
                        if stuck_cnt % 5 == 0 and (match := detect_screen_object(ScreenObjects.ShrineArea)).valid:
                            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_shrine_check_before" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                            Logger.debug(f"Shrine found, activating it")
                            #select_screen_object_match(match) #this does NOT work :(
                            x_m, y_m = convert_abs_to_monitor((0, -130)) #above head
                            mouse.move(x_m, y_m)
                            wait(0.1, 0.15)
                            mouse.click(button="left")
                            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_shrine_check_after" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                    else:
                        last_node_pos_abs = node_pos_abs
                        stuck_cnt = 0

                    dist = math.dist(node_pos_abs, (0, 0)) * 6
                    if dist < Config().ui_pos["reached_node_dist"]:
                        continue_to_next_node = True
                    else:
                        # Move the char
                        last_direction = (node_pos_abs[0]*8, node_pos_abs[1]*8)
                        x_m, y_m = convert_abs_to_monitor(last_direction, avoid_hud=True)
                        char.move((x_m, y_m), force_tp=force_tp, force_move=force_move)
                        last_move = time.time()
        if toggle_map:
            toggle_automap(False)
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
                        cv2.putText(display_img, str(node_idx), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                        x, y = convert_abs_to_screen(ref_pos_abs)
                        cv2.circle(display_img, (x, y), 5, (0, 255, 0), 3)
                        cv2.putText(display_img, template_type, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                        wrt_origin = (-ref_pos_abs[0], -ref_pos_abs[1])
                        print(f'Found template "{template_type}" at abs coordinates: {ref_pos_abs}')
                        # print(f'Template: "{template_type}", coordinates with respect to origin: {wrt_origin}')
            # display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5)
            # if round(time.time() - start) % 3 == 0:
            #     cv2.imwrite("./log/screenshots/info/pather_" + time.strftime("%Y%m%d_%H%M%S") + ".png", display_img)
            cv2.imshow("debug", display_img)
            cv2.waitKey(1)
    
    def show_automap_pos(template: list[str], threshold=0.78):
        match = template_finder.search_and_wait(template, threshold=threshold, timeout=0.1, suppress_debug=True)
        if match.valid:
            ref_pos_abs = convert_screen_to_abs(match.center)
            #Logger.info(f"{match.name}: {-ref_pos_abs[0], -ref_pos_abs[1]}")
            print("    '" + str(match.name) + "': (" + str(-ref_pos_abs[0]) + ", " + str(-ref_pos_abs[1]) + "),")
        else:
            print("    #'" + str(template) + "': (0, 0),")

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
