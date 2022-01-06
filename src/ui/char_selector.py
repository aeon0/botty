from config import Config
from utils.custom_mouse import mouse
from utils.misc import cut_roi, wait
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch


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
        # TODO: check which character is currently selected rather than assuming the top one is the correct one
        self._char_template = cut_roi(img, self._config.ui_roi["char_selection_top"])

    def select_char(self):
        if self._char_template is not None:
            scrolls_attempts = 0
            template_result = TemplateMatch()
            coords = self._config.ui_roi["char_selection_all"]
            while not template_result.valid and scrolls_attempts < 2:  # 2 scrolls should suffice to see all possible characters
                template_result = self._template_finder.search(
                    self._char_template,
                    self._screen.grab(),
                    threshold=0.8,
                    roi=coords, normalize_monitor=True
                )
                if not template_result.valid:
                    # We can scroll the characters only if we have the mouse in the char names selection so move the mouse there
                    pos = self._screen.convert_screen_to_monitor((coords[0], coords[1]))
                    mouse.move(*pos)
                    wait(0.5)
                    mouse.wheel(-14)
                    scrolls_attempts += 1
                    wait(0.5)
                else:
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
    keyboard.wait("f11")
    selector.select_char()
