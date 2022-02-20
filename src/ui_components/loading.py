import time
import numpy as np
from screen import grab
from config import Config

def check_for_black_screen() -> bool:
    img = grab()
    return np.average(img[:, 0:Config().ui_roi["loading_left_black"][2]]) < 1.5

def wait_for_loading_screen(time_out: float = 10.0) -> bool:
    """
    Waits until loading screen apears
    :param time_out: Maximum time to search for a loading screen
    :return: True if loading screen was found within the timeout. False otherwise
    """
    start = time.time()
    while time.time() - start < time_out:
        if check_for_black_screen():
            return True
    return False
