# f: wait_for_loading_screen(self, time_out: float = None) -> bool:
# - door
# - blizz_splash
# - connect_to_bnet
# - queue
# - black_screen
# - others?

from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator

@Locator(ref=["LOADING"], roi="difficulty_select", threshold=0.9)
class Loading(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)