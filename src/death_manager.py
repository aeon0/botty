from utils.misc import kill_thread, color_filter, cut_roi, wait
from template_finder import TemplateFinder
from screen import Screen
from config import Config
from utils.custom_mouse import mouse
import keyboard
import cv2
from logger import Logger
import time
from threading import Thread


class DeathManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        _, self._you_have_died_filtered = color_filter(cv2.imread("assets/templates/you_have_died.png"), self._config.colors["red"])
        self._died = False
        self._do_monitor = False
        self._loop_delay = 1.0

    def get_loop_delay(self):
        return self._loop_delay

    def stop_monitor(self):
        self._do_monitor = False

    def died(self):
        return self._died

    def pick_up_corpse(self):
        Logger.debug("Pick up corpse")
        x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["corpse_x"], self._config.ui_pos["corpse_y"]))
        mouse.move(x, y)
        mouse.click(button="left")
        self._died = False

    def start_monitor(self, run_thread: Thread):
        self._do_monitor = True
        while self._do_monitor:
            time.sleep(self._loop_delay) # no need to do this too frequent, when we died we are not in a hurry...
            roi_img = cut_roi(self._screen.grab(), self._config.ui_roi["death"])
            _, filtered_roi_img = color_filter(roi_img, self._config.colors["red"])
            res = cv2.matchTemplate(filtered_roi_img, self._you_have_died_filtered, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.94:
                Logger.warning("You have died! Waiting 30 sec to make sure chicken does not do any funny during with this logic.")
                # first wait a bit to make sure health manager is done with its chicken stuff which obviously failed
                kill_thread(run_thread)
                # clean up key presses that might be pressed in the run_thread
                keyboard.release(self._config.char["stand_still"])
                wait(0.1, 0.2)
                keyboard.release(self._config.char["show_items"])
                time.sleep(20)
                self._died = True
                if self._template_finder.search("D2_LOGO_HS", self._screen.grab())[0]:
                    # in this case chicken executed and left the game, but we were still dead.
                    return
                else:
                    keyboard.send("esc")
                    self._template_finder.search_and_wait("A5_TOWN_1")
                    time.sleep(2)
                    self._do_monitor = False


# Testing:
if __name__ == "__main__":
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    manager = DeathManager(screen, template_finder)
    manager.start_monitor(None)
