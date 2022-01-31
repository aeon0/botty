from utils.misc import color_filter, cut_roi, wait
from template_finder import TemplateFinder
from screen import Screen
from config import Config
from utils.custom_mouse import mouse
import keyboard
import cv2
from logger import Logger
import time


class DeathManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
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
    def pick_up_corpse(screen: Screen):
        Logger.debug("Pick up corpse")
        config = Config()
        x, y = screen.convert_screen_to_monitor((config.ui_pos["corpse_x"], config.ui_pos["corpse_y"]))
        mouse.move(x, y)
        mouse.click(button="left")

    def handle_death_screen(self):
        img = self._screen.grab()
        template_match = self._template_finder.search("YOU_HAVE_DIED", img, threshold=0.9, roi=self._config.ui_roi["death"])
        if template_match.valid:
            Logger.warning("You have died!")
            if self._config.general["info_screenshots"]:
                self._last_death_screenshot = "./info_screenshots/info_debug_death_" + time.strftime("%Y%m%d_%H%M%S") + ".png"
                cv2.imwrite(self._last_death_screenshot, img)
            # first wait a bit to make sure health manager is done with its chicken stuff which obviously failed
            if self._callback is not None:
                self._callback()
                self._callback = None
            # clean up key presses that might be pressed
            keyboard.release(self._config.char["stand_still"])
            wait(0.1, 0.2)
            keyboard.release(self._config.char["show_items"])
            wait(0.1, 0.2)
            mouse.release(button="right")
            wait(0.1, 0.2)
            mouse.release(button="left")
            time.sleep(1)
            if self._template_finder.search(["MAIN_MENU_TOP_LEFT","MAIN_MENU_TOP_LEFT_DARK"], self._screen.grab(), roi=self._config.ui_roi["main_menu_top_left"]).valid:
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
    config = Config()
    screen = Screen()
    manager = DeathManager(screen)
    manager.pick_up_corpse(screen)
