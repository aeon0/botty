from config import Config
from utils.custom_mouse import mouse
from utils.misc import cut_roi, wait
from screen import Screen
from template_finder import TemplateFinder


class CharSelector:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._char_template = None
        self._screen = screen
        self._template_finder = template_finder

    def has_char_template_saved(self):
        return self._char_template is not None

    def save_char_template(self):
        img = self._screen.grab()
        # TODO: check which character is currently selected rather than assuming the top one is the correct one
        self._char_template = cut_roi(img, self._config.ui_roi["char_selection_top"])

    def select_char(self):
        if self._char_template is not None:
            scrolls_attempts = 0
            while scrolls_attempts < 2:  # 2 scrolls should suffice to see all possible characters
                template_result = self._template_finder.search(
                    self._char_template,
                    self._screen.grab(),
                    threshold=0.8,
                    roi=self._config.ui_roi["char_selection_all"],
                    normalize_monitor=True
                )
                if template_result.valid:
                    # move cursor to result and select
                    mouse.move(*template_result.position)
                    wait(0.5)
                    mouse.click(button="left")
                    break
                else:
                    # We can scroll the characters only if we have the mouse in the char names selection so move the mouse there
                    pos = (self._config.ui_pos["char_selection_center_x"], self._config.ui_pos["char_selection_center_y"])
                    pos = self._screen.convert_screen_to_monitor(pos)
                    mouse.move(*pos)
                    wait(0.5)
                    mouse.wheel(-14)
                    scrolls_attempts += 1
                    wait(0.5)
        return False


if __name__ == "__main__":
    import keyboard
    keyboard.wait("f11")
    from config import Config
    config = Config()
    screen = Screen()
    tf = TemplateFinder(screen)
    selector = CharSelector(screen, tf)
    if not selector.has_char_template_saved():
        selector.save_char_template()
    selector.select_char()
