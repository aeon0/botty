# f: transfer_shared_to_private_gold (self, count: int):
# f: gambling_needed(self) -> bool:
# f: set__gold_full (self, bool: bool):
# f: _move_to_stash_tab(self, stash_idx: int):
# - tabs (personal, shared, shared, shared)
# - gold (different per tab)
import ui_components.inventory as inventory
from ui_components.inventory import gambling_round
from template_finder import TemplateFinder
from screen import grab, convert_screen_to_monitor
from config import Config
import mouse
import keyboard
from utils.misc import wait
from utils.custom_mouse import mouse

gold_full = False
curr_stash = {
    "items": 3 if Config().char["fill_shared_stash_first"] else 0,
    "gold": 0
}

def transfer_shared_to_private_gold(count: int):
    for x in range (3):
        inventory.move_to_stash_tab(count)
        stash_gold_btn = TemplateFinder().search("INVENTORY_GOLD_BTN", grab(), roi=Config().ui_roi["gold_btn_stash"], threshold=0.83)
        if stash_gold_btn.valid:
            x,y = convert_screen_to_monitor(stash_gold_btn.center)
            mouse.move(x, y, randomize=4)
            wait (0.4, 0.5)
            mouse.press(button="left")
            wait (0.1, 0.15)
            mouse.release(button="left")
            wait (0.1, 0.15)
            keyboard.send ("Enter")
            wait (0.1, 0.15)
            inventory.move_to_stash_tab(0)
            inventory_gold_btn = TemplateFinder().search("INVENTORY_GOLD_BTN", grab(), roi=Config().ui_roi["gold_btn"], threshold=0.83)
            if inventory_gold_btn.valid:
                x,y = convert_screen_to_monitor(inventory_gold_btn.center)
                mouse.move(x, y, randomize=4)
                wait (0.4, 0.5)
                mouse.press(button="left")
                wait (0.1, 0.15)
                mouse.release(button="left")
                wait (0.1, 0.15)
                keyboard.send ("Enter")
                wait (0.1, 0.15)
    global gambling_round
    gambling_round += 1

def gambling_needed() -> bool:
    global gold_full
    return gold_full

def set_gold_full (bool: bool):
    global gold_full
    gold_full = bool
    global gambling_round
    gambling_round = 1