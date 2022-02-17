# f: wait_for_loading_screen(self, time_out: float = None) -> bool:
# - door
# - blizz_splash
# - connect_to_bnet
# - queue
# - black_screen
# - others?

import time
import numpy as np

from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator
from utils.misc import wait
from screen import Screen
from config import Config

@Locator(ref=["LOADING", "CREATING_GAME"], roi="difficulty_select", threshold=0.9)
class Loading(ScreenObject):
    def __init__(self, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(template_finder, match)

def wait_for_loading_screen(time_out: float = None) -> bool:
    """
    Waits until loading screen apears
    :param time_out: Maximum time to search for a loading screen
    :return: True if loading screen was found within the timeout. False otherwise
    """
    start = time.time()
    while True:
        img = Screen().grab()
        is_loading_black_roi = np.average(img[:, 0:Config().ui_roi["loading_left_black"][2]]) < 1.5
        if is_loading_black_roi:
            return True
        if time_out is not None and time.time() - start > time_out:
            return False