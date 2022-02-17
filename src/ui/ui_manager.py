import keyboard
import cv2
import itertools
import os
import numpy as np
import json
from utils.custom_mouse import mouse
from utils.misc import wait, cut_roi, color_filter
from logger import Logger
from config import Config
from screen import grab, convert_screen_to_monitor
from item import ItemFinder
from template_finder import TemplateFinder, TemplateMatch
from messages import Messenger
from game_stats import GameStats
from ui.screen_objects import ScreenObject, ScreenObjects

class UiManager():
    """Everything that is clicking on some static 2D UI or is checking anything in regard to it should be placed here."""

    def __init__(self, game_stats: GameStats = None):
        self._messenger = Messenger()
        self._game_stats = game_stats

def inventory_has_items(img, num_loot_columns: int, num_ignore_columns=0) -> bool:
    """
    Check if Inventory has any items
    :param img: Img from screen.grab() with inventory open
    :param num_loot_columns: Number of columns to check from left
    :return: Bool if inventory still has items or not
    """
    for column, row in itertools.product(range(num_ignore_columns, num_loot_columns), range(4)):
        _, slot_img = get_slot_pos_and_img(img, column, row)
        if slot_has_item(slot_img):
            return True
    return False

def get_slot_pos_and_img(img: np.ndarray, column: int, row: int) -> tuple[tuple[int, int],  np.ndarray]:
    """
    Get the pos and img of a specific slot position in Inventory. Inventory must be open in the image.
    :param config: The config which should be used
    :param img: Image from screen.grab() not cut
    :param column: Column in the Inventory
    :param row: Row in the Inventory
    :return: Returns position and image of the cut area as such: [[x, y], img]
    """
    top_left_slot = (Config().ui_pos["inventory_top_left_slot_x"], Config().ui_pos["inventory_top_left_slot_y"])
    slot_width = Config().ui_pos["slot_width"]
    slot_height= Config().ui_pos["slot_height"]
    slot = (top_left_slot[0] + slot_width * column, top_left_slot[1] + slot_height * row)
    # decrease size to make sure not to have any borders of the slot in the image
    offset_w = int(slot_width * 0.12)
    offset_h = int(slot_height * 0.12)
    min_x = slot[0] + offset_w
    max_x = slot[0] + slot_width - offset_w
    min_y = slot[1] + offset_h
    max_y = slot[1] + slot_height - offset_h
    slot_img = img[min_y:max_y, min_x:max_x]
    center_pos = (int(slot[0] + (slot_width // 2)), int(slot[1] + (slot_height // 2)))
    return center_pos, slot_img

def slot_has_item(slot_img: np.ndarray) -> bool:
    """
    Check if a specific slot in the inventory has an item or not based on color
    :param slot_img: Image of the slot
    :return: Bool if there is an item or not
    """
    slot_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
    avg_brightness = np.average(slot_img[:, :, 2])
    return avg_brightness > 16.0

def detect_screen_object(screen_object: ScreenObject, img: np.ndarray = None) -> TemplateMatch:
    roi = Config().ui_roi[screen_object.roi] if screen_object.roi else None
    img = grab() if img is None else img
    match = TemplateFinder().search(
        ref = screen_object.ref,
        inp_img = img,
        threshold = screen_object.threshold,
        roi = roi,
        best_match = screen_object.best_match,
        use_grayscale = screen_object.use_grayscale,
        normalize_monitor = screen_object.normalize_monitor)
    if match.valid:
        return match
    return match

def select_screen_object_match(match: TemplateMatch) -> None:
    mouse.move(*convert_screen_to_monitor(match.center))
    wait(0.05, 0.09)
    mouse.click("left")
    wait(0.05, 0.09)

def wait_for_screen_object(screen_object: ScreenObject, time_out: int = None) -> TemplateMatch:
    roi = Config().ui_roi[screen_object.roi] if screen_object.roi else None
    time_out = time_out if time_out else 30
    match = TemplateFinder().search_and_wait(
        ref = screen_object.ref,
        time_out = time_out,
        threshold = screen_object.threshold,
        roi = roi,
        best_match = screen_object.best_match,
        use_grayscale = screen_object.use_grayscale,
        normalize_monitor = screen_object.normalize_monitor)
    if match.valid:
        return match
    return match

def hover_over_screen_object_match(match) -> None:
    mouse.move(*convert_screen_to_monitor(match.center))
    wait(0.2, 0.4)

# Testing: Move to whatever ui to test and run
if __name__ == "__main__":
    import keyboard
    from ui_components.vendor import gamble
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")
    print("Start")
    from config import Config
    game_stats = GameStats()
    item_finder = ItemFinder()
    ui_manager = UiManager(game_stats)
    gamble()
