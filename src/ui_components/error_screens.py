# - server issues?
from screen import Screen
from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator

@Locator(ref=["SERVER_ISSUES"])
class ServerError(ScreenObject):
    def __init__(self, screen: Screen, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(screen, template_finder, match)
