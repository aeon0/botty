from pather import Location
import cv2
import time
import keyboard
from ui_components.globes import get_health, get_mana
from ui_components.belt import drink_potion
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
from screen import grab
import time
from config import Config
from ui_components.ingame_menu import save_and_exit
from ui_components.merc import get_merc_health
from ui.ui_manager import detect_screen_object
from ui.screen_objects import ScreenObjects

class HealthManager:
    def __init__(self):
        self._do_monitor = False
        self._did_chicken = False
        self._last_rejuv = time.time()
        self._last_health = time.time()
        self._last_mana = time.time()
        self._last_merc_heal = time.time()
        self._callback = None
        self._pausing = True
        self._last_chicken_screenshot = None

    def stop_monitor(self):
        self._do_monitor = False

    def set_callback(self, callback):
        self._callback = callback

    def did_chicken(self):
        return self._did_chicken

    def reset_chicken_flag(self):
        self._did_chicken = False
        self._pausing = True

    def update_location(self, loc: Location):
        if loc is not None and type(loc) == str:
            bosses = ["shenk", "eldritch", "pindle", "nihlathak", "trav", "arc", "diablo"]
            prev_value = self._pausing
            self._pausing = not any(substring in loc for substring in bosses)
            if self._pausing != prev_value:
                debug_str = "pausing" if self._pausing else "active"
                Logger.info(f"Health Manager is now {debug_str}")

    def _do_chicken(self, img):
        if self._callback is not None:
            self._callback()
            self._callback = None
        if Config().general["info_screenshots"]:
            self._last_chicken_screenshot = "./info_screenshots/info_debug_chicken_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
            cv2.imwrite(self._last_chicken_screenshot, img)
        # clean up key presses that might be pressed in the run_thread
        keyboard.release(Config().char["stand_still"])
        wait(0.02, 0.05)
        keyboard.release(Config().char["show_items"])
        wait(0.02, 0.05)
        mouse.release(button="left")
        wait(0.02, 0.05)
        mouse.release(button="right")
        time.sleep(0.01)
        save_and_exit(does_chicken=True)
        self._did_chicken = True
        self._pausing = True

    def start_monitor(self):
        Logger.info("Start health monitoring")
        self._do_monitor = True
        self._did_chicken = False
        start = time.time()
        while self._do_monitor:
            time.sleep(0.1)
            # Wait until the flag is reset by main.py
            if self._did_chicken or self._pausing: continue
            img = grab()
            # TODO: Check if in town or not! Otherwise risk endless chicken loop
            match = detect_screen_object(ScreenObjects.BarAnchor, img)
            if match.valid:
                health_percentage = get_health(img)
                mana_percentage = get_mana(img)
                # check rejuv
                success_drink_rejuv = False
                last_drink = time.time() - self._last_rejuv
                if (health_percentage < Config().char["take_rejuv_potion_health"] and last_drink > 1) or \
                   (mana_percentage < Config().char["take_rejuv_potion_mana"] and last_drink > 2):
                    success_drink_rejuv = drink_potion("rejuv", stats=[health_percentage, mana_percentage])
                    self._last_rejuv = time.time()
                # in case no rejuv was used, check for chicken, health pot and mana pot usage
                if not success_drink_rejuv:
                    # check health
                    last_drink = time.time() - self._last_health
                    if health_percentage < Config().char["take_health_potion"] and last_drink > 3.5:
                        drink_potion("health", stats=[health_percentage, mana_percentage])
                        self._last_health = time.time()
                    # give the chicken a 6 sec delay to give time for a healing pot and avoid endless loop of chicken
                    elif health_percentage < Config().char["chicken"] and (time.time() - start) > 6:
                        Logger.warning(f"Trying to chicken, player HP {(health_percentage*100):.1f}%!")
                        self._do_chicken(img)
                    # check mana
                    last_drink = time.time() - self._last_mana
                    if mana_percentage < Config().char["take_mana_potion"] and last_drink > 4:
                        drink_potion("mana", stats=[health_percentage, mana_percentage])
                        self._last_mana = time.time()
                # check merc
                match = detect_screen_object(ScreenObjects.MercIcon)
                if match.valid:
                    merc_health_percentage = get_merc_health(img)
                    last_drink = time.time() - self._last_merc_heal
                    if merc_health_percentage < Config().char["merc_chicken"]:
                        Logger.warning(f"Trying to chicken, merc HP {(merc_health_percentage*100):.1f}%!")
                        self._do_chicken(img)
                    if merc_health_percentage < Config().char["heal_rejuv_merc"] and last_drink > 4.0:
                        drink_potion("rejuv", merc=True, stats=[merc_health_percentage])
                        self._last_merc_heal = time.time()
                    elif merc_health_percentage < Config().char["heal_merc"] and last_drink > 7.0:
                        drink_potion("health", merc=True, stats=[merc_health_percentage])
                        self._last_merc_heal = time.time()
        Logger.debug("Stop health monitoring")


# Testing: Start dying or lossing mana and see if it works
if __name__ == "__main__":
    import threading
    import keyboard
    import os
    keyboard.add_hotkey('f12', lambda: Logger.info('Exit Health Manager') or os._exit(1))
    manager = HealthManager()
    manager._pausing = False
    Logger.info("Press f12 to exit health manager")
    health_monitor_thread = threading.Thread(target=manager.start_monitor)
    health_monitor_thread.start()
    while 1:
        if manager.did_chicken():
            manager.stop_monitor()
            health_monitor_thread.join()
            break
        wait(0.5)
