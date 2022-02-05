from operator import is_
import cv2
import numpy as np
import time

from config import Config
from utils.custom_mouse import mouse
from utils.misc import cut_roi, roi_center, wait, is_in_roi
from screen import Screen
from template_finder import TemplateFinder
from logger import Logger

class CharSelector:
    _last_char_template = None
    _online_character = None

    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder

    def has_char_template_saved(self):
        return CharSelector._last_char_template is not None

    def save_char_template(self):
        img = self._screen.grab()
        active_character = self._template_finder.search("CHARACTER_ACTIVE", img, roi = self._config.ui_roi["character_select"], threshold = 0.8)
        if active_character.valid:
            x, y, w, h = self._config.ui_roi["character_name_sub_roi"]
            x, y = x + active_character.region[0], y + active_character.region[1]
            char_template = cut_roi(img, [x, y, w, h])
            if self._config.general["info_screenshots"]:
                cv2.imwrite("./info_screenshots/saved_character_" + time.strftime("%Y%m%d_%H%M%S") + ".png", char_template)
            Logger.debug(f"Saved character template")
        else:
            Logger.error("save_char_template: Could not save character template")
            return
        CharSelector._last_char_template = char_template

    def save_char_online_status(self):
        online_tabs = self._template_finder.search(["CHARACTER_STATE_OFFLINE","CHARACTER_STATE_ONLINE"], self._screen.grab(), roi=self._config.ui_roi["character_online_status"], threshold=0.8, best_match = True)
        if online_tabs.valid:
            if online_tabs.name == "CHARACTER_STATE_ONLINE":
                online_status = True
            else:
                online_status = False
            Logger.debug(f"Saved online status. Online={online_status}")
        else:
            Logger.error("save_char_online_status: Could not determine character's online status")
            return
        CharSelector._online_character = online_status

    def select_online_tab(self, region: tuple[int, int, int, int] = None, center: tuple[int, int] = None):
        btn_width = center[0] - region[0]
        if CharSelector._online_character:
            Logger.debug(f"Selecting online tab")
            x = region[0] + (btn_width / 2)
        else:
            Logger.debug(f"Selecting offline tab")
            x = region[0] + (3 * btn_width / 2)
        pos = self._screen.convert_screen_to_monitor((x, center[1]))
        # move cursor to result and select
        mouse.move(*pos)
        wait(0.4, 0.6)
        mouse.click(button="left")
        wait(0.4, 0.6)

    def select_char(self):
        if CharSelector._last_char_template is not None:
            online_tabs = self._template_finder.search(["CHARACTER_STATE_OFFLINE","CHARACTER_STATE_ONLINE"], self._screen.grab(), roi=self._config.ui_roi["character_online_status"], threshold=0.8, best_match = True)
            if online_tabs.valid:
                if online_tabs.name == "CHARACTER_STATE_ONLINE" and (not CharSelector._online_character):
                    self.select_online_tab(online_tabs.region, online_tabs.center)
                elif online_tabs.name == "CHARACTER_STATE_OFFLINE" and (CharSelector._online_character):
                    self.select_online_tab(online_tabs.region, online_tabs.center)
                wait(1, 1.5)
            else:
                Logger.error("select_char: Could not find online/offline tabs")
                return
            img = self._screen.grab()
            active_char = self._template_finder.search("CHARACTER_ACTIVE", img, roi = self._config.ui_roi["character_select"], threshold = 0.8, normalize_monitor = True)
            if not active_char.valid:
                Logger.error("select_char: Could not find highlighted profile")
                return
            scrolls_attempts = 0
            while scrolls_attempts < 2:
                if scrolls_attempts > 0:
                    img = self._screen.grab()
                desired_char = self._template_finder.search(CharSelector._last_char_template, img, roi = self._config.ui_roi["character_select"], threshold = 0.8, normalize_monitor = True)
                if desired_char.valid:
                    if is_in_roi(active_char.region, desired_char.center) and scrolls_attempts == 0:
                        Logger.debug("Saved character template found and already highlighted, continue")
                        return
                    else:
                        Logger.debug("Selecting saved character")
                        mouse.move(*desired_char.center)
                        wait(0.4, 0.6)
                        mouse.click(button="left")
                        wait(0.4), 0.6
                        return
                else:
                    Logger.debug("Highlighted profile found but saved character not in view, scroll")
                    # We can scroll the characters only if we have the mouse in the char names selection so move the mouse there
                    center = roi_center(self._config.ui_roi["character_select"])
                    center = self._screen.convert_screen_to_monitor(center)
                    mouse.move(*center)
                    wait(0.4, 0.6)
                    mouse.wheel(-14)
                    scrolls_attempts += 1
                    wait(0.4, 0.6)
            Logger.error(f"select_char: unable to find saved profile after {scrolls_attempts} scroll attempts")


if __name__ == "__main__":
    import keyboard
    keyboard.wait("f11")
    from config import Config
    config = Config()
    screen = Screen()
    tf = TemplateFinder(screen)
    selector = CharSelector(screen, tf)
    if not selector.has_char_template_saved():
        selector.save_char_template()
    print("Move D2R window, select another character and press F11 to continue")
    keyboard.wait("f11")
    screen = Screen()
    tf = TemplateFinder(screen)
    selector = CharSelector(screen,tf)
    selector.select_char()
