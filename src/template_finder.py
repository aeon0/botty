import cv2
from enum import Enum
from screen import Screen
from typing import Tuple, Union, List
import numpy as np
from logger import Logger
import time


def load_template(path, scale_factor):
    template_img = cv2.imread(path)
    template_img = cv2.resize(template_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
    return template_img

class TemplateFinder:
    def __init__(self, screen: Screen, scale_factor: float = 0.5):
        self.debug_last_score = -1.0
        self._screen = screen
        self._scale_factor = scale_factor
        self._templates = {
            # Templates for node in A5 Town
            "A5_TOWN_0": [load_template("assets/templates/a5_town/a5_town_0.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_0.5": [load_template("assets/templates/a5_town/a5_town_0.5.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_1": [load_template("assets/templates/a5_town/a5_town_1.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_2": [load_template("assets/templates/a5_town/a5_town_2.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_3": [load_template("assets/templates/a5_town/a5_town_3.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_4": [load_template("assets/templates/a5_town/a5_town_4.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_5": [load_template("assets/templates/a5_town/a5_town_5.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_6": [load_template("assets/templates/a5_town/a5_town_6.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_7": [load_template("assets/templates/a5_town/a5_town_7.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_8": [load_template("assets/templates/a5_town/a5_town_8.png", self._scale_factor), self._scale_factor],
            "A5_TOWN_9": [load_template("assets/templates/a5_town/a5_town_9.png", self._scale_factor), self._scale_factor],
            # Template Pindle area (currently only used to check if we are at pindle, the walking is done statically)
            "PINDLE_STONE": [load_template("assets/templates/pindle_stone.png", self._scale_factor), self._scale_factor],
            # Template Shenk area (currently only used to check if we are at shenk at wp, the walking is done statically)
            "SHENK_FLAME": [load_template("assets/templates/shenk_flame.png", self._scale_factor), self._scale_factor],
            # Template Selectables
            "A5_STASH": [load_template("assets/templates/a5_stash.png", self._scale_factor), self._scale_factor],
            "A5_WP": [load_template("assets/templates/a5_wp.png", self._scale_factor), self._scale_factor],
            "A5_RED_PORTAL": [load_template("assets/templates/a5_red_portal.png", self._scale_factor), self._scale_factor],
            "BLUE_PORTAL": [load_template("assets/templates/blue_portal.png", self._scale_factor), self._scale_factor],
            "BLUE_PORTAL_2": [load_template("assets/templates/blue_portal_2.png", self._scale_factor), self._scale_factor],
            # Template Inventory / UI
            "INVENTORY_GOLD_BTN": [load_template("assets/templates/inventory_gold_btn.png", 1.0), 1.0],
            "D2_LOGO_HS": [load_template("assets/templates/d2_logo_hs.png", 1.0), 1.0],
            "LOADING": [load_template("assets/templates/loading.png", 1.0), 1.0],
            "PLAY_BTN": [load_template("assets/templates/play_btn.png", 1.0), 1.0],
            "HELL_BTN": [load_template("assets/templates/hell_btn.png", 1.0), 1.0],
            "SAVE_AND_EXIT": [load_template("assets/templates/save_and_exit.png", 1.0), 1.0],
            "SERVER_ISSUES": [load_template("assets/templates/server_issues.png", 1.0), 1.0],
            "WAYPOINT_MENU": [load_template("assets/templates/waypoint_menu.png", 1.0), 1.0],
            "MERC": [load_template("assets/templates/merc.png", 1.0), 1.0],
            "TELE_ACTIVE": [load_template("assets/templates/tele_active.png", 1.0), 1.0],
            "TELE_INACTIVE": [load_template("assets/templates/tele_inactive.png", 1.0), 1.0],
            # NPC: Qual-Kehk
            "QUAL_FRONT": [load_template("assets/npc/qual_kehk/qual_front.png", 1.0), 1.0],
            "QUAL_SIDE": [load_template("assets/npc/qual_kehk/qual_side.png", 1.0), 1.0],
            "QUAL_BACK": [load_template("assets/npc/qual_kehk/qual_back.png", 1.0), 1.0],
            "QUAL_45": [load_template("assets/npc/qual_kehk/qual_45.png", 1.0), 1.0],
            "QUAL_45_2": [load_template("assets/npc/qual_kehk/qual_45_2.png", 1.0), 1.0],
            "QUAL_45_3": [load_template("assets/npc/qual_kehk/qual_45_3.png", 1.0), 1.0],
            "QUAL_NAME_TAG_WHITE": [load_template("assets/npc/qual_kehk/qual_kehk_white.png", 1.0), 1.0],
            "QUAL_NAME_TAG_GOLD": [load_template("assets/npc/qual_kehk/qual_kehk_gold.png", 1.0), 1.0],
            "QUAL_RESURRECT_BTN": [load_template("assets/npc/qual_kehk/resurrect_btn.png", 1.0), 1.0],
            # NPC: Malah
            "MALAH_FRONT": [load_template("assets/npc/malah/malah_front.png", 1.0), 1.0],
            "MALAH_BACK": [load_template("assets/npc/malah/malah_BACK.png", 1.0), 1.0],
            "MALAH_45": [load_template("assets/npc/malah/malah_45.png", 1.0), 1.0],
            "MALAH_SIDE": [load_template("assets/npc/malah/malah_side.png", 1.0), 1.0],
            "MALAH_SIDE_2": [load_template("assets/npc/malah/malah_side_2.png", 1.0), 1.0],
            "MALAH_NAME_TAG_WHITE": [load_template("assets/npc/malah/malah_white.png", 1.0), 1.0],
            "MALAH_NAME_TAG_GOLD": [load_template("assets/npc/malah/malah_gold.png", 1.0), 1.0],
            "MALAH_TRADE_BTN": [load_template("assets/npc/malah/trade_btn.png", 1.0), 1.0],
        }

    def get_template(self, key):
        return self._templates[key][0]

    def search(self, ref: Union[str, np.ndarray], inp_img: np.ndarray, threshold: float = 0.7, roi: List[float] = None) -> Tuple[bool, Tuple[float, float]]:
        if roi is None:
            # if no roi is provided roi = full inp_img
            roi = [0, 0, inp_img.shape[1], inp_img.shape[0]]
        rx, ry, rw, rh = roi
        inp_img = inp_img[ry:ry + rh, rx:rx + rw]

        if type(ref) == str:
            template = self._templates[ref][0]
            scale = self._templates[ref][1]
        else:
            template = ref
            scale = 1.0

        img: np.ndarray = cv2.resize(inp_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
        rx *= scale
        ry *= scale
        rw *= scale
        rh *= scale

        if img.shape[0] > template.shape[0] and img.shape[1] > template.shape[1]:
            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_pos = cv2.minMaxLoc(res)
            self.debug_last_score = max_val
            if max_val > threshold:
                ref_point = (max_pos[0] + int(template.shape[1] * 0.5) + rx, max_pos[1] + int(template.shape[0] * 0.5) + ry)
                ref_point = (int(ref_point[0] * (1.0 / scale)), int(ref_point[1] * (1.0 / scale)))
                return True, ref_point
        return False, None

    def search_and_wait(self, ref: str, roi: List[float] = None, time_out: float = None, threshold: float = 0.7) -> Tuple[float, float]:
        Logger.debug(f"Waiting for Template {ref}")
        start = time.time()
        while 1:
            img = self._screen.grab()
            # TODO: 1920x1080 specific params
            is_loading_black_roi = np.average(img[:, 0:500]) < 1.0
            success, pos = self.search(ref, img, roi=roi, threshold=threshold)
            if not is_loading_black_roi and success:
                return True, pos
            if time_out is not None and (time.time() - start) > time_out:
                cv2.imwrite(f"info_wait_for_{ref}_time_out.png", img)
                return False, None


# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    from screen import Screen
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    while 1:
        img = screen.grab()
        success, pos = template_finder.search("BLUE_PORTAL", img)
        print(template_finder.debug_last_score)
        if success:
            cv2.circle(img, pos, 7, (255, 0, 0), thickness=5)
        img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('test', img)
        key = cv2.waitKey(1)
