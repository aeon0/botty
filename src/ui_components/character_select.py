# DONE: f: has_char_template_saved(self):
# DONE: f: save_char_template(self):
# DONE: f: save_char_online_status(self):
# DONE: f: select_online_tab(self, region: tuple[int, int, int, int] = None, center: tuple[int, int] = None):
# DONE: f: select_char(self):

import cv2
import numpy as np
import time

from utils.custom_mouse import mouse
from utils.misc import cut_roi, roi_center, wait, is_in_roi

from config import Config
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from utils.misc import wait
from logger import Logger
from ocr import Ocr

from ui_components import ScreenObject, Locator

@Locator(ref=["CHARACTER_STATE_ONLINE", "CHARACTER_STATE_OFFLINE"], roi="character_online_status", best_match = True)
class OnlineStatus(ScreenObject):
    _online_character = None

    def __init__(self, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(template_finder, match)

    def online_active(self) -> bool:
        return self.match.name == "CHARACTER_STATE_ONLINE"

    @staticmethod
    def select_online_tab(region, center):
        btn_width = center[0] - region[0]
        if OnlineStatus._online_character:
            Logger.debug(f"Selecting online tab")
            x = region[0] + (btn_width / 2)
        else:
            Logger.debug(f"Selecting offline tab")
            x = region[0] + (3 * btn_width / 2)
        pos = Screen().convert_screen_to_monitor((x, center[1]))
        # move cursor to appropriate tab and select
        mouse.move(*pos)
        wait(0.4, 0.6)
        mouse.click(button="left")
        wait(0.4, 0.6)

@Locator(ref=["CHARACTER_ACTIVE"], roi="character_select", threshold=0.8)
class SelectedCharacter(ScreenObject):
    _last_char_template = None

    def __init__(self, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(template_finder, match)

    @staticmethod
    def has_char_template_saved():
        return SelectedCharacter._last_char_template is not None


class SelectCharacter():
    def __init__(self, template_finder: TemplateFinder) -> None:
        self._template_finder = template_finder

    def save_char_online_status(self):
        res, m = OnlineStatus.detect(self._template_finder)
        if m.valid:
            online_status = res.online_active()
            Logger.debug(f"Saved online status. Online={online_status}")
        else:
            Logger.error("save_char_online_status: Could not determine character's online status")
            return
        OnlineStatus._online_character = online_status

    def save_char_template(self):
        img = Screen().grab()
        res, m = SelectedCharacter.detect(self._template_finder, img)
        if m.valid:
            x, y, w, h = Config().ui_roi["character_name_sub_roi"]
            x, y = x + m.region[0], y + m.region[1]
            char_template = cut_roi(img, [x, y, w, h])

            ocr_result = Ocr().image_to_text(
                images = char_template,
                model = "engd2r_ui",
                psm = 6,
                scale = 1.2,
                crop_pad = False,
                erode = False,
                invert = False,
                threshold = 0,
                digits_only = False,
                fix_regexps = False,
                check_known_errors = False,
                check_wordlist = False,
            )[0]
            Logger.debug(f"Saved character template: {ocr_result.text.splitlines()[0]}")
        else:
            Logger.error("save_char_template: Could not save character template")
            return
        SelectedCharacter._last_char_template = char_template

    def select_char(self):
        if SelectedCharacter._last_char_template is not None:
            img = Screen().grab()
            res, m = OnlineStatus.detect(self._template_finder, img)
            if m.valid:
                if res.online_active() and (not OnlineStatus._online_character):
                    OnlineStatus.select_online_tab(m.region, m.center)
                    img = Screen().grab()
                elif not res.online_active() and (OnlineStatus._online_character):
                    OnlineStatus.select_online_tab(m.region, m.center)
                    img = Screen().grab()
                wait(1, 1.5)
            else:
                Logger.error("select_char: Could not find online/offline tabs")
                return

            res, m = SelectedCharacter.detect(self._template_finder, img)
            if not m.valid:
                Logger.error("select_char: Could not find highlighted profile")
                return

            scrolls_attempts = 0
            while scrolls_attempts < 2:
                if scrolls_attempts > 0:
                    img = Screen().grab()
                # TODO: can cleanup logic here, can we utilize a generic ScreenObject or use custom locator?
                desired_char = self._template_finder.search(SelectedCharacter._last_char_template, img, roi = Config().ui_roi["character_select"], threshold = 0.8, normalize_monitor = False)
                if desired_char.valid:
                    print(f"{m.region} {desired_char.center}")
                    if is_in_roi(m.region, desired_char.center) and scrolls_attempts == 0:
                        Logger.debug("Saved character template found and already highlighted, continue")
                        return
                    else:
                        Logger.debug("Selecting saved character")
                        pos = Screen().convert_screen_to_monitor(desired_char.center)
                        mouse.move(*pos)
                        wait(0.4, 0.6)
                        mouse.click(button="left")
                        wait(0.4), 0.6
                        return
                else:
                    Logger.debug("Highlighted profile found but saved character not in view, scroll")
                    # We can scroll the characters only if we have the mouse in the char names selection so move the mouse there
                    center = roi_center(Config().ui_roi["character_select"])
                    center = Screen().convert_screen_to_monitor(center)
                    mouse.move(*center)
                    wait(0.4, 0.6)
                    mouse.wheel(-14)
                    scrolls_attempts += 1
                    wait(0.4, 0.6)
            Logger.error(f"select_char: unable to find saved profile after {scrolls_attempts} scroll attempts")
