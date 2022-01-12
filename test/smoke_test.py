from version import __version__
from logger import Logger
from game_stats import GameStats
from bot import Bot
from template_finder import TemplateFinder
from mocks.screen_mock import ScreenMock
from config import Config


class TestSmoke:
    """
    Just import Bot and create an instance to ensure there is no major issue e.g. indent error
    """
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

    def test_smoke(self):
        screen = ScreenMock()
        config = Config()
        game_stats = GameStats(config)
        template_finder = TemplateFinder(screen)
        bot = Bot(screen, game_stats, template_finder)
