import time
import keyboard
import mouse
from utils.misc import wait
from screen import Screen
from config import Config
from template_finder import TemplateFinder


def save_and_exit(does_chicken: bool = False) -> bool:
    """
    Performes save and exit action from within game
    :return: Bool if action was successful
    """
    start = time.time()
    while (time.time() - start) < 15:
        templates = ["SAVE_AND_EXIT_NO_HIGHLIGHT","SAVE_AND_EXIT_HIGHLIGHT"]
        if not TemplateFinder().search(templates, Screen().grab(), roi=Config().ui_roi["save_and_exit"], threshold=0.85).valid:
            keyboard.send("esc")
        wait(0.3)
        exit_btn_pos = (Config().ui_pos["save_and_exit_x"], Config().ui_pos["save_and_exit_y"])
        x_m, y_m = Screen().convert_screen_to_monitor(exit_btn_pos)
        mouse.move(x_m, y_m)
        wait(0.05)
        mouse.click(button="left")
        wait(0.05)
        mouse.click(button="left")
        wait(0.1, 0.5)
        return True
    return False
