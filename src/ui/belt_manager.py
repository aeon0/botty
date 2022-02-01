import numpy as np
from typing import List
import keyboard
import itertools
import cv2

from utils.misc import cut_roi, wait, color_filter
from utils.custom_mouse import mouse

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from ui import UiManager


class BeltManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._pot_needs = {"rejuv": 0, "health": 0, "mana": 0}
        self._item_pot_map = {
            "misc_rejuvenation_potion": "rejuv",
            "misc_full_rejuvenation_potion": "rejuv",
            "misc_super_healing_potion": "health",
            "misc_greater_healing_potion": "health",
            "misc_super_mana_potion": "mana",
            "misc_greater_mana_potion": "mana"
        }

    def get_pot_needs(self):
        return self._pot_needs

    def should_buy_pots(self):
        return self._pot_needs["health"] > 2 or self._pot_needs["mana"] > 3

    def _potion_type(self, img: np.ndarray) -> str:
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
        mask, _ = color_filter(img, self._config.colors["rejuv_potion"])
        score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
        # health
        mask1, _ = color_filter(img, self._config.colors["health_potion_0"])
        mask2, _ = color_filter(img, self._config.colors["health_potion_1"])
        mask_health = cv2.bitwise_or(mask1, mask2)
        score_list.append((float(np.sum(mask_health)) / mask_health.size) * (1/255.0))
        # mana
        mask, _ = color_filter(img, self._config.colors["mana_potion"])
        score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
        # find max score
        max_val = np.max(score_list)
        if max_val > 0.28:
            idx = np.argmax(score_list)
            types = ["rejuv", "health", "mana"]
            return types[idx]
        else:
            return "empty"

    def _cut_potion_img(self, img: np.ndarray, column: int, row: int) -> np.ndarray:
        roi = [
            self._config.ui_pos["potion1_x"] - (self._config.ui_pos["potion_width"] // 2) + column * self._config.ui_pos["potion_next"],
            self._config.ui_pos["potion1_y"] - (self._config.ui_pos["potion_height"] // 2) - int(row * self._config.ui_pos["potion_next"] * 0.92),
            self._config.ui_pos["potion_width"],
            self._config.ui_pos["potion_height"]
        ]
        return cut_roi(img, roi)

    def drink_potion(self, potion_type: str, merc: bool = False, stats: List = []) -> bool:
        img = self._screen.grab()
        for i in range(4):
            potion_img = self._cut_potion_img(img, i, 0)
            if self._potion_type(potion_img) == potion_type:
                key = f"potion{i+1}"
                if merc:
                    Logger.debug(f"Give {potion_type} potion in slot {i+1} to merc. HP: {(stats[0]*100):.1f}%")
                    keyboard.send(f"left shift + {self._config.char[key]}")
                else:
                    Logger.debug(f"Drink {potion_type} potion in slot {i+1}. HP: {(stats[0]*100):.1f}%, Mana: {(stats[1]*100):.1f}%")
                    keyboard.send(self._config.char[key])
                self._pot_needs[potion_type] = max(0, self._pot_needs[potion_type] + 1)
                return True
        return False

    def picked_up_pot(self, item_name: str):
        """Adjust the _pot_needs when a specific pot was picked up by the pickit
        :param item_name: Name of the item as it is in the pickit
        """
        if item_name in self._item_pot_map:
            self._pot_needs[self._item_pot_map[item_name]] = max(0, self._pot_needs[self._item_pot_map[item_name]] - 1)
        else:
            Logger.warning(f"BeltManager does not know about item: {item_name}")

    def update_pot_needs(self) -> List[int]:
        """
        Check how many pots are needed
        :return: [need_rejuv_pots, need_health_pots, need_mana_pots]
        """
        self._pot_needs = {"rejuv": 0, "health": 0, "mana": 0}
        rows_left = {
            "rejuv": self._config.char["belt_rejuv_columns"],
            "health": self._config.char["belt_hp_columns"],
            "mana": self._config.char["belt_mp_columns"],
        }
        # In case we are in danger that the mouse hovers the belt rows, move it to the center
        screen_mouse_pos = self._screen.convert_monitor_to_screen(mouse.get_position())
        if screen_mouse_pos[1] > self._config.ui_pos["screen_height"] * 0.72:
            center_m = self._screen.convert_abs_to_monitor((-200, -120))
            mouse.move(*center_m, randomize=100)
        keyboard.send(self._config.char["show_belt"])
        wait(0.5)
        # first clean up columns that might be too much
        img = self._screen.grab()
        for column in range(4):
            potion_type = self._potion_type(self._cut_potion_img(img, column, 0))
            if potion_type != "empty":
                rows_left[potion_type] -= 1
                if rows_left[potion_type] < 0:
                    rows_left[potion_type] += 1
                    key = f"potion{column+1}"
                    for _ in range(5):
                        keyboard.send(self._config.char[key])
                        wait(0.2, 0.3)
        # calc how many potions are needed
        img = self._screen.grab()
        current_column = None
        for column in range(4):
            for row in range(self._config.char["belt_rows"]):
                potion_type = self._potion_type(self._cut_potion_img(img, column, row))
                if row == 0:
                    if potion_type != "empty":
                        current_column = potion_type
                    else:
                        for key in rows_left:
                            if rows_left[key] > 0:
                                rows_left[key] -= 1
                                self._pot_needs[key] += self._config.char["belt_rows"]
                                break
                        break
                elif current_column is not None and potion_type == "empty":
                    self._pot_needs[current_column] += 1
        wait(0.2)
        Logger.debug(f"Will pickup: {self._pot_needs}")
        keyboard.send(self._config.char["show_belt"])

    def fill_up_belt_from_inventory(self, num_loot_columns: int):
        """
        Fill up your belt with pots from the inventory e.g. after death. It will open and close invetory by itself!
        :param num_loot_columns: Number of columns used for loot from left
        """
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.7, 1.0)
        img = self._screen.grab()
        pot_positions = []
        for column, row in itertools.product(range(num_loot_columns), range(4)):
            center_pos, slot_img = UiManager.get_slot_pos_and_img(self._config, img, column, row)
            found = self._template_finder.search(["GREATER_HEALING_POTION", "GREATER_MANA_POTION", "SUPER_HEALING_POTION", "SUPER_MANA_POTION", "FULL_REJUV_POTION", "REJUV_POTION"], slot_img, threshold=0.9).valid
            if found:
                pot_positions.append(center_pos)
        keyboard.press("shift")
        for pos in pot_positions:
            x, y = self._screen.convert_screen_to_monitor(pos)
            mouse.move(x, y, randomize=9, delay_factor=[1.0, 1.5])
            wait(0.2, 0.3)
            mouse.click(button="left")
            wait(0.3, 0.4)
        keyboard.release("shift")
        wait(0.2, 0.25)
        keyboard.send(self._config.char["inventory_screen"])
        wait(0.5)


if __name__ == "__main__":
    keyboard.wait("f11")
    config = Config()
    screen = Screen()
    template_finder = TemplateFinder(screen)
    ui_manager = UiManager(screen, template_finder)
    belt_manager = BeltManager(screen, template_finder)
    belt_manager.update_pot_needs()
    print(belt_manager._pot_needs)