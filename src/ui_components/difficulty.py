# normal
# nightmare
# hell
from template_finder import TemplateMatch
from ui_components import ScreenObject, Locator

@Locator(ref=["NORMAL_BTN"], roi="difficulty_select", threshold=0.9)
class Normal(ScreenObject):
    def __init__(self, match: TemplateMatch) -> None:
        super().__init__(match)

@Locator(ref=["NIGHTMARE_BTN"], roi="difficulty_select", threshold=0.9)
class Nightmare(ScreenObject):
    def __init__(self, match: TemplateMatch) -> None:
        super().__init__(match)

@Locator(ref=["HELL_BTN"], roi="difficulty_select", threshold=0.9)
class Hell(ScreenObject):
    def __init__(self, match: TemplateMatch) -> None:
        super().__init__(match)
