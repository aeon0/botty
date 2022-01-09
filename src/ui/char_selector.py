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

    def save_char_template(self) -> bool:
        img = self._screen.grab()
        matched_template = self._template_finder.search(
            "CHARACTER_SELECTION_RECTANGLE",
            self._screen.grab(),
            normalize_monitor=True,
            filters=[self._config.filters['character_selection_rectangle']])
        if matched_template.valid:
            template_shape = self._template_finder.get_template("CHARACTER_SELECTION_RECTANGLE").shape
            matched_template_top_left = self._screen.convert_monitor_to_screen(
                (matched_template.position[0] - template_shape[1]/2, matched_template.position[1] - template_shape[0]/2))
            # Remove golden border and fit into char_selection_all roi
            self._char_template = cut_roi(img,
                                          (self._config.ui_roi["char_selection_all"][0], int(matched_template_top_left[1]) + 23, template_shape[1] - 42, template_shape[0] - 32))
            return True
        return False

    def select_char(self) -> bool:
        if self._char_template is not None:
            scrolls_attempts = 0
            template_result = TemplateMatch()
            coords = self._config.ui_roi["char_selection_all"]
            while scrolls_attempts < 3:  # 3 scrolls should suffice to see all possible characters
                template_result = self._template_finder.search(
                    self._char_template,
                    self._screen.grab(),
                    threshold=0.9,
                    roi=coords, normalize_monitor=True
                )
                if template_result.valid:
                    # move cursor to result and select
                    mouse.move(*template_result.position)
                    wait(0.5)
                    mouse.click(button="left")
                    return True
                else:
                    # We can scroll the characters only if we have the mouse in the char names selection so move the mouse there
                    pos = self._screen.convert_screen_to_monitor((coords[0]+40, coords[1]+20))
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
    screen = Screen(config.general["monitor"])
    selector = CharSelector(screen, config)
    if not selector.has_char_template_saved():
        if selector.save_char_template():
            print('template saved')
    keyboard.wait("f11")
    selector.select_char()
