# f: wait_for_loading_screen(self, time_out: float = None) -> bool:
# - door
# - blizz_splash
# - connect_to_bnet
# - queue
# - black_screen
# - others?

import time
import numpy as np

from template_finder import TemplateMatch
from ui_components import ScreenObject, Locator
from utils.misc import wait
from screen import Screen
from config import Config

@Locator(ref=["LOADING", "CREATING_GAME"], roi="difficulty_select", threshold=0.9)
class Loading(ScreenObject):
    def __init__(self, match: TemplateMatch) -> None:
        super().__init__(match)

def check_for_black_screen() -> bool:
    img = Screen().grab()
    return np.average(img[:, 0:Config().ui_roi["loading_left_black"][2]]) < 1.5

def wait_for_loading_screen(time_out: float = None) -> bool:
    """
    Waits until loading screen apears
    :param time_out: Maximum time to search for a loading screen
    :return: True if loading screen was found within the timeout. False otherwise
    """
    start = time.time()
    while True:
        is_loading_black_roi = check_for_black_screen()
        if is_loading_black_roi:
            return True
        if time_out is not None and time.time() - start > time_out:
            return False
