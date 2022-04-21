import time
from screen import grab
from config import Config
import keyboard
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
from ui_manager import wait_until_hidden, wait_until_visible, detect_screen_object, select_screen_object_match, ScreenObjects, list_visible_objects, is_visible
from inventory import common
from screen import convert_screen_to_monitor

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
    if not (item_pickup_text := wait_until_visible(ScreenObjects.ItemPickupText, timeout=1.3)).valid:
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

def save_and_exit() -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    attempts = 0
    success = False
    while attempts < 2 and not success:
        # if exit button isn't detected already, press escape
        while not (highlight := detect_screen_object(ScreenObjects.GameMenu)).valid:
            keyboard.send("esc")
            time.sleep(0.02)
        roi = Config().ui_roi[ScreenObjects.GameMenu.roi]
        y_pos = (highlight.center[1] - roi[1]) / roi[3]
        if y_pos > 0.6:
            keyboard.send("up")
            time.sleep(0.005)
        elif y_pos < 0.4:
            keyboard.send("down")
            time.sleep(0.005)
        keyboard.send("enter")
        # if center icon on player bar disappears then save/exit was successful
        if not (success := wait_until_hidden(ScreenObjects.InGame, 3)):
            Logger.debug("Failed to find or click save/exit button")
        attempts += 1
    return success

def dismiss_skills_icon() -> bool:
    start = time.time()
    while (match := detect_screen_object(ScreenObjects.QuestSkillBtn)).valid:
        select_screen_object_match(match)
        wait(0.6)
        common.close()
        if (time.time() - start) > 15:
            return False
    return True

def pickup_corpse():
    Logger.info("Pickup corpse")
    move_to_corpse()
    wait(0.4,0.6)
    mouse.click(button="left")
    #TODO: handle "Overburdened"

def move_to_corpse():
    pos = convert_screen_to_monitor((Config().ui_pos["corpse_x"], Config().ui_pos["corpse_y"]))
    mouse.move(*pos)

def return_to_play() -> bool:
    substrings = ["NPC", "Panel", "GameMenu"]
    img=grab()
    start=time.time()
    while (elapsed := (time.time() - start) < 8):
        need_escape = False
        match = detect_screen_object(ScreenObjects.InGame, img)
        if match.valid and "DARK" in match.name:
            need_escape = True
        if not need_escape:
            for substring in substrings:
                if (need_escape := any(substring in string for string in list_visible_objects(img))):
                    break
        if need_escape:
            keyboard.send("esc")
            wait(1.7)
            img=grab()
        else:
            break
    if not elapsed:
        Logger.error("return_to_play(): failed to return to neutral play screen")
        return False
    return True

# Testing
if __name__ == "__main__":
    import keyboard
    import os
    from screen import start_detecting_window, stop_detecting_window
    start_detecting_window()
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")
    from config import Config
    from template_finder import TemplateFinder

    return_to_play()