import keyboard
from ui import skills
import time
import random
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from pather import Pather
from logger import Logger
from config import Config
from utils.misc import wait
from screen import convert_abs_to_screen, convert_abs_to_monitor
from pather import Pather
#import cv2 #for Diablo
from item.pickit import PickIt #for Diablo

class Paladin(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        Logger.info("Setting up Paladin")
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
        wait(self._cast_duration, self._cast_duration + 0.06)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not skills.is_right_skill_selected(["VIGOR"])
        can_teleport = self.capabilities.can_teleport_natively and skills.is_right_skill_active()
        if should_cast_vigor and not can_teleport:
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)

    def _log_cast(self, skill_name: str, cast_pos_abs: tuple[float, float], spray: int, min_duration: float, aura: str):
        msg = f"Casting skill {skill_name}"
        if cast_pos_abs:
            msg += f" at screen coordinate {convert_abs_to_screen(cast_pos_abs)}"
        if spray:
            msg += f" with spray of {spray}"
        if min_duration:
            msg += f" for {round(min_duration, 1)}s"
        if aura:
            msg += f" with {aura} active"
        Logger.debug(msg)

    def _click_cast(self, cast_pos_abs: tuple[float, float], spray: int, mouse_click_type: str = "left"):
        if cast_pos_abs:
            x = cast_pos_abs[0]
            y = cast_pos_abs[1]
            if spray:
                x += (random.random() * 2 * spray - spray)
                y += (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.1, 0.2])
            wait(0.06, 0.08)
        mouse.press(button = mouse_click_type)
        wait(0.06, 0.08)
        mouse.release(button = mouse_click_type)

    def _cast_skill_with_aura(self, skill_name: str, cast_pos_abs: tuple[float, float] = None, spray: int = 0, min_duration: float = 0, aura: str = ""):
        #self._log_cast(skill_name, cast_pos_abs, spray, min_duration, aura)

        # set aura if needed
        if aura:
            self._select_skill(aura, mouse_click_type = "right")

        # ensure character stands still
        keyboard.send(Config().char["stand_still"], do_release=False)

        # set left hand skill
        self._select_skill(skill_name, mouse_click_type = "left")
        wait(0.04)

        # cast left hand skill
        start = time.time()
        if min_duration:
            while (time.time() - start) <= min_duration:
                self._click_cast(cast_pos_abs, spray)
        else:
            self._click_cast(cast_pos_abs, spray)

        # release stand still key
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _activate_redemption_aura(self, delay = [0.6, 0.8]):
        self._select_skill("redemption", delay=delay)

    def _activate_cleanse_aura(self, delay = [0.3, 0.4]):
        self._select_skill("cleansing", delay=delay)

    def _activate_cleanse_redemption(self):
        self._activate_cleanse_aura()
        self._activate_redemption_aura()