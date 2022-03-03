from numpy import size
from transmute import InventoryCollection, InventoryCollection2
from transmute.inventory_collection import InventoryItem


class TestInventory:
    def test_inventory2(self):
        x = InventoryCollection2(10, 10)
        x.append_one_cell(InventoryItem("Gem1", (1, 1)), 2, 3)
        assert x.get_item_count() == 1
        x.append_one_cell(InventoryItem("Gem2", (1, 1)), 2, 4)
        assert x.get_item_count() == 2
        x.pop_by_type("Gem2")
        assert x.get_item_count() == 1
        assert x.get_item_count(type="Gem2") == 0

    def test_inventory(self):
        x = InventoryCollection()
        x.append("Gem1", (2, 3))
        assert x.count() == 1
        x.append("Gem2", (2, 4))
        assert x.count() == 2
        x.pop("Gem2")
        assert x.count() == 1
        assert x.count_by("Gem2") == 0
