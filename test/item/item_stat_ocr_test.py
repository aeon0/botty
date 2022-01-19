import pytest
import numpy as np
import cv2
from logger import Logger
from item.item_stat_ocr import ItemStatOCR
from utils.misc import load_template

class TestItemStatOcr:
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

        self.reader = ItemStatOCR()

    @pytest.mark.parametrize("img_path", [
        ("test/assets/item_stat_ocr.png"),
    ])
    def test_read_magic_find(self, img_path: str):
        inp_img = cv2.imread(img_path)

        template_img = load_template("assets/item_properties/getting_magic_items.png", 1.0, True)
        template_np = cv2.cvtColor(template_img, cv2.COLOR_BGRA2BGR)

        results = self.reader.read_line(inp_img, ref=template_np, max_dist_left=250)

        assert(len(results) > 0)
        assert(results[0] == 112)
