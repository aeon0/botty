import pytest
from logger import Logger
from game_stats import GameStats


class TestGameStats:
    def setup_method(self):
        Logger.init()
        Logger.remove_file_logger()
        self.game_stats = GameStats()

    @pytest.mark.parametrize("item_name, item_should_be_added", [
        ("some_magic_item", True),
        ("misc_jewel", True),
        ("misc_gold", False),
        ("some_potion", False),
        ("super_healing_potion", False),
    ])
    def test_adjust_abs_range_to_screen(self, item_name: str, item_should_be_added: bool):
        self.game_stats.update_location("test_location")
        previous_item_count = len(self.game_stats._location_stats["test_location"]["items"])
        self.game_stats.log_item_pickup(item_name, send_message=False)
        new_item_count = len(self.game_stats._location_stats["test_location"]["items"])
        item_was_added = previous_item_count < new_item_count
        assert(item_was_added == item_should_be_added)
