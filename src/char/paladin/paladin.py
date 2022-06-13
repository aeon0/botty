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
        # Logger.info("Setting up Paladin")
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._do_pre_move = True
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo

    def pre_buff(self):
        self._pre_buff_cta()
        self._cast_holy_shield()
        wait(self._cast_duration, self._cast_duration + 0.06)

    def on_capabilities_discovered(self, capabilities: CharacterCapabilities):
        # In case we have a running pala, we want to switch to concentration when moving to the boss
        # ass most likely we will click on some mobs and already cast hammers
        if capabilities.can_teleport_natively:
            self._do_pre_move = False

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not skills.is_right_skill_selected(["VIGOR"])
        can_teleport = self.capabilities.can_teleport_natively and skills.is_right_skill_active()
        if should_cast_vigor and not can_teleport:
            self._select_skill("vigor", delay=None)

    def _move_and_attack(self, abs_move: tuple[int, int], atk_len: float):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)
        self._cast_hammers(atk_len)

    def _activate_concentration_aura(self, delay=None):
        self._select_skill("concentration", delay=delay)

    def _activate_redemption_aura(self, delay = [0.6, 0.8]):
        self._select_skill("redemption", delay=delay)

    def _activate_cleanse_aura(self, delay = [0.3, 0.4]):
        self._select_skill("cleansing", delay=delay)

    def _activate_cleanse_redemption(self):
        self._activate_cleanse_aura()
        self._activate_redemption_aura()

    def _cast_holy_shield(self):
        self._cast_simple(skill_name="holy_shield", mouse_click_type="right")

    def _cast_hammers(self, min_duration: float = 0, aura: str = "concentration"): #for nihlathak
        return self._cast_left_with_aura(skill_name = "blessed_hammer", spray = 0, min_duration = min_duration, aura = aura)