import cv2
from screen import Screen
from typing import Tuple, Union, List
from dataclasses import dataclass
import numpy as np
from logger import Logger
import time
import os
from config import Config
from utils.misc import load_template, list_files_in_folder


@dataclass
class TemplateMatch:
    name: str = None
    score: float = -1.0
    position: Tuple[float, float] = None
    valid: bool = False

class TemplateFinder:
    """
    Loads images from assets/templates and assets/npc and provides search functions
    to find these assets within another image
    """
    def __init__(self, screen: Screen):
        self._screen = screen
        self._config = Config()
        self.last_res = None
        # load templates with their filename as key in the dict
        template_path = "assets\\templates"
        npc_path = "assets\\npc"
        pathes = list_files_in_folder(npc_path) + list_files_in_folder(template_path)
        self._templates = {}
        for file_path in pathes:
            file_name: str = os.path.basename(file_path)
            if file_name.endswith('.png'):
                key = file_name[:-4].upper()
                self._templates[key] = [load_template(file_path, 1.0, True), 1.0]

    def get_template(self, key):
        return cv2.cvtColor(self._templates[key][0], cv2.COLOR_BGRA2BGR)

    def search(
        self,
        ref: Union[str, np.ndarray, List[str]],
        inp_img: np.ndarray,
        threshold: float = None,
        roi: List[float] = None,
        normalize_monitor: bool = False,
        best_match: bool = False
    ) -> TemplateMatch:
        """
        Search for a template in an image
        :param ref: Either key of a already loaded template, list of such keys, or a image which is used as template
        :param inp_img: Image in which the template will be searched
        :param threshold: Threshold which determines if a template is found or not
        :param roi: Region of Interest of the inp_img to restrict search area. Format [left, top, width, height]
        :param normalize_monitor: If True will return positions in monitor coordinates. Otherwise in coordinates of the input image.
        :param best_match: If list input, will search for list of templates by best match. Default behavior is first match.
        :return: Returns a TempalteMatch object with a valid flag
        """
        threshold = self._config.advanced_options["template_threshold"] if threshold is None else threshold
        if roi is None:
            # if no roi is provided roi = full inp_img
            roi = [0, 0, inp_img.shape[1], inp_img.shape[0]]
        rx, ry, rw, rh = roi
        inp_img = inp_img[ry:ry + rh, rx:rx + rw]

        if type(ref) == str:
            templates = [self._templates[ref][0]]
            scales = [self._templates[ref][1]]
            names = [ref]
            best_match = False
        elif type(ref) == list:
            templates = [self._templates[i][0] for i in ref]
            scales = [self._templates[i][1] for i in ref]
            names = ref
        else:
            templates = [ref]
            scales = [1.0]
            best_match = False

        scores = [0] * len(ref)
        ref_points = [(0, 0)] * len(ref)
        for count, template in enumerate(templates):
            template_match = TemplateMatch()
            scale = scales[count]

            # create a mask from template where alpha == 0
            # TODO: This could be precalculated in the __init__() for each template
            mask = None
            if template.shape[2] == 4:
                if np.min(template[:, :, 3]) == 0:
                    _, mask = cv2.threshold(template[:,:,3], 1, 255, cv2.THRESH_BINARY)
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

            img: np.ndarray = cv2.resize(inp_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
            rx *= scale
            ry *= scale
            rw *= scale
            rh *= scale

            if img.shape[0] > template.shape[0] and img.shape[1] > template.shape[1]:
                self.last_res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED, mask=mask)
                np.nan_to_num(self.last_res, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
                _, max_val, _, max_pos = cv2.minMaxLoc(self.last_res)
                if max_val > threshold:
                    ref_point = (max_pos[0] + int(template.shape[1] * 0.5) + rx, max_pos[1] + int(template.shape[0] * 0.5) + ry)
                    ref_point = (int(ref_point[0] * (1.0 / scale)), int(ref_point[1] * (1.0 / scale)))

                    if normalize_monitor:
                        ref_point =  self._screen.convert_screen_to_monitor(ref_point)

                    if best_match:
                        scores[count]=max_val
                        ref_points[count]=ref_point
                    else:
                        try: template_match.name = names[count]
                        except: pass
                        template_match.position = ref_point
                        template_match.score = max_val
                        template_match.valid = True
                        return template_match

        if max(scores) > 0:
            idx=scores.index(max(scores))
            try: template_match.name = names[idx]
            except: pass
            template_match.position = ref_points[idx]
            template_match.score = scores[idx]
            template_match.valid = True

        return template_match

    def search_and_wait(
        self,
        ref: Union[str, List[str]],
        roi: List[float] = None,
        time_out: float = None,
        threshold: float = None,
        best_match: bool = False,
        take_ss: bool = True
    ) -> TemplateMatch:
        """
        Helper function that will loop and keep searching for a template
        :param time_out: After this amount of time the search will stop and it will return [False, None]
        :param take_ss: Bool value to take screenshot on timeout or not (flag must still be set in params!)
        Other params are the same as for TemplateFinder.search()
        """
        if type(ref) is str:
            ref = [ref]
        threshold = self._config.advanced_options["template_threshold"] if threshold is None else threshold
        Logger.debug(f"Waiting for Template {ref}")
        start = time.time()
        while 1:
            img = self._screen.grab()
            template_match = self.search(ref, img, roi=roi, threshold=threshold, best_match=best_match)
            is_loading_black_roi = np.average(img[:, 0:self._config.ui_roi["loading_left_black"][2]]) < 1.0
            if not is_loading_black_roi or "LOADING" in ref:
                if template_match.valid:
                    return template_match
                if time_out is not None and (time.time() - start) > time_out:
                    if self._config.general["info_screenshots"] and take_ss:
                        cv2.imwrite(f"./info_screenshots/info_wait_for_{ref}_time_out_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                    return template_match


# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    from screen import Screen
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    search_templates = ["QUAL_45_2", "QUAL_45_3", "QUAL_45", "QUAL_BACK", "QUAL_FRONT", "QUAL_SIDE"]
    while 1:
        # img = cv2.imread("")
        img = screen.grab()
        display_img = img.copy()
        start = time.time()
        for key in search_templates:
            template_match = template_finder.search(key, img, best_match=True, threshold=0.35)
            if template_match.valid:
                cv2.putText(display_img, str(template_match.name), template_match.position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.circle(display_img, template_match.position, 7, (255, 0, 0), thickness=5)
                print(f"Name: {template_match.name} Pos: {template_match.position}, Score: {template_match.score}")
        # print(time.time() - start)
        display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('test', display_img)
        key = cv2.waitKey(1)
