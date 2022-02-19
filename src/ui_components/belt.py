# f: open/close
# f: inspect slots
import itertools
from logger import Logger
from typing import List
import numpy as np
from template_finder import TemplateFinder
from ui_components.slots import get_slot_pos_and_img
from utils.custom_mouse import mouse
from utils.misc import cut_roi, wait, color_filter
from config import Config
from screen import convert_abs_to_monitor, convert_monitor_to_screen, convert_screen_to_monitor, grab
import keyboard

pot_needs = {"rejuv": 0, "health": 0, "mana": 0}
item_pot_map = {
    "misc_rejuvenation_potion": "rejuv",
    "misc_full_rejuvenation_potion": "rejuv",
    "misc_super_healing_potion": "health",
    "misc_greater_healing_potion": "health",
    "misc_super_mana_potion": "mana",
    "misc_greater_mana_potion": "mana"
}

def get_pot_needs():
    global pot_needs
    return pot_needs

def should_buy_pots():
    global pot_needs
    return pot_needs["health"] > 2 or pot_needs["mana"] > 3

def _potion_type(img: np.ndarray) -> str:
    """
    Based on cut out image from belt, determines what type of potion it is.
    :param img: Cut out image of a belt slot
    :return: Any of ["empty", "rejuv", "health", "mana"]
    """
    h, w, _ = img.shape
    roi = [int(w * 0.4), int(h * 0.3), int(w * 0.4), int(h * 0.7)]
    img = cut_roi(img, roi)
    avg_brightness = np.average(img)
    if avg_brightness < 47:
        return "empty"
    score_list = []
    # rejuv
    mask, _ = color_filter(img, Config().colors["rejuv_potion"])
    score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
    # health
    mask, _ = color_filter(img, Config().colors["health_potion"])
    score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
    # mana
    mask, _ = color_filter(img, Config().colors["mana_potion"])
    score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
    # find max score
    max_val = np.max(score_list)
    if max_val > 0.28:
        idx = np.argmax(score_list)
        types = ["rejuv", "health", "mana"]
        return types[idx]
    else:
        return "empty"

def _cut_potion_img(img: np.ndarray, column: int, row: int) -> np.ndarray:
    roi = [
        Config().ui_pos["potion1_x"] - (Config().ui_pos["potion_width"] // 2) + column * Config().ui_pos["potion_next"],
        Config().ui_pos["potion1_y"] - (Config().ui_pos["potion_height"] // 2) - int(row * Config().ui_pos["potion_next"] * 0.92),
        Config().ui_pos["potion_width"],
        Config().ui_pos["potion_height"]
    ]
    return cut_roi(img, roi)

def drink_potion(potion_type: str, merc: bool = False, stats: List = []) -> bool:
    global pot_needs
    img = grab()
    for i in range(4):
        potion_img = _cut_potion_img(img, i, 0)
        if _potion_type(potion_img) == potion_type:
            key = f"potion{i+1}"
            if merc:
                Logger.debug(f"Give {potion_type} potion in slot {i+1} to merc. HP: {(stats[0]*100):.1f}%")
                keyboard.send(f"left shift + {Config().char[key]}")
            else:
                Logger.debug(f"Drink {potion_type} potion in slot {i+1}. HP: {(stats[0]*100):.1f}%, Mana: {(stats[1]*100):.1f}%")
                keyboard.send(Config().char[key])
            pot_needs[potion_type] = max(0, pot_needs[potion_type] + 1)
            return True
    return False

def picked_up_pot(item_name: str):
    """Adjust the _pot_needs when a specific pot was picked up by the pickit
    :param item_name: Name of the item as it is in the pickit
    """
    global pot_needs, item_pot_map
    if item_name in item_pot_map:
        pot_needs[item_pot_map[item_name]] = max(0, pot_needs[item_pot_map[item_name]] - 1)
    else:
        Logger.warning(f"BeltManager does not know about item: {item_name}")

def update_pot_needs() -> List[int]:
    """
    Check how many pots are needed
    :return: [need_rejuv_pots, need_health_pots, need_mana_pots]
    """
    global pot_needs
    pot_needs = {"rejuv": 0, "health": 0, "mana": 0}
    rows_left = {
        "rejuv": Config().char["belt_rejuv_columns"],
        "health": Config().char["belt_hp_columns"],
        "mana": Config().char["belt_mp_columns"],
    }
    # In case we are in danger that the mouse hovers the belt rows, move it to the center
    screen_mouse_pos = convert_monitor_to_screen(mouse.get_position())
    if screen_mouse_pos[1] > Config().ui_pos["screen_height"] * 0.72:
        center_m = convert_abs_to_monitor((-200, -120))
        mouse.move(*center_m, randomize=100)
    keyboard.send(Config().char["show_belt"])
    wait(0.5)
    # first clean up columns that might be too much
    img = grab()
    for column in range(4):
        potion_type = _potion_type(_cut_potion_img(img, column, 0))
        if potion_type != "empty":
            rows_left[potion_type] -= 1
            if rows_left[potion_type] < 0:
                rows_left[potion_type] += 1
                key = f"potion{column+1}"
                for _ in range(5):
                    keyboard.send(Config().char[key])
                    wait(0.2, 0.3)
    # calc how many potions are needed
    img = grab()
    current_column = None
    for column in range(4):
        for row in range(Config().char["belt_rows"]):
            potion_type = _potion_type(_cut_potion_img(img, column, row))
            if row == 0:
                if potion_type != "empty":
                    current_column = potion_type
                else:
                    for key in rows_left:
                        if rows_left[key] > 0:
                            rows_left[key] -= 1
                            pot_needs[key] += Config().char["belt_rows"]
                            break
                    break
            elif current_column is not None and potion_type == "empty":
                pot_needs[current_column] += 1
    wait(0.2)
    Logger.debug(f"Will pickup: {pot_needs}")
    keyboard.send(Config().char["show_belt"])

def fill_up_belt_from_inventory(num_loot_columns: int):
    """
    Fill up your belt with pots from the inventory e.g. after death. It will open and close invetory by itself!
    :param num_loot_columns: Number of columns used for loot from left
    """
    keyboard.send(Config().char["inventory_screen"])
    wait(0.7, 1.0)
    img = grab()
    pot_positions = []
    for column, row in itertools.product(range(num_loot_columns), range(4)):
        center_pos, slot_img = get_slot_pos_and_img(img, column, row)
        found = TemplateFinder().search(["GREATER_HEALING_POTION", "GREATER_MANA_POTION", "SUPER_HEALING_POTION", "SUPER_MANA_POTION", "FULL_REJUV_POTION", "REJUV_POTION"], slot_img, threshold=0.9).valid
        if found:
            pot_positions.append(center_pos)
    keyboard.press("shift")
    for pos in pot_positions:
        x, y = convert_screen_to_monitor(pos)
        mouse.move(x, y, randomize=9, delay_factor=[1.0, 1.5])
        wait(0.2, 0.3)
        mouse.click(button="left")
        wait(0.3, 0.4)
    keyboard.release("shift")
    wait(0.2, 0.25)
    keyboard.send(Config().char["inventory_screen"])
    wait(0.5)
