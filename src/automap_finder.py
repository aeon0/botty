import cv2
import numpy as np
import keyboard
import template_finder
from logger import Logger
from config import Config
from utils.misc import wait


def find_cross_on_map(img: np.array, name: str, roi, YCbCr = False) -> tuple[float, float]:
    center_area = img[roi[1]:roi[1]+roi[3],roi[0]:roi[0]+roi[2]]
    color_range = Config().colors[name+"_cross"]
    if YCbCr:
        converted = cv2.cvtColor(center_area, cv2.COLOR_BGR2YCrCb)
    else:
        converted = cv2.cvtColor(center_area, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(converted, color_range[0], color_range[1])
    if cv2.countNonZero(mask) < 10:
        return None
    dist = cv2.distanceTransform(~mask, cv2.DIST_L1, cv2.DIST_MASK_3)
    k = 5
    bw = np.uint8(dist < k)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    bw2 = cv2.morphologyEx(bw, cv2.MORPH_ERODE, kernel)
    contours, _ = cv2.findContours(bw2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    largest_contour = -1
    for i,c in enumerate(contours):
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            largest_contour = i
    m = cv2.moments(contours[largest_contour])
    center = (m['m10']/m['m00']+roi[0]-0.5, m['m01']/m['m00']+roi[1]-5)
    print(center)
    return center

def toggle_automap(active: bool = True) -> bool:
    """
    Helper function that will check if the Automap is active (and optionally activate or deactivate it)
    :param active: set to "True" if Automap should be activated, set "False" if Automap should be deactivated, default True
    :returns a TemplateMatch object
    """
    if active:
        if template_finder.search_and_wait(["MAP_CHECK1", "MAP_CHECK"], roi=[1100,10,160,40], best_match=True, threshold=0.5, timeout=0.1).valid: #check if the Automap is already on
            Logger.info("Automap Status: ON")
        else:
            keyboard.send(Config().char["show_automap"])
            Logger.info("Automap Status: OFF -> ON")
            wait(0.1,0.15)
    else:
        keyboard.send(Config().char["clear_screen"])
        Logger.info("Automap Status: OFF")
        wait(0.1,0.15)
    return True