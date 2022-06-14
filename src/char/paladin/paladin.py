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
        self.default_move_skill = "vigor"

    def pre_buff(self):
        self._pre_buff_cta()
        self._cast_holy_shield()
        wait(self._cast_duration, self._cast_duration + 0.06)

    def _activate_concentration_aura(self, delay=None) -> bool:
        return self._select_skill("concentration", delay=delay, mouse_click_type="right")

    def _activate_redemption_aura(self, delay = [0.6, 0.8]) -> bool:
        return self._select_skill("redemption", delay=delay, mouse_click_type="right")

    def _activate_cleanse_aura(self, delay = [0.3, 0.4]) -> bool:
        return self._select_skill("cleansing", delay=delay, mouse_click_type="right")

    def _activate_conviction_aura(self, delay = None) -> bool:
        return self._select_skill("conviction", delay=delay, mouse_click_type="right")

    def _activate_vigor_aura(self, delay = None) -> bool:
        return self._select_skill("vigor", delay=delay, mouse_click_type="right")

    def _cast_holy_shield(self) -> bool:
        return self._cast_simple(skill_name="holy_shield", mouse_click_type="right")

    def _activate_cleanse_redemption(self) -> bool:
        return self._activate_cleanse_aura() or self._activate_redemption_aura()
