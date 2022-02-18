from utils.misc import color_filter, cut_roi, wait
from template_finder import TemplateFinder
from screen import convert_screen_to_monitor, grab
from config import Config
from utils.custom_mouse import mouse
import keyboard
import cv2
from logger import Logger
import time
from ui_components import view


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

    @staticmethod
    def pick_up_corpse():
        Logger.debug("Pick up corpse")
        x, y = convert_screen_to_monitor((Config().ui_pos["corpse_x"], Config().ui_pos["corpse_y"]))
        mouse.move(x, y)
        mouse.click(button="left")

    def start_monitor(self):
        self._do_monitor = True
        self._died = False
        Logger.info("Start Death monitoring")
        while self._do_monitor:
            if self._died: continue
            time.sleep(self._loop_delay) # no need to do this too frequent, when we died we are not in a hurry...
            # Wait until the flag is reset by main.py
            if self._died: continue
            view.handle_death_screen()
        Logger.debug("Stop death monitoring")


# Testing:
if __name__ == "__main__":
    keyboard.wait("f11")
    manager = DeathManager()
    manager.pick_up_corpse()
