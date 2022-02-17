import keyboard
import os
import numpy as np
from utils.custom_mouse import mouse
from utils.misc import wait
from logger import Logger
from config import Config
from screen import grab, convert_screen_to_monitor
from item import ItemFinder
from template_finder import TemplateFinder, TemplateMatch
from messages import Messenger
from game_stats import GameStats
from ui.screen_objects import ScreenObject

messenger = Messenger()
game_stats = GameStats()

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
    gamble()
