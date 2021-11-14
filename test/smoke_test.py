from logger import Logger
from bot import Bot


class TestSmoke:
    """
    Just import Bot and create an instance to ensure there is no major issue e.g. indent error
    """
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

    def test_smoke(self):
        bot = Bot()
        assert(0 == 1)

    def test_x(self):
        assert(0 == 0)
