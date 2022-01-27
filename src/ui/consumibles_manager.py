import numpy as np
from typing import List
import keyboard
import parse
import time
import cv2

from utils.misc import cut_roi, wait, color_filter
from utils.custom_mouse import mouse

from logger import Logger
from config import Config
from screen import Screen
from template_finder import TemplateFinder
from item import ItemCropper

class ConsumiblesManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        self._consumible_needs = {"rejuv": 0, "health": 0, "mana": 0, "tp": 0, "id": 0, "key": 0}
        self._item_cropper = ItemCropper(self._template_finder)
        self._item_consumible_map = {
            "misc_rejuvenation_potion": "rejuv",
            "misc_full_rejuvenation_potion": "rejuv",
            "misc_super_healing_potion": "health",
            "misc_greater_healing_potion": "health",
            "misc_super_mana_potion": "mana",
            "misc_greater_mana_potion": "mana",
            "misc_scroll_tp": "tp",
            "misc_scroll_id": "id",
            "misc_key": "key"
        }
        self._pot_rows = {
            "rejuv": self._config.char["belt_rejuv_columns"],
            "health": self._config.char["belt_hp_columns"],
            "mana": self._config.char["belt_mp_columns"],
        }

    def get_needs(self):
        return self._consumible_needs

    def reset_need(self, item_type):
        self._consumible_needs["item_type"] = 0

    def conv_need_to_remaining(self, item_name: str = None):
        if item_name is None:
            Logger.error("conv_need_to_remaining: param item_name is required")
            return False
        if item_name.lower() in ["health", "mana", "rejuv"]:
            return self._pot_rows[item_name] * self._config.char["belt_rows"] - self._consumible_needs[item_name]
        elif item_name.lower() in ['tp', 'id']:
            return 20 - self._consumible_needs[item_name]
        elif item_name.lower() == "key":
            return 12 - self._consumible_needs[item_name]
        else:
            Logger.error(f"conv_need_to_remaining: error with item_name={item_name}")

    def should_buy(self, item_name: str = None, min_remaining: int = None, min_needed: int = None):
        if item_name is None:
            Logger.error("should_buy: param item_name is required")
            return False
        if min_needed:
            return self._consumible_needs[item_name] >= min_needed
        elif min_remaining:
            return self.conv_need_to_remaining(item_name) <= min_remaining
        else:
            Logger.error("should_buy: need to specify min_remaining or min_needed")
            return False

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
        mask, _ = color_filter(img, self._config.colors["health_potion"])
        score_list.append((float(np.sum(mask)) / mask.size) * (1/255.0))
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
                self.increment_consumible_need(potion_type, 1)
                return True
        return False

    def increment_consumible_need(self, consumible_type: str = None, quantity: int = 1):
        """
        Adjust the _consumible_needs of a specific consumible
        :param consumible_type: Name of item in pickit or in consumible_map
        :param quantity: Increase the need (+int) or decrease the need (-int)
        """
        if consumible_type is None:
            Logger.error("adjust_consumible_need: required param consumible_type not given")
        if consumible_type in self._item_consumible_map:
            consumible_type = self._item_consumible_map[consumible_type]
        elif consumible_type in self._item_consumible_map.values():
            pass
        else:
            Logger.warning(f"ConsumiblesManager does not know about item: {consumible_type}")
            return
        self._consumible_needs[consumible_type] = max(0, self._consumible_needs[consumible_type] + quantity)

    def update_pot_needs(self):
        """
        Check how many pots are needed
        """
        needs = {"rejuv": 0, "health": 0, "mana": 0}
        pot_rows = self._pot_rows.copy()
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
                pot_rows[potion_type] -= 1
                if pot_rows[potion_type] < 0:
                    pot_rows[potion_type] += 1
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
                        for key in pot_rows:
                            if pot_rows[key] > 0:
                                pot_rows[key] -= 1
                                needs[key] += self._config.char["belt_rows"]
                                break
                        break
                elif current_column is not None and potion_type == "empty":
                    needs[current_column] += 1
        wait(0.2)
        keyboard.send(self._config.char["show_belt"])
        self._consumible_needs["health"] = needs["health"]
        self._consumible_needs["mana"] = needs["mana"]
        self._consumible_needs["rejuv"] = needs["rejuv"]

    def update_tome_key_needs(self, img: np.ndarray = None, item_type: str = "tp"):
        if img is None:
            inventory_open = self._template_finder.search("CLOSE_PANEL", self._screen.grab(), roi = self._config.ui_roi["right_panel_header"], threshold = 0.9).valid
            if not inventory_open:
                keyboard.send(self._config.char["inventory_screen"])
                wait(0.4, 0.6)
            img = self._screen.grab()
        if item_type.lower() in ["tp", "id"]:
            tome_found = self._template_finder.search([f"{item_type.upper()}_TOME", f"{item_type.upper()}_TOME_RED"], img, roi = self._config.ui_roi["inventory"], threshold = 0.9, best_match = True)
            if tome_found.valid:
                if tome_found.name == f"{item_type.upper()}_TOME_RED":
                    self._consumible_needs[item_type] = 0
                    return
                else:
                    pos = self._screen.convert_screen_to_monitor(tome_found.position)
            # else the tome exists and is not empty, continue
        elif item_type.lower() in ["key"]:
            res = self._template_finder.search("INV_KEY", img, roi=self._config.ui_roi["inventory"], threshold=0.9)
            pos = self._screen.convert_screen_to_monitor(res.position)
        else:
            Logger.error(f"update_tome_key_needs failed, item_type: {item_type} not supported")
            return
        mouse.move(pos[0], pos[1], randomize=4, delay_factor=[0.5, 0.7])
        wait(0.2, 0.2)
        hovered_item = self._screen.grab()
        # get the item description box
        try:
            item_box = self._item_cropper.crop_item_descr(hovered_item, ocr_language="engd2r_inv_th_fast")[0]
            result = parse.search("Quantity: {:d}", item_box.ocr_result.text).fixed[0]
            if item_type.lower() in ["tp", "id"]:
                self._consumible_needs[item_type] = 20 - result
            if item_type.lower() == "key":
                self._consumible_needs[item_type] = 12 - result
        except:
            Logger.error(f"update_tome_key_needs: Failed to capture item description box for {item_type}, box is below:")
            Logger.error(item_box)
            cv2.imwrite("./info_screenshots/failed_capture_item_description_box" + time.strftime("%Y%m%d_%H%M%S") + ".png", self._screen.grab())

if __name__ == "__main__":
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    consumibles_manager = ConsumiblesManager(screen, template_finder)
    consumibles_manager.update_consumible_needs()
    print(consumibles_manager._consumible_needs)