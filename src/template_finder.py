import cv2
import threading
from copy import deepcopy
from screen import Screen
from typing import Union
from dataclasses import dataclass
import numpy as np
from logger import Logger
import time
import os
from config import Config
from utils.misc import load_template, list_files_in_folder, alpha_to_mask

template_finder_lock = threading.Lock()


@dataclass
class TemplateMatch:
    name: str = None
    score: float = -1.0
    position: tuple[float, float] = None
    rec: list[float] = None
    valid: bool = False

class TemplateFinder:
    """
    Loads images from assets/templates and assets/npc and provides search functions
    to find these assets within another image
    IMPORTANT: This method must be thread safe!
    """
    def __init__(
        self,
        screen: Screen,
        template_pathes: list[str] = ["assets\\templates", "assets\\npc", "assets\\item_properties", "assets\\chests"],
        save_last_res: bool = False
    ):
        self._screen = screen
        self._config = Config()
        self._save_last_res = save_last_res
        if self._save_last_res:
            # do not use this when running botty as it is used accross multiple threads! Just used in shopper as a workaround for now
            self.last_res = None
        # load templates with their filename as key in the dict
        pathes = []
        for path in template_pathes:
            pathes += list_files_in_folder(path)
        self._templates = {}
        for file_path in pathes:
            file_name: str = os.path.basename(file_path)
            if file_name.endswith('.png'):
                key = file_name[:-4].upper()
                template_img = load_template(file_path, 1.0, True)
                mask = alpha_to_mask(template_img)
                self._templates[key] = [
                    cv2.cvtColor(template_img, cv2.COLOR_BGRA2BGR),
                    cv2.cvtColor(template_img, cv2.COLOR_BGRA2GRAY),
                    1.0,
                    mask
                ]

    def get_template(self, key):
        return cv2.cvtColor(self._templates[key][0], cv2.COLOR_BGRA2BGR)

    def search(
        self,
        ref: Union[str, np.ndarray, list[str]],
        inp_img: np.ndarray,
        threshold: float = 0.68,
        roi: list[float] = None,
        normalize_monitor: bool = False,
        best_match: bool = False,
        use_grayscale: bool = False,
    ) -> TemplateMatch:
        """
        Search for a template in an image
        :param ref: Either key of a already loaded template, list of such keys, or a image which is used as template
        :param inp_img: Image in which the template will be searched
        :param threshold: Threshold which determines if a template is found or not
        :param roi: Region of Interest of the inp_img to restrict search area. Format [left, top, width, height]
        :param normalize_monitor: If True will return positions in monitor coordinates. Otherwise in coordinates of the input image.
        :param best_match: If list input, will search for list of templates by best match. Default behavior is first match.
        :param use_grayscale: Use grayscale template matching for speed up
        :return: Returns a TempalteMatch object with a valid flag
        """
        if roi is None:
            # if no roi is provided roi = full inp_img
            roi = [0, 0, inp_img.shape[1], inp_img.shape[0]]
        rx, ry, rw, rh = roi
        inp_img = inp_img[ry:ry + rh, rx:rx + rw]

        if type(ref) == str:
            templates = [self._templates[ref][0]]
            templates_gray = [self._templates[ref][1]]
            scales = [self._templates[ref][2]]
            masks = [self._templates[ref][3]]
            names = [ref]
            best_match = False
        elif type(ref) == list:
            templates = [self._templates[i][0] for i in ref]
            templates_gray = [self._templates[i][1] for i in ref]
            scales = [self._templates[i][2] for i in ref]
            masks = [self._templates[i][3] for i in ref]
            names = ref
        else:
            templates = [ref]
            templates_gray = [cv2.cvtColor(ref, cv2.COLOR_BGRA2GRAY)]
            scales = [1.0]
            masks = [None]
            best_match = False

        scores = [0] * len(templates)
        ref_points = [(0, 0)] * len(templates)
        recs = [[0, 0, 0, 0]] * len(templates)

        for count, template in enumerate(templates):
            template_match = TemplateMatch()
            scale = scales[count]
            mask = masks[count]

            img: np.ndarray = cv2.resize(inp_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
            rx *= scale
            ry *= scale
            rw *= scale
            rh *= scale

            if img.shape[0] > template.shape[0] and img.shape[1] > template.shape[1]:
                if use_grayscale:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    template = templates_gray[count]
                res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED, mask=mask)
                np.nan_to_num(res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
                _, max_val, _, max_pos = cv2.minMaxLoc(res)
                if self._save_last_res:
                    with template_finder_lock:
                        self.last_res = deepcopy(res)
                if max_val > threshold:
                    ref_point = (max_pos[0] + int(template.shape[1] * 0.5) + rx, max_pos[1] + int(template.shape[0] * 0.5) + ry)
                    ref_point = (int(ref_point[0] * (1.0 / scale)), int(ref_point[1] * (1.0 / scale)))
                    rec = [int(max_pos[0] // scale), int(max_pos[1] // scale), int(template.shape[1] // scale), int(template.shape[0] // scale)]

                    if normalize_monitor:
                        ref_point =  self._screen.convert_screen_to_monitor(ref_point)

                    if best_match:
                        scores[count] = max_val
                        ref_points[count] = ref_point
                        recs[count] = rec
                    else:
                        try: template_match.name = names[count]
                        except: pass
                        template_match.position = ref_point
                        template_match.score = max_val
                        template_match.rec = rec
                        template_match.valid = True
                        return template_match

        if len(scores) > 0 and max(scores) > 0:
            idx=scores.index(max(scores))
            try: template_match.name = names[idx]
            except: pass
            template_match.position = ref_points[idx]
            template_match.score = scores[idx]
            template_match.rec = recs[idx]
            template_match.valid = True
        else:
            template_match = TemplateMatch()

        return template_match

    def search_and_wait(
        self,
        ref: Union[str, list[str]],
        roi: list[float] = None,
        time_out: float = None,
        threshold: float = 0.68,
        best_match: bool = False,
        take_ss: bool = True,
        use_grayscale: bool = False
    ) -> TemplateMatch:
        """
        Helper function that will loop and keep searching for a template
        :param time_out: After this amount of time the search will stop and it will return [False, None]
        :param take_ss: Bool value to take screenshot on timeout or not (flag must still be set in params!)
        Other params are the same as for TemplateFinder.search()
        """
        if type(ref) is str:
            ref = [ref]
        Logger.debug(f"Waiting for Template {ref}")
        start = time.time()
        while 1:
            img = self._screen.grab()
            template_match = self.search(ref, img, roi=roi, threshold=threshold, best_match=best_match, use_grayscale=use_grayscale)
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 1.0
            if not is_loading_black_roi or "LOADING" in ref:
                if template_match.valid:
                    Logger.debug(f"Found Match: {template_match.name} ({template_match.score*100:.1f}% confidence)")
                    return template_match
                if time_out is not None and (time.time() - start) > time_out:
                    if self._config.general["info_screenshots"] and take_ss:
                        cv2.imwrite(f"./info_screenshots/info_wait_for_{ref}_time_out_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                    if take_ss:
                        Logger.debug(f"Could not find any of the above templates")
                    return template_match


# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    from screen import Screen
    screen = Screen()
    template_finder = TemplateFinder(screen)
    search_templates = ["DIABLO_PENT_0", "DIABLO_PENT_1", "DIABLO_PENT_2", "DIABLO_PENT_3"]

    while 1:
        # img = cv2.imread("")
        img = screen.grab()
        display_img = img.copy()
        start = time.time()
        for key in search_templates:
            template_match = template_finder.search(key, img, best_match=True, threshold=0.5, use_grayscale=True)
            if template_match.valid:
                cv2.putText(display_img, str(template_match.name), template_match.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(display_img, template_match.position, 7, (255, 0, 0), thickness=5)
                x, y = template_match.position
                print(f"Name: {template_match.name} Pos: {template_match.position}, Dist: {625-x, 360-y}, Score: {template_match.score}")

        # print(time.time() - start)
        # display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('test', display_img)
        key = cv2.waitKey(1)
