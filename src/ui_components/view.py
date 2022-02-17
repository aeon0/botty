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
from ui.ui_manager import wait_for_screen_object
from ui.screen_objects import ScreenObjects

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
    item_pickup_text = wait_for_screen_object(ScreenObjects.ItemPickupText, time_out=3)
    if not item_pickup_text.valid:
        return False
    if item_pickup_text.name == "ITEM_PICKUP_DISABLED":
        return True
    keyboard.send('enter')
    wait(0.1, 0.25)
    keyboard.send('up')
    wait(0.1, 0.25)
    keyboard.send('enter')
    wait(0.1, 0.25)
    return True