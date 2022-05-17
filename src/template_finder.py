import cv2
import threading
from copy import deepcopy
from screen import convert_screen_to_monitor, grab
from typing import Union
from dataclasses import dataclass
import numpy as np
from logger import Logger
import time
import os
from config import Config
from utils.misc import cut_roi, load_template, list_files_in_folder, alpha_to_mask, roi_center, color_filter, mask_by_roi
from functools import cache

templates_lock = threading.Lock()

@dataclass
class Template:
    name: str = None
    img_bgra: np.ndarray = None
    img_bgr: np.ndarray = None
    img_gray: np.ndarray = None
    alpha_mask: np.ndarray = None

@dataclass
class TemplateMatch:
    name: str = None
    score: float = -1.0
    center: tuple[int, int] = None
    center_monitor: tuple[int, int] = None
    region: list[float] = None
    region_monitor: list[float] = None
    valid: bool = False


TEMPLATE_PATHS = [
    "assets\\templates",
    "assets\\npc",
    "assets\\shop",
    "assets\\item_properties",
    "assets\\chests",
    "assets\\gamble",
]

@cache
def _templates() -> dict[Template]:
    paths = []
    templates = {}
    for path in TEMPLATE_PATHS:
        paths += list_files_in_folder(path)
    for file_path in paths:
        file_name: str = os.path.basename(file_path)
        if file_name.lower().endswith('.png'):
            key = file_name[:-4].upper()
            template_img = load_template(file_path)
            templates[key] = Template(
                name = key,
                img_bgra = template_img,
                img_bgr = cv2.cvtColor(template_img, cv2.COLOR_BGRA2BGR),
                img_gray = cv2.cvtColor(template_img, cv2.COLOR_BGRA2GRAY),
                alpha_mask = alpha_to_mask(template_img)
            )
    return templates

def get_template(key):
    with templates_lock:
        return _templates()[key].img_bgr

def _process_template_refs(ref: Union[str, np.ndarray, list[str]]) -> list[Template]:
    templates = []
    if type(ref) != list:
        ref = [ref]
    for i in ref:
        # if the reference is a string, then it's a reference to a named template asset
        if type(i) == str:
            templates.append(_templates()[i.upper()])
        # if the reference is an image, append new Template class object
        elif type(i) == np.ndarray:
            templates.append(Template(
                img_bgr = i,
                img_gray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY),
                alpha_mask = alpha_to_mask(i)
            ))
    return templates

def _single_template_match(template: Template, inp_img: np.ndarray = None, roi: list = None, color_match: list = None, use_grayscale: bool = False) -> TemplateMatch:
    inp_img = inp_img if inp_img is not None else grab()
    template_match = TemplateMatch()

    # crop image to roi
    if roi is None:
        # if no roi is provided roi = full inp_img
        roi = [0, 0, inp_img.shape[1], inp_img.shape[0]]
    rx, ry, rw, rh = roi
    img = inp_img[ry:ry + rh, rx:rx + rw]

    # filter for desired color or make grayscale
    if color_match:
        template_img,  = color_filter(template.img_bgr, color_match)[1],
        img = color_filter(img, color_match)[1]
    elif use_grayscale:
        template_img = template.img_gray
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        template_img = template.img_bgr

    if not (img.shape[0] > template_img.shape[0] and img.shape[1] > template_img.shape[1]):
        Logger.error(f"Image shape and template shape are incompatible: {template.name}. Image: {img.shape}, Template: {template_img.shape}")
    else:
        res = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED, mask = template.alpha_mask)
        np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        _, max_val, _, max_pos = cv2.minMaxLoc(res)

        # save rectangle corresponding to matched region
        rec_x = int((max_pos[0] + rx))
        rec_y = int((max_pos[1] + ry))
        rec_w = int(template_img.shape[1])
        rec_h = int(template_img.shape[0])
        template_match.region = [rec_x, rec_y, rec_w, rec_h]
        template_match.region_monitor = [*convert_screen_to_monitor((rec_x, rec_y)), rec_w, rec_h]
        template_match.center = roi_center(template_match.region)
        template_match.center_monitor = convert_screen_to_monitor(template_match.center)
        template_match.name = template.name
        template_match.score = max_val
        template_match.valid = True

    return template_match


