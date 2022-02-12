from screen import Screen
from template_finder import TemplateFinder
from config import Config

class ScreenObject():

    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._template_finder = template_finder
        self._screen = screen

    def detect(self, *args, **kwargs):
        result = self._template_finder(**args, **kwargs)
        pass