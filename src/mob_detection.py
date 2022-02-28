import cv2
import numpy as np
import time
from math import sqrt #for object detection
from screen import grab, convert_screen_to_abs, convert_abs_to_monitor
from logger import Logger


#Changes Brightness and Contrast - adapted from Nathan's Live-view
def bright_contrast(img, brightness=255, contrast=127):
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
        img = img
        if info_ss: cv2.imwrite(f"./info_screenshots/info_apply_filter_input_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
        if mask_hud: 
            _hud_mask = cv2.imread(f"./assets/hud_mask.png", cv2.IMREAD_GRAYSCALE)
            img = cv2.bitwise_and(img, img, mask=_hud_mask)
        if mask_char: img = cv2.rectangle(img, (600,250), (700,400), (0,0,0), -1) # black out character by drawing a black box above him (e.g. ignore set glow)
        if erode:
            kernel = np.ones((erode, erode), 'uint8')
            img = cv2.erode(img, kernel, None, iterations=1)
        if dilate:
            kernel = np.ones((dilate, dilate), 'uint8')
            img = cv2.dilate(img, kernel, iterations=1)
        if blur: img = cv2.blur(img, (blur, blur))
        if bright or contrast: img = bright_contrast(img, bright, contrast)
        if lh or ls or lv or uh or us or uv:
            lower = np.array([lh, ls, lv])
            upper = np.array([uh, us, uv])
            self.hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            cont_mask = cv2.inRange(self.hsv, lower, upper)
            img = cv2.bitwise_and(img, img, mask=cont_mask)        
        if thresh: img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]
        threshz = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if thresh: _, threshz = cv2.threshold(threshz, thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if invert: img = 255 - img
        filterimage = img
        if info_ss: cv2.imwrite(f"./info_screenshots/info_apply_filter_output_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
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
            cv2.rectangle(img, (x, y), (x + w, y + h), color=line_color, thickness=1)
            rect = [int(x), int(y), int(w), int(h)]
            pos_rectangles.append(rect)
            if marker:#draw crosshairs on center of rectangle.
                #line_color = (0, 255, 0)
                #line_type = cv2.LINE_4
                #marker_color = (255, 0, 255)
                #marker_type = cv2.MARKER_CROSS
                center_x = x + int(w/2)
                center_y = y + int(h/2)
                cv2.drawMarker(img, (center_x, center_y), color=marker_color, markerType=marker_type, markerSize=15, thickness=2)
                mark = [int(center_x), int(center_y)]
                pos_marker.append(mark)
    self.frame_markup = img.copy()
    img = img
    if info_ss: cv2.imwrite(f"./info_screenshots/info_add_markers" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
    return img, pos_rectangles, pos_marker

# adapted from BEN Open CV Bot Tutorial #9
def pythagorean_distance(pos_x, pos_y):
        my_pos = (1280/2, 720/2) #center of the screen
        return sqrt((pos_x - my_pos[0])**2 + (pos_y - my_pos[1])**2)

# adapted from BEN Open CV Bot Tutorial #9
def get_targets_ordered_by_distance(targets, ignore_radius:int=0):
    my_pos = (1280/2, 720/2) #center of the screen
    def pythagorean_distance(pos):
        return sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
    targets.sort(key=pythagorean_distance)
    targets = [t for t in targets if pythagorean_distance(t) > ignore_radius] #ignore targets that are too close
    return targets #a sorted arry of all targets, nearest to farest away

def mobcheck(self, info_ss:bool=False) -> bool:
    #wait(1) # let the merc paint some mobs
    img = grab()
    input = img #for drawing lines later
    if info_ss: cv2.imwrite(f"./info_screenshots/info_mob_" + time.strftime("%Y%m%d_%H%M%S") + ".png", img)
    filterimage, threshz = apply_filter(self, img, mask_char=True, mask_hud=True, info_ss=False, erode=0, dilate=2, blur=4, lh=35, ls=0, lv=43, uh=133, us=216, uv=255, bright=255, contrast=139, thresh=10, invert=0) # HSV Filter for BLUE and GREEN (Posison Nova & Holy Freeze)
    pos_marker = []
    pos_rectangle = []
    filterimage, pos_rectangle, pos_marker = add_markers(self, filterimage, threshz, info_ss=False, rect_min_size=100, rect_max_size=200, marker=True) # rather large rectangles
    if info_ss: cv2.imwrite(f"./info_screenshots/info_mob__filtered" + time.strftime("%Y%m%d_%H%M%S") + ".png", filterimage)
    order = get_targets_ordered_by_distance(pos_marker, 150)
    if not order:
        Logger.info('\033[93m' + "Mobcheck: no Mob detected" + '\033[0m')
        return False
    else:
        pos_m = convert_screen_to_abs(order[0]) #nearest marker
        pos_m = convert_abs_to_monitor(pos_m)
        Logger.debug('\033[92m' + "Mobcheck: Found Mob at " + str(pos_m) + " attacking now!" + '\033[0m')
        if info_ss:
            #draw an arrow on a screenshot where a mob was found 
            pt2 = (640,360)
            x1, y1 = order[0]
            pt1 = (int(x1),int(y1))
            input = np.ascontiguousarray(input)
            cv2.arrowedLine(input, pt2, pt1, line_type=cv2.LINE_4, thickness=2, tipLength=0.3, color=(255, 0, 255))
            cv2.imwrite(f"./info_screenshots/info_mob_add_line" + time.strftime("%Y%m%d_%H%M%S") + ".png", input)
        return True

# Testing: Have whatever you want to find on the screen
if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")
    import cv2
    import numpy as np
    import time
    from math import sqrt #for object detection
    from screen import grab, convert_screen_to_abs, convert_abs_to_monitor
    from logger import Logger