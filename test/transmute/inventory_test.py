from transmute import InventoryCollection


class TestInventory:

    def test_inventory(self):
        x = InventoryCollection()
        x.append("Gem1", (2, 3))
        assert(x.count() == 1)
        x.append("Gem2", (2, 4))
        assert(x.count() == 2)
        x.pop("Gem2")
        assert(x.count() == 1)
        assert(x.count_by("Gem2") == 0)