def search(
    ref: Union[str, np.ndarray, list[str]],
    inp_img: np.ndarray,
    threshold: float = 0.68,
    roi: list[float] = None,
    use_grayscale: bool = False,
    color_match: list = False,
    best_match: bool = False
) -> TemplateMatch:
    """
    Search for a template in an image
    :param ref: Either key of a already loaded template, list of such keys, or a image which is used as template
    :param inp_img: Image in which the template will be searched
    :param threshold: Threshold which determines if a template is found or not
    :param roi: Region of Interest of the inp_img to restrict search area. Format [left, top, width, height]
    :param use_grayscale: Use grayscale template matching for speed up
    :param color_match: Pass a color to be used by misc.color_filter to filter both image of interest and template image (format Config().colors["color"])
    :param best_match: If list input, will search for list of templates by best match. Default behavior is first match.
    :return: Returns a TemplateMatch object with a valid flag
    """
    templates = _process_template_refs(ref)
    matches = []
    for template in templates:
        match = _single_template_match(template, inp_img, roi, color_match, use_grayscale)
        if match.score >= threshold:
            if not best_match:
                return match
            else:
                matches.append(match)
    if matches:
        matches = sorted(matches, key=lambda obj: obj.score, reverse=True)
        return matches[0]
    return TemplateMatch()


def search_and_wait(
    ref: Union[str, list[str]],
    roi: list[float] = None,
    timeout: float = 30,
    threshold: float = 0.68,
    use_grayscale: bool = False,
    color_match: list = False,
    best_match: bool = False,
    suppress_debug: bool = False,
) -> TemplateMatch:
    """
    Helper function that will loop and keep searching for a template
    :param timeout: After this amount of time the search will stop and it will return [False, None]
    :Other params are the same as for TemplateFinder.search()
    :returns a TemplateMatch object
    """
    if not suppress_debug:
        Logger.debug(f"Waiting for templates: {ref}")
    start = time.time()
    template_match = TemplateMatch()
    while (time_remains := time.time() - start < timeout):
        img = grab()
        is_loading_black_roi = np.average(img[:, 0:Config().ui_roi["loading_left_black"][2]]) < 1.0
        if not is_loading_black_roi or "LOADING" in ref:
            template_match = search(ref, img, roi=roi, threshold=threshold, use_grayscale=use_grayscale, color_match=color_match, best_match=best_match)
            if template_match.valid:
                break
    if not time_remains:
        Logger.debug(f"Could not find desired templates")
    else:
        Logger.debug(f"Found match: {template_match.name} ({template_match.score*100:.1f}% confidence)")
    return template_match


def search_all(
    ref: Union[str, np.ndarray, list[str]],
    inp_img: np.ndarray,
    threshold: float = 0.68,
    roi: list[float] = None,
    use_grayscale: bool = False,
    color_match: list = False,
) -> list[TemplateMatch]:
    """
    Returns a list of all templates scoring above set threshold on the screen
    :Other params are the same as for TemplateFinder.search()
    :return: Returns a list of TemplateMatch objects
    """
    templates = _process_template_refs(ref)
    matches = []
    img = inp_img
    while True:
        any_found = False
        for template in templates:
            match = _single_template_match(template, img, roi, color_match, use_grayscale)
            if (ind_found := match.score >= threshold):
                matches.append(match)
                img = mask_by_roi(img, match.region, "inverse")
                any_found |= ind_found
        if not any_found:
            break
    return matches


# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, stop_detecting_window
    from utils.misc import wait
    import template_finder
    start_detecting_window()
    wait(0.1)

    print("\n== Hotkeys ==")
    print("F11: Start")
    print("F12: Exit")
    print("Down arrow: decrease template matching threshold")
    print("Up arrow: increase template matching threshold")
    print("Left arrow: decrease template index")
    print("Right arrow: increase template index")
    print("F9: toggle all vs. individual template(s)")
    print("F10: save visible template(s)")

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    keyboard.wait("f11")

    # enter the template names you are trying to detect here

    _template_list = ["SHENK_0","SHENK_1","SHENK_10","SHENK_11","SHENK_12","SHENK_13","SHENK_15","SHENK_16","SHENK_17","SHENK_18","SHENK_19","SHENK_2","SHENK_20","SHENK_3","SHENK_4","SHENK_6","SHENK_7","SHENK_8","SHENK_9","SHENK_DEATH_0","SHENK_DEATH_1","SHENK_DEATH_2","SHENK_DEATH_3","SHENK_DEATH_4","SHENK_V2_3","SHENK_V2_4","SHENK_V2_6","SHENK_V2_7","SHENK_V2_8"]

    _current_template_idx = -1
    _last_stored_idx = 0
    _current_threshold = 0.5
    _visible_templates = []

    def _save_visible_templates():
        if not os.path.exists("info_screenshots"):
            os.system("mkdir info_screenshots")
        for match in _visible_templates:
            cv2.imwrite(match['filename'], match['img'])
            Logger.info(f"{match['filename']} saved")

    def _toggle_templates():
        global _current_template_idx
        _current_template_idx = -1 if _current_template_idx != -1 else _last_stored_idx
        if _current_template_idx == -1:
            Logger.info(f"Searching for templates: {_template_list}")
        else:
            Logger.info(f"Searching for template: {_template_list[_current_template_idx]}")

    def _incr_template_idx(direction: int = 1):
        global _current_template_idx, _last_stored_idx
        if \
            (-1 < _current_template_idx < len(_template_list) - 1) or \
            (_current_template_idx == -1 and direction > 0) or \
            (_current_template_idx  == len(_template_list) - 1 and direction < 0):
            _current_template_idx += direction
            _last_stored_idx = _current_template_idx
        if _current_template_idx == -1:
            Logger.info(f"Searching for templates: {_template_list}")
        else:
            Logger.info(f"Searching for template: {_template_list[_current_template_idx]}")

    def _incr_threshold(direction: int = 1):
        global _current_threshold
        if (_current_threshold < 1 and direction > 0) or (_current_threshold > 0 and direction < 0):
            _current_threshold = round(_current_threshold + direction, 2)
        Logger.info(f"_current_threshold = {_current_threshold}")

    keyboard.add_hotkey('down', lambda: _incr_threshold(-0.05))
    keyboard.add_hotkey('up', lambda: _incr_threshold(0.05))
    keyboard.add_hotkey('left', lambda: _incr_template_idx(-1))
    keyboard.add_hotkey('right', lambda: _incr_template_idx(1))
    keyboard.add_hotkey('f9', lambda: _toggle_templates())
    keyboard.add_hotkey('f10', lambda: _save_visible_templates())

    while 1:
        _visible_templates = []
        img = grab()
        display_img = img.copy()
        if _current_template_idx < 0:
            templates = _template_list
        else:
            templates = [_template_list[_current_template_idx]]
        for key in templates:
            template_match = template_finder.search(key, img, threshold=_current_threshold)
            if template_match.valid:
                x, y = template_match.center
                cv2.putText(display_img, str(template_match.name), template_match.center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(display_img, template_match.center, 7, (255, 0, 0), thickness=5)
                cv2.rectangle(display_img, template_match.region[:2], (template_match.region[0] + template_match.region[2], template_match.region[1] + template_match.region[3]), (0, 0, 255), 1)
                print(f"Name: {template_match.name} Pos: {template_match.center}, Dist: {625-x, 360-y}, Score: {template_match.score}")
                match = {
                    'filename': f"./info_screenshots/{key.lower()}.png",
                    'img': cut_roi(img, template_match.region)
                }
                _visible_templates.append(match)
        cv2.imshow('test', display_img)
        key = cv2.waitKey(3000)
