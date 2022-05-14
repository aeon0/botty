from version import __version__
from logger import Logger
from game_stats import GameStats
from bot import Bot
import template_finder
from mocks.screen_mock import ScreenMock


class TestSmoke:
    """
    Just import Bot and create an instance to ensure there is no major issue e.g. indent error
    """
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

    def test_smoke(self):
        screen = ScreenMock("test/assets/hero_select.png")
        game_stats = GameStats()
        bot = Bot(game_stats)
