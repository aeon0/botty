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
from utils.misc import load_template, list_files_in_folder, alpha_to_mask, roi_center
from math import sqrt #for object detection

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

        templates_gray = None
        if type(ref) == str:
            templates = [self._templates[ref][0]]
            if use_grayscale:
                templates_gray = [self._templates[ref][1]]
            scales = [self._templates[ref][2]]
            masks = [self._templates[ref][3]]
            names = [ref]
            best_match = False
        elif type(ref) == list:
            if type(ref[0]) == str:
                templates = [self._templates[i][0] for i in ref]
                if use_grayscale:
                    templates_gray = [self._templates[i][1] for i in ref]
                scales = [self._templates[i][2] for i in ref]
                masks = [self._templates[i][3] for i in ref]
                names = ref
            else:
                templates = ref
                templates_gray = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in ref]
                scales =  [1.0] * len(ref)
                masks = [None] * len(ref)
        else:
            templates = [ref]
            if use_grayscale:
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
                    template = templates_gray[count]
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
                        ref_point =  convert_screen_to_monitor(ref_point)
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
            idx=scores.index(max(scores))
            try: template_match.name = names[idx]
            except: pass
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
        time_out: float = None,
        threshold: float = 0.68,
        normalize_monitor: bool = False,
        best_match: bool = False,
        take_ss: bool = True,
        use_grayscale: bool = False,
        suppress_debug: bool = False,
        filterimage:str = None, 
    ) -> TemplateMatch:
        """
        Helper function that will loop and keep searching for a template
        :param time_out: After this amount of time the search will stop and it will return [False, None]
        :param take_ss: Bool value to take screenshot on timeout or not (flag must still be set in params!)
        :param filterimage: Search using a filtered image. By default None, in this case a screenshot is taken on which no filter was applied
        Other params are the same as for TemplateFinder.search()
        """
        if type(ref) is str:
            ref = [ref]
        if not suppress_debug:
            Logger.debug(f"Waiting for templates: {ref}")
        start = time.time()
        while 1:
            if filterimage is not None:
                img = filterimage
            else:
                img = grab()
            template_match = self.search(ref, img, roi=roi, threshold=threshold, best_match=best_match, use_grayscale=use_grayscale, normalize_monitor=normalize_monitor)
            is_loading_black_roi = np.average(img[:, 0:Config().ui_roi["loading_left_black"][2]]) < 1.0
            if not is_loading_black_roi or "LOADING" in ref:
                if template_match.valid:
                    Logger.debug(f"Found Match: {template_match.name} ({template_match.score*100:.1f}% confidence)")
                    return template_match
                if time_out is not None and (time.time() - start) > time_out:
                    if Config().general["info_screenshots"] and take_ss:
                        cv2.imwrite(f"./info_screenshots/info_wait_for_{ref}_time_out_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
                    if take_ss:
                        Logger.debug(f"Could not find any of the above templates")
                    return template_match

    #Changes Brightness and Contrast - adapted from Nathan's Live-view
    def bright_contrast(self, img, brightness=255, contrast=127):
        """
        Helper function to change brightness and contrast
        :param img: The image to which filters should be applied
        :param brightness: adjust Brightness of the picture [Default: 255, Integer 0 - 255]
        :param contrast: adjust Contrast of the picture [Default: 127, Integer 0 - 254]
        Returns variables cal
        """        
        brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
        
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max = 255
            else:
                shadow = 0
                max = 255 + brightness
            al_pha = (max - shadow) / 255
            ga_mma = shadow
            cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma)
        else:
            cal = img

        if contrast != 0:
            alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            gamma = 127 * (1 - alpha)
            cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)
        return cal

    #Applies filters to an image - adapted from Nathan's Live-view
    def apply_filter(self, img, mask_char:bool=False, mask_hud:bool=True, info_ss:bool=False, erode:int=None, dilate:int=None, blur:int=None, lh:int=None, ls:int=None, lv:int=None, uh:int=None, us:int=None, uv:int=None, bright:int=None, contrast:int=None, thresh:int=None, invert:int=None):
            """
            Helper function that will apply HSV filters
            :param img: The image to which filters should be applied
            :param mask_char: apply a black rectangle to mask your char (e.g. filter out Set-Item glow effect or auras)  [Default: False, Bool]
            :param hud_mask: removes the HUD from the returned image  [Default: True, Bool]
            :param info_ss: Save an image of the applied filters in folder INFO_SCREENSHOTS  [Default: False, Bool]
            :param erode: erode (thin lines) in the picture [Default: None, Integer, no filter: 0,  0 - 36]
            :param dilate: dilate (thicken lines) in the picture [Default: None, Integer, no filter: 0, 0 - 36]
            :param blur: blur the picture [Default: None, no filter: 0, Integer, 0 - 30] 
            :param lh: cut-off Hue BELOW this value [Default: None, no filter: 0, Integer 0 - 255]
            :param ls: cut-off Saturation BELOW this value [Default: None, no filter: 0,  Integer 0 - 255]
            :param lv: cut-off Value BELOW this value [Default: None, no filter: 0, Integer 0 - 255]
            :param uh: cut-off Hue ABOVE this value [Default: None, no filter: 255, Integer 0 - 255]
            :param us: cut-off Saturation ABOVE this value [Default: None, no filter: 255, Integer 0 - 255]
            :param uv: cut-off Value ABOVE this value [Default: None, no filter: 255, Integer 0 - 255]
            :param bright: adjust Brightness of the picture [Default: None, no filter: 255, Integer 0 - 255]
            :param contrast: adjust Contrast of the picture [Default: None, no filter: 127, Integer 0 - 254]
            :param thresh: adjust Threshold of the picture [Default: None, no filter: 0, Integer 0 - 255]
            :param invert: Invert the picture [Default: None, no filter: 0, Integer 0 - 1]
            Returns variables filterimage and threshz
            """
            self.image = img
            if info_ss: cv2.imwrite(f"./info_screenshots/info_apply_filter_input_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.image)
            if mask_hud: 
                _hud_mask = cv2.imread(f"./assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
                self.image = cv2.bitwise_and(self.image, self.image, mask=_hud_mask)
            if mask_char: self.image = cv2.rectangle(self.image, (600,250), (700,400), (0,0,0), -1) # black out character by drawing a black box above him (e.g. ignore set glow)
            if erode:
                kernel = np.ones((erode, erode), 'uint8')
                self.image = cv2.erode(self.image, kernel, None, iterations=1)
            if dilate:
                kernel = np.ones((dilate, dilate), 'uint8')
                self.image = cv2.dilate(self.image, kernel, iterations=1)
            if blur: self.image = cv2.blur(self.image, (blur, blur))
            if bright or contrast: self.image = self.bright_contrast(self.image, bright, contrast)
            if lh or ls or lv or uh or us or uv:
                lower = np.array([lh, ls, lv])
                upper = np.array([uh, us, uv])
                self.hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
                cont_mask = cv2.inRange(self.hsv, lower, upper)
                self.image = cv2.bitwise_and(self.image, self.image, mask=cont_mask)        
            if thresh: self.image = cv2.threshold(self.image, thresh, 255, cv2.THRESH_BINARY)[1]
            threshz = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            if thresh: _, threshz = cv2.threshold(threshz, thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if invert: self.image = 255 - self.image
            filterimage = self.image
            if info_ss: cv2.imwrite(f"./info_screenshots/info_apply_filter_output_" + time.strftime("%Y%m%d_%H%M%S") + ".png", self.image)
            return filterimage, threshz
   
    # add rectangles and crosses - adapted from Nathan's Live-View
    def add_markers(self, img:str, threshz:str, info_ss:bool=False, rect_min_size:int=20, rect_max_size:int=50, line_color:str=(0, 255, 0), line_type:str=cv2.LINE_4, marker:bool=False, marker_color:str=(0, 255, 255), marker_type:str=cv2.MARKER_CROSS):
        """
        Helper function that will add rectangles and crosshairs to allow object detection
        :param img: The image to which filters should be applied
        :param threshz: The image that had the threshold adjusted (obtained from apply_filter())
        :param info_ss: Take a screenshot for each step [Default: False, Bool]
        :param rect_min_size: Minimum size for the rectangle to be drawn [Default: 20, Integer]
        :param rect_max_size: Minimum size for the rectangle to be drawn [Default: 50, Integer]
        :param line_color: Color of the rectangle line [Default: (0, 255, 0)]
        :param line_type: Type of Line of the rectangle [Default: cv2.LINE_4]
        :param marker: Add Marker to center of rectangles [Default: False, Bool]
        :param marker_color: Color for the Marker [Default: (0, 255, 255)]
        :param marker_type: Type for the Marker [Default: cv2.MARKER_CROSS]
        Returns variables img (containing markers) & rectangles (x,y,w,h for each) & marker (x,y for eah)
        """
        self.image = img
        #add rectangles
        n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(threshz)
        pos_rectangles = []
        pos_marker = []
        for i in range(1, n_labels):
            if stats[i, cv2.CC_STAT_AREA] >= rect_min_size <= rect_max_size:
                x = stats[i, cv2.CC_STAT_LEFT]
                y = stats[i, cv2.CC_STAT_TOP]
                w = stats[i, cv2.CC_STAT_WIDTH]
                h = stats[i, cv2.CC_STAT_HEIGHT]
                cv2.rectangle(self.image, (x, y), (x + w, y + h), color=line_color, thickness=1)
                rect = [int(x), int(y), int(w), int(h)]
                pos_rectangles.append(rect)
                if marker:#draw crosshairs on center of rectangle.
                    #line_color = (0, 255, 0)
                    #line_type = cv2.LINE_4
                    #marker_color = (255, 0, 255)
                    #marker_type = cv2.MARKER_CROSS
                    center_x = x + int(w/2)
                    center_y = y + int(h/2)
                    cv2.drawMarker(self.image, (center_x, center_y), color=marker_color, markerType=marker_type, markerSize=15, thickness=2)
                    mark = [int(center_x), int(center_y)]
                    pos_marker.append(mark)
        self.frame_markup = self.image.copy()
        img = self.image
        if info_ss: cv2.imwrite(f"./info_screenshots/info_add_markers" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        return img, pos_rectangles, pos_marker

    # adapted from BEN Open CV Bot Tutorial #9
    def pythagorean_distance(pos_x, pos_y):
            my_pos = (1280/2, 720/2) #center of the screen
            return sqrt((pos_x - my_pos[0])**2 + (pos_y - my_pos[1])**2)

    # adapted from BEN Open CV Bot Tutorial #9
    def get_targets_ordered_by_distance(self, targets, ignore_radius:int=0):
        my_pos = (1280/2, 720/2) #center of the screen
        def pythagorean_distance(pos):
            return sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)
        targets = [t for t in targets if pythagorean_distance(t) > ignore_radius] #ignore targets that are too close

        return targets #a sorted arry of all targets, nearest to farest away

# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window
    start_detecting_window()
    from template_finder import TemplateFinder
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")

    search_templates = ["CORPSE", "CORPSE_BARB", "CORPSE_DRU", "CORPSE_NEC", "CORPSE_PAL", "CORPSE_SIN", "CORPSE_SORC", "CORPSE_ZON"]

    while 1:
        # img = cv2.imread("")
        img = grab()
        display_img = img.copy()
        start = time.time()
        for key in search_templates:
            template_match = TemplateFinder().search(key, img, best_match=True, threshold=0.5, use_grayscale=True)
            if template_match.valid:
                x, y = template_match.center
                cv2.putText(display_img, str(template_match.name), template_match.center, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(display_img, template_match.center, 7, (255, 0, 0), thickness=5)
                print(f"Name: {template_match.name} Pos: {template_match.center}, Dist: {625-x, 360-y}, Score: {template_match.score}")

        # print(time.time() - start)
        # display_img = cv2.resize(display_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
        cv2.imshow('test', display_img)
        key = cv2.waitKey(1)
