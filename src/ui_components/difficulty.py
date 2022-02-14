# normal
# nightmare
# hell
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator

@Locator(ref=["NORMAL_BTN"], roi="difficulty_select", threshold=0.9)
class Normal(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)

@Locator(ref=["NIGHTMARE_BTN"], roi="difficulty_select", threshold=0.9)
class Nightmare(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)

@Locator(ref=["HELL_BTN"], roi="difficulty_select", threshold=0.9)
class Hell(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)
