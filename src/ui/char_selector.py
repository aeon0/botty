from config import Config
from utils.custom_mouse import mouse
from utils.misc import cut_roi, wait
from screen import Screen
from template_finder import TemplateFinder


class CharSelector:
    def __init__(self, screen: Screen, config: Config):
        self._config = config
        self._char_template = None
        self._screen = screen
        self._template_finder = TemplateFinder(screen)

    def has_char_template_saved(self):
        return self._char_template is not None

    def save_char_template(self):
        img = self._screen.grab()
        self._char_template = cut_roi(img, self._config.ui_roi["char_selection_top"])

    def select_char(self):
        if self._char_template is not None:
            template_result = self._template_finder.search(
                self._char_template,
                self._screen.grab(),
                threshold=0.8,
                roi=self._config.ui_roi["char_selection_all"], normalize_monitor=True
            )
            if template_result.valid:
                # move cursor to result and select
                mouse.move(*template_result.position)
                wait(0.5)
                mouse.click(button="left")
        return False


if __name__ == "__main__":
    import keyboard
    keyboard.wait("f11")
    from config import Config
    config = Config()
    screen = Screen(config.general["monitor"])
    selector = CharSelector(screen, config)
    if not selector.has_char_template_saved():
        selector.save_char_template()
    selector.select_char()
