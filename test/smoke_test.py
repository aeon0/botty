from game_stats import GameStats
from logger import Logger
from bot import Bot
from screen import Screen
from config import Config
import cv2


class ScreenMock(Screen):
    def grab(self):
        img = cv2.imread("test/hero_select.png")
        return img


class TestSmoke:
    """
    Just import Bot and create an instance to ensure there is no major issue e.g. indent error
    """
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

    def test_smoke(self):
        screen = ScreenMock()
        game_stats = GameStats()
        bot = Bot(screen, game_stats)
