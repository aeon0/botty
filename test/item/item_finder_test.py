import pytest
import numpy as np
import cv2
from logger import Logger
from item.item_finder import ItemFinder, Item
from config import Config, ItemProps

class TestItemFinder:
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

        config = Config()
        config.items["misc_flawless_amethyst"] = ItemProps(pickit_type=1)
        config.items["uniq_armor_ormus_robes"] = ItemProps(pickit_type=1)
        config.items["rune_26_vex"] = ItemProps(pickit_type=1)
        config.items["misc_super_healing_potion"] = ItemProps(pickit_type=1)
        config.items["magic_small_charm"] = ItemProps(pickit_type=1)
        config.items["rare_stag_bow"] = ItemProps(pickit_type=1)
        self.item_finder = ItemFinder()

    @pytest.mark.parametrize("img_path, expected", [
        ("test/assets/item_finder.png", 6),
    ])
    def test_search(self, img_path: str, expected: int):
        inp_img = cv2.imread(img_path)
        item_list = self.item_finder.search(inp_img)
        assert(len(item_list) == expected)
