import keyboard
from ui import skills
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from pather import Pather
from logger import Logger
from config import Config
from utils.misc import wait
from pather import Pather
#import cv2 #for Diablo
from item.pickit import PickIt #for Diablo

class Paladin(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        Logger.info("Setting up Paladin")
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._do_pre_move = True
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        keyboard.send(self._skill_hotkeys["holy_shield"])
        wait(0.04, 0.1)
        mouse.click(button="right")
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
            keyboard.send(self._skill_hotkeys["vigor"])
            wait(0.15, 0.25)