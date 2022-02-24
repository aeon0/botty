from template_finder import TemplateFinder
from screen import grab, convert_screen_to_monitor
from config import Config
import keyboard
from utils.misc import wait
from utils.custom_mouse import mouse
from ui_manager import detect_screen_object, ScreenObjects

gambling_round = 1
gold_full = False
curr_stash = {
    "items": 3 if Config().char["fill_shared_stash_first"] else 0,
    "gold": 0
}

def transfer_shared_to_private_gold(count: int):
    move_to_stash_tab(count)
    stash_gold_btn = detect_screen_object(ScreenObjects.GoldBtnStash)
    if stash_gold_btn.valid:
        mouse.move(*stash_gold_btn.center, randomize=4)
        wait (0.4, 0.5)
        mouse.press(button="left")
        wait (0.1, 0.15)
        mouse.release(button="left")
        wait (0.1, 0.15)
        keyboard.send ("Enter")
        wait (0.1, 0.15)
        move_to_stash_tab(0)
        inventory_gold_btn = detect_screen_object(ScreenObjects.GoldBtnInventory)
        if inventory_gold_btn.valid:
            mouse.move(*inventory_gold_btn.center, randomize=4)
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

def move_to_stash_tab(stash_idx: int):
    """Move to a specifc tab in the stash
    :param stash_idx: idx of the stash starting at 0 (personal stash)
    """
    str_to_idx_map = {"STASH_0_ACTIVE": 0, "STASH_1_ACTIVE": 1, "STASH_2_ACTIVE": 2, "STASH_3_ACTIVE": 3}
    template_match = TemplateFinder().search([*str_to_idx_map], grab(), threshold=0.7, best_match=True, roi=Config().ui_roi["stash_btn_roi"])
    curr_active_stash = str_to_idx_map[template_match.name] if template_match.valid else -1
    if curr_active_stash != stash_idx:
        # select the start stash
        personal_stash_pos = (Config().ui_pos["stash_personal_btn_x"], Config().ui_pos["stash_personal_btn_y"])
        stash_btn_width = Config().ui_pos["stash_btn_width"]
        next_stash_pos = (personal_stash_pos[0] + stash_btn_width * stash_idx, personal_stash_pos[1])
        x_m, y_m = convert_screen_to_monitor(next_stash_pos)
        mouse.move(x_m, y_m, randomize=[30, 7], delay_factor=[1.0, 1.5])
        wait(0.2, 0.3)
        mouse.click(button="left")
        wait(0.3, 0.4)
