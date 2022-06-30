from char import IChar
from item.pickit import PickIt #for Diablo
from pather import Pather
from pather import Pather

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

    def _activate_concentration_aura(self, delay=None) -> bool:
        return self._activate_aura("concentration", delay=delay)

    def _activate_redemption_aura(self, delay = None) -> bool:
        return self._activate_aura("redemption", delay=delay)

    def _activate_cleansing_aura(self, delay = None) -> bool:
        return self._activate_aura("cleansing", delay=delay)

    def _activate_conviction_aura(self, delay = None) -> bool:
        return self._activate_aura("conviction", delay=delay)

    def _activate_vigor_aura(self, delay = None) -> bool:
        return self._activate_aura("vigor", delay=delay)

    def _cast_holy_shield(self) -> bool:
        return self._cast_simple(skill_name="holy_shield")

    def _activate_cleanse_redemption(self) -> bool:
        self._activate_cleansing_aura([0.3, 0.5])
        return self._activate_redemption_aura([0.3, 0.5])
