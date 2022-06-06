import cv2
import numpy as np
import time
from screen import convert_screen_to_monitor, grab, convert_screen_to_abs, convert_abs_to_monitor
from logger import Logger
from math import dist
from utils.misc import color_filter
import json
from dataclasses import dataclass

FILTER_RANGES=[
    {"erode": 1, "blur": 3, "lh": 38, "ls": 169, "lv": 50, "uh": 70, "us": 255, "uv": 255}, # poison
    {"erode": 1, "blur": 3, "lh": 110, "ls": 169, "lv": 50, "uh": 120, "us": 255, "uv": 255} # frozen
]

@dataclass
class TargetInfo:
    roi: tuple = None
    center: tuple = None
    center_monitor: tuple = None
    distance: int = 0

def _dist_to_center(pos):
    return dist(pos, (1280/2, 720/2))

def get_visible_targets(img: np.ndarray = None, radius_min: int = 150, radius_max: int = 1280) -> list[TargetInfo]:
    img = grab() if img is None else img
    targets = []
    for filter in FILTER_RANGES:
        filterimage, threshz = _process_image(img, mask_char=True, mask_hud=True, info_ss=False, **filter) # HSV Filter for BLUE and GREEN (Posison Nova & Holy Freeze)
        filterimage, rectangles, positions = _add_markers(filterimage, threshz, info_ss=False, rect_min_size=100, rect_max_size=200, marker=True) # rather large rectangles
        if positions:
            for cnt, position in enumerate(positions):
                distance = _dist_to_center(position)
                if radius_min <= _dist_to_center(position) <= radius_max:
                    targets.append(TargetInfo(
                        roi = rectangles[cnt],
                        center = position,
                        center_monitor = convert_screen_to_monitor(position),
                        distance = distance
                    ))
    if targets:
        targets = sorted(targets, key=lambda obj: obj.distance)
    return targets

def _bright_contrast(img: np.ndarray, brightness: int = 255, contrast: int = 127):
    """
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

def _process_image(img, mask_char:bool=False, mask_hud:bool=True, info_ss:bool=False, erode:int=None, dilate:int=None, blur:int=None, lh:int=None, ls:int=None, lv:int=None, uh:int=None, us:int=None, uv:int=None, bright:int=None, contrast:int=None, thresh:int=None, invert:int=None):
    """
    Helper function that will apply HSV filters
    :param img: The image to which filters should be applied
    :param mask_char: apply a black rectangle to mask your char (e.g. filter out Set-Item glow effect or auras)  [Default: False, Bool]
    :param hud_mask: removes the HUD from the returned image  [Default: True, Bool]
    :param info_ss: Save an image of the applied filters in folder INFO_SCREENSHOTS  [Default: False, Bool]
    :param erode: erode (thin lines) in the picture [Default: None, Integer, no filter: 0,  0 - 36]
    :param dilate: dilate (thicken lines) in the picture [Default: None, Integer, no filter: 0, 0 - 36]
    :param blur: blur the picture [Default: None, no filter: 0, Integer, 0 - 30]
    :param lh: cut-off Hue BELOW this value [Default: None, no filter: 0, Integer 0 - 180]
    :param ls: cut-off Saturation BELOW this value [Default: None, no filter: 0,  Integer 0 - 255]
    :param lv: cut-off Value BELOW this value [Default: None, no filter: 0, Integer 0 - 255]
    :param uh: cut-off Hue ABOVE this value [Default: None, no filter: 180, Integer 0 - 180]
    :param us: cut-off Saturation ABOVE this value [Default: None, no filter: 255, Integer 0 - 255]
    :param uv: cut-off Value ABOVE this value [Default: None, no filter: 255, Integer 0 - 255]
    :param bright: adjust Brightness of the picture [Default: None, no filter: 255, Integer 0 - 255]
    :param contrast: adjust Contrast of the picture [Default: None, no filter: 127, Integer 0 - 254]
    :param thresh: adjust Threshold of the picture [Default: None, no filter: 0, Integer 0 - 255]
    :param invert: Invert the picture [Default: None, no filter: 0, Integer 0 - 1]
    Returns variables filterimage and threshz
    """
    img = img
    if info_ss: cv2.imwrite(f"./info_screenshots/info_apply_filter_input_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
    if mask_hud:
        hud_mask = cv2.imread(f"./assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
        img = cv2.bitwise_and(img, img, mask=hud_mask)
    if mask_char: img = cv2.rectangle(img, (600,250), (700,400), (0,0,0), -1) # black out character by drawing a black box above him (e.g. ignore set glow)
    if erode:
        kernel = np.ones((erode, erode), 'uint8')
        img = cv2.erode(img, kernel, None, iterations=1)
    if dilate:
        kernel = np.ones((dilate, dilate), 'uint8')
        img = cv2.dilate(img, kernel, iterations=1)
    if blur: img = cv2.blur(img, (blur, blur))
    if bright or contrast: img = _bright_contrast(img, bright, contrast)
    if lh or ls or lv or uh or us or uv:
        _, img = color_filter(img, (np.array([lh, ls, lv]), np.array([uh, us, uv])))
    if thresh: img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]
    threshz = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if thresh: _, threshz = cv2.threshold(threshz, thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if invert: img = 255 - img
    filterimage = img
    if info_ss: cv2.imwrite(f"./info_screenshots/info_apply_filter_output_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
    return filterimage, threshz

# add rectangles and crosses - adapted from Nathan's Live-View
def _add_markers(img:str, threshz:str, info_ss:bool=False, rect_min_size:int=20, rect_max_size:int=50, line_color:str=(0, 255, 0), line_type:str=cv2.LINE_4, marker:bool=False, marker_color:str=(0, 255, 255), marker_type:str=cv2.MARKER_CROSS):
    """
    Helper function that will add rectangles and crosshairs to allow object detection
    :param img: The image to which filters should be applied
    :param threshz: The image that had the threshold adjusted (obtained from _process_image())
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
    #add rectangles
    n_labels, _, stats, _ = cv2.connectedComponentsWithStats(threshz)
    rectangles = []
    markers = []
    for i in range(1, n_labels):
        if stats[i, cv2.CC_STAT_AREA] >= rect_min_size <= rect_max_size:
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            cv2.rectangle(img, (x, y), (x + w, y + h), color=line_color, thickness=1)
            rect = (int(x), int(y), int(w), int(h))
            rectangles.append(rect)
            if marker:
                center_x = x + int(w/2)
                center_y = y + int(h/2)
                cv2.drawMarker(img, (center_x, center_y), color=marker_color, markerType=marker_type, markerSize=15, thickness=2)
                mark = (int(center_x), int(center_y))
                markers.append(mark)
    return img, rectangles, markers

