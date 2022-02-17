# f: is_overburdened(self) -> bool:
# f: repair_needed(self) -> bool:
# f: enable_no_pickup(self) -> bool:
# f: wait_for_town_spawn
# f: handle_death_screen
# f: pick_up_item(self, pos: Tuple[float, float], item_name: str = None, prev_cast_start: float = 0):
# - repair_needed
# - ammo_low
# - chat_box (might be same roi as is_overburdened? diablo walks? item pickup?)
# - enemy_name / enemy_health
# - enemy_info / enemy_resistances
# - death message
# - death button
# - red portal
# - blue portal
from template_finder import TemplateFinder
from screen import grab
from config import Config
import keyboard
from utils.misc import wait

def repair_needed() -> bool:
    template_match = TemplateFinder().search(
        "REPAIR_NEEDED",
        grab(),
        roi=Config().ui_roi["repair_needed"],
        use_grayscale=True)
    return template_match.valid

def enable_no_pickup() -> bool:
    """
    Checks the best match between enabled and disabled an retrys if already set.
    :return: Returns True if we succesfully set the nopickup option
    """
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.write('/nopickup',delay=.20)
    keyboard.send('enter')
    wait(0.1, 0.25)
    no_pickup = TemplateFinder().search_and_wait(["ITEM_PICKUP_ENABLED","ITEM_PICKUP_DISABLED"], roi=Config().ui_roi["no_pickup"], best_match=True, time_out=3)
    if not no_pickup.valid:
        return False
    if no_pickup.name == "ITEM_PICKUP_DISABLED":
        return True
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.send('up')
    wait(0.1, 0.25)
    keyboard.send('enter')
    wait(0.1, 0.25)
    return True