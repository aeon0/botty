# merc_portrait
# merc_life
# life_globe
# mana_globe
# experience
# left_skill
# right_skill
# belt_row_1
# repair_needed
# ammo_low
# chat_box (might be same roi as is_overburdened?)
# enemy_name / enemy_health
# enemy_info / enemy_resistances

from ui_elements import SceenObject

class Hud(ScreenObject):
    def __init__(self) -> None:
        super().__init__()

    def get_experience():
        # ensure EXP bar is present
        ScreenObject.detect("EXP_BAR")
        # color filter
        # calculate percentage

        # or read exp with OCR
        pass

    def get_left_skill():
        pass