class LiveViewer:
    def __init__(self):
        with open("./src/utils/live-view-last-settings.json") as f:
            self.settings = json.loads(f.read())
        self.hud_mask = cv2.imread(f"./assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
        self.hud_mask = cv2.threshold(self.hud_mask, 1, 255, cv2.THRESH_BINARY)[1]
        self.use_existing_image = False
        self.existing_image_path = "test/assets/mobs.png"
        self.setup()
        self.live_view()

    def setup(self):
        cv2.namedWindow("Settings", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Results", cv2.WINDOW_NORMAL)
        cv2.createTrackbar('erode', 'Settings', self.settings['erode'], 36, self.value_update)
        cv2.createTrackbar('dilate', 'Settings', self.settings['dilate'], 36, self.value_update)
        cv2.createTrackbar('blur', 'Settings', self.settings['blur'], 30, self.value_update)
        cv2.createTrackbar('lh', 'Settings', self.settings['lh'], 180, self.value_update)
        cv2.createTrackbar('ls', 'Settings', self.settings['ls'], 255, self.value_update)
        cv2.createTrackbar('lv', 'Settings', self.settings['lv'], 255, self.value_update)
        cv2.createTrackbar('uh', 'Settings', self.settings['uh'], 180, self.value_update)
        cv2.createTrackbar('us', 'Settings', self.settings['us'], 255, self.value_update)
        cv2.createTrackbar('uv', 'Settings', self.settings['uv'], 255, self.value_update)
        cv2.createTrackbar('bright', 'Settings', self.settings['bright'], 255, self.value_update)
        cv2.createTrackbar('contrast', 'Settings', self.settings['contrast'], 254, self.value_update)
        cv2.createTrackbar('thresh', 'Settings', self.settings['thresh'], 255, self.value_update)
        cv2.createTrackbar('invert', 'Settings', self.settings['invert'], 1, self.value_update)

    def value_update(self, ignore: bool = False):
        if not self.use_existing_image:
            self.image = grab()
        else:
            self.image = cv2.imread(self.existing_image_path)
        self.image = cv2.bitwise_and(self.image, self.image, mask=self.hud_mask)
        # black out character
        self.image = cv2.rectangle(self.image, (550,250), (700,400), (0,0,0), -1)
        try:
            self.settings['erode'] = cv2.getTrackbarPos('erode', 'Settings')
            self.settings['dilate'] = cv2.getTrackbarPos('dilate', 'Settings')
            self.settings['blur'] = cv2.getTrackbarPos('blur', 'Settings')
            self.settings['lh'] = cv2.getTrackbarPos('lh', 'Settings')
            self.settings['ls'] = cv2.getTrackbarPos('ls', 'Settings')
            self.settings['lv'] = cv2.getTrackbarPos('lv', 'Settings')
            self.settings['uh'] = cv2.getTrackbarPos('uh', 'Settings')
            self.settings['us'] = cv2.getTrackbarPos('us', 'Settings')
            self.settings['uv'] = cv2.getTrackbarPos('uv', 'Settings')
            self.settings['bright'] = cv2.getTrackbarPos('bright', 'Settings')
            self.settings['contrast'] = cv2.getTrackbarPos('contrast', 'Settings')
            self.settings['thresh'] = cv2.getTrackbarPos('thresh', 'Settings')
            self.settings['invert'] = cv2.getTrackbarPos('invert', 'Settings')
            with open("./src/utils/live-view-last-settings.json", 'w') as f:
                f.write(json.dumps(self.settings))
        except cv2.error:
            return
        self.image, threshz = _process_image(self.image, **self.settings)
        filterimage, _, _ = _add_markers(self.image, threshz, info_ss=False, rect_min_size=100, rect_max_size=200, marker=True)

        cv2.imshow("Results", filterimage)
        cv2.waitKey(1)

    def live_view(self):
        while True:
            self.value_update()

# Testing: Have whatever you want to detect on the screen
if __name__ == "__main__":
    import keyboard
    import os
    from logger import Logger
    from screen import start_detecting_window, stop_detecting_window
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    start_detecting_window()
    print("Move to d2r window and press f11")
    keyboard.wait("f11")
    l = LiveViewer()