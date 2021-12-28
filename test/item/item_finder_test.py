import pytest
import numpy as np
from logger import Logger
from item.item_finder import ItemFinder
from config import Config


class TestItemFinder:
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()

        config = Config()
        self.item_finder = ItemFinder(config)

    @pytest.mark.parametrize("test_input, expected", [
        (
            ["unique_ring", "some_potion", "rare_amulet", "misc_gold", "unique_amulet", "rune_xyz"],
            ["rune_xyz", "unique_ring", "unique_amulet", "rare_amulet", "some_potion", "misc_gold"],
        ),
    ])
    def test_sort_items(self, test_input: list[str], expected: list[str]):
        items_sorted = self.item_finder.sort_items(test_input)
        assert(np.array_equal(items_sorted, expected))
