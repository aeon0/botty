import time
from screen import grab
from config import Config
import keyboard
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait
from ui_manager import wait_for_screen_object, detect_screen_object, select_screen_object_match, ScreenObjects, list_visible_objects
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

def save_and_exit() -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    start=time.time()
    while not (exit_button := detect_screen_object(ScreenObjects.SaveAndExit)).valid:
        keyboard.send("esc")
        wait(0.1)
        if time.time() - start > 5:
            return False
    select_screen_object_match(exit_button, delay_factor=(0.1, 0.3))
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
    substrings = ["NPC", "Panel", "SaveAndExit"]
    img=grab()
    start=time.time()
    while (elapsed := (time.time() - start) < 5):
        need_escape = False
        if "DARK" in detect_screen_object(ScreenObjects.InGame, img).name:
            need_escape = True
        if not need_escape:
            for substring in substrings:
                if (need_escape := any(substring in string for string in list_visible_objects(img))):
                    break
        if need_escape:
            keyboard.send("esc")
            wait(0.6, 1)
            img=grab()
        else:
            break
    if not elapsed:
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

    while True:
        img = grab()
        if (result := TemplateFinder().search(["YOU_HAVE_DIED", "NOT_ENOUGH_GOLD"], img, color_match=Config().colors["red"], use_grayscale=True, best_match=True)).valid:
            print(f"match: {result.score}")
        else:
            print("no match")
