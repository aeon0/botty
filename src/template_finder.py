"""Helper classes to find templates in images."""

import os
import threading
import time

import cv2
import numpy as np

from copy import deepcopy
from dataclasses import dataclass
from typing import Union

from screen import convert_screen_to_monitor, grab
from logger import Logger
from config import Config
from utils.misc import cut_roi, load_template, list_files_in_folder, alpha_to_mask, roi_center, color_filter

template_finder_lock = threading.Lock()


@dataclass
class TemplateMatch:
    name: str = None
    score: float = -1.0
    center: tuple[float, float] = None
    region: list[float] = None
    valid: bool = False


class TemplateFinder:
    """
    Loads images from assets/templates and assets/npc and provides search functions
    to find these assets within another image
    IMPORTANT: This method must be thread safe!
    """
    TEMPLATE_PATHS = [
        "assets\\templates",
        "assets\\npc",
        "assets\\shop",
        "assets\\item_properties",
        "assets\\chests",
        "assets\\gamble",
    ]
    _instance = None

    def __new__(cls, save_last_res=False):
        if cls._instance is None:
            cls._instance = super(TemplateFinder, cls).__new__(cls)
            cls._instance._save_last_res = save_last_res
            if cls._instance._save_last_res:
                # do not use this when running botty as it is used accross multiple threads! Just used in shopper as a workaround for now
                cls._instance.last_res = None
            # load templates with their filename as key in the dict
            pathes = []
            for path in TemplateFinder.TEMPLATE_PATHS:
                pathes += list_files_in_folder(path)
            cls._instance._templates = {}
            for file_path in pathes:
                file_name: str = os.path.basename(file_path)
                if file_name.lower().endswith('.png'):
                    key = file_name[:-4].upper()
                    template_img = load_template(file_path, 1.0, True)
                    mask = alpha_to_mask(template_img)
                    cls._instance._templates[key] = [
                        cv2.cvtColor(template_img, cv2.COLOR_BGRA2BGR),
                        cv2.cvtColor(template_img, cv2.COLOR_BGRA2GRAY),
                        1.0,
                        mask
                    ]
        return cls._instance

    @staticmethod
    def _make_template(template, match, scale, roi, normalize_monitor) -> TemplateMatch:
        """Helper function to make a TemplateMatch object from ."""
        rx, ry, rw, rh = roi
        template_match = TemplateMatch()
        rec = [
            int((match[1] + rx) // scale),
            int((match[0] + ry) // scale),
            int(template.shape[1] // scale),
            int(template.shape[0] // scale)
        ]
        ref_point = roi_center(rec)

        if normalize_monitor:
            rec[0], rec[1] = convert_screen_to_monitor((rec[0], rec[1]))
        else:
            template_match.center = ref_point
            template_match.region = rec
            template_match.valid = True
        return template_match

    def get_template(self, key):
        return cv2.cvtColor(self._templates[key][0], cv2.COLOR_BGRA2BGR)

    def search_v2(
            self,
            image: np.ndarray,
            template_name: str = None,
            template_image: np.ndarray = None,
            threshold: float = 0.88,
            roi: list[float] = None,
            normalize_monitor: bool = False,
            use_grayscale: bool = False,
            color_match: list = False,
    ) -> list[TemplateMatch]:
        """Look for matches for a template inside an image.

        :param image: The image to find the template in.
        :param template_name: The name of the template to load to look for in the image.
        :param template_image: An already loaded template to look for in the image.
        :param threshold: The confidence threshold to consider a match valid.
        :param roi: Optional region of the image to look for templates in.
        :param normalize_monitor: Return monitor coordinates instead of input image coordinates.
        :param use_grayscale: Whether the match should be in grayscale.
        :param color_match: Pass a color to be used as a filter for the template and image.

        :returns results: All templates found in the specified region.
        """
        results = []
        if template_name:
            scale = self._templates[template_name][2]
            mask = self._templates[template_name][3]
            if color_match:
                templates = [color_filter(self._templates[template_name][0], color_match)[1]]
                image = color_filter(image, color_match)[1]
            else:
                templates = [self._templates[template_name][use_grayscale]]
        elif template_image is not None:
            if not color_match:
                templates = [template_image]
            else:
                templates = [color_filter(template_image, color_match)[1]]
            scale = 1.0
            mask = None
        else:
            raise ValueError('We need either a template_name or template_image to search for.')
        if use_grayscale:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            templates = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in templates]
        # Default ROI to full image if not specified.
        roi = roi if roi is not None else [0, 0, image.shape[1], image.shape[0]]
        if scale != 1:
            image: np.ndarray = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
            roi = [val * scale for val in roi]
        # Crop image to region of interest.
        rx, ry, rw, rh = roi
        image = image[ry:ry + rh, rx:rx + rw]

        for idx, template in enumerate(templates):
            if image.shape[0] > template.shape[0] and image.shape[1] > template.shape[1]:
                res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED, mask=mask)
                res = np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
                matches = np.where(res >= threshold)
                matches = [pos for pos in zip(*matches)]
                for coords in matches:
                    # TODO: The TemplateMatch class should be able to construct itself with this information.
                    template_match = self._make_template(template, coords, scale, roi, normalize_monitor)
                    template_match.name = template_name
                    template_match.score = res[coords[0]][coords[1]]
                    results.append(template_match)
        return results

    def search(
        self,
        ref: Union[str, np.ndarray, list[str]],
        inp_img: np.ndarray,
        threshold: float = 0.68,
        roi: list[float] = None,
        normalize_monitor: bool = False,
        best_match: bool = False,
        use_grayscale: bool = False,
        color_match: list = False,
    ) -> TemplateMatch:
        """
        Search for a template in an image
        :param ref: Either key of an already loaded template, list of such keys, or an image which is used as template.
        :param inp_img: Image in which the template will be searched
        :param threshold: Threshold which determines if a template is found or not
        :param roi: Region of Interest of the inp_img to restrict search area. Format [left, top, width, height]
        :param normalize_monitor: If True will return positions in monitor coordinates. Otherwise in coordinates of the input image.
        :param best_match: If list input, will search for list of templates by best match. Default behavior is first match.
        :param use_grayscale: Use grayscale template matching for speed up
        :param color_match: Pass a color to be used by misc.color_filter to filter both image of interest and template image (format Config().colors["color"])
        :return: Returns a TemplateMatch object with a valid flag
        """
        if roi is None:
            # if no roi is provided roi = full inp_img
            roi = [0, 0, inp_img.shape[1], inp_img.shape[0]]
        rx, ry, rw, rh = roi
        inp_img = inp_img[ry:ry + rh, rx:rx + rw]

        if type(ref) == str:
            if not color_match:
                templates = [self._templates[ref][use_grayscale]]
            else:
                templates = [color_filter(self._templates[ref][0], color_match)[1]]
                if use_grayscale:
                    templates = [cv2.cvtColor(templates[0], cv2.COLOR_BGR2GRAY)]
            scales = [self._templates[ref][2]]
            masks = [self._templates[ref][3]]
            names = [ref]
            best_match = False
        elif type(ref) == list:
            if type(ref[0]) == str:
                if not color_match:
                    templates = [self._templates[i][use_grayscale] for i in ref]
                else:
                    templates = [color_filter(self._templates[i][0], color_match)[1] for i in ref]
                    if use_grayscale:
                        templates = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in templates]
                scales = [self._templates[i][2] for i in ref]
                masks = [self._templates[i][3] for i in ref]
                names = ref
            else:
                if not color_match:
                    templates = ref
                else:
                    templates = [color_filter(i, color_match)[1] for i in ref]
                if use_grayscale:
                    templates = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in templates]
                scales =  [1.0] * len(ref)
                masks = [None] * len(ref)
        else:
            if not color_match:
                templates = [ref]
            else:
                templates = [color_filter(ref, color_match)[1]]
            if use_grayscale:
                templates = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in templates]
            scales = [1.0]
            masks = [None]
            best_match = False

        scores = [0] * len(templates)
        ref_points = [(0, 0)] * len(templates)
        recs = [[0, 0, 0, 0]] * len(templates)

        if color_match:
            inp_img = color_filter(inp_img, color_match)[1]

        for count, template in enumerate(templates):
            template_match = TemplateMatch()
            scale = scales[count]
            mask = masks[count]

            if scale != 1:
                img: np.ndarray = cv2.resize(inp_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
                rx *= scale
                ry *= scale
                rw *= scale
                rh *= scale
            else:
                img: np.ndarray = inp_img

            if img.shape[0] > template.shape[0] and img.shape[1] > template.shape[1]:
                if use_grayscale:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED, mask=mask)
                np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
                _, max_val, _, max_pos = cv2.minMaxLoc(res)
                if self._save_last_res:
                    with template_finder_lock:
                        self.last_res = deepcopy(res)
                if max_val > threshold:
                    rec = [int((max_pos[0] + rx) // scale), int((max_pos[1] +ry) // scale), int(template.shape[1] // scale), int(template.shape[0] // scale)]
                    ref_point = roi_center(rec)

                    if normalize_monitor:
                        ref_point = convert_screen_to_monitor(ref_point)
                        rec[0], rec[1] = convert_screen_to_monitor((rec[0], rec[1]))
                    if best_match:
                        scores[count] = max_val
                        ref_points[count] = ref_point
                        recs[count] = rec
                    else:
                        try: template_match.name = names[count]
                        except: pass
                        template_match.center = ref_point
                        template_match.score = max_val
                        template_match.region = rec
                        template_match.valid = True
                        return template_match

        if len(scores) > 0 and max(scores) > 0:
            idx = scores.index(max(scores))
            try:
                template_match.name = names[idx]
            except:
                pass
            template_match.center = ref_points[idx]
            template_match.score = scores[idx]
            template_match.region = recs[idx]
            template_match.valid = True
        else:
            template_match = TemplateMatch()

        return template_match

    def search_and_wait(
        self,
        ref: Union[str, list[str]],
        roi: list[float] = None,
        timeout: float = None,
        threshold: float = 0.68,
        normalize_monitor: bool = False,
        best_match: bool = False,
        take_ss: bool = True,
        use_grayscale: bool = False,
        suppress_debug: bool = False,
        color_match: list = False,
    ) -> TemplateMatch:
        """
        Helper function that will loop and keep searching for a template
        :param timeout: After this amount of time the search will stop and it will return [False, None]
        :param take_ss: Bool value to take screenshot on timeout or not (flag must still be set in params!)
        Other params are the same as for TemplateFinder.search()
        """
        if type(ref) is str:
            ref = [ref]
        if not suppress_debug:
            Logger.debug(f"Waiting for templates: {ref}")
        start = time.time()
        while 1:
            img = grab()
            template_match = self.search(ref, img, roi=roi, threshold=threshold, best_match=best_match, use_grayscale=use_grayscale, normalize_monitor=normalize_monitor, color_match=color_match)
            is_loading_black_roi = np.average(img[:, 0:Config().ui_roi["loading_left_black"][2]]) < 1.0
            if not is_loading_black_roi or "LOADING" in ref:
                if template_match.valid:
                    Logger.debug(f"Found Match: {template_match.name} ({template_match.score*100:.1f}% confidence)")
                    return template_match
                if timeout is not None and (time.time() - start) > timeout:
                    if Config().general["info_screenshots"] and take_ss:
                        cv2.imwrite(f"./info_screenshots/info_wait_for_{ref}_timeout_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                    if take_ss:
                        Logger.debug(f"Could not find any of the above templates")
                    return template_match


# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, stop_detecting_window
    from utils.misc import wait
    from template_finder import TemplateFinder
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

    def _toggle_all_templates():
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
    keyboard.add_hotkey('f9', lambda: _toggle_all_templates())
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
            template_match = TemplateFinder().search(key, img, threshold=_current_threshold)
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
