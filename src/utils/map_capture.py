import cv2
import numpy as np
import time
import keyboard
from asyncio.log import logger
import cv2
import time
import random
import keyboard
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from typing import Union
from item.pickit import PickIt
from template_finder import TemplateFinder
from town.town_manager import TownManager
from ui import UiManager
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import Screen
import numpy as np


class map_fun:
    def __init__(
        self,
        screen: Screen,
        template_finder: TemplateFinder,
        #pather: Pather,
        #town_manager: TownManager,
        #ui_manager: UiManager,
        #char: IChar,
        #pickit: PickIt
    ):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        # self._pather = pather
        # self._town_manager = town_manager
        # self._ui_manager = ui_manager
        # self._char = char
        # self._pickit = pickit
        # self._picked_up_items = False
        # self.used_tps = 0

    def _map_capture(self):
        pre = self._screen.grab()
        pre = cv2.cvtColor(pre, cv2.COLOR_BGRA2BGR)
        keyboard.press_and_release("tab")
        wait(.075)

        # Map is shown
        during_1 = self._screen.grab()
        during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGRA2BGR)
        wait(.075)

        # Map is still there, but we can tell if any carvers/flames are underneath fucking up the diff
        during_2 = self._screen.grab()
        during_2 = cv2.cvtColor(during_2, cv2.COLOR_BGRA2BGR)
        keyboard.press_and_release("tab")

        pre = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)
                
        during_1 = cv2.cvtColor(during_1, cv2.COLOR_HSV2BGR)  # convert it to bgr which lets us convert to gray..
        during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGR2GRAY)

        absdiff_1 = cv2.absdiff(pre, during_1)

        diffed = absdiff_1
        diffed = cv2.cvtColor(diffed, cv2.COLOR_GRAY2BGR)

        # Debug showing captures
        cv2.imshow('pre', pre)
        cv2.waitKey(0)
        cv2.imshow('during 1', during_1)
        cv2.waitKey(0)
        cv2.imshow('during 2', during_2)
        cv2.waitKey(0)
        cv2.imshow('diffed', diffed)
        cv2.waitKey(0)
        return pre, during_1, during_2, diffed

    def map_diff(pre, during_1, during_2, is_start=False, show_current_location=True, threshold=0.11):
        """Takes the 3 stages of map capture and outputs a final diff, removing carvers and adding our own markers"""

        # image without map
        pre = cv2.cvtColor(pre, cv2.COLOR_BGR2GRAY)
        """
        # images displaying the map, clean up some things from this display so it's less cluttered
        original_during_1 = during_1.copy()

        # during_1 = _mask_image(during_1, (0x20, 0x84, 0xF6))  # player marker
        # during_1 = _mask_image(during_1, (0x44, 0x70, 0x74))  # merc marker
        # during_1 = _mask_image(during_1, (0xff, 0xff, 0xff))  # npc marker

        # TODO: HSV it up..
        #   1. White (i.e. npc) is HSV (0, 1, 75%) through (0, 0, 100)
        #   2. Blue on minimap (i.e. you) is HSV (210, 85%, 85%) through (215, 87%, 99%)
        #   3. Greenish on minimap (i.e. merc) is HSV (180, 40%, 40%) through (190, 42%, 42%)
        during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGR2HSV)
        # during_1 = _remove_range(during_1, (0, 0, .75 * 255), (0, 25, 255))  # white npcs
        # during_1 = _remove_range(during_1, (210, .85 * 255, .85 * 255), (215, .90 * 255, 255))  # blue, current player marker
        # during_1 = _remove_range(during_1, (180, .4 * 255, .4 * 255), (190, .42 * 255, .42 * 255))  # green mercs
        masks_to_remove = [
            cv2.inRange(during_1, (0, 0, .75 * 255), (0, 25, 255)),  # white npcs
            # cv2.inRange(during_1, (200, .80 * 255, .85 * 255), (215, .95 * 255, 255)),  # blue, current player marker
            cv2.inRange(during_1, (105, int(.85 * 255), int(.8 * 255)), (110, int(.90 * 255), int(1 * 255))),  # blue, current player marker
            # (185,41,45) .. (183,37,41) .. (184,40,39)
            cv2.inRange(during_1, (90, int(.35 * 255), int(.35 * 255)), (95, int(.45 * 255), int(.50 * 255))),  # green mercs

            # TODO: Yellow warps ??? Red portal ?? remove it, but re-add it colored as warp?
        ]
        
        # Debug showing masked things being removed
        # cv2.imshow('mask', during_1)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        """
        during_1 = cv2.cvtColor(during_1, cv2.COLOR_HSV2BGR)  # convert it to bgr which lets us convert to gray..
        during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGR2GRAY)
        # during_2 = cv2.cvtColor(during_2, cv2.COLOR_BGR2GRAY)

        # Get diff of original pre-map image vs both map snapshots, combine the artifacts from both snapshots
        absdiff_1 = cv2.absdiff(pre, during_1)
        # _, thresholded_1 = cv2.threshold(absdiff_1, int(threshold * 255), 255, cv2.THRESH_BINARY)

        # absdiff_2 = cv2.absdiff(pre, during_2)
        # _, thresholded_2 = cv2.threshold(absdiff_2, int(threshold * 255), 255, cv2.THRESH_BINARY)

        # diffed = cv2.bitwise_and(thresholded_1, thresholded_2)
        # diffed = thresholded_1
        diffed = absdiff_1
        """
        # earlier we masked some things from the minimap, remove them now post-diff
        for mask_locations in masks_to_remove:
            img_mask = cv2.blur(mask_locations, (2, 2))
            _, img_mask = cv2.threshold(img_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)

            diffed = cv2.bitwise_and(diffed, diffed, mask=255 - img_mask)
        """
        # Debug showing diff before adding circles
        # cv2.imshow('absdiff_1', absdiff_1)
        # cv2.waitKey(0)
        # cv2.imshow('absdiff_2', absdiff_2)
        # cv2.waitKey(0)
        # cv2.imshow('diffed', diffed)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Draw a big red/green circle + warps that will stick around between images
        diffed = cv2.cvtColor(diffed, cv2.COLOR_GRAY2BGR)

        # TODO: RE-DO WARP MASKS WITH HSV!

        # # were there any warps here? highlight them!
        # # range_start, range_end = color_rgb_to_bgr_range((0xD9, 0x58, 0xEB))  # gets top of warp
        # # range_start, range_end = color_rgb_to_bgr_range((0xA2, 0x46, 0xEA))  # middle of warp
        # # range_start, range_end = color_rgb_to_bgr_range((0xB5, 0x4C, 0xEB))  # middle of warp
        # range_start, range_end = _color_rgb_to_bgr_range((0x8D, 0x3C, 0xB2), range=1.5)  # middle of warp
        # # range_start, range_end = (0xEB - 15, 0x58 - 15, 0xD9 - 15), (0xEA + 15, 0x46 + 15, 0xA2 + 15)
        # warp_mask = cv2.inRange(original_during_1, range_start, range_end)
        # warp_mask = cv2.blur(warp_mask, (5, 5))
        # _, warp_mask = cv2.threshold(warp_mask, int(0.1 * 255), 255, cv2.THRESH_BINARY)
        #
        # diffed[warp_mask > 0] = [0xD9, 0x58, 0xEB]  # Where ever there is a warp color it in with da purps
        """
        if show_current_location:
            if is_start:
                color = (0, 0, 255)  # red
            else:
                color = (0, 255, 0)  # green

            # I don't know why I have to offset the center x/y, but if I don't it is .. offset!
            cv2.circle(diffed, (center_x + 12, center_y - 12), 2, color, -1)

        # Debug showing diff post circles
        # cv2.imshow('diffed', diffed)
        # cv2.waitKey(0)
        """
        return diffed   

if __name__ == "__main__":
    from screen import Screen
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from config import Config
    config = Config()
    screen = Screen()

    pre, during_1, during_2, differ = map_fun.self._map_capture()