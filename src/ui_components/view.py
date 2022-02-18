# f: repair_needed(self) -> bool:
# f: wait_for_town_spawn
# f: pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
# - repair_needed
# - ammo_low
# - chat_box (might be same roi as is_overburdened? diablo walks? item pickup?)
# - enemy_name / enemy_health
# - enemy_info / enemy_resistances
# - death message
# - death button
# - red portal
# - blue portal
import time
import cv2
from screen import grab
from config import Config
import keyboard
import mouse
from logger import Logger
from template_finder import TemplateFinder
from utils.misc import color_filter, cut_roi, wait
from ui.ui_manager import wait_for_screen_object
from ui.screen_objects import ScreenObjects

last_death_screenshot = None

def is_overburdened() -> bool:
    """
    :return: Bool if the last pick up overburdened your char. Must be called right after picking up an item.
    """
    img = cut_roi(grab(), Config().ui_roi["is_overburdened"])
    _, filtered_img = color_filter(img, Config().colors["gold"])
    templates = [cv2.imread("assets/templates/inventory_full_msg_0.png"), cv2.imread("assets/templates/inventory_full_msg_1.png")]
    for template in templates:
        _, filtered_template = color_filter(template, Config().colors["gold"])
        res = cv2.matchTemplate(filtered_img, filtered_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > 0.8:
            return True
    return False

def enable_no_pickup() -> bool:
    """
    Checks the best match between enabled and disabled an retrys if already set.
    :return: Returns True if we succesfully set the nopickup option
    """
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.write('/nopickup',delay=.20)
    keyboard.send('enter')
    wait(0.1, 0.25)
    item_pickup_text = wait_for_screen_object(ScreenObjects.ItemPickupText, time_out=3)
    if not item_pickup_text.valid:
        return False
    if item_pickup_text.name == "ITEM_PICKUP_DISABLED":
        return True
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.send('up')
    wait(0.1, 0.25)
    keyboard.send('enter')
    wait(0.1, 0.25)
    return True

def handle_death_screen():
    global last_death_screenshot
    img = grab()
    template_match = TemplateFinder().search("YOU_HAVE_DIED", img, threshold=0.9, roi=Config().ui_roi["death"])
    if template_match.valid:
        Logger.warning("You have died!")
        if Config().general["info_screenshots"]:
            last_death_screenshot = "./info_screenshots/info_debug_death_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
            cv2.imwrite(last_death_screenshot, img)
        # clean up key presses that might be pressed
        keyboard.release(Config().char["stand_still"])
        wait(0.1, 0.2)
        keyboard.release(Config().char["show_items"])
        wait(0.1, 0.2)
        mouse.release(button="right")
        wait(0.1, 0.2)
        mouse.release(button="left")
        time.sleep(1)
        if TemplateFinder().search(["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"], grab(), roi=Config().ui_roi["main_menu_top_left"]).valid:
            # in this case chicken executed and left the game, but we were still dead.
            return True
        keyboard.send("esc")
        return True
    return False
