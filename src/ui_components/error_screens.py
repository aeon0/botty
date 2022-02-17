# - server issues?
from template_finder import TemplateFinder, TemplateMatch
from ui_components import ScreenObject, Locator
from logger import Logger
from utils.misc import wait
import keyboard

@Locator(ref=["SERVER_ISSUES"])
class ServerError(ScreenObject):
    def __init__(self, template_finder: TemplateFinder, match: TemplateMatch) -> None:
        super().__init__(template_finder, match)

    @staticmethod
    def handle_error() -> bool:
        Logger.warning("Server connection issue. waiting 20s")
        ScreenObject.select_self()
        wait(1, 2)
        keyboard.send("esc")
        wait(18, 22)
