
from collections import defaultdict
from functools import reduce

class InventoryCollection:
    def __init__(self) -> None:
        self._empty_cells = set()
        self._all_items = defaultdict(list)

    def __str__(self) -> str:
        return dict(self._all_items).__str__()

    def append(self, item: str, position: 'tuple(int, int)'):
        self._empty_cells.discard(position)
        self._all_items[item].append(position)

    def pop(self, item: str) -> 'tuple(int, int)':
        poped = self._all_items[item].pop()
        self._empty_cells.add(poped)
        return poped

    def set_empty(self, position: 'tuple(int, int)') -> None:
        self._empty_cells.add(position)

    def count_empty(self) -> int:
        return len(self._empty_cells)

    def count_by(self, item: str):
        return len(self._all_items[item])

    def count(self):
        return reduce(lambda x, y: x + self.count_by(y),
                      self._all_items.keys(), 0)

    def all_items(self):
        return filter(lambda key: len(self._all_items[key]) > 0, self._all_items.keys())
