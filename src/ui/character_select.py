from utils.custom_mouse import mouse
from utils.misc import cut_roi, roi_center, wait, is_in_roi

from config import Config
from screen import convert_screen_to_monitor, grab
import template_finder
from utils.misc import wait
from logger import Logger
from d2r_image import ocr
import numpy as np
from ui_manager import detect_screen_object, ScreenObjects

last_char_template = None
online_character = None

def select_online_tab(region, center) -> bool:
    btn_width = center[0] - region[0]
    if online_character:
        Logger.debug(f"Selecting online tab")
        x = region[0] + (btn_width / 2)
    else:
        Logger.debug(f"Selecting offline tab")
        x = region[0] + (3 * btn_width / 2)
    pos = convert_screen_to_monitor((x, center[1]))
    # move cursor to appropriate tab and select
    mouse.move(*pos)
    wait(0.3, 0.5)
    attempts = 0
    while attempts <= 4:
        attempts += 1
        mouse.click(button="left")
        if (match := detect_screen_object(ScreenObjects.OnlineStatus, grab())).valid and online_character == online_active(match):
            return True
        wait(1.5)
    online_str = "online" if online_character else "offline"
    Logger.error(f"select_online_tab: unable to select {online_str} tab after {attempts} attempts")
    return False

def get_saved_char_template() -> np.ndarray | None:
    return None if not has_char_template_saved() else last_char_template

def has_char_template_saved():
    return last_char_template is not None

def save_char_online_status():
    if (match := detect_screen_object(ScreenObjects.OnlineStatus)).valid:
        online_status = online_active(match)
        Logger.debug(f"Saved online status. Online={online_status}")
    else:
        Logger.error("save_char_online_status: Could not determine character's online status")
        return
    global online_character
    online_character = online_status

def online_active(match) -> bool:
    return match.name == "CHARACTER_STATE_ONLINE"

def save_char_template():
    img = grab()
    if (match := detect_screen_object(ScreenObjects.SelectedCharacter)).valid:
        x, y, w, h = Config().ui_roi["character_name_sub_roi"]
        x, y = x + match.region[0], y + match.region[1]
        char_template = cut_roi(img, [x, y, w, h])
        msg=""
        try:
            ocr_result = ocr.image_to_text(
                images = cut_roi(img, [x, y, w, h]),
                model = "hover-eng_inconsolata_inv_th_fast",
                psm = 6,
                scale = 1.2,
                crop_pad = False,
                erode = False,
                invert = False,
                threshold = 0,
                digits_only = False,
                fix_regexps = False,
                check_known_errors = False,
                correct_words = False,
            )[0]
            msg += f": {ocr_result.text.splitlines()[0]}"
        except:
            pass
        Logger.debug(f"Saved character template{msg}")
    else:
        Logger.error("save_char_template: Could not save character template")
        return
    global last_char_template
    last_char_template = char_template

def select_char() -> bool:
    if last_char_template is not None:
        img = grab()
        if (match := detect_screen_object(ScreenObjects.OnlineStatus, img)).valid:
            if online_active(match) != online_character:
                if not select_online_tab(match.region, match.center):
                    return False
                img = grab()
            wait(1, 1.5)
        else:
            Logger.error("select_char: Could not find online/offline tabs")
            return False
        if not (match := detect_screen_object(ScreenObjects.SelectedCharacter, img)).valid:
            Logger.error("select_char: Could not find highlighted profile")
            return False
        scrolls_attempts = 0
        while scrolls_attempts < 2:
            if scrolls_attempts > 0:
                img = grab()
            # TODO: can cleanup logic here, can we utilize a generic ScreenObject or use custom locator?
            desired_char = template_finder.search(last_char_template, img, roi = Config().ui_roi["character_select"], threshold = 0.8)
            if desired_char.valid:
                #print(f"{match.region} {desired_char.center}")
                if is_in_roi(match.region, desired_char.center) and scrolls_attempts == 0:
                    Logger.debug("Saved character template found and already highlighted, continue")
                    return True
                else:
                    Logger.debug("Selecting saved character")
                    mouse.move(*desired_char.center_monitor)
                    wait(0.4, 0.6)
                    mouse.click(button="left")
                    wait(0.4, 0.6)
                    return True
            else:
                Logger.debug("Highlighted profile found but saved character not in view, scroll")
                # We can scroll the characters only if we have the mouse in the char names selection so move the mouse there
                center = roi_center(Config().ui_roi["character_select"])
                center = convert_screen_to_monitor(center)
                mouse.move(*center)
                wait(0.4, 0.6)
                mouse.wheel(-14)
                scrolls_attempts += 1
                wait(0.4, 0.6)
        Logger.error(f"select_char: unable to find saved profile after {scrolls_attempts} scroll attempts")
        return False