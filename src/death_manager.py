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
    def __init__(self, screen: Screen):
        self._config = Config()
        self._screen = screen
        self._template_finder = TemplateFinder(screen)
        _, self._you_have_died_filtered = color_filter(cv2.imread(f"assets/templates/you_have_died.png"), self._config.colors["red"])
        self._died = False
        self._do_monitor = False
        self._loop_delay = 1.0
        self._callback = None

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
    def pick_up_corpse(config: Config, screen: Screen):
        Logger.debug("Pick up corpse")
        x, y = screen.convert_screen_to_monitor((config.ui_pos["corpse_x"], config.ui_pos["corpse_y"]))
        mouse.move(x, y)
        mouse.click(button="left")

    def handle_death_screen(self):
        roi_img = cut_roi(self._screen.grab(), self._config.ui_roi["death"])
        _, filtered_roi_img = color_filter(roi_img, self._config.colors["red"])
        res = cv2.matchTemplate(filtered_roi_img, self._you_have_died_filtered, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > 0.9:
            self._died = True
            Logger.warning("You have died!")
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
            if self._template_finder.search("D2_LOGO_HS", self._screen.grab(), roi=self._config.ui_roi["hero_selection_logo"]).valid:
                # in this case chicken executed and left the game, but we were still dead.
                return True
            keyboard.send("esc")
            return True
        return False

    def start_monitor(self):
        self._do_monitor = True
        self._died = False
        Logger.info("Start Death monitoring")
        while self._do_monitor:
            time.sleep(self._loop_delay) # no need to do this too frequent, when we died we are not in a hurry...
            # Wait until the flag is reset by run.py
            if self._died: continue
            self.handle_death_screen()
        Logger.debug("Stop death monitoring")


# Testing:
if __name__ == "__main__":
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    manager = DeathManager(screen, template_finder)
    manager.start_monitor(None)
