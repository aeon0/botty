from transmute import Stash
from transmute.inventory_collection import InventoryCollection


class TestStash:
    def test_tab_count(self):
        s = Stash()
        s.add_tab(0, InventoryCollection(10, 10))
        assert s.tab_count() == 1
    
    def test_empty_count_after_append(self):
        s = Stash()
        s.add_tab(0, InventoryCollection(10, 10))
        s.append(0, "Gem", 2, 5)
        assert s.get_empty_on_tab(0) == 99

    def test_pop(self):
        s = Stash()
        s.add_tab(0, InventoryCollection(10, 10))
        s.append(0, "Gem", 2, 5)
        row, _, col, _ = s.pop(0, "Gem")
        assert (row, col) == (2, 5)
        assert s.get_empty_on_tab(0) == 100
    
