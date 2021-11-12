import cv2
from enum import Enum
from screen import Screen
from typing import Tuple, Union, List
import numpy as np
from logger import Logger
import time
from config import Config


def load_template(path, scale_factor):
    template_img = cv2.imread(path)
    template_img = cv2.resize(template_img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
    return template_img

class TemplateFinder:
    def __init__(self, screen: Screen, scale_factor: float = 0.7):
        """
        :param screen: Screen object
        :param scale_factor: Scale factor that is used for templates. Note: UI and NPC templates will always have scale of 1.0
        """
        self.last_score = -1.0
        self._screen = screen
        self._scale_factor = scale_factor
        self._config = Config()
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
            "A5_TOWN_10": [load_template("assets/templates/a5_town/a5_town_10.png", self._scale_factor), self._scale_factor],
            # Templates for nod at Pindle
            "PINDLE_0": [load_template("assets/templates/pindle/pindle_0.png", self._scale_factor), self._scale_factor],
            "PINDLE_1": [load_template("assets/templates/pindle/pindle_1.png", self._scale_factor), self._scale_factor],
            "PINDLE_2": [load_template("assets/templates/pindle/pindle_2.png", self._scale_factor), self._scale_factor],
            "PINDLE_3": [load_template("assets/templates/pindle/pindle_3.png", self._scale_factor), self._scale_factor],
            "PINDLE_4": [load_template("assets/templates/pindle/pindle_4.png", self._scale_factor), self._scale_factor],
            "PINDLE_5": [load_template("assets/templates/pindle/pindle_5.png", self._scale_factor), self._scale_factor],
            "PINDLE_6": [load_template("assets/templates/pindle/pindle_6.png", self._scale_factor), self._scale_factor],
            "PINDLE_7": [load_template("assets/templates/pindle/pindle_7.png", self._scale_factor), self._scale_factor],
            # Templates for nodes to Eldritch
            "ELDRITCH_0": [load_template("assets/templates/eldritch/eldritch_0.png", self._scale_factor), self._scale_factor],
            "ELDRITCH_1": [load_template("assets/templates/eldritch/eldritch_1.png", self._scale_factor), self._scale_factor],
            "ELDRITCH_2": [load_template("assets/templates/eldritch/eldritch_2.png", self._scale_factor), self._scale_factor],
            "ELDRITCH_3": [load_template("assets/templates/eldritch/eldritch_3.png", self._scale_factor), self._scale_factor],
            "ELDRITCH_4": [load_template("assets/templates/eldritch/eldritch_4.png", self._scale_factor), self._scale_factor],
            # Templates for nodes to Shenk (from Eldritch)
            "SHENK_0": [load_template("assets/templates/shenk/shenk_0.png", self._scale_factor), self._scale_factor],
            "SHENK_1": [load_template("assets/templates/shenk/shenk_1.png", self._scale_factor), self._scale_factor],
            "SHENK_2": [load_template("assets/templates/shenk/shenk_2.png", self._scale_factor), self._scale_factor],
            "SHENK_3": [load_template("assets/templates/shenk/shenk_3.png", self._scale_factor), self._scale_factor],
            "SHENK_4": [load_template("assets/templates/shenk/shenk_4.png", self._scale_factor), self._scale_factor],
            "SHENK_6": [load_template("assets/templates/shenk/shenk_6.png", self._scale_factor), self._scale_factor],
            "SHENK_7": [load_template("assets/templates/shenk/shenk_7.png", self._scale_factor), self._scale_factor],
            "SHENK_8": [load_template("assets/templates/shenk/shenk_8.png", self._scale_factor), self._scale_factor],
            "SHENK_9": [load_template("assets/templates/shenk/shenk_9.png", self._scale_factor), self._scale_factor],
            "SHENK_10": [load_template("assets/templates/shenk/shenk_10.png", self._scale_factor), self._scale_factor],
            "SHENK_11": [load_template("assets/templates/shenk/shenk_11.png", self._scale_factor), self._scale_factor],
            "SHENK_12": [load_template("assets/templates/shenk/shenk_12.png", self._scale_factor), self._scale_factor],
            "SHENK_13": [load_template("assets/templates/shenk/shenk_13.png", self._scale_factor), self._scale_factor],
            "SHENK_15": [load_template("assets/templates/shenk/shenk_15.png", self._scale_factor), self._scale_factor],
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
            "PLAY_BTN_GRAY": [load_template("assets/templates/play_btn_gray.png", 1.0), 1.0],
            "NORMAL_BTN": [load_template("assets/templates/normal_btn.png", 1.0), 1.0],
            "NIGHTMARE_BTN": [load_template("assets/templates/nightmare_btn.png", 1.0), 1.0],            
            "HELL_BTN": [load_template("assets/templates/hell_btn.png", 1.0), 1.0],
            "SAVE_AND_EXIT_NO_HIGHLIGHT": [load_template("assets/templates/save_and_exit_no_highlight.png", 1.0), 1.0],
            "SAVE_AND_EXIT_HIGHLIGHT": [load_template("assets/templates/save_and_exit_highlight.png", 1.0), 1.0],
            "SERVER_ISSUES": [load_template("assets/templates/server_issues.png", 1.0), 1.0],
            "WAYPOINT_MENU": [load_template("assets/templates/waypoint_menu.png", 1.0), 1.0],
            "MERC": [load_template("assets/templates/merc.png", 1.0), 1.0],
            "TELE_ACTIVE": [load_template("assets/templates/tele_active.png", 1.0), 1.0],
            "TELE_INACTIVE": [load_template("assets/templates/tele_inactive.png", 1.0), 1.0],
            "REPAIR_BTN": [load_template("assets/templates/repair_btn.png", 1.0), 1.0],
            "TP_TOMB": [load_template("assets/templates/tp_tomb.png", 1.0), 1.0],
            "SUPER_HEALING_POTION": [load_template("assets/templates/super_healing_potion.png", 1.0), 1.0],
            "SUPER_MANA_POTION": [load_template("assets/templates/super_mana_potion.png", 1.0), 1.0],
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
            # NPC: Larzuk
            "LARZUK_FRONT": [load_template("assets/npc/larzuk/larzuk_front.png", 1.0), 1.0],
            "LARZUK_BACK": [load_template("assets/npc/larzuk/larzuk_back.png", 1.0), 1.0],
            "LARZUK_SIDE": [load_template("assets/npc/larzuk/larzuk_side.png", 1.0), 1.0],
            "LARZUK_SIDE_2": [load_template("assets/npc/larzuk/larzuk_side_2.png", 1.0), 1.0],
            "LARZUK_SIDE_3": [load_template("assets/npc/larzuk/larzuk_side_3.png", 1.0), 1.0],
            "LARZUK_NAME_TAG_WHITE": [load_template("assets/npc/larzuk/larzuk_white.png", 1.0), 1.0],
            "LARZUK_NAME_TAG_GOLD": [load_template("assets/npc/larzuk/larzuk_gold.png", 1.0), 1.0],
            "LARZUK_TRADE_REPAIR_BTN": [load_template("assets/npc/larzuk/trade_repair_btn.png", 1.0), 1.0],
        }

    def get_template(self, key):
        return self._templates[key][0]

    def search(self, ref: Union[str, np.ndarray], inp_img: np.ndarray, threshold: float = 0.7, roi: List[float] = None) -> Tuple[bool, Tuple[float, float]]:
        """
        Search for a template in an image
        :param ref: Either key of a already loaded template or a image which is used as template
        :param inp_img: Image in which the template will be searched
        :param threshold: Threshold which determines if a template is found or not
        :param roi: Region of Interest of the inp_img to restrict search area. Format [left, top, width, height]
        :return: Returns found flag and the position as [bool, [x, y]]. If not found, position will be None. Position in image space.
        """
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
            self.last_score = max_val
            if max_val > threshold:
                ref_point = (max_pos[0] + int(template.shape[1] * 0.5) + rx, max_pos[1] + int(template.shape[0] * 0.5) + ry)
                ref_point = (int(ref_point[0] * (1.0 / scale)), int(ref_point[1] * (1.0 / scale)))
                return True, ref_point
        return False, None

    def search_and_wait(self, ref: Union[str, List[str]], roi: List[float] = None, time_out: float = None, threshold: float = 0.7) -> Tuple[bool, Tuple[float, float]]:
        """
        Helper function that will loop and keep searching for a template
        :param ref: Key of template which has been loaded beforehand
        :param time_out: After this amount of time the search will stop and it will return [False, None]
        Rest of params same as TemplateFinder.search()
        """
        Logger.debug(f"Waiting for Template {ref}")
        start = time.time()
        while 1:
            img = self._screen.grab()
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 1.0

            if type(ref) is str:
                ref = [ref]
            for x in ref:
                success, pos = self.search(x, img, roi=roi, threshold=threshold)
                if success:
                    break
            if not is_loading_black_roi:
                if success:
                    return True, pos
                elif time_out is not None and (time.time() - start) > time_out:
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
        success, pos = template_finder.search("BLUE_PORTAL", img, threshold=0.67)
        print(template_finder.last_score)
        if success:
            cv2.circle(img, pos, 7, (255, 0, 0), thickness=5)
        img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('test', img)
        key = cv2.waitKey(1)
