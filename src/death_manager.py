from utils.misc import wait
from screen import grab
from config import Config
from utils.custom_mouse import mouse
import keyboard
import cv2
from logger import Logger
import time
from ui_manager import ScreenObjects, is_visible


class DeathManager:
    def __init__(self):
        self._died = False
        self._do_monitor = False
        self._loop_delay = 1.0
        self._callback = None
        self._last_death_screenshot = None

    def get_loop_delay(self):
        return self._loop_delay

    def stop_monitor(self):
        self._do_monitor = False

    def set_callback(self, callback):
        self._callback = callback

    def reset_death_flag(self):
        self._died = False

    def died(self):
        return self._died

    def handle_death_screen(self):
        img = grab()
        if is_visible(ScreenObjects.YouHaveDied, img):
            Logger.warning("You have died!")
            if Config().general["info_screenshots"]:
                self._last_death_screenshot = "./log/screenshots/info/info_debug_death_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
                cv2.imwrite(self._last_death_screenshot, img)
            # first wait a bit to make sure health manager is done with its chicken stuff which obviously failed
            if self._callback is not None:
                self._callback()
                self._callback = None
            # clean up key presses that might be pressed
            keyboard.release(Config().char["stand_still"])
            wait(0.1, 0.2)
            keyboard.release(Config().char["show_items"])
            wait(0.1, 0.2)
            mouse.release(button="right")
            wait(0.1, 0.2)
            mouse.release(button="left")
            time.sleep(1)
            if is_visible(ScreenObjects.MainMenu):
                # in this case chicken executed and left the game, but we were still dead.
                return True
            keyboard.send("esc")
            self._died = True
            return True
        return False

    def start_monitor(self):
        self._do_monitor = True
        self._died = False
        Logger.info("Start Death monitoring")
        while self._do_monitor:
            if self._died: continue
            time.sleep(self._loop_delay) # no need to do this too frequent, when we died we are not in a hurry...
            # Wait until the flag is reset by main.py
            if self._died: continue
            self.handle_death_screen()
        Logger.debug("Stop death monitoring")

# Testing:
if __name__ == "__main__":
    keyboard.wait("f11")
    manager = DeathManager()
    manager.pickup_corpse()
