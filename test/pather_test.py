import pytest
from logger import Logger
from pather import Pather
import screen
import cv2

MONITOR_ROI = {'left': 0, 'top': 0, 'width': 1280, 'height': 720}

class TestPather:
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

        self.pather = Pather()

    @pytest.mark.parametrize("test_input, expected", [
        ((90, 90), True),
        ((25, 70), True),
        ((150, 120), False),
        ((500, 400), False),
        ((400, 1300), True),
    ])
    def test_adjust_abs_range_to_screen(self, test_input, expected, mocker):
        mocker.patch.object(screen, 'monitor_roi', MONITOR_ROI)
        should_be_adapted = expected
        pos_abs = screen.convert_screen_to_abs(test_input)
        new_pos_abs = self.pather._adjust_abs_range_to_screen(pos_abs)
        is_adapted = new_pos_abs != pos_abs
        assert(should_be_adapted == is_adapted)
        new_pos_abs_2 = self.pather._adjust_abs_range_to_screen(new_pos_abs)
        assert(new_pos_abs == new_pos_abs_2)
