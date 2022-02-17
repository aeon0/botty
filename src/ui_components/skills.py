# - left skill
# 	- left skill
# 	f: is_left_skill_selected(self, template_list: List[str]) -> bool:
# - Right skill
# 	- right_skill
# 	f: has_tps(self) -> bool:
# 	f: is_right_skill_active(self) -> bool:
# 	f: is_right_skill_selected(self, template_list: List[str]) -> bool:
#     f:  _discover_capabilities(self) -> CharacterCapabilities:
#     f:  discover_capabilities(self, force = False):
#     f: on_capabilities_discovered(self, capabilities: CharacterCapabilities):
# 	f: skill_is_charged(self, img: np.ndarray = None) -> bool:
# 	f: is_low_on_teleport_charges(self):
#     f: _remap_skill_hotkey(self, skill_asset, hotkey, skill_roi, expanded_skill_roi):
#     f: remap_right_skill_hotkey(self, skill_asset, hotkey):
#     f: def select_tp(self):
#     f: get_skill_charges(self, img: np.ndarray = None):
from typing import List
import keyboard
from logger import Logger
import cv2
import time
import numpy as np
from utils.misc import cut_roi, color_filter, wait
from screen import grab
from config import Config
from template_finder import TemplateFinder

def is_left_skill_selected(template_list: List[str]) -> bool:
    """
    :return: Bool if skill is currently the selected skill on the left skill slot.
    """
    skill_left_ui_roi = Config().ui_roi["skill_left"] 
    for template in template_list:
        if TemplateFinder().search(template, grab(), threshold=0.84, roi=skill_left_ui_roi).valid:
            return True
    return False

def has_tps() -> bool:
    """
    :return: Returns True if botty has town portals available. False otherwise
    """
    if Config().char["tp"]:
        keyboard.send(Config().char["tp"])
        skill_right_ui_roi = Config().ui_roi["skill_right"]
        template_match = TemplateFinder().search_and_wait(
            ["TP_ACTIVE", "TP_INACTIVE"],
            roi=skill_right_ui_roi,
            best_match=True,
            threshold=0.79,
            time_out=4)
        if not template_match.valid:
            Logger.warning("You are out of tps")
            if Config().general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/debug_out_of_tps_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        return template_match.valid
    else:
        return False

def select_tp(tp_hotkey):
    if tp_hotkey and not is_right_skill_selected(
        ["TELE_ACTIVE", "TELE_INACTIVE"]):
        keyboard.send(tp_hotkey)
        wait(0.1, 0.2)
    return is_right_skill_selected(["TELE_ACTIVE", "TELE_INACTIVE"])

def is_right_skill_active() -> bool:
    """
    :return: Bool if skill is red/available or not. Skill must be selected on right skill slot when calling the function.
    """
    roi = [
        Config().ui_pos["skill_right_x"] - (Config().ui_pos["skill_width"] // 2),
        Config().ui_pos["skill_y"] - (Config().ui_pos["skill_height"] // 2),
        Config().ui_pos["skill_width"],
        Config().ui_pos["skill_height"]
    ]
    img = cut_roi(grab(), roi)
    avg = np.average(img)
    return avg > 75.0

def is_right_skill_selected(template_list: List[str]) -> bool:
    """
    :return: Bool if skill is currently the selected skill on the right skill slot.
    """
    skill_right_ui_roi = Config().ui_roi["skill_right"]
    for template in template_list:
        if TemplateFinder().search(template, grab(), threshold=0.84, roi=skill_right_ui_roi).valid:
            return True
    return False

def get_skill_charges(ocr, img: np.ndarray = None):
    if img is None:
        img = grab()
    x, y, w, h = Config().ui_roi["skill_right"]
    x = x - 1
    y = y + round(h/2)
    h = round(h/2 + 5)
    img = cut_roi(img, [x, y, w, h])
    mask, _ = color_filter(img, Config().colors["skill_charges"])
    ocr_result = ocr.image_to_text(
        images = mask,
        model = "engd2r_inv_th",
        psm = 7,
        word_list = "",
        scale = 1.4,
        crop_pad = False,
        erode = False,
        invert = True,
        threshold = 0,
        digits_only = True,
        fix_regexps = False,
        check_known_errors = False,
        check_wordlist = False,
        word_match_threshold = 0.9
    )[0]
    try:
        return int(ocr_result.text)
    except:
        return None
