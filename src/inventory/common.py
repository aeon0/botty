from config import Config
import cv2
import numpy as np
import keyboard
import time
from utils.custom_mouse import mouse
from template_finder import TemplateFinder
from ui_manager import detect_screen_object, ScreenObjects, is_visible, wait_until_hidden
from utils.misc import wait, trim_black, color_filter, cut_roi
from inventory import consumables
from ui import view
from screen import convert_screen_to_monitor, grab
from logger import Logger
from ocr import Ocr
from template_finder import TemplateMatch

def get_slot_pos_and_img(img: np.ndarray, column: int, row: int) -> tuple[tuple[int, int],  np.ndarray]:
    """
    Get the pos and img of a specific slot position in Inventory. Inventory must be open in the image.
    :param config: The config which should be used
    :param img: Image from screen.grab() not cut
    :param column: Column in the Inventory
    :param row: Row in the Inventory
    :return: Returns position and image of the cut area as such: [[x, y], img]
    """
    top_left_slot = (Config().ui_pos["inventory_top_left_slot_x"], Config().ui_pos["inventory_top_left_slot_y"])
    slot_width = Config().ui_pos["slot_width"]
    slot_height= Config().ui_pos["slot_height"]
    slot = (top_left_slot[0] + slot_width * column, top_left_slot[1] + slot_height * row)
    # decrease size to make sure not to have any borders of the slot in the image
    offset_w = int(slot_width * 0.12)
    offset_h = int(slot_height * 0.12)
    min_x = slot[0] + offset_w
    max_x = slot[0] + slot_width - offset_w
    min_y = slot[1] + offset_h
    max_y = slot[1] + slot_height - offset_h
    slot_img = img[min_y:max_y, min_x:max_x]
    center_pos = (int(slot[0] + (slot_width // 2)), int(slot[1] + (slot_height // 2)))
    return center_pos, slot_img

def slot_has_item(slot_img: np.ndarray) -> bool:
    """
    Check if a specific slot in the inventory has an item or not based on color
    :param slot_img: Image of the slot
    :return: Bool if there is an item or not
    """
    slot_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
    avg_brightness = np.average(slot_img[:, :, 2])
    return avg_brightness > 16.0

def close(img: np.ndarray = None) -> np.ndarray:
    img = grab() if img is None else img
    if is_visible(ScreenObjects.RightPanel, img) or is_visible(ScreenObjects.LeftPanel, img):
        keyboard.send("esc")
        if not wait_until_hidden(ScreenObjects.RightPanel, 1) and not wait_until_hidden(ScreenObjects.LeftPanel, 1):
            success = view.return_to_play()
            if not success:
                return None
    return img

def calc_item_roi(img_pre, img_post):
    try:
        diff = cv2.absdiff(img_pre, img_post)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        diff_thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)[1]

        blue_mask, _ = color_filter(img_pre, Config().colors["blue_slot"])
        red_mask, _ = color_filter(img_pre, Config().colors["red_slot"])
        green_mask, _ = color_filter(img_post, Config().colors["green_slot"])

        blue_red_mask = np.bitwise_or(blue_mask, red_mask)
        final = np.bitwise_and.reduce([blue_red_mask, green_mask, diff_thresh])
        _, roi = trim_black(final)
        return roi
    except ValueError:
        Logger.debug(f"_calc_item_roi: Couldn't determine item dimensions--tooltip likely obscuring")
    except BaseException as err:
        Logger.error(f"_calc_item_roi: Unexpected {err=}, {type(err)=}")
        return None

def tome_state(img: np.ndarray = None, tome_type: str = "tp", roi: list = None):
    img = img if img is not None else grab()
    if (tome_found := TemplateFinder().search([f"{tome_type.upper()}_TOME", f"{tome_type.upper()}_TOME_RED"], img, roi = roi, threshold = 0.8, best_match = True, normalize_monitor = True)).valid:
        if tome_found.name == f"{tome_type.upper()}_TOME":
            state = "ok"
        else:
            state = "empty"
        position = tome_found.center
    else:
        state = position = None
    return state, position

def id_item_with_tome(item_location: list, id_tome_location: list):
    mouse.move(id_tome_location[0], id_tome_location[1], randomize=4, delay_factor=[0.4, 0.8])
    wait(0.2, 0.4)
    mouse.click(button="right")
    wait(0.1)
    mouse.move(item_location[0], item_location[1], randomize=4, delay_factor=[0.4, 0.8])
    wait(0.1)
    mouse.click(button="left")
    consumables.increment_need("id", 1)
    wait(0.1)

# use with caution--unreliable
def read_gold(img: np.ndarray = None, type: str = "inventory"):
    if type not in ["vendor", "inventory", "stash"]:
        Logger.error(f"read_gold: type {type} not supported")
        return False
    img = img if img is not None else grab()
    img = cut_roi(img, Config().ui_roi[f"{type}_gold_digits"])
    # _, img = color_filter(img, Config().colors["gold_numbers"])
    img = np.pad(img, pad_width=[(8, 8),(8, 8),(0, 0)], mode='constant')
    ocr_result = Ocr().image_to_text(
        images = img,
        model = "engd2r_inv_th_fast",
        psm = 13,
        scale = 1.2,
        crop_pad = False,
        erode = False,
        invert = False,
        threshold = 76,
        digits_only = True,
        fix_regexps = False,
        check_known_errors = False,
        check_wordlist = False,
    )[0]
    number=int(ocr_result.text.strip())
    Logger.debug(f"{type.upper()} gold: {number}")
    return number

def wait_for_left_inventory(timeout: int = 5):
    start=time.time()
    while time.time() - start < timeout:
        if left_inventory_ready(grab()):
            Logger.debug("Vendor/stash inventory ready")
            return True
        wait(0.1)
    Logger.error("wait_for_left_inventory: Vendor/stash inventory not detected")
    return False

def left_inventory_ready(img = np.ndarray):
    # on laggy PC's or online the vendor may take longer to have all of its inventory ready
    if is_visible(ScreenObjects.LeftPanel, img):
        # check for tab text
        text, _ = color_filter(img, Config().colors["tab_text"])
        text = cut_roi(text, Config().ui_roi["left_inventory_tabs"])
        # check for red slots in inventory space
        red, _ = color_filter(img, Config().colors["red_slot"])
        red = cut_roi(red, Config().ui_roi["left_inventory"])
        # check for blue slots in inventory space
        blue, _ = color_filter(img, Config().colors["blue_slot"])
        blue = cut_roi(blue, Config().ui_roi["left_inventory"])
        # if none of the above are true, then inventory is empty and there are no tabs (not loaded yet)
        return any(np.sum(i) > 0 for i in [text, red, blue])
    return False

def tab_properties(idx: int = 0) -> dict[int, int, tuple]:
    tab_width = round(int(Config().ui_roi["tab_indicator"][2]) / 4)
    x_start = int(Config().ui_roi["tab_indicator"][0])
    left = idx * tab_width + x_start
    right = (idx + 1) * tab_width + x_start
    x_center = (left + right) / 2
    y_center = int(Config().ui_roi["tab_indicator"][1]) - 5
    return {
        "left": round(left),
        "right": round(right),
        "center": (x_center, y_center)
    }

def indicator_location_to_tab_count(pos: tuple) -> int:
    for i in range(4):
        tab = tab_properties(i)
        if tab["left"] <= pos[0] < tab["right"]:
            return i
    return -1

def get_active_tab(indicator: TemplateMatch = None) -> int:
    indicator = detect_screen_object(ScreenObjects.TabIndicator) if indicator is None else indicator
    if indicator.valid:
        return indicator_location_to_tab_count(indicator.center)
    else:
        Logger.error("common/get_active_tab(): Error finding tab indicator")
    return -1

def select_tab(idx: int):
    # stash or vendor must be open
    # indices start from 0
    if not get_active_tab() == idx:
        tab = tab_properties(idx)
        pos = convert_screen_to_monitor(tab["center"])
        mouse.move(*pos)
        wait(0.2, 0.3)
        mouse.click("left")
        wait(0.2, 0.3)

if __name__ == "__main__":
    import os
    import keyboard
    from config import Config
    from screen import start_detecting_window, stop_detecting_window
    from utils.misc import color_filter
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    print("Move to d2r window and press f11")
    keyboard.wait("f11")

    #select_tab(0)

    color = Config().colors["tab_text"]
    while 1:
        # img = cv2.imread("")
        img = grab()

        a = cut_roi(img, Config().ui_roi["deposit_ok"])
        b, _ = color_filter(img, Config().colors["tab_text"])

        print(np.sum(b))

        cv2.imshow('test', b)
        key = cv2.waitKey(1)
