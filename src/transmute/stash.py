from collections import defaultdict
from .inventory_collection import InventoryCollection, InventoryItem

class Stash:
    def __str__(self) -> str:
        result = {}
        for tab in self._all_gems.keys():
            tab = defaultdict(int)
            for gem in self.get_by_tab(tab):
                tab[gem] += 1
            result[tab] = dict(tab)
        return result.__str__()

    def __init__(self) -> None:
        self._all_gems:defaultdict[str, InventoryCollection] = defaultdict(InventoryCollection)

    def add_tab(self, tab_index: int, inventory: InventoryCollection) -> None:
        self._all_gems[tab_index] = inventory

    def tab_count(self) -> int:
        return len(self._all_gems.keys())

    def append(self, tab: int, type: str, row: int, column: int):
        self._all_gems[tab].append_one_cell(InventoryItem(size=(1,1), type=type), row, column)

    def pop(self, tab: int, item: str):
        return self._all_gems[tab].pop_by_type(item)

    def get_by_tab(self, tab_index: int) -> InventoryCollection:
        return self._all_gems[tab_index]

    def get_empty_on_tab(self, tab_index: int) -> int:
        return self._all_gems[tab_index].get_empty_count()