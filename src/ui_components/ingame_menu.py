import time
import keyboard
import mouse
from utils.misc import wait
from screen import Screen
from config import Config
from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator

@Locator(ref=["SAVE_AND_EXIT_NO_HIGHLIGHT","SAVE_AND_EXIT_HIGHLIGHT"], roi="save_and_exit", threshold=0.85)
class SaveAndExit(ScreenObject):
    def __init__(self, template_finder: TemplateFinder, match: TemplateMatch = TemplateMatch()) -> None:
        super().__init__(template_finder, match)
        self._template_finder = template_finder
        self._match = match

    def save_and_exit(self, does_chicken: bool = False) -> bool:
        """
        Performes save and exit action from within game
        :return: Bool if action was successful
        """
        start = time.time()
        while (time.time() - start) < 15:
            if not self._match.valid:
                _, m = self.detect(self._template_finder)
                if not m.valid:
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