from collections import defaultdict
from dataclasses import dataclass, field
from re import L
from typing import ClassVar, Union

from functools import reduce
import itertools

from config import Config
from screen import grab
import cv2
import numpy as np
from template_finder import TemplateFinder


def _is_slot_empty(img, treshold=16.0):
    slot_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    avg_brightness = np.average(slot_img[:, :, 2])
    return avg_brightness > treshold


@dataclass
class InventoryItem:
    _ItemCounter: ClassVar[int] = 0
    id: int = field(init=False)
    type: str
    size: "tuple[int, int]"
    # can add more properties later

    def __post_init__(self):
        InventoryItem._ItemCounter += 1
        self.id = InventoryItem._ItemCounter


class InventoryCollection2:
    # Internal state of this class is represented by a virtual grid rows x columns and items mapped to that grid
    # We track ids of the items against the grid but also keep a reverse index from id to Item and to it's position

    def __init__(self, rows, columns) -> None:
        self._grid = np.ndarray((rows, columns), int)
        self._grid.fill(-1)
        self._items_by_type = defaultdict(list)
        self._items = dict()

    def append(self, item: InventoryItem, placement: "tuple[int, int, int, int]"):
        row_min, row_max, col_min, col_max = placement
        self._grid[row_min:row_max, col_min:col_max].fill(item.id)
        self._items_by_type[item.type].append(item)
        self._items[item.id] = item

    def append_one_cell(self, item: InventoryItem, row: int, col: int):
        self.append(item, (row, row + 1, col, col + 1))

    def _remove_from_grid(self, item: InventoryItem):
        self._grid = np.where(self._grid == item.id, -1, self._grid)

    def pop_by_type(self, type: str) -> InventoryItem:
        item: InventoryItem = self._items_by_type[type].pop()
        self._remove_from_grid(item)
        self._items.pop(item.id)
        return item

    def pop_item(self, item: InventoryItem):
        self._items_by_type[item.type].remove(item)
        self._items.pop(item.id)
        self._remove_from_grid(item)

    def get_item_at(self, row: int, col: int) -> "Union[None, InventoryItem]":
        item_id = self._grid[row, col]
        if item_id >= 0:
            return self._items[item_id]
        return None

    def get_item_count(self, type=None):
        if type is None:
            return len(self._items)
        return len(self._items_by_type[type])


class InventoryCollection:
    def __init__(self) -> None:
        self._empty_cells = set()
        self._all_items = defaultdict(list)

    def __str__(self) -> str:
        return dict(self._all_items).__str__()

    def append(self, item: str, position: "tuple(int, int)"):
        self._empty_cells.discard(position)
        self._all_items[item].append(position)

    def pop(self, item: str) -> "tuple(int, int)":
        poped = self._all_items[item].pop()
        self._empty_cells.add(poped)
        return poped

    def set_empty(self, position: "tuple(int, int)") -> None:
        self._empty_cells.add(position)

    def count_empty(self) -> int:
        return len(self._empty_cells)

    def count_by(self, item: str):
        return len(self._all_items[item])

    def count(self):
        return reduce(lambda x, y: x + self.count_by(y), self._all_items.keys(), 0)

    def all_items(self):
        return filter(lambda key: len(self._all_items[key]) > 0, self._all_items.keys())


def inspect_area(total_rows, total_columns, roi, known_items) -> InventoryCollection:
    result = InventoryCollection()
    x, y, w, h = roi
    img = grab()[y : y + h, x : x + w]
    slot_w = Config.ui_pos["slot_width"]
    slot_h = Config.ui_pos["slot_height"]
    for column, row in itertools.product(range(total_columns), range(total_rows)):
        y_start, y_end = row * slot_h, slot_h * (row + 1)
        x_start, x_end = column * slot_w, slot_w * (column + 1)
        slot_img = img[y_start:y_end, x_start:x_end]
        if not _is_slot_empty(slot_img[+4:-4, +4:-4], treshold=36):
            result.set_empty((column, row))

        if len(known_items) > 0:
            match = TemplateFinder().search(
                known_items, slot_img, threshold=0.91, best_match=True
            )

            if match.valid:
                result.append(match.name, (column, row))

    return result
