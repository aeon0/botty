import pytest
from logger import Logger
from utils.misc import load_template
import utils.download_test_assets # downloads assets if they don't already exist, doesn't need to be called

class TestUtilsMisc:
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

    @pytest.mark.parametrize("path, should_be_success", [
        ("test/assets/hero_select.png", True),
        ("some/random/path/that/not/a/file.png", False),
    ])
    def test_load_template(self, path: str, should_be_success: bool):
        template_img = load_template(path)
        success = template_img is not None
        assert(success == should_be_success)
