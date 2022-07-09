import cv2
import numpy as np
import keyboard
import template_finder
from logger import Logger
from config import Config
from utils.misc import wait
from screen import convert_abs_to_screen, grab

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

def toggle_automap(active: bool = None) -> bool:
    """
    Helper function that will check if the Automap is active (and optionally activate or deactivate it)
    :param active: "True" - activated, "False" - deactivated, "None" - toggle without check. default "None"
    :returns a TemplateMatch object
    """
    if active is None:
        keyboard.send(Config().char["show_automap"])
    elif active:
        if template_finder.search(["MAP_CHECK"], inp_img=grab(force_new=True), roi=[1100,10,160,40], threshold=0.9).valid: #check if the Automap is already on
            Logger.debug("Automap Status: "+ '\033[92m' + "ALREADY ON" + '\033[0m')
        else:
            keyboard.send(Config().char["show_automap"])
            #we should put a keybinding for switching show_items OFF!
            wait(0.1,0.15)
    else:
        keyboard.send(Config().char["clear_screen"])
        wait(0.1,0.15)
    return True


def map_capture(active: bool = True) -> bool:
    """Gets 3 captures of the map:
        1. Before map displayed
        2. Map displayed (tab pressed)
        3. Map displayed a few frames later (tab still pressed)
    Tab is then depressed. The purpose for the third grab is to filter out any animations, later.
    :returns a the image grabbed "img" and the map "during_1" and without the map "during_2"
    """

    # Map OFF
    pre = np.array(grab())
    pre = cv2.cvtColor(pre, cv2.COLOR_BGRA2BGR)
    keyboard.send(Config().char["show_automap"])
    wait(.075)

    # Map ON
    during_1 = np.array(grab())
    during_1 = cv2.cvtColor(during_1, cv2.COLOR_BGRA2BGR)
    wait(.075)

    # Map ON, but we can tell if any carvers/flames are underneath fucking up the diff
    during_2 = np.array(grab())
    during_2 = cv2.cvtColor(during_2, cv2.COLOR_BGRA2BGR)
    keyboard.send(Config().char["show_automap"])

    return pre, during_1, during_2


