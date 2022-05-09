from inventory import belt
from pather import Location
import cv2
import time
import keyboard
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
from screen import grab
import time
from config import Config
from inventory import common
from ui import view, meters
from ui_manager import ScreenObjects, is_visible
from random import uniform

pause_state = True

def get_pause_state():
    global pause_state
    return pause_state

def set_pause_state(state: bool):
    global pause_state
    prev = get_pause_state()
    if prev != state:
        debug_str = "pausing" if state else "active"
        Logger.info(f"Health Manager is now {debug_str}")
        pause_state = state

class HealthManager:
    def __init__(self):
        self._do_monitor = False
        self._did_chicken = False
        self._last_rejuv = time.time()
        self._last_health = time.time()
        self._last_mana = time.time()
        self._last_merc_heal = time.time()
        self._callback = None
        self._last_chicken_screenshot = None
        self._count_panel_detects = 0

    def stop_monitor(self):
        self._do_monitor = False

    def set_callback(self, callback):
        self._callback = callback

    def did_chicken(self):
        return self._did_chicken

    def reset_chicken_flag(self):
        self._did_chicken = False
        set_pause_state(True)

    def _do_chicken(self, img):
        if self._callback is not None:
            self._callback()
            self._callback = None
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(Config().char["stand_still"])
        keyboard.release(Config().char["show_items"])
        mouse.release(button="left")
        mouse.release(button="right")
        view.save_and_exit()
        if Config().general["info_screenshots"]:
            self._last_chicken_screenshot = "./info_screenshots/info_debug_chicken_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
            cv2.imwrite(self._last_chicken_screenshot, img)
        self._did_chicken = True
        set_pause_state(True)

    def start_monitor(self):
        Logger.info("Start health monitoring")
        self._do_monitor = True
        self._did_chicken = False
        start = time.time()

        while self._do_monitor:
            time.sleep(0.1)
            # Wait until the flag is reset by main.py
            if self._did_chicken or get_pause_state(): continue
            img = grab()
            if is_visible(ScreenObjects.InGame, img):
                health_percentage = meters.get_health(img)
                mana_percentage = meters.get_mana(img)

                lp_hp_potion_delay = 0 if health_percentage >= 0.99 else uniform(9, 10)
                lp_mp_potion_delay = 0 if mana_percentage >= 0.99 else uniform(9, 10)

                # check rejuv
                success_drink_rejuv = False
                last_drink = time.time() - self._last_rejuv
                if (health_percentage <= Config().char["take_rejuv_potion_health"] and last_drink > 1) or \
                   (mana_percentage <= Config().char["take_rejuv_potion_mana"] and last_drink > 2):
                    success_drink_rejuv = belt.drink_potion("rejuv", stats=[health_percentage, mana_percentage])
                    self._last_rejuv = time.time()
                # in case no rejuv was used, check for chicken, health pot and mana pot usage
                if not success_drink_rejuv:
                    # check health
                    last_drink = time.time() - self._last_health
                    if health_percentage <= Config().char["take_health_potion"] and last_drink > lp_hp_potion_delay:
                        belt.drink_potion("health", stats=[health_percentage, mana_percentage])
                        self._last_health = time.time()
                    # give the chicken a 6 sec delay to give time for a healing pot and avoid endless loop of chicken
                    elif health_percentage <= Config().char["chicken"] and (time.time() - start) > 6:
                        Logger.warning(f"Trying to chicken, player HP {(health_percentage*100):.1f}%!")
                        self._do_chicken(img)
                    # check mana
                    last_drink = time.time() - self._last_mana
                    if mana_percentage <= Config().char["take_mana_potion"] and last_drink > lp_mp_potion_delay:
                        belt.drink_potion("mana", stats=[health_percentage, mana_percentage])
                        self._last_mana = time.time()
                # check merc
                if is_visible(ScreenObjects.MercIcon, img):
                    merc_health_percentage = meters.get_merc_health(img)
                    merc_hp_potion_delay = 0 if merc_health_percentage == 1 else uniform(9, 10)
                    last_drink = time.time() - self._last_merc_heal
                    if merc_health_percentage <= Config().char["merc_chicken"]:
                        Logger.warning(f"Trying to chicken, merc HP {(merc_health_percentage*100):.1f}%!")
                        self._do_chicken(img)
                    if merc_health_percentage <= Config().char["heal_rejuv_merc"] and last_drink > 4.0:
                        belt.drink_potion("rejuv", merc=True, stats=[merc_health_percentage])
                        self._last_merc_heal = time.time()
                    elif merc_health_percentage <= Config().char["heal_merc"] and last_drink > merc_hp_potion_delay:
                        belt.drink_potion("health", merc=True, stats=[merc_health_percentage])
                        self._last_merc_heal = time.time()
                if is_visible(ScreenObjects.LeftPanel, img) or is_visible(ScreenObjects.RightPanel, img):
                    Logger.warning(f"Found an open inventory / quest / skill / stats page. Close it.")
                    self._count_panel_detects += 1
                    if self._count_panel_detects >= 2:
                        self._count_panel_detects = 0
                        Logger.warning(f"Found an open inventory / quest / skill / stats page again. Chicken to dismiss.")
                        self._do_chicken(img)
                    common.close()
        Logger.debug("Stop health monitoring")


# Testing: Start dying or losing mana and see if it works
if __name__ == "__main__":
    import threading
    import keyboard
    import os
    from health_manager import set_pause_state
    keyboard.add_hotkey('f12', lambda: Logger.info('Exit Health Manager') or os._exit(1))
    manager = HealthManager()
    set_pause_state(True)
    Logger.info("Press f12 to exit health manager")
    health_monitor_thread = threading.Thread(target=manager.start_monitor)
    health_monitor_thread.start()
    while 1:
        if manager.did_chicken():
            manager.stop_monitor()
            health_monitor_thread.join()
            break
        wait(0.5)
