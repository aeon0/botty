from char import IChar, CharacterCapabilities
from item.pickit import PickIt #for Diablo
from pather import Pather
from pather import Pather
from screen import convert_abs_to_monitor
from ui import skills
from utils.misc import wait

class Paladin(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        # Logger.info("Setting up Paladin")
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._pickit = pickit #for Diablo
        self._picked_up_items = False #for Diablo

    def pre_buff(self):
        self._pre_buff_cta()
        self._cast_holy_shield()
        wait(self._cast_duration, self._cast_duration + 0.06)

    def pre_move(self):
        # select teleport if available
        super().pre_move()
        # in case teleport hotkey is not set or teleport can not be used, use vigor if set
        should_cast_vigor = self._skill_hotkeys["vigor"] and not skills.is_right_skill_selected(["VIGOR"])
        if should_cast_vigor and not self.can_teleport():
            self._select_skill("vigor", delay=None)

    def _activate_concentration_aura(self, delay=None):
        self._select_skill("concentration", delay=delay)

    def _activate_redemption_aura(self, delay = [0.6, 0.8]):
        self._select_skill("redemption", delay=delay)

    def _activate_cleanse_aura(self, delay = [0.3, 0.4]):
        self._select_skill("cleansing", delay=delay)

    def _activate_conviction_aura(self, delay = None):
        self._select_skill("conviction", delay=delay)

    def _activate_cleanse_redemption(self):
        self._activate_cleanse_aura()
        self._activate_redemption_aura()

    def _cast_holy_shield(self):
        self._cast_simple(skill_name="holy_shield", mouse_click_type="right")
