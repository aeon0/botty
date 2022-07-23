import keyboard
from logger import Logger
import cv2
import time
from utils.custom_mouse import mouse
import numpy as np
from utils.misc import cut_roi, color_filter, wait
from screen import grab, convert_screen_to_monitor
from config import Config
import template_finder
from ui_manager import is_visible, wait_until_visible, ScreenObjects
from d2r_image import ocr

LEFT_SKILL_ROI = [
        Config().ui_pos["skill_left_x"] - (Config().ui_pos["skill_width"] // 2),
        Config().ui_pos["skill_y"] - (Config().ui_pos["skill_height"] // 2),
        Config().ui_pos["skill_width"],
        Config().ui_pos["skill_height"]
]


RIGHT_SKILL_ROI = [
        Config().ui_pos["skill_right_x"] - (Config().ui_pos["skill_width"] // 2),
        Config().ui_pos["skill_y"] - (Config().ui_pos["skill_height"] // 2),
        Config().ui_pos["skill_width"],
        Config().ui_pos["skill_height"]
]


def _is_skill_active(roi: list[int]) -> bool:
    """
    :return: Bool if skill is currently active in the desired ROI
    """
    img = cut_roi(grab(), roi)
    avg = np.average(img)
    return avg > 75.0

def is_skill_active(roi: list[int]) -> bool:
    return _is_skill_active(roi)

def is_right_skill_active() -> bool:
    return _is_skill_active(roi = RIGHT_SKILL_ROI)

def is_left_skill_active() -> bool:
    return _is_skill_active(roi = LEFT_SKILL_ROI)


def _is_skill_bound(template_list: list[str] | str, roi: list[int]) -> bool:
    """
    :return: Bool if skill is currently the selected skill on the right skill slot.
    """
    if isinstance(template_list, str):
        template_list = [template_list]
    for template in template_list:
        if template_finder.search(template, grab(), threshold=0.84, roi=roi).valid:
            return True
    return False

def is_skill_bound(template_list: list[str] | str, roi: list[int] = Config().ui_roi["active_skills_bar"]) -> bool:
    """
    :return: Bool if skill is visible in ROI, defaults to active skills bar.
    """
    return _is_skill_bound(template_list, roi)

def is_right_skill_bound(template_list: list[str] | str) -> bool:
    return _is_skill_bound(template_list, RIGHT_SKILL_ROI)

def is_left_skill_bound(template_list: list[str] | str) -> bool:
    return _is_skill_bound(template_list, LEFT_SKILL_ROI)

def is_teleport_active(img: np.ndarray = None) -> bool:
    img = grab() if img is None else img
    if (match := template_finder.search(["BAR_TP_ACTIVE", "BAR_TP_INACTIVE"], img, roi=Config().ui_roi["active_skills_bar"], best_match=True)).valid:
        return not "inactive" in match.name.lower()
    return False

def has_tps() -> bool:
    if not (tps_remain := is_visible(ScreenObjects.BarTownPortalSkill)):
        Logger.warning("You are out of tps")
        if Config().general["info_screenshots"]:
            cv2.imwrite("./log/screenshots/info/debug_out_of_tps_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
    return tps_remain

def get_skill_charges(img: np.ndarray = None):
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
        model = "hover-eng_inconsolata_inv_th_fast",
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
        correct_words = False
    )[0]
    try:
        return int(ocr_result.text)
    except:
        return None

def skill_is_charged(img: np.ndarray = None) -> bool:
    img = grab() if img is None else img
    skill_img = cut_roi(img, Config().ui_roi["skill_right"])
    charge_mask, _ = color_filter(skill_img, Config().colors["blue"])
    if np.sum(charge_mask) > 0:
        return True
    return False

def is_low_on_teleport_charges(img: np.ndarray = None) -> bool:
    img = grab() if img is None else img
    charges_remaining = get_skill_charges(img)
    if charges_remaining:
        Logger.debug(f"{charges_remaining} teleport charges remain")
        return charges_remaining <= 3
    else:
        charges_present = skill_is_charged(img)
        if charges_present:
            Logger.error("is_low_on_teleport_charges: unable to determine skill charges, assume zero")
        return True

def _remap_skill_hotkey(skill_assets: list[str] | str, hotkey: str, skill_roi: list[int], expanded_skill_roi: list[int]) -> bool:
    x, y, w, h = skill_roi
    x, y = convert_screen_to_monitor((x, y))
    mouse.move(x + w/2, y + h / 2)
    mouse.click("left")
    wait(0.3)

    if isinstance(skill_assets, str):
        skill_assets = [skill_assets]
    for skill_asset in skill_assets:
        match = template_finder.search(skill_asset, grab(), threshold=0.84, roi=expanded_skill_roi)
        if match.valid:
            mouse.move(*match.center_monitor)
            wait(0.3)
            keyboard.send(hotkey)
            wait(0.3)
            mouse.click("left")
            wait(0.3)
            return True
    return False

def remap_right_skill_hotkey(skill_assets: list[str] | str, hotkey: str) -> bool:
    return _remap_skill_hotkey(skill_assets, hotkey, Config().ui_roi["skill_right"], Config().ui_roi["skill_speed_bar"